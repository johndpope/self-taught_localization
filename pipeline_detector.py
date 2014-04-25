import cPickle as pickle
import bsddb
import gc
import glob
import logging
import numpy as np
import os
import os.path
import sys
import scipy.misc
import scipy.io
import skimage.io
import tempfile
from vlg.util.parfun import *

from detector import *
from featextractor import *
from heatextractor import *
from util import *
from stats import *

class PipelineDetectorParams:

    def __init__(self):
        """
        Default parameters.
        Note: all the parameters "None" are mandatory and must be filled out.
        """

        # *******************  MANDATORY PARAMETERS TO SET *******************

        # Input directory, containing the AnnotatedImages in Pickle2 format.
        # The pipeline expects a file for each <key> (i.e. <key>.pkl).
        # The AnnotatedImages might contain the features as well.
        self.input_dir = None
        # Output directory for the pipeline. The output directory contains
        # the following elements:
        #   category_dog/ // a directory for each category
        #     iter0.pkl   // containing the PipelineDetector object of the
        #     ...         // completed iterations.
        #     iter5.pkl        
        self.output_dir = None
        # experiment name. used for the job names
        self.exp_name = None
        # Text file, containing the classes to elaborate.
        self.categories_file = None
        # Directory containing the splits. It is expected to contain
        # to text files for each class:
        #   <class>_train.txt   defining the training set
        #   <class>_test.txt    defining the test set
        # Each line of these two textfiles is in the format '<key> <+1/-1>'.
        self.splits_dir = None

        # FeatureExtractor module to use (parameters object)
        self.feature_extractor_params = None
        # Detector module to use (parameters object)
        self.detector_params = None
        # which field of AnnotatedImage.pred_objects the pipeline should use
        # for the bboxes used at prediction time, as well as to compose the
        # negative set. We expect the selected dictionary to have a single
        # class.
        self.field_name_for_pred_objects_in_AnnotatedImage = None

        # *******************  OPTIONAL PARAMETERS TO SET *******************
        
        # Run the script on Anthill
        self.run_on_anthill = False
        # Number of cores
        self.num_cores = 1

        # number of iterations to perform
        self.num_iterations = 3 
        # max total number of negative bbox per image
        self.max_num_neg_bbox_per_image = 10       
        # num of negative bbox per image to add during the iterations
        self.num_neg_bboxes_to_add_per_image_per_iter = 1
        # num of negative bboxes from a positive image to add during the init
        self.num_neg_bboxes_per_positive_image_during_init = 5
        # thresholds to define duplicate boxes for the evaluation
        self.threshold_duplicates = 0.3
        # max number of positive images per category
        self.max_train_pos_images_per_category = sys.maxint
        # max number of negative images per category
        self.max_train_neg_images_per_category = sys.maxint

#==============================================================================

class PipelineImage:
    def __init__(self, key, label, fname, feature_extractor_params):
        # check input
        assert isinstance(key, str)
        assert isinstance(label, int)
        assert isinstance(fname, str)
        assert isinstance(feature_extractor_params, FeatureExtractorParams)
        # the key of the image
        self.key = key
        # the label (+1, -1)
        self.label = label
        # the full pathname of the associated AnnotatedImage
        self.fname = fname
        # the parameters to use for the feature extractor module
        self.feature_extractor_params = feature_extractor_params
        # The list of bounding boxes to use for prediction
        # (as well as for the neg set)
        # Each element of this list is 2-elements-list of the format:
        # [Bbox, True/False] where the confidence value of the Bbox indicates
        # the confidence of the bbox given the model learned in the
        # previous iteration, and boolean value indicates whether
        # or not the bbox has been already used as a negative example.
        self.bboxes = []
        # the annotated image
        self.ai_ = None

    def get_ai(self):
        """
        Returns the associated AnnotatedImage.
        """
        if not self.ai_:
            # load the image from the disk
            fd = open(self.fname, 'r')
            self.ai_ = pickle.load(fd)
            fd.close()
            # TODO. This is a pure hack. The AnnotatedImage.feature_extractor_
            #       should not be pickled.
            self.ai_.feature_extractor_ = None
            # register the feature extractor
            self.ai_.register_feature_extractor(self.feature_extractor_params)
        return self.ai_

    def save_ai(self):
        """
        Dump the AnnotatedImage to the disk, overwriting the old one.
        """
        fd = open(self.fname, 'wb')
        pickle.dump(self.ai_, fd, protocol=2)
        fd.close()

    def clear_ai(self):
        """
        Clear the (eventually) loaded AnnotedImage from the memory
        """
        self.ai_ = None
        gc.collect()
            
#==============================================================================

def pipeline_single_detector(cl, params):        
    detector = PipelineDetector(cl, params)
    detector.train_evaluate()
    return 0
    
class PipelineDetector:
    def __init__(self, category, params):
        # check the input parameters
        assert isinstance(category, str)
        assert isinstance(params, PipelineDetectorParams)
        # check that all the mandatory PipelineDetectorParams were set
        params.input_dir != None
        params.output_dir != None
        params.exp_name != None
        params.categories_file != None
        params.splits_dir != None
        params.feature_extractor_params != None
        params.detector_params != None
        params.field_name_for_pred_objects_in_AnnotatedImage != None
        # init
        self.category = category
        self.params = params
        self.train_set = None
        self.test_set = None
        self.detector_output_dir = '{0}/{1}'.format(params.output_dir, category)
        self.iteration = 0
        self.detector = Detector.create_detector(params.detector_params)

    def init(self):
        # create output directory for this detector
        if os.path.exists(self.detector_output_dir) == False:
            os.makedirs(self.detector_output_dir)           
        # read the training set
        fname = '{0}/{1}_train.txt'.format(params.splits_dir, category)
        key_label_list = self.read_key_label_file_( \
                              fname, params.max_train_pos_images_per_category, \
                              params.max_train_neg_images_per_category)
        self.train_set = self.create_pipeline_images_(key_label_list, params)
        # read the test set
        fname = '{0}/{1}_test.txt'.format(params.splits_dir, category)
        key_label_list = self.read_key_label_file_(fname, sys.maxint, sys.maxint)
        self.test_set = self.create_pipeline_images_(key_label_list, params)
        # check: make sure all the files exists
        error = False
        for pi in (self.train_set + self.test_set):
            if not os.path.exists(pi.fname):
                error = True
                logging.info('The file {0} does not exist'.format(pi.fname))
        assert not error, 'Some required files were not found. Abort.'        

    def train_evaluate(self):
        for iteration in range(self.params.num_iterations):
            self.iteration = iteration
            logging.info('Iteration {0}'.format(iteration))
            # check if we already trained the model for this iteration
            fname = '{0}/iter{1}.pkl'.format(self.detector_output_dir, iteration)
            if os.path.exists(fname):                
                # load the current detector
                logging.info('The model for the iteration {0} already exists.'\
                             'We load it: {1}'.format(iteration, fname))
                self.load(fname)
                assert iteration == self.iteration
            else:
                # train the detector and save the model
                logging.info('Training the  model for the iteration {0}.'\
                             .format(iteration))
                self.train()
                logging.info('Saving the model to {0}'.format(fname))
                self.save(fname)
            # check if we have already evaluated the model for this iteration
            fname = '{0}/iter_stats{1}.pkl'.format( \
                    self.detector_output_dir, iteration)
            if os.path.exists(fname):
                logging.info('The stats file for iteration {0} already '\
                             'exists: {1}'.format(iteration, fname))
            else:
                logging.info('Evaluation the model of iteration {0}'.format( \
                             iteration))
                stats = self.evaluate()
                pickle.dump(fname, stats)

    def train(self):
        """ Train an iteration of the detector """
        Xtrain = None
        Ytrain = None
        idx = 0
        for pi in self.train_set:
            logging.info('Elaborating train key: {0}'.format(pi.key))
            assert (pi.label == 1) or (pi.label == -1)
            # get the AnnotatedImage
            ai = pi.get_ai()
            # evaluate the model learned in the previous iteration
            if self.iteration > 0:
                for bb in pi.bboxes:
                    feat = ai.extract_features(bb[0])
                    bb[0].confidence = self.detector.predict(feat)
            # sample positive and negative bboxes
            pos_bboxes = []
            if pi.label == 1:
                # *********  POSITIVE IMAGE  ********
                pos_bboxes = ai.gt_objects[self.category]
                if self.iteration == 0:
                    self.mark_bboxes_sligtly_overlapping_with_pos_bboxes_( \
                        pos_bboxes, pi.bboxes, \
                        self.params.num_neg_bboxes_per_pos_image_during_init)
                else:
                    # TODO. add negative examples from the positive image?
                    #       For now, do nothing.
                    pass
            elif pi.label == -1:
                # ********* NEGATIVE IMAGE **********
                nmax = self.params.num_neg_bboxes_to_add_per_image_per_iter
                if self.iteration == 0:
                    # we pick a bunch of randomly-selected bboxes
                    idxperm = util.randperm_deterministic(len(pi.bboxes))
                    for i in range(min(len(idxperm), nmax)):
                        pi.bboxes[idxperm[i]][1] = True
                else:
                    # we sort the bboxes by confidence score
                    pi.bboxes = sorted(pi.bboxes, \
                                         key=lambda x: -x[0].confidence)
                    # we pick the top ones that have not been already selected
                    num_neg_bboxes = len([1 for x in pi.bboxes if x[1]==True])
                    # REMOVE num_neg_bboxes = len(filter(pi.bboxes, lambda x: x[1]))
                    nmax -= num_neg_bboxes
                    n = 0
                    for bb in pi.bboxes:
                        if (n < nmax) and (not bb[1]):
                            bb[1] = True
                            n += 1
            # add the features
            for bb in pos_bboxes:
                Xtrain[idx, :] = ai.extract_features(bb)
                Ytrain[idx] = 1
                idx += 1
            for bb in [b for b in pi.bboxes if b[1]]:
                Xtrain[idx, :] = ai.extract_features(bb[0])
                Ytrain[idx] = -1
                idx += 1
            # clear the AnnotatedImage
            pi.clear_ai()
        # resize the buffer
        Xtrain = Xtrain[0:idx, :]
        Ytrain = Ytrain[0:idx]
        # train the detector
        self.detector.train(Xtrain, Ytrain)
        
    def evaluate(self):
        for pi in self.test_set:
            logging.info('Elaborating test key: {0}'.format(pi.key))
            # get the AnnotatedImage
            ai = pi.get_ai()
            # evaluate the learned model
            for bb in pi.bboxes:
                feat = pi.get_ai().extract_features(bb[0])
                bb[0].confidence = self.detector.predict(feat)
            # create a dummy AnnotatedImage, without features
            ai2 = copy.deepcopy(ai)
            ai2.features = None
            # TODO complete it with Loris
        return Stats()
    
    def create_train_buffer_(self, num_dims):
        """ Create an appropriate matrix that will be able to contain
        for sure the entire training set for the detector.
        It return Xtrain, Ytrain"""
        MAX_NUM_POS_BBOXES_PER_IMAGE = 30
        num_pos_images = len([pi for pi in self.train_set if pi.label==1])
        buffer_size = num_pos_images*MAX_NUM_POS_BBOXES_PER_IMAGE \
                    + self.params.max_num_neg_bbox_per_image*len(self.train_set)
        Xtrain = np.ndarray(shape=(buffer_size,num_dims), dtype=float)
        Ytrain = np.ndarray(shape=(buffer_size,1), dtype=float)
        return Xtrain, Ytrain

    def load(self, fname):
        """ Load from a Pickled file, and substitute the current fields """
        fd = open(fname, 'r')
        pd = pickle.load(fd)
        fd.close()
        assert self.category == pd.category
        self.params = pd.params
        self.train_set = pd.train_set
        self.test_set = pd.test_set
        assert self.detector_output_dir == pd.detector_output_dir
        self.iteration = pd.iteration
        self.detector = pd.detector
        
    def save(self, fname):
        """ Pickle and save the current object to a file """
        fd = open(fname, 'wb')
        pickle.dump(self, fd, protocol=2)
        fd.close()

    @staticmethod
    def mark_bboxes_sligtly_overlapping_with_pos_bboxes_( \
                            pos_bboxes, bboxes, max_num_bboxes):
        """
        Mark the bboxes that sligtly overlap with the pos bboxes.
        If there are too many bboxes, we
        randomly-chosen subset of 'max_num_bboxes' bboxes.
        Input: pos_bboxes: is a list of BBox objects.
               bboxes: is a list of [BBox, False] 2-elems-lists
        Output: Nothing.
        """
        # check input
        for bb in pos_bboxes:
            assert isinstance(bb, BBox)
        for bb in bboxes:
            assert isinstance(bb, list)
            assert isinstance(bb[0], BBox)
            assert bb[1] == False
        assert max_num_bboxes > 0
        out = []
        MIN_OVERLAP = 0.2
        MAX_OVERLAP = 0.5
        MAX_OVERLAP_WITH_POS = 0.5
        NMS_OVERLAP = 0.7
        # select the bboxes that have an overlap between 0.2 and 0.5
        # with any positive
        for bb in bboxes:
            for pos_bb in pos_bboxes:
                overlap = bb[0].jaccard_similarity(pos_bb)
                if (overlap >= MIN_OVERLAP) and (overlap <= MAX_OVERLAP):
                    out.append(bb)
                    break
        # remove the bboxes that overlap too much with a positive
        # (this might happen when there are >1 pos objs per image)
        out2 = []
        for bb in out:
            remove_bb = False
            for pos_bb in pos_bboxes:
                overlap = bb[0].jaccard_similarity(pos_bb)
                if overlap > MAX_OVERLAP_WITH_POS:
                    remove_bb = True
                    break
            if not remove_bb:
                out2.append(bb)
        out = out2
        # randomly shuffle 
        out = [out[i] for i in util.randperm_deterministic(len(out))]        
        # remove near-duplicates
        out2 = []
        while len(out) > 0:
            bb = out.pop()
            out2.append(bb)
            out = [bb2 for bb2 in out \
                   if bb[0].jaccard_similarity(bb2[0]) <= NMS_OVERLAP]
        out = out2
        # mark the bboxes to keep
        for i in range(min(len(out), max_num_bboxes)):
            out[i][1] = True
                
    @staticmethod
    def create_pipeline_images_(key_label_list, params):
        """
        Input: list of (<key>, <+1/-1>), and PipelineDetectorParams.
        Output: list of PipelineImage
        """
        assert isinstance(key_label_list, list)
        assert isinstance(params, PipelineDetectorParams)
        out = []
        for key_label in key_label_list:
            key, label = key_label
            pi = PipelineImage( \
                    key, label, '{0}/{1}.pkl'.format(params.input_dir, key), \
                    params.feature_extractor_params)
            # bboxes field
            name = params.field_name_for_pred_objects_in_AnnotatedImage
            ai = pi.get_ai()
            assert len(ai.pred_objects[name]) == 1
            for label in ai.pred_objects[name]:
                for bb in ai.pred_objects[name][label].bboxes:
                    pi.bboxes.append( [bb, False] )
            # append the PipelineImage
            out.append(pi)
        return out
                
    @staticmethod
    def read_key_label_file_(fname, max_pos_examples, max_neg_examples):
        """
        Read a text file each line being '<key> <+1/-1>'.
        We select randomly at most max_pos_examples and max_neg_examples.
        Returns a list of tuples (<key>, <+1/-1>) where key is a string.
        The list is randomly shuffled.
        """
        assert isinstance(fname, str)
        assert max_pos_examples >= 0
        assert max_neg_examples >= 0
        out = []
        # read the file
        pos_set = []
        neg_set = []        
        fd = open(fname, 'r')
        for line in fd:
            elems = line.strip().split()
            assert len(elems)==2
            key, label = elems
            if int(label) == 1:
                pos_set.append(key)
            elif int(label) == -1:
                neg_set.append(key)
            else:
                raise ValueError('The label {0} is not recognized'.format(label))
        fd.close()
        # subsample randomly the set
        idx_pos = randperm_deterministic(len(pos_set))
        idx_pos = idx_pos[0:min(len(idx_pos), max_pos_examples)]
        idx_neg = randperm_deterministic(len(neg_set))
        idx_neg = idx_neg[0:min(len(idx_neg), max_neg_examples)]
        for i in idx_pos:
            out.append( (pos_set[i], 1) )
        for i in idx_neg:
            out.append( (neg_set[i], -1) )
        # shuffle randomly the set
        idxperm = randperm_deterministic(len(out))
        return [out[i] for i in idxperm]
                
    @staticmethod
    def train_evaluate_detectors(params):
        """
        Train a set of detectors.
        """
        # create output directory
        if os.path.exists(params.output_dir) == False:
            os.makedirs(params.output_dir)        
        # read the list of classes to elaborate
        classes = []
        fd = open(params.classes_file, 'r')
        for line in fd:
            classes.append(line.strip())
        fd.close()
        logging.info('Loaded {0} classes'.format(len(classes)))
        # run the pipeline
        parfun = None
        if params.run_on_anthill:
            jobname = 'Job{0}'.format(params.exp_name).replace('exp','')
            parfun = ParFunAnthill(pipeline, time_requested=10, \
                                   memory_requested=4, job_name=jobname)
        else:
            parfun = ParFunDummy(pipeline_single_detector)
        for cl in classes:
            parfun.add_task(cl, params)
        out = parfun.run()
        for i, val in enumerate(out):
            if val != 0:
                logging.info('Task {0} didn''t exit properly'.format(i))
        logging.info('End of the script')


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

        # Input directories, containing the AnnotatedImages in Pickle2 format.
        # The pipeline expects a file for each <key> (i.e. <key>.pkl).
        # The AnnotatedImages might contain the features as well.
        # For differentiating the directories for training and test, see below.
        self.input_dir_train = None
        self.input_dir_test = None
        # Output directory for the pipeline. The output directory contains
        # the following elements:
        #   category_dog/ // a directory for each category
        #     iter0.pkl   // containing the PipelineDetector object of the
        #     ...         // completed iterations.
        #     iter5.pkl        
        self.output_dir = None
        # Text file, containing the classes to elaborate.
        self.categories_file = None
        # Directory containing the splits. It is expected to contain
        # to text files for each class:
        #   <class>_train.txt   defining the training set
        #   <class>_test.txt    defining the test set
        # Each line of these two textfiles is in the format '<key> <+1/-1>'.
        # The suffix 'train' and 'test' can be changed, see options below.
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
        # experiment name. used for the job names
        self.exp_name = None
        # categories to learn (None means everything)
        self.categories_to_process = None

        # name of the split for the training set
        self.split_train_name = 'train'
        # name of the split for the testing set
        self.split_test_name = 'test'
        
        # number of iterations to perform
        self.num_iterations = 3 
        # max total number of negative bbox per image
        self.max_num_neg_bbox_per_image = 10       
        # num of negative bbox per image to add during the iterations
        self.num_neg_bboxes_to_add_per_image_per_iter = 1
        # num of negative bboxes from a positive image to add during the init
        self.num_neg_bboxes_per_pos_image_during_init = 5
        # thresholds to define duplicate boxes for the evaluation
        self.threshold_duplicates = 0.3
        # max number of positive images per category
        self.max_train_pos_images_per_category = sys.maxint
        # max number of negative images per category
        self.max_train_neg_images_per_category = sys.maxint

#==============================================================================

class PipelineImage:
    def __init__(self, key, label, fname, feature_extractor_params, \
                 field_name_for_pred_objects_in_AnnotatedImage=None):
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
        #
        # Note: for efficiency we defer the filling of this field to later,
        #  while loading for the first time the AnnotatedImage.
        #  Therefore, before using this field you must have called get_ai()
        # TODO: replace the field with set/get methods
        self.bboxes = None
        # the annotated image
        self.ai_ = None
        # field_name_for_pred_objects_in_AnnotatedImage
        self.field_name_for_pred_objects_in_AnnotatedImage = \
                 field_name_for_pred_objects_in_AnnotatedImage
                    
    def get_ai(self):
        """
        Returns the associated AnnotatedImage.
        """
        # load the image from the disk, if never done it before
        if not self.ai_:
            fd = open(self.fname, 'r')
            self.ai_ = pickle.load(fd)
            fd.close()
            assert self.ai_.image_name == self.key
            # TODO. This is a pure hack. The AnnotatedImage.feature_extractor_
            #       should not be pickled.
            self.ai_.feature_extractor_ = None
            # register the feature extractor
            self.ai_.register_feature_extractor(self.feature_extractor_params)
        # fill-out self.bboxes, if never done before
        if self.bboxes == None:
            if self.field_name_for_pred_objects_in_AnnotatedImage == None:
                self.bboxes = []
            else:
                self.bboxes = []
                name = self.field_name_for_pred_objects_in_AnnotatedImage            
                ai = self.ai_
                assert len(ai.pred_objects[name]) == 1
                for label in ai.pred_objects[name]:
                    for bb in ai.pred_objects[name][label].bboxes:
                        self.bboxes.append( [bb, False] )
                if len(self.bboxes) <= 0:
                    logging.warning('Warning. The AnnotatedImage {0} '\
                        'does not contain bboxes under the pred_objects[{1}] field'\
                        .format(fname, name))
        # return the AnnotatedImage
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
    detector.init()
    detector.train_evaluate()
    return 0

def PipelineDetector_evaluate_single_image(pi, detector, category):
    logging.info('Elaborating test key: {0}'.format(pi.key))
    pi.get_ai()
    Xtest = None
    for idx_bb, bb in enumerate(pi.bboxes):
        feat = pi.get_ai().extract_features(bb[0])
        if Xtest == None:
            Xtest = np.empty((len(pi.bboxes),feat.size), dtype=float)
        Xtest[idx_bb, :] = feat
    confidences = detector.predict(Xtest)
    assert len(confidences) == Xtest.shape[0]
    assert len(confidences) == len(pi.bboxes)
    for idx_bb, bb in enumerate(pi.bboxes):            
        bb[0].confidence = confidences[idx_bb]
    # calculate the Stats
    pred_bboxes = [bb[0].copy() for bb in pi.bboxes]
    if category in pi.get_ai().gt_objects:
        gt_bboxes = pi.get_ai().gt_objects[category].bboxes
    else:
        gt_bboxes = []
    stats = Stats()
    stats.compute_stats(pred_bboxes, gt_bboxes)
    pi.clear_ai()
    return stats

class PipelineDetector:
    def __init__(self, category, params):
        # check the input parameters
        assert isinstance(category, str)
        assert isinstance(params, PipelineDetectorParams)
        # check that all the mandatory PipelineDetectorParams were set
        assert params.input_dir_train != None
        assert params.input_dir_test != None
        assert params.output_dir != None
        assert params.splits_dir != None
        assert params.feature_extractor_params != None
        assert params.detector_params != None
        assert params.field_name_for_pred_objects_in_AnnotatedImage != None
        # init
        self.category = category
        self.params = params
        self.train_set = None
        self.test_set = None
        self.detector_output_dir = '{0}/{1}'.format(params.output_dir, category)
        self.iteration = 0
        self.detector = Detector.create_detector(params.detector_params)

    def init(self):
        logging.info('Initializing the detector for {0}'.format(self.category))
        # create output directory for this detector
        if os.path.exists(self.detector_output_dir) == False:
            os.makedirs(self.detector_output_dir)           
        # read the training set
        fname = '{0}/{1}_{2}.txt'.format(self.params.splits_dir, self.category,\
                                         self.params.split_train_name)
        key_label_list = self.read_key_label_file_( \
                    fname, self.params.max_train_pos_images_per_category, \
                    self.params.max_train_neg_images_per_category)
        self.train_set = self.create_pipeline_images_( \
                    key_label_list, self.params, self.params.input_dir_train)
        # read the test set
        fname = '{0}/{1}_{2}.txt'.format(self.params.splits_dir, self.category, \
                                         self.params.split_test_name)
        key_label_list = self.read_key_label_file_(fname, sys.maxint, sys.maxint)
        self.test_set = self.create_pipeline_images_( \
                    key_label_list, self.params, self.params.input_dir_test)
        # check: make sure all the files exists
        error = False
        for pi in (self.train_set + self.test_set):
            if not os.path.exists(pi.fname):
                error = True
                logging.info('The file {0} does not exist'.format(pi.fname))
        assert not error, 'Some required files were not found. Abort.'
        logging.info('Initialization complete')       

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
            fname_mat = '{0}/iter_stats{1}.mat'.format( \
                    self.detector_output_dir, iteration)                    
            if os.path.exists(fname):
                logging.info('The stats file for iteration {0} already '\
                             'exists: {1}'.format(iteration, fname))
            else:
                logging.info('Evaluation the model of iteration {0}'.format( \
                             iteration))
                stats = self.evaluate()
                dump_obj_to_file_using_pickle(stats, fname, 'binary')
                stats.save_mat(fname_mat)

    def train(self):
        """ Train an iteration of the detector """
        Xtrain = None
        Ytrain = None
        idx = 0
        for idx_pi, pi in enumerate(self.train_set):
            logging.info('Elaborating train key: {0} ({1}/{2})'.format( \
                          pi.key, idx_pi, len(self.train_set)))
            assert (pi.label == 1) or (pi.label == -1)
            # get the AnnotatedImage
            ai = pi.get_ai()
            # evaluate the model learned in the previous iteration
            if self.iteration > 0:
                for bb in pi.bboxes:
                    feat = ai.extract_features(bb[0])
                    bb[0].confidence = self.detector.predict(feat)
            # select pos and neg bboxes that will compose our train set
            pos_bboxes = []
            if pi.label == 1:
                # elaborate POSITIVE image
                pos_bboxes = self.train_elaborate_pos_example_(pi)
            elif pi.label == -1:
                # elaborate NEGATIVE image
                self.train_elaborate_neg_example_(pi)
            # extract the features
            for bb in pos_bboxes:
                feat = ai.extract_features(bb)                
                if Xtrain == None:
                    Xtrain, Ytrain = self.create_train_buffer_(feat.size)
                Xtrain[idx, :] = feat
                Ytrain[idx] = 1
                idx += 1
            for bb in [b for b in pi.bboxes if b[1]]:
                feat = ai.extract_features(bb[0])                
                if Xtrain == None:
                    Xtrain, Ytrain = self.create_train_buffer_(feat.size)
                Xtrain[idx, :] = feat
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
        """ calculate the stats for each image """
        if self.params.num_cores > 1:
            parfun = ParFunProcesses(PipelineDetector_evaluate_single_image, \
                                     self.params.num_cores)
        else:
            parfun = ParFunDummy(PipelineDetector_evaluate_single_image)              
        for pi in self.test_set:
            parfun.add_task(pi, self.detector, self.category)
        stats_all = parfun.run()
        assert len(stats_all)==len(self.test_set)
        # aggregate the stats for this detector
        stats, hist_overlap = Stats.aggregate_results(stats_all)
        return stats
    
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
        dump_obj_to_file_using_pickle(self, fname, 'binary')
        
    def train_elaborate_pos_example_(self, pi):
        """ Elaborate a positive example during the training phase.
        It marks eventual pi.bboxes as negatives.
        It returns the set of positive BBox. """
        assert pi.label == 1
        ai = pi.get_ai()
        pos_bboxes = ai.gt_objects[self.category].bboxes
        if self.iteration == 0:
            self.mark_bboxes_sligtly_overlapping_with_pos_bboxes_( \
                pos_bboxes, pi.bboxes, \
                self.params.num_neg_bboxes_per_pos_image_during_init)
        else:
            # TODO. add negative examples from the positive image?
            #       For now, do nothing.
            pass
        return pos_bboxes

    def train_elaborate_neg_example_(self, pi):
        """ Elaborate a negative example during the training phase.
        It marks pi.bboxes as negatives. It returns void """
        niter = self.params.num_neg_bboxes_to_add_per_image_per_iter
        if self.iteration == 0:
            # check the input
            for bb in pi.bboxes:
                assert bb[1]==False
            # we pick a bunch of randomly-selected bboxes
            idxperm = util.randperm_deterministic(len(pi.bboxes))
            for i in range(min(len(idxperm), niter)):
                pi.bboxes[idxperm[i]][1] = True
        else:
            # we sort the bboxes by confidence score
            pi.bboxes = sorted(pi.bboxes, \
                                 key=lambda x: -x[0].confidence)
            # we pick the top ones that have not been already selected
            num_neg_bboxes = len([x for x in pi.bboxes if x[1]==True])
            nmax = self.params.max_num_neg_bbox_per_image - num_neg_bboxes
            niter = min(nmax, niter)
            n = 0
            for bb in pi.bboxes:
                if (n < nmax) and (not bb[1]):
                    bb[1] = True
                    n += 1       

    def create_train_buffer_(self, num_dims):
        """ Create an appropriate matrix that will be able to contain
        for sure the entire training set for the detector.
        It return Xtrain, Ytrain"""
        MAX_NUM_POS_BBOXES_PER_IMAGE = 30
        num_pos_images = len([pi for pi in self.train_set if pi.label==1])
        buffer_size = num_pos_images*MAX_NUM_POS_BBOXES_PER_IMAGE \
                    + self.params.max_num_neg_bbox_per_image*len(self.train_set)
        Xtrain = np.ndarray(shape=(buffer_size,num_dims), dtype=float)
        Ytrain = np.ndarray(shape=(buffer_size), dtype=int)
        return Xtrain, Ytrain        

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
        assert isinstance(pos_bboxes, list)
        assert isinstance(bboxes, list)
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
    def create_pipeline_images_(key_label_list, params, input_dir):
        """
        Input: list of (<key>, <+1/-1>), and PipelineDetectorParams.
        Output: list of PipelineImage
        """
        assert isinstance(key_label_list, list)
        assert isinstance(params, PipelineDetectorParams)
        out = []
        for idx, key_label in enumerate(key_label_list):
            key, label = key_label
            fname = '{0}/{1}.pkl'.format(input_dir, key)
            logging.info('Create PipelineImage for {0} ({1}/{2})'.format( \
                         fname, idx, len(key_label_list)))
            # create the PipelineImage
            pi = PipelineImage( \
                    key, label, fname, \
                    params.feature_extractor_params, \
                    params.field_name_for_pred_objects_in_AnnotatedImage)
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
        fd = open(params.categories_file, 'r')
        for line in fd:
            classes.append(line.strip())
        fd.close()
        logging.info('Loaded {0} classes'.format(len(classes)))
        # select the categories to process
        if params.categories_to_process:
            classes = [classes[i] for i in params.categories_to_process]
        # run the pipeline
        parfun = None
        if params.run_on_anthill:
            jobname = None
            if params.exp_name != None:
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

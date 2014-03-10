from util import *
import numpy as np
import os
import os.path
import skimage.io
from vlg.util.parfun import *

from heatmap import *
from network import *
from configuration import *
from imgsegmentation import *
from heatextractor import *
from htmlreport import *
import exp17

if __name__ == "__main__":
    # load configurations and parameters  
    conf = Configuration()
    params = exp17.Params()
    # experiment name
    params.exp_name = 'exp17_01'
    params.exp_name_input = 'exp03_04' # take results from here
    # Gray box params (bbox size, stride)
    params.gray_par = [(50, 10), (75, 15), (100, 15), (125, 20), \
                       (150, 20), (175, 25), (200, 25)]
    # Num elements in batch (for decaf/caffe eval)
    params.batch_sz = 1     
    # Select segmentations
    params.min_sz_segm = 20 # smallest size of the segment sqrt(Area)
    params.subset_par = False #
    # Num elements in batch (for decaf/caffe eval)
    params.batch_sz = 1
    # default Configuration, image and label files
    params.conf = conf
    # select network: 'CAFFE' or 'DECAF'
    params.classifier = 'CAFFE'
    params.center_only = True
    # select top C classes used to generate the heatmaps
    params.topC = 5
    # method for calculating the confidence
    params.heatextractor_confidence_tech = 'full_obf_positive'
    # load the correct segmentation masks dependigly of the exp
    params.segm_type_load = 'warped' # warp to net size
    conf.ilsvrc2012_segm_results_dir += '_ext'
    # normalize the confidence by area?
    params.heatextractor_area_normalization = True
    # input/output directory
    params.output_dir = conf.experiments_output_directory \
                        + '/' + params.exp_name
    params.input_dir = conf.experiments_output_directory \
                        + '/' + params.exp_name_input 
    # parallelize the script on Anthill?
    params.run_on_anthill = True 
    # Set jobname in case the process stop or crush
    params.job_name = None # set to None if you do not want to resume things
    params.task = [] # specify tasks to debug
    logging.info('Started')
    # RUN THE EXPERIMENT
    exp17.run_exp(params)


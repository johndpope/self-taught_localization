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
import exp16

if __name__ == "__main__":
    # load configurations and parameters  
    conf = Configuration()
    params = exp16.Params()
    # experiment name
    params.exp_name = 'exp16_03'
    # input dataset
    params.exp_name_input = 'exp19_01'
    # we do NOT include the GT heatmap (PASCAL has many "imagenet" labels)
    params.include_gt_label_heatmap = False
    # Gray box params (bbox size, stride)
    params.gray_par = [(32, 10), (48, 10), (64, 10), (80, 10), (96, 10)]
    # Num elements in batch (for decaf/caffe eval)
    params.batch_sz = 1
    # default Configuration, image and label files
    params.conf = conf
    # select network: 'CAFFE' or 'DECAF'
    params.classifier = 'CAFFE'
    params.center_only = True
    # select top C classes used to generate the heatmaps
    params.topC = 20
    # quantile of the classes scores
    params.quantile_pred = 0.98
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
    # select which shards to process
    params.task = []
    logging.info('Started')
    # RUN THE EXPERIMENT
    exp16.run_exp(params)

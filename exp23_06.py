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
from compute_statistics_exp import *
from htmlreport import *
import exp23

if __name__ == "__main__":
    # load configurations and parameters  
    conf = Configuration()
    params = exp23.Params()
    # experiment name
    params.exp_name = 'exp23_06'
    # input (GT AnnotatatedImages)
    params.exp_name_input = 'exp03_06'
    # Num elements in batch (for decaf/caffe eval)
    params.batch_sz = 1
    # default Configuration, image and label files
    params.conf = conf
    # select network: 'CAFFE' or 'DECAF'
    params.classifier = 'CAFFE'
    params.center_only = True
    # select top C classes used to generate the predicted bboxes
    params.topC = 5     # if 0, take the max across classes
    # method for calculating the confidence
    params.heatextractor_confidence_tech = 'full_obf_positive'     
    # obfuscation search params
    params.ss_version = 'fast'
    params.min_sz_segm = 5 # keep this low (because we resize!!)
    params.alpha = np.array([1/3.0, 1/3.0, 1/3.0])
    params.obfuscate_bbox = True
    # input/output directory
    params.output_dir = conf.experiments_output_directory \
                        + '/' + params.exp_name
    params.input_dir = conf.experiments_output_directory \
                        + '/' + params.exp_name_input 
    # parallelize the script on Anthill?
    params.run_on_anthill = True 
    # list of tasks to execute
    params.task = []
    logging.info('Started')
    # RUN THE EXPERIMENT
    if 1:
        exp23.run_exp(params)
    # RUN THE STATISTICS PIPELINE
    if 1:
        compute_statistics_exp(input_exp=params.exp_name)
    # RUN THE STATISTICS PIPELINE WITH NMS
    if 0:
        # NMS=0.3
        params_stats = ComputeStatParams(params.exp_name, 'stats_NMS_03')
        params_stats.nms_execution = True
        params_stats.nms_iou_threshold = 0.3
        compute_statistics_exp(input_exp=params.exp_name, params=params_stats)
    if 1:
        # NMS=0.5
        params_stats = ComputeStatParams(params.exp_name, 'stats_NMS_05')
        params_stats.nms_execution = True
        params_stats.nms_iou_threshold = 0.5
        compute_statistics_exp(input_exp=params.exp_name, params=params_stats)
    if 1:
        # NMS=0.9
        params_stats = ComputeStatParams(params.exp_name, 'stats_NMS_09')
        params_stats.nms_execution = True
        params_stats.nms_iou_threshold = 0.9
        compute_statistics_exp(input_exp=params.exp_name, params=params_stats)

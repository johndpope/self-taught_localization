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
import exp12

if __name__ == "__main__":
    # load configurations and parameters  
    conf = Configuration()
    params = exp12.Params()
    # experiment name
    params.exp_name = 'exp12_01'
    params.exp_name_input = 'exp03_01' # take results from here
    # Select segmentations
    params.min_sz_segm = 30 # smallest size of the segment sqrt(Area)
    params.subset_par = False #
    # default Configuration, image and label files
    params.conf = conf
    # method for calculating the confidence
    params.heatextractor_confidence_tech = 'full_obf_positive'
    # image transformation. it could be 'centered_crop', or 'original'
    params.image_transformation = 'centered_crop'
         
    # normalize the confidence by area?
    params.heatextractor_area_normalization = True
    # input/output directory
    params.output_dir = conf.experiments_output_directory \
                        + '/' + params.exp_name
    params.input_dir = conf.experiments_output_directory \
                        + '/' + params.exp_name_input 
    # parallelize the script on Anthill?
    params.run_on_anthill = False
    # Set jobname in case the process stop or crush
    params.job_name = None # set to None if you do not want to resume things
    params.task = 50 # specify task to debug
    logging.info('Started')
    # RUN THE EXPERIMENT
    exp12.run_exp(params)


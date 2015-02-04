function visualize_results_PASCAL2007_trainval()
% This script plots results for PASCAL VOC 2007 - TRAINVAL set.
%
%

% clear the variables
clear;

% load common plot definitions
plot_defs;

% parameters
params.exp_dir = '/home/ironfs/scratch/vlg/Data_projects/grayobfuscation';
params.dataset_name = 'PASCAL2007trainval';
params.prefix_output_files = strcat('results_',params.dataset_name);
params.save_output_files = 1;
params.set_log_scale = 1;
params.mean_precision = 1;
params.MATLAB = MATLAB;

% *** our experiments
% this is list of cells of 2-elements-cells {experiment_name, legend}
% params.exps = {{'exp06_13stats','exp06_13 (GrayBox, topC=5)'}, ...
%                {'exp06_14stats', 'exp06_14 (SlidingWindow, topC=5)'}, ...
%                {'exp06_15stats', 'exp06_15 (GraySegm, topC=5)'}, ...
%                {'exp06_17stats', 'exp06_17 (GrayBox, topC=5, quantile_pred=0.98)'}, ...
%                {'exp06_18stats', 'exp06_18 (GrayBox, topC=20, quantile_pred=0.99, minTopC=5'}, ...
%                {'exp14_04stats', 'exp14_04 (SelectiveSearch, fast)'}, ...               
%                {'exp21_02stats', 'exp21_02 (GrayBox+GraySegm, topC=5)'}, ...
%                {'exp22_03stats', 'exp22_03 (Re-ranked GrayBox, topC=5)'}, ...
%                {'exp22_04stats', 'exp22_04 (Re-ranked GrayBox+GraySegm, topC=5)'}, ...
%                };

params.exps = {{'exp34_06stats_NMS_05',' ObfuscationSearch, topC=5'}, ...
               {'exp35_01stats',' ObfuscationSearch, GT mapping)'}, ...
               {'exp14_08stats',' Selective Search'}, ...
               {'exp29_02stats',' BING'}
               };
          

% params.exps = {{'exp06_13stats_NMS_05','exp06_13_NMS_05 (GrayBox, topC=5)'}, ...
%                {'exp06_25stats_NMS_05', 'exp06_25_NMS_05 (GraySegm, topC=5)'}, ...
%                {'exp14_04stats', 'exp14_04 (SelectiveSearch, fast)'}, ...              
%                {'exp23_07stats_NMS_05', 'exp23_07_NMS_05 (ObfuscationSearch, topC=5)'}, ...
%                };
           

visualize_plot_and_save(params);

end

function ILSVRC2012_200rnd_VAL_mean_precision()

config;

figure('name','ILSVRC2012_200rnd_VAL_mean_precision','Position', conf.figure_position);
hold on;
grid on;
set(gcf, 'DefaultLineLineWidth', conf.lw);
set(gcf, 'DefaultLineMarkerSize', conf.ms);
set(gca, 'fontsize', conf.fs);
xlabel(conf.figure_precision_xlabel);
ylabel(conf.figure_precision_ylabel);
set(gca, 'XScale', 'log');
%title('This is the title');
%set(gca, 'XTick', xvalues);
%axis([1, 50, 0, 1]);

% ****** exp28_01stats_NMS_05 / mean_precision *** SlidingWindow, topC=5   **********
num_bboxes = [ 1.000000, 2.000000, 3.000000, 4.000000, 5.000000, 6.000000, 7.000000, 8.000000, 9.000000, 10.000000, 11.000000, 12.000000, 13.000000, 14.000000, 15.000000, 20.000000, 30.000000, 50.000000, 100.000000, 200.000000, 500.000000, 1000.000000, 2000.000000 ];
mean_precision = [ 0.030600, 0.027450, 0.024333, 0.022125, 0.020260, 0.018683, 0.017286, 0.016337, 0.015578, 0.014710, 0.014191, 0.013692, 0.013154, 0.012771, 0.012333, 0.010484, 0.008190, 0.005881, 0.003565, 0.002097, 0.001008, 0.000645, 0.000625 ];
plot(num_bboxes, mean_precision, ['-' SW.marker], 'DisplayName', SW.legend, 'Color', SW.color);
h=legend('-DynamicLegend'); set(h,'Interpreter','none');


% ****** exp14_05stats / mean_precision *** SelectiveSearch, fast   **********
num_bboxes = [ 1.000000, 2.000000, 3.000000, 4.000000, 5.000000, 6.000000, 7.000000, 8.000000, 9.000000, 10.000000, 11.000000, 12.000000, 13.000000, 14.000000, 15.000000, 20.000000, 30.000000, 50.000000, 100.000000, 200.000000, 500.000000, 1000.000000, 2000.000000, 3000.000000, 5000.000000 ];
mean_precision = [ 0.224900, 0.170650, 0.143067, 0.124075, 0.109400, 0.097567, 0.088486, 0.080687, 0.074711, 0.069870, 0.065482, 0.061892, 0.058608, 0.055779, 0.053140, 0.043740, 0.032560, 0.021602, 0.012270, 0.006828, 0.003041, 0.001622, 0.000942, 0.000811, 0.000788 ];
plot(num_bboxes, mean_precision, ['-' SS.marker], 'DisplayName', SS.legend, 'Color', SS.color);
h=legend('-DynamicLegend'); set(h,'Interpreter','none');


% % ****** exp06_21stats_NMS_05 / mean_precision *** exp06_21_NMS_05 (SlidingWindow-heatmap, topC=5)   **********
% num_bboxes = [ 1.000000, 2.000000, 3.000000, 4.000000, 5.000000, 6.000000, 7.000000, 8.000000, 9.000000, 10.000000, 11.000000, 12.000000, 13.000000, 14.000000, 15.000000, 20.000000, 30.000000, 50.000000 ];
% mean_precision = [ 0.178200, 0.152362, 0.135177, 0.122342, 0.110611, 0.101534, 0.094653, 0.088679, 0.083416, 0.078837, 0.075238, 0.072179, 0.069918, 0.067869, 0.066571, 0.062838, 0.061927, 0.061898 ];
% plot(num_bboxes, mean_precision, '-o', 'DisplayName', SWheat.legend, 'Color', SWheat.color);
% h=legend('-DynamicLegend'); set(h,'Interpreter','none');


% ****** exp29_03stats / mean_precision *** BING (our code)   **********
num_bboxes = [ 1.000000, 2.000000, 3.000000, 4.000000, 5.000000, 6.000000, 7.000000, 8.000000, 9.000000, 10.000000, 11.000000, 12.000000, 13.000000, 14.000000, 15.000000, 20.000000, 30.000000, 50.000000, 100.000000, 200.000000, 500.000000, 1000.000000, 2000.000000, 3000.000000 ];
mean_precision = [ 0.391000, 0.236100, 0.177767, 0.145250, 0.123900, 0.108467, 0.097343, 0.088463, 0.081100, 0.074880, 0.069809, 0.065167, 0.061431, 0.057993, 0.054840, 0.043235, 0.030980, 0.021014, 0.012102, 0.006676, 0.002918, 0.001555, 0.000824, 0.000814 ];
plot(num_bboxes, mean_precision, ['-' BING.marker], 'DisplayName', BING.legend, 'Color', BING.color);
h=legend('-DynamicLegend'); set(h,'Interpreter','none');


% ****** exp39_02stats / mean_precision *** EdgeBoxes   **********
num_bboxes = [ 1.000000, 2.000000, 3.000000, 4.000000, 5.000000, 6.000000, 7.000000, 8.000000, 9.000000, 10.000000, 11.000000, 12.000000, 13.000000, 14.000000, 15.000000, 20.000000, 30.000000, 50.000000, 100.000000, 200.000000, 500.000000, 1000.000000, 2000.000000, 3000.000000, 5000.000000 ];
mean_precision = [ 0.323100, 0.227800, 0.178967, 0.149200, 0.128960, 0.114100, 0.102671, 0.093200, 0.085589, 0.078950, 0.073500, 0.068850, 0.064854, 0.061472, 0.058361, 0.046602, 0.033542, 0.021958, 0.012185, 0.006646, 0.002918, 0.001554, 0.000848, 0.000628, 0.000494 ];
plot(num_bboxes, mean_precision, ['-' EDGEBOXES.marker], 'DisplayName', EDGEBOXES.legend, 'Color', EDGEBOXES.color);
h=legend('-DynamicLegend'); set(h,'Interpreter','none');


% ****** exp40_02stats / mean_precision *** MCG   **********
num_bboxes = [ 1.000000, 2.000000, 3.000000, 4.000000, 5.000000, 6.000000, 7.000000, 8.000000, 9.000000, 10.000000, 11.000000, 12.000000, 13.000000, 14.000000, 15.000000, 20.000000, 30.000000, 50.000000, 100.000000, 200.000000, 500.000000, 1000.000000, 2000.000000, 3000.000000, 5000.000000 ];
mean_precision = [ 0.387800, 0.274650, 0.213000, 0.177250, 0.151940, 0.133767, 0.120057, 0.108875, 0.100089, 0.092880, 0.086473, 0.080942, 0.075992, 0.071721, 0.067787, 0.053840, 0.038360, 0.024658, 0.013338, 0.007072, 0.003001, 0.001572, 0.000978, 0.000905, 0.000903 ];
plot(num_bboxes, mean_precision, ['-' MCG.marker], 'DisplayName', MCG.legend, 'Color', MCG.color);
h=legend('-DynamicLegend'); set(h,'Interpreter','none');


% % ****** exp23_10stats_NMS_05 / mean_precision *** ObfuscationSearch, GT   **********
% num_bboxes = [ 1.000000, 2.000000, 3.000000, 4.000000, 5.000000, 6.000000, 7.000000, 8.000000, 9.000000, 10.000000, 11.000000, 12.000000, 13.000000, 14.000000, 15.000000, 20.000000, 30.000000, 50.000000, 100.000000, 200.000000, 500.000000, 1000.000000 ];
% mean_precision = [ 0.462900, 0.292450, 0.218033, 0.174800, 0.146700, 0.126900, 0.112057, 0.100763, 0.091556, 0.084150, 0.077700, 0.072317, 0.067715, 0.063707, 0.060153, 0.047261, 0.033671, 0.021755, 0.011875, 0.006536, 0.004213, 0.004185 ];
% ****** exp30_05stats_NMS_05 / mean_precision *** ObfuscationSearch similarity + NET features, GT   **********
num_bboxes = [ 1.000000, 2.000000, 3.000000, 4.000000, 5.000000, 6.000000, 7.000000, 8.000000, 9.000000, 10.000000, 11.000000, 12.000000, 13.000000, 14.000000, 15.000000, 20.000000, 30.000000, 50.000000, 100.000000, 200.000000, 500.000000, 1000.000000 ];
mean_precision = [ 0.484700, 0.311300, 0.229400, 0.184100, 0.153340, 0.131817, 0.116343, 0.104062, 0.094533, 0.086660, 0.080082, 0.074542, 0.069562, 0.065314, 0.061707, 0.048450, 0.034351, 0.022194, 0.012225, 0.006713, 0.004002, 0.003927 ];
plot(num_bboxes, mean_precision, ['-' OBFSgt.marker], 'DisplayName', OBFSgt.legend, 'Color', OBFSgt.color);
h=legend('-DynamicLegend'); set(h,'Interpreter','none');


% % ****** exp23_06stats_NMS_05 / mean_precision *** exp23_06_NMS_05 (ObfuscationSearch, topC=5)   **********
% num_bboxes = [ 1.000000, 2.000000, 3.000000, 4.000000, 5.000000, 6.000000, 7.000000, 8.000000, 9.000000, 10.000000, 11.000000, 12.000000, 13.000000, 14.000000, 15.000000, 20.000000, 30.000000, 50.000000, 100.000000, 200.000000, 500.000000, 1000.000000 ];
% mean_precision = [ 0.478100, 0.295100, 0.218300, 0.174800, 0.146580, 0.126383, 0.111857, 0.100187, 0.091100, 0.083610, 0.077336, 0.071975, 0.067254, 0.063193, 0.059713, 0.046980, 0.033431, 0.021582, 0.011842, 0.006513, 0.004293, 0.004272 ];
% ****** exp30_08stats_NMS_05 / mean_precision *** ObfuscationSearch similarity + NET features, topC=5   **********
num_bboxes = [ 1.000000, 2.000000, 3.000000, 4.000000, 5.000000, 6.000000, 7.000000, 8.000000, 9.000000, 10.000000, 11.000000, 12.000000, 13.000000, 14.000000, 15.000000, 20.000000, 30.000000, 50.000000, 100.000000, 200.000000, 500.000000, 1000.000000 ];
mean_precision = [ 0.485800, 0.312500, 0.229033, 0.182550, 0.151920, 0.131033, 0.115629, 0.103562, 0.093989, 0.086430, 0.079927, 0.074342, 0.069554, 0.065350, 0.061753, 0.048435, 0.034438, 0.022378, 0.012376, 0.006849, 0.004034, 0.003950 ];
plot(num_bboxes, mean_precision, ['-' OBFStopC.marker], 'DisplayName', OBFStopC.legend, 'Color', OBFStopC.color);
h=legend('-DynamicLegend'); set(h,'Interpreter','none');
set(h,'position',conf.legend_position)

%legend('Location', 'SouthEast');

end

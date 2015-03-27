function ILSVRC2012_200rnd_VAL_mean_recall()

config;

figure('name','ILSVRC2012_200rnd_VAL_mean_recall','Position', conf.figure_position);
hold on;
grid on;
set(gcf, 'DefaultLineLineWidth', conf.lw);
set(gcf, 'DefaultLineMarkerSize', conf.ms);
set(gca, 'fontsize', conf.fs);
xlabel(conf.figure_recall_xlabel);
ylabel(conf.figure_recall_ylabel);
set(gca, 'XScale', 'log');
%title('This is the title');
%set(gca, 'XTick', xvalues);
%axis([1, 50, 0, 1]);


% ****** exp28_01stats_NMS_05 / mean_recall *** SlidingWindow, topC=5   **********
num_bboxes = [ 1.000000, 2.000000, 3.000000, 4.000000, 5.000000, 6.000000, 7.000000, 8.000000, 9.000000, 10.000000, 11.000000, 12.000000, 13.000000, 14.000000, 15.000000, 20.000000, 30.000000, 50.000000, 100.000000, 200.000000, 500.000000, 1000.000000, 2000.000000 ];
mean_recall = [ 0.021431, 0.037567, 0.049603, 0.059719, 0.067987, 0.075290, 0.081113, 0.087289, 0.093312, 0.097808, 0.103665, 0.108682, 0.112520, 0.117061, 0.121215, 0.136355, 0.157485, 0.183314, 0.216552, 0.247016, 0.284081, 0.305698, 0.307066 ];
plot(num_bboxes, mean_recall, ['-' SW.marker], 'DisplayName', SW.legend, 'Color', SW.color);
h=legend('-DynamicLegend'); set(h,'Interpreter','none');


% ****** exp14_05stats / mean_recall *** SelectiveSearch, fast   **********
num_bboxes = [ 1.000000, 2.000000, 3.000000, 4.000000, 5.000000, 6.000000, 7.000000, 8.000000, 9.000000, 10.000000, 11.000000, 12.000000, 13.000000, 14.000000, 15.000000, 20.000000, 30.000000, 50.000000, 100.000000, 200.000000, 500.000000, 1000.000000, 2000.000000, 3000.000000, 5000.000000 ];
mean_recall = [ 0.162616, 0.245926, 0.307500, 0.354514, 0.388487, 0.414413, 0.437003, 0.454217, 0.472229, 0.489498, 0.503264, 0.516739, 0.528609, 0.540384, 0.550614, 0.598311, 0.659556, 0.718882, 0.796641, 0.862426, 0.924993, 0.952894, 0.966196, 0.969432, 0.969673 ];
plot(num_bboxes, mean_recall, ['-' SS.marker], 'DisplayName', SS.legend, 'Color', SS.color);
h=legend('-DynamicLegend'); set(h,'Interpreter','none');


% % ****** exp06_21stats_NMS_05 / mean_recall *** exp06_21_NMS_05 (SlidingWindow-heatmap, topC=5)   **********
% num_bboxes = [ 1.000000, 2.000000, 3.000000, 4.000000, 5.000000, 6.000000, 7.000000, 8.000000, 9.000000, 10.000000, 11.000000, 12.000000, 13.000000, 14.000000, 15.000000, 20.000000, 30.000000, 50.000000 ];
% mean_recall = [ 0.125164, 0.211618, 0.281325, 0.338616, 0.381199, 0.418443, 0.452411, 0.480624, 0.503078, 0.520873, 0.537250, 0.550698, 0.563738, 0.572420, 0.582889, 0.605824, 0.611789, 0.611854 ];
% plot(num_bboxes, mean_recall, '-o', 'DisplayName', SWheat.legend, 'Color', SWheat.color);
% h=legend('-DynamicLegend'); set(h,'Interpreter','none');


% ****** exp29_03stats / mean_recall *** BING (our code)   **********
num_bboxes = [ 1.000000, 2.000000, 3.000000, 4.000000, 5.000000, 6.000000, 7.000000, 8.000000, 9.000000, 10.000000, 11.000000, 12.000000, 13.000000, 14.000000, 15.000000, 20.000000, 30.000000, 50.000000, 100.000000, 200.000000, 500.000000, 1000.000000, 2000.000000, 3000.000000 ];
mean_recall = [ 0.288872, 0.346975, 0.389748, 0.421617, 0.448068, 0.468785, 0.489201, 0.506206, 0.520668, 0.532811, 0.544881, 0.554001, 0.564037, 0.571917, 0.578588, 0.603022, 0.640649, 0.709760, 0.787686, 0.844239, 0.899575, 0.940484, 0.957904, 0.958013 ];
plot(num_bboxes, mean_recall, ['-' BING.marker], 'DisplayName', BING.legend, 'Color', BING.color);
h=legend('-DynamicLegend'); set(h,'Interpreter','none');


% ****** exp39_02stats / mean_recall *** EdgeBoxes   **********
num_bboxes = [ 1.000000, 2.000000, 3.000000, 4.000000, 5.000000, 6.000000, 7.000000, 8.000000, 9.000000, 10.000000, 11.000000, 12.000000, 13.000000, 14.000000, 15.000000, 20.000000, 30.000000, 50.000000, 100.000000, 200.000000, 500.000000, 1000.000000, 2000.000000, 3000.000000, 5000.000000 ];
mean_recall = [ 0.229292, 0.323708, 0.379822, 0.420116, 0.452011, 0.478836, 0.501583, 0.519100, 0.534782, 0.546721, 0.559740, 0.570815, 0.581413, 0.592332, 0.601841, 0.636297, 0.679367, 0.730983, 0.793674, 0.847216, 0.901148, 0.930324, 0.951752, 0.958378, 0.962719 ];
plot(num_bboxes, mean_recall, ['-' EDGEBOXES.marker], 'DisplayName', EDGEBOXES.legend, 'Color', EDGEBOXES.color);
h=legend('-DynamicLegend'); set(h,'Interpreter','none');


% ****** exp40_02stats / mean_recall *** MCG   **********
num_bboxes = [ 1.000000, 2.000000, 3.000000, 4.000000, 5.000000, 6.000000, 7.000000, 8.000000, 9.000000, 10.000000, 11.000000, 12.000000, 13.000000, 14.000000, 15.000000, 20.000000, 30.000000, 50.000000, 100.000000, 200.000000, 500.000000, 1000.000000, 2000.000000, 3000.000000, 5000.000000 ];
mean_recall = [ 0.274289, 0.382507, 0.440584, 0.486134, 0.518411, 0.544958, 0.568282, 0.586613, 0.605069, 0.621668, 0.634672, 0.645689, 0.655467, 0.664802, 0.672421, 0.707056, 0.747150, 0.790275, 0.840137, 0.877609, 0.917552, 0.946051, 0.958653, 0.960005, 0.960071 ];
plot(num_bboxes, mean_recall, ['-' MCG.marker], 'DisplayName', MCG.legend, 'Color', MCG.color);
h=legend('-DynamicLegend'); set(h,'Interpreter','none');


% % ****** exp23_10stats_NMS_05 / mean_recall *** ObfuscationSearch, GT   **********
% num_bboxes = [ 1.000000, 2.000000, 3.000000, 4.000000, 5.000000, 6.000000, 7.000000, 8.000000, 9.000000, 10.000000, 11.000000, 12.000000, 13.000000, 14.000000, 15.000000, 20.000000, 30.000000, 50.000000, 100.000000, 200.000000, 500.000000, 1000.000000 ];
% mean_recall = [ 0.339083, 0.425434, 0.471865, 0.501032, 0.522948, 0.540458, 0.554264, 0.567347, 0.577607, 0.587618, 0.595744, 0.602776, 0.609622, 0.615795, 0.621452, 0.643495, 0.676278, 0.713577, 0.759104, 0.801625, 0.865478, 0.869860 ];
% ****** exp30_05stats_NMS_05 / mean_recall *** ObfuscationSearch similarity + NET features, GT   **********
num_bboxes = [ 1.000000, 2.000000, 3.000000, 4.000000, 5.000000, 6.000000, 7.000000, 8.000000, 9.000000, 10.000000, 11.000000, 12.000000, 13.000000, 14.000000, 15.000000, 20.000000, 30.000000, 50.000000, 100.000000, 200.000000, 500.000000, 1000.000000 ];
mean_recall = [ 0.355011, 0.452314, 0.496777, 0.528101, 0.547356, 0.562248, 0.576038, 0.586920, 0.597566, 0.606069, 0.614388, 0.622205, 0.627758, 0.633312, 0.639185, 0.662251, 0.693525, 0.731520, 0.782132, 0.828005, 0.893694, 0.900189 ];
plot(num_bboxes, mean_recall, ['-' OBFSgt.marker], 'DisplayName', OBFSgt.legend, 'Color', OBFSgt.color);
h=legend('-DynamicLegend'); set(h,'Interpreter','none');


% % ****** exp23_06stats_NMS_05 / mean_recall *** exp23_06_NMS_05 (ObfuscationSearch, topC=5)   **********
% num_bboxes = [ 1.000000, 2.000000, 3.000000, 4.000000, 5.000000, 6.000000, 7.000000, 8.000000, 9.000000, 10.000000, 11.000000, 12.000000, 13.000000, 14.000000, 15.000000, 20.000000, 30.000000, 50.000000, 100.000000, 200.000000, 500.000000, 1000.000000 ];
% mean_recall = [ 0.351879, 0.432041, 0.474992, 0.503598, 0.524798, 0.540209, 0.554582, 0.565311, 0.576138, 0.585525, 0.593815, 0.600852, 0.606453, 0.612346, 0.618274, 0.641659, 0.673631, 0.709108, 0.756593, 0.794482, 0.840542, 0.841998 ];
% ****** exp30_08stats_NMS_05 / mean_recall *** ObfuscationSearch similarity + NET features, topC=5   **********
num_bboxes = [ 1.000000, 2.000000, 3.000000, 4.000000, 5.000000, 6.000000, 7.000000, 8.000000, 9.000000, 10.000000, 11.000000, 12.000000, 13.000000, 14.000000, 15.000000, 20.000000, 30.000000, 50.000000, 100.000000, 200.000000, 500.000000, 1000.000000 ];
mean_recall = [ 0.356513, 0.455985, 0.497552, 0.525479, 0.543791, 0.559967, 0.574301, 0.585245, 0.595455, 0.606247, 0.615212, 0.622692, 0.629747, 0.635345, 0.641567, 0.664812, 0.697646, 0.740067, 0.794518, 0.844824, 0.899149, 0.904258 ];
plot(num_bboxes, mean_recall, ['-' OBFStopC.marker], 'DisplayName', OBFStopC.legend, 'Color', OBFStopC.color);
h=legend('-DynamicLegend'); set(h,'Interpreter','none');


legend(h, 'Location', 'Best');

end

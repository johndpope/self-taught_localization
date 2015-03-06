function ILSVRC2012_200rnd_VAL_detection_AP_GT_SS()

config;

% -------------- Second mAP graph -------------- %
figure('name','ILSVRC2012_200rnd_VAL_detection_AP','Position', conf.figure_position);
hold on;
grid on;
set(gcf, 'DefaultLineLineWidth', conf.lw);
set(gcf, 'DefaultLineMarkerSize', conf.ms);
set(gca, 'fontsize', conf.fs);
ylabel('Classes');
xlabel('Average Precision');
set(gca, 'YTick', [0:10:num_classes]);
set(gca, 'XLim', [0 1]);
axis(gca, [0 1 1 num_classes]);
LEG = {};

[average_precision_sort2, idx2] = sort(OBFSgt.average_precision);
this_legend = plot_detection_graph(OBFSgt.average_precision(idx2), [1:num_classes], 'o', OBFSgt.legend, OBFSgt.color);
h=legend('-DynamicLegend'); set(h,'Interpreter','none');
LEG = cat(1, LEG, this_legend);

this_legend = plot_detection_graph(SS.average_precision(idx2), [1:num_classes], 'o', SS.legend, SS.color);
h=legend('-DynamicLegend'); set(h,'Interpreter','none');
LEG = cat(1, LEG, this_legend);

h = legend(LEG);
legend(h, 'Location', 'Best');

end
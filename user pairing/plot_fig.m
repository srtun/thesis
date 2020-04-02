clearvars
clc

%B = [0;1;2]
%save('arr2.dat','B')
data = importdata('sim1_data.dat')

fig = 0

fig = fig + 1;
h_figure = figure(fig)
clf;
%title('SE comparison stat', 'FontSize', 14);
hold on;

%x_val = zeros(2, 5);
x_val(1, :) = 20:20:100;
x_val(2, :) = 500:200:1300;
%x = categorical(x);
x = x_val(2, :)
p = plot(x,data(1,:),'-*b',x,data(2,:),'-sr',x,data(3,:), '-og',x, data(4,:), '-*y');
p(1).LineWidth = 2;
p(2).LineWidth = 2;
p(3).LineWidth = 2;
p(4).LineWidth = 2;

xlim([x(1), x(5)]);
set(gca,'XTick',x, 'FontSize', 24);
ylim([0, inf]);
set(gca, 'FontSize', 24);
x_label_text = ["percentage of interfering UEs(%)";"expectation of traffic demand (bits)"];
y_label_text = ["sum rate (Mbps)";"sum rate (Mbps)"];

xlabel(x_label_text(2),'FontSize', 24) 
ylabel(y_label_text(2),'FontSize', 24)
%xlabel("number of UEs",'FontSize', 24) 
%ylabel("average sum-rate (Mbps)",'FontSize', 24)
%legend('interference-aware(opt pairing)','interference-aware(random pairing)','interference free','interference-aware(threshold pairing)', 'interference-aware(heuristic pairing)'  ,'FontSize', 18); 
legend_text = ["optimal";"greedy";"pairing";"interference-free"]
legend(legend_text,'FontSize', 18)

savefig(fig, 'sim_figure1.fig')



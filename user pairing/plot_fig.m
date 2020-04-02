clearvars
clc

%B = [0;1;2]
%save('arr2.dat','B')

formatOut = 'mmdd';
today = datestr(now,formatOut)
data_num = 3
fig = 0
while fig < data_num
    fig = fig + 1;
    if fig == 1
        exp = int2str(700)
        filename = strcat('sim1_exp=', exp, '_', today, '.dat')
    elseif fig == 2
        exp = int2str(1100)
        filename = strcat('sim1_exp=', exp, '_', today, '.dat')
    elseif fig == 3
        filename = strcat('sim2_', today, '.dat')
    end
    data = importdata(filename)
    h_figure = figure(fig)
    clf;
    %title('SE comparison stat', 'FontSize', 14);
    hold on;

    %x_val = zeros(2, 5);
    x_val(1, :) = 20:20:100;
    x_val(2, :) = 500:200:1300;
    %x = categorical(x);
    x = x_val(1, :)
    if fig == 3
        x = x_val(2, :)
    end
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
    if fig == 3
        xlabel(x_label_text(2),'FontSize', 24)
    else 
        xlabel(x_label_text(2),'FontSize', 24)
    end
    ylabel(y_label_text(1),'FontSize', 24)
    %xlabel("number of UEs",'FontSize', 24) 
    %ylabel("average sum-rate (Mbps)",'FontSize', 24)
    %legend('interference-aware(opt pairing)','interference-aware(random pairing)','interference free','interference-aware(threshold pairing)', 'interference-aware(heuristic pairing)'  ,'FontSize', 18); 
    legend_text = ["optimal";"greedy";"pairing";"interference-free"]
    legend(legend_text,'FontSize', 18)
    if fig == 1
        exp = int2str(700)
        filename = strcat('sim1_fig_exp=', exp, '_', today, '.fig')
    elseif fig == 2
        exp = int2str(1100)
        filename = strcat('sim1_fig_exp=', exp, '_', today, '.fig')
    elseif fig == 3
        filename = strcat('sim2_fig_', today, '.fig')
    end
    savefig(fig, filename)
end


% main 
clearvars
clc

%{
clf
figure(1)

x=1:1:5;
x = categorical(x);
y = [5,4,3,2,1];
a=[203.024;113.857;256.259;244.888;293.376]; % y value
b=[334.4,143.2,297.4,487.2,596.2]; % y value
plot(x,a,'-*b',x,b,'-or');
xlabel('') 
ylabel('')
%}

p_x = 1 : 10;
p_x = p_x(randperm(length(p_x)))

% MCS table
[MCS_value, texting, rawdata] = xlsread('CQI_index.xlsx');

sim_times = 1000;
%[rb_total; rb_total_bi; rb_total_random];
Bw = 1;
%min_pilo t = 3;  % ??
num_of_time_slot = 20;
num_of_sc = 20;

symbol_per_RB = 84;
RB_assigned = zeros(num_of_time_slot, num_of_sc);
%U_i = 10;
%U_j = 10;

% mode => weighting mode
mode_type = ["sumrate";"RB_number";"spectrum efficiency"];
%mode = 'spectrum efficiency';
%mode = 'RB_number';
%mode = 'sumrate';
mode = mode_type(2);
%mode = mode_type(3);
parameter = [10;20;30;40;50]; % user number

line_rb_h = zeros(size(parameter));
line_rb_random = zeros(size(parameter));
line_rb_if = zeros(size(parameter));
line_rb_bi =  zeros(size(parameter));
line_rb_heur = zeros(size(parameter));

line_SE_h = zeros(size(parameter));
line_SE_random = zeros(size(parameter));
line_SE_if = zeros(size(parameter));
line_SE_bi =  zeros(size(parameter));
line_SE_heur = zeros(size(parameter));

for para = 1 : 5
U_i = parameter(para) / 2;
U_j = parameter(para) / 2;
stat_rb = zeros(1, 5);
stat_SE = zeros(1, 5);
for t = 1 : sim_times
t
% traffic demand
avg_bit = 3000;
least_bit = 50;
traffic_demand_i = randi(avg_bit, 1, U_i) + least_bit;
traffic_demand_j = randi(avg_bit, 1, U_j) + least_bit;
total_td = sum(traffic_demand_i, 'all') + sum(traffic_demand_j, 'all');
% channel state
H_i = randi(90, U_i, 1) + 10; 
H_j = randi(90, U_j, 1) + 10;
%itf_i = randi(5, U_i, 1) + 1;
%itf_j = randi(5, U_j, 1) + 1;
itf_i = zeros(U_i, 1);
itf_j = zeros(U_j, 1);
% fixed power allocation
P_i = randi(100, U_i, 1) / 100 + 1;
P_i = P_i / sum(P_i) * U_i;
P_j = randi(100, U_j, 1) / 100 + 1;
P_j = P_j / sum(P_j) * U_j;
% SNR
SNR_i = H_i .* P_i;
SNR_j = H_j .* P_j;
% noise
%noise_i = 1 / mean(SNR_i); % ??? need to correct
%noise_j = 1 / mean(SNR_j);
noise_i = 1;
noise_j = 1;

% SINR
SINR_ij = zeros(max(U_i, U_j));
SINR_ji = zeros(max(U_i, U_j));
% Spectrum efficiency
SE_ij = zeros(max(U_i, U_j));
% SIC 
pair_ij = zeros(max(U_i, U_j)) + 1;

for i = 1 : size(SINR_ij, 1)
    for j = 1 : size(SINR_ij, 2)
        if i > U_i
            SINR_ji(j, i) = SNR_j(j) / noise_j;
        elseif j > U_j
            SINR_ij(i, j) = SNR_i(i) / noise_i;
        else       
            temp = randi(10) / 10 + 1;
            SINR_ij(i, j) = SNR_i(i) / (noise_i * temp + itf_j(j) * P_j(j));
            SINR_ji(j, i) = SNR_j(j) / (noise_j * temp + itf_i(i) * P_i(i));
        end
    end
end

SINR_agg = log2(1 + SINR_ij) + log2(1 + SINR_ji');
rb_ij = zeros(max(U_i, U_j));
rb_ji = zeros(max(U_i, U_j));
mcs_idx_ij = zeros(max(U_i, U_j));
mcs_idx_ji = zeros(max(U_i, U_j));

rb_i = zeros(U_i, 1);
rb_j = zeros(U_j, 1);
mcs_idx_i = zeros(U_i, 1);
mcs_idx_j = zeros(U_j, 1);

% find the mcs index and RB needed for every user u
for i = 1 : U_i
    for mcs_idx = 1 : (size(MCS_value, 1) + 1)
        if mcs_idx == size(MCS_value, 1) + 1 || 10*log10(SNR_i(i)) < MCS_value(mcs_idx, 5)
            if mcs_idx == 1
                %rb_i(i) = intmax;
                rb_i(i) = traffic_demand_i(i) / (symbol_per_RB * MCS_value(mcs_idx, 4));
                mcs_idx_i(i) = mcs_idx;
            else 
                rb_i(i) = traffic_demand_i(i) / (symbol_per_RB * MCS_value(mcs_idx - 1, 4));
                mcs_idx_i(i) = mcs_idx - 1;
            end
            break;
        end
    end    
end
rb_i = ceil(rb_i);
% find the mcs index and RB needed for every user v
for j = 1 : U_j
    for mcs_idx = 1 : (size(MCS_value, 1) + 1)
        if mcs_idx == size(MCS_value, 1) + 1 || 10*log10(SNR_j(j)) < MCS_value(mcs_idx, 5)
            if mcs_idx == 1
                %rb_j(j) = intmax;
                rb_j(j) = traffic_demand_j(j) / (symbol_per_RB * MCS_value(mcs_idx, 4));
                mcs_idx_j(j) = mcs_idx;
            else 
                rb_j(j) = traffic_demand_j(j) / (symbol_per_RB * MCS_value(mcs_idx - 1, 4));
                mcs_idx_j(j) = mcs_idx - 1;
            end
            break;
        end
    end    
end
rb_j = ceil(rb_j);
% find the mcs index and RB needed for every user u w.r.t. interference user v 
for i = 1 : size(rb_ij, 1)
    for j = 1 : size(rb_ij, 2)
        if i > U_i
            rb_ij(i, j) = 0;
            mcs_idx_ij(i, j) = 0;
            continue;
        end
        for mcs_idx = 1 : (size(MCS_value, 1) + 1)
            if mcs_idx == size(MCS_value, 1) + 1 || 10*log10(SINR_ij(i, j)) < MCS_value(mcs_idx, 5)
                if mcs_idx == 1
                    %rb_ij(i, j) = intmax;
                    rb_ij(i, j) = traffic_demand_i(i) / (symbol_per_RB * MCS_value(mcs_idx, 4));
                    mcs_idx_ij(i, j) = mcs_idx;
                else 
                    rb_ij(i, j) = traffic_demand_i(i) / (symbol_per_RB * MCS_value(mcs_idx - 1, 4));
                    mcs_idx_ij(i, j) = mcs_idx - 1;
                end
                break;
            end
        end    
    end
end
rb_ij = ceil(rb_ij);
% find the mcs index and RB needed for every user v w.r.t. interference user u 
for i = 1 : size(rb_ij, 1)
    for j = 1 : size(rb_ij, 1)
        if j > U_j
            rb_ji(j, i) = 0;
            mcs_idx_ji(j, i) = 0;
            continue;
        end
        for mcs_idx = 1 : (size(MCS_value, 1) + 1)
            if mcs_idx == size(MCS_value, 1) + 1 || 10*log10(SINR_ji(j, i)) < MCS_value(mcs_idx, 5)
                if mcs_idx == 1
                    %rb_ji(j, i) = intmax;
                    rb_ji(j, i) = traffic_demand_j(j) / (symbol_per_RB * MCS_value(mcs_idx, 4));
                    mcs_idx_ji(j, i) = mcs_idx;
                else 
                    rb_ji(j, i) = traffic_demand_j(j) / (symbol_per_RB * MCS_value(mcs_idx - 1, 4));
                    mcs_idx_ji(j, i) = mcs_idx - 1;
                end
                break;
            end
        end    
    end
end
rb_ji = ceil(rb_ji);

% muting / rb_needed
rb_muting = zeros(max(U_i, U_j));
for i = 1 : size(rb_muting, 1)
    for j = 1 : size(rb_muting, 2)
        rb_muting(i, j) = rb_i(i) + rb_j(j);
    end
end

for i = 1 : size(rb_ij, 1)
    for j = 1 : size(rb_ij, 1)
        if j > U_j
            rb_ji(j, i) = 0;
            mcs_idx_ji(j, i) = 0;
            continue;
        end
        for mcs_idx = 1 : (size(MCS_value, 1) + 1)
            if mcs_idx == size(MCS_value, 1) + 1 || 10*log10(SINR_ji(j, i)) < MCS_value(mcs_idx, 5)
                if mcs_idx == 1
                    %rb_ji(j, i) = intmax;
                    rb_ji(j, i) = traffic_demand_j(j) / (symbol_per_RB * MCS_value(mcs_idx, 4));
                    mcs_idx_ji(j, i) = mcs_idx;
                else 
                    rb_ji(j, i) = traffic_demand_j(j) / (symbol_per_RB * MCS_value(mcs_idx - 1, 4));
                    mcs_idx_ji(j, i) = mcs_idx - 1;
                end
                break;
            end
        end    
    end
end
rb_ji = ceil(rb_ji);


rb_alloc = zeros(max(U_i, U_j));

% paired users are always served simultaneously 
for i = 1 : max(U_i, U_j)
    for j = 1 : max(U_i, U_j)
        rb_alloc(i, j) = max(rb_ij(i, j), rb_ji(j, i));
    end
end


% if one of the paired users complete, the other can decode w/o interference
%{
for i = 1 : max(U_i, U_j)
    i;
    for j = 1 : max(U_i, U_j)
        rb_alloc(i, j) = min(rb_ij(i, j), rb_ji(j, i));
        rb_remain = 0;
        if rb_ij(i, j) > rb_alloc(i, j)
            remain_bit = traffic_demand_i(i) - (rb_alloc(i, j) * symbol_per_RB * MCS_value(mcs_idx_ij(i, j), 4));
            rb_remain = remain_bit / (symbol_per_RB * MCS_value(mcs_idx_i(i), 4));
        elseif rb_ji(j, i) > rb_alloc(i, j)
            remain_bit = traffic_demand_j(j) - (rb_alloc(i, j) * symbol_per_RB * MCS_value(mcs_idx_ji(j, i), 4));
            rb_remain = remain_bit / (symbol_per_RB * MCS_value(mcs_idx_j(j), 4));
        end
        rb_remain = ceil(rb_remain);
        rb_alloc(i, j) = rb_alloc(i, j) + rb_remain;
    end
end
%}
%{
for i = 1 : max(U_i, U_j)
    for j = 1 : max(U_i, U_j)
        SE_ij(i, j) = (log2(1 + SINR_ij(i, j)) + log2(1 + SINR_ji(j, i))) / 2;
        if i <= U_i && j <= U_j
            SE_unpair = (log2(1 + SNR_i(i)) / 2 * rb_i(i) + log2(1 + SNR_j(j)) / 2 * rb_j(j)) / (rb_i(i) + rb_j(j));
            if SE_ij(i, j) < SE_unpair
                SE_ij(i, j) = SE_unpair;
                pair_ij(i, j) = 0;
                rb_alloc(i, j) = rb_i(i) + rb_j(j);
            end
        end
    end
end
%}
%{
for i = 1 : max(U_i, U_j)
    for j = 1 : max(U_i, U_j)
        %SE_ij(i, j) = (log2(1 + SINR_ij(i, j)) + log2(1 + SINR_ji(j, i))) / 2;
        if i <= U_i && j <= U_j
            %SE_unpair = (log2(1 + SNR_i(i)) / 2 * rb_i(i) + log2(1 + SNR_j(j)) / 2 * rb_j(j)) / (rb_i(i) + rb_j(j));
            if rb_alloc(i, j) > rb_i(i) + rb_j(j)
                %SE_ij(i, j) = SE_unpair;
                pair_ij(i, j) = 0;
                rb_alloc(i, j) = rb_i(i) + rb_j(j);
            end
        end
    end
end
%}
fig = 0;

%% random pairing
p_x = 1 : U_i;
p_x = p_x(randperm(length(p_x)));
p_y = zeros(1, U_j);
for x = 1 : U_i
   p_y(p_x(x)) = x; 
end

% plot topo
%{
topo_i = zeros(U_i, 2) + 1;
for n = 1 : U_i
    topo_i(n, 1) = n;
end
topo_j = zeros(U_j, 2) + 3;
for n = 1 : U_j
    topo_j(n, 1) = n;
end
fig = fig + 1;
figure(fig);
clf;
title('random user-pairing', 'FontSize', 14);
hold on;
plot(topo_i(:, 1), topo_i(:, 2), 'bo');
plot(topo_j(:, 1), topo_j(:, 2), 'ro');
for n = 1 : U_i 
    txt = sprintf('u%d', n);
    text(n, 0.8, txt);
end
for n = 1 : U_j
    txt = sprintf('v%d', n);
    text(n, 3.2, txt);
end
for n = 1 :U_i
    if ~p_x(n)
       continue; 
    end
    plot([topo_i(n, 1),topo_j(p_x(n), 1)],[topo_i(n, 2), topo_j(p_x(n), 2)], 'g');
end
hold off;
x_len = max(U_i, U_j) + 1;
axis([0 x_len 0 4]);
%}

% print the sumrate
sumrate_i_random = 0;
sumrate_j_random = 0;
rb_total_random = 0;
SE_random = 0;

for n = 1 : max(U_i, U_j)
   if ~p_x(n)
       sumrate_i_random = sumrate_i_random + log2(1 + SNR_i(n));
       rb_total_random = rb_total_random + rb_i(n);
       SE_random = SE_random + log2(1 + SNR_i(n)) / 2 * 2 * rb_i(n);
       continue;
   end
   sumrate_i_random = sumrate_i_random + log2(1 + SINR_ij(n, p_x(n)));
   rb_total_random = rb_total_random + rb_alloc(n, p_x(n));
   SE_random = SE_random + SE_ij(n, p_x(n)) * 2 * rb_alloc(n, p_x(n));
end
for n = 1 : max(U_i, U_j)
   if ~p_y(n)
       sumrate_j_random = sumrate_j_random + log2(1 + SNR_j(n));
       rb_total_random = rb_total_random + rb_j(n);
       SE_random = SE_random + log2(1 + SNR_j(n)) / 2 * 2 * rb_j(n);
       continue;
   end
   sumrate_j_random = sumrate_j_random + log2(1 + SINR_ji(n, p_y(n)));
end

%sumrate_i_bi
%sumrate_j_bi
sumrate_random = sumrate_i_random + sumrate_j_random;
rb_total_random;
SE_random = SE_random / (rb_total_random * 2);
SE_td_random = total_td / rb_total_random;
%% interference free

rb_total_if = 0;
for i = 1 : U_i
    rb_total_if = rb_total_if + rb_i(i); 
end
for j = 1 : U_j
    rb_total_if = rb_total_if + rb_j(j);
end

rb_total_if;
SE_td_if = total_td / rb_total_if;

%% exhausted search by SE
%{
SE_exhausted = 0;
[p_x, SE_exhausted] = exhausted_search(SE_ij, rb_alloc);
% plot 
topo_i = zeros(U_i, 2) + 1;
for n = 1 : U_i
    topo_i(n, 1) = n;
end
topo_j = zeros(U_j, 2) + 3;
for n = 1 : U_j
    topo_j(n, 1) = n;
end
fig = 1;
figure(fig);
clf;
title('bipartite user-pairing', 'FontSize', 14);
hold on;
plot(topo_i(:, 1), topo_i(:, 2), 'bo');
plot(topo_j(:, 1), topo_j(:, 2), 'ro');
for n = 1 : U_i 
    txt = sprintf('u%d', n);
    text(n, 0.8, txt);
end
for n = 1 : U_j
    txt = sprintf('v%d', n);
    text(n, 3.2, txt);
end
for n = 1 :U_i
    if ~p_x(n)
       continue; 
    end
    plot([topo_i(n, 1),topo_j(p_x(n), 1)],[topo_i(n, 2), topo_j(p_x(n), 2)], 'g');
end
hold off;
x_len = max(U_i, U_j) + 1;
axis([0 x_len 0 4]);
%}

%% threshold-based bipartite

% build the adjacent matrix by SINR
SINR_threshold = 5; %16QAM threshold
adj = zeros(max(U_i, U_j)) + 1;
for i = 1 : U_i
    for j = 1 : U_j
        if 10*log10(SINR_ij(i, j)) < SINR_threshold || 10*log10(SINR_ji(j, i)) < SINR_threshold
            adj(i, j) = 0;
        end
    end
end
[p_x_16qam, p_y_16qam, pair_16qam] = user_pairing_bipartite(adj);

SINR_threshold = 10.85; %64QAM threshold
% build the adjacent matrix
adj = zeros(max(U_i, U_j)) + 1;
for i = 1 : U_i
    for j = 1 : U_j
        if 10*log10(SINR_ij(i, j)) < SINR_threshold || 10*log10(SINR_ji(j, i)) < SINR_threshold
            adj(i, j) = 0;
        end
    end
end
[p_x_64qam, p_y_64qam, pair_64qam] = user_pairing_bipartite(adj);
sumrate_16qam = 0;
sumrate_64qam = 0;
for n = 1 : length(p_x_16qam)
   if p_x_16qam(n) ~= 0
       sumrate_16qam = sumrate_16qam + SINR_agg(n, p_x_16qam(n));
   end
   if p_x_64qam(n) ~= 0
       sumrate_64qam = sumrate_64qam + SINR_agg(n, p_x_64qam(n));
   end
end
if sumrate_16qam > sumrate_64qam
    p_x = p_x_16qam;
    p_y = p_y_16qam;
    pair = pair_16qam;
else 
    p_x = p_x_64qam;
    p_y = p_y_64qam;
    pair = pair_64qam;
end
%}
% build the adjacent matrix by SE
min_SE = min(SE_ij, [], 'all');
max_SE = max(SE_ij, [], 'all');
SE_threshold = min_SE + 0.25 * (max_SE - min_SE);
adj = zeros(max(U_i, U_j)) + 1;
for i = 1 : U_i
    for j = 1 : U_j
        if SE_ij(i, j) < SE_threshold
            adj(i, j) = 0;
        end
    end
end
[p_x, p_y, pair] = user_pairing_bipartite(adj);

% plot topo
%{
topo_i = zeros(U_i, 2) + 1;
for n = 1 : U_i
    topo_i(n, 1) = n;
end
topo_j = zeros(U_j, 2) + 3;
for n = 1 : U_j
    topo_j(n, 1) = n;
end
fig = fig + 1;
figure(fig);
clf;
title('bipartite user-pairing', 'FontSize', 14);
hold on;
plot(topo_i(:, 1), topo_i(:, 2), 'bo');
plot(topo_j(:, 1), topo_j(:, 2), 'ro');
for n = 1 : U_i 
    txt = sprintf('u%d', n);
    text(n, 0.8, txt);
end
for n = 1 : U_j
    txt = sprintf('v%d', n);
    text(n, 3.2, txt);
end
for n = 1 :U_i
    if ~p_x(n)
       continue; 
    end
    plot([topo_i(n, 1),topo_j(p_x(n), 1)],[topo_i(n, 2), topo_j(p_x(n), 2)], 'g');
end
hold off;
x_len = max(U_i, U_j) + 1;
axis([0 x_len 0 4]);
%}

% print the sumrate
sumrate_i_bi = 0;
sumrate_j_bi = 0;
%sumrate_check = 0;
rb_total_bi = 0;
SE_bi = 0;
%SE_td_bi = 0;

for n = 1 : max(U_i, U_j)
   if ~p_x(n)
       sumrate_i_bi = sumrate_i_bi + log2(1 + SNR_i(n));
       rb_total_bi = rb_total_bi + rb_i(n);
       SE_bi = SE_bi + log2(1 + SNR_i(n)) / 2 * 2 * rb_i(n);
       continue;
   end
   sumrate_i_bi = sumrate_i_bi + log2(1 + SINR_ij(n, p_x(n)));
   rb_total_bi = rb_total_bi + rb_alloc(n, p_x(n));
   SE_bi = SE_bi + SE_ij(n, p_x(n)) * 2 * rb_alloc(n, p_x(n));
end
for n = 1 : max(U_i, U_j)
   if ~p_y(n)
       sumrate_j_bi = sumrate_j_bi + log2(1 + SNR_j(n));
       rb_total_bi = rb_total_bi + rb_j(n);
       SE_bi = SE_bi + log2(1 + SNR_j(n)) / 2 * 2 * rb_j(n);
       continue;
   end
   sumrate_j_bi = sumrate_j_bi + log2(1 + SINR_ji(n, p_y(n)));
end

sumrate_i_bi;
sumrate_j_bi;
sumrate_bi = sumrate_i_bi + sumrate_j_bi;
rb_total_bi;
SE_bi = SE_bi / (rb_total_bi * 2);
SE_td_bi = total_td / rb_total_bi;
%% hungarian

% build the weight matrix
if strcmp(mode, 'spectrum efficiency')
    max_val = max(SE_ij, [], 'all');
    weight = max_val - SE_ij;
elseif strcmp(mode, 'RB_number')
    weight = rb_alloc;
else
    max_val = max(SINR_agg, [], 'all');
    weight = max_val - SINR_agg;
end

[Z, cost] = user_pairing_hungarian(weight);
% coordinates of users
topo_i = zeros(U_i, 2) + 1;
for n = 1 : U_i
    topo_i(n, 1) = n;
end
topo_j = zeros(U_j, 2) + 3;
for n = 1 : U_j
    topo_j(n, 1) = n;
end
% plot topo
%{
fig = fig + 1;
figure(fig);
clf;
title('hungarian user-pairing', 'FontSize', 14);
hold on;
plot(topo_i(:, 1), topo_i(:, 2), 'bo'); % plot user u 
plot(topo_j(:, 1), topo_j(:, 2), 'ro'); % plot user v
for n = 1 : U_i 
    txt = sprintf('u%d', n);
    text(n, 0.8, txt);
end
for n = 1 : U_j
    txt = sprintf('v%d', n);
    text(n, 3.2, txt);
end
% plot the pairing line
for i = 1 : U_i
    for j = 1 : U_j
        if Z(i, j)
            if pair_ij(i, j)
                plot([topo_i(i, 1),topo_j(j, 1)],[topo_i(i, 2), topo_j(j, 2)], 'g');
            else
                plot([topo_i(i, 1),topo_j(j, 1)],[topo_i(i, 2), topo_j(j, 2)], 'g:');
            end
        end
    end
end
hold off;
x_len = max(U_i, U_j) + 1;
axis([0 x_len 0 4]);
%}

% print the sumrate
sumrate_i = 0;
sumrate_j = 0;
sumrate = 0;
rb_total = 0;
SE = 0;

for i = 1 : size(Z, 1)
    for j = 1 : size(Z, 2)
        if Z(i,j)
            sumrate_i = sumrate_i + log2(1 + SINR_ij(i, j));
            sumrate_j = sumrate_j + log2(1 + SINR_ji(j, i));
            sumrate = sumrate + SINR_agg(i, j);
            rb_total = rb_total + rb_alloc(i, j);
            SE = SE + SE_ij(i, j) * rb_alloc(i, j) * 2;
        end
    end
end

sumrate_i;
sumrate_j;
sumrate ;
rb_total;
SE = SE / (rb_total * 2) ;
SE_td = total_td / rb_total;
%% heuristic

if strcmp(mode, 'spectrum efficiency')
    [p_x, p_y] = user_pairing_heuristic(SE_ij);
elseif strcmp(mode, 'RB_number')
    max_val = max(rb_alloc, [], 'all') + 1;
    weight = max_val - rb_alloc;
    [p_x, p_y] = user_pairing_heuristic(weight);
else
    [p_x, p_y] = user_pairing_heuristic(SINR_agg);
end

%{
% plot 
topo_i = zeros(U_i, 2) + 1;
for n = 1 : U_i
    topo_i(n, 1) = n;
end
topo_j = zeros(U_j, 2) + 3;
for n = 1 : U_j
    topo_j(n, 1) = n;
end

fig = fig + 1;
figure(fig);
clf;
title('heuristic user-pairing', 'FontSize', 14);
hold on;
plot(topo_i(:, 1), topo_i(:, 2), 'bo');
plot(topo_j(:, 1), topo_j(:, 2), 'ro');
for n = 1 : U_i 
    txt = sprintf('u%d', n);
    text(n, 0.8, txt);
end
for n = 1 : U_j
    txt = sprintf('v%d', n);
    text(n, 3.2, txt);
end
for n = 1 :U_i
    if ~p_x(n)
       continue; 
    end
    if pair_ij(n, p_x(n))
        plot([topo_i(n, 1),topo_j(p_x(n), 1)],[topo_i(n, 2), topo_j(p_x(n), 2)], 'g');
    else
        plot([topo_i(n, 1),topo_j(p_x(n), 1)],[topo_i(n, 2), topo_j(p_x(n), 2)], 'g:');
    end
end
hold off;
x_len = max(U_i, U_j) + 1;
axis([0 x_len 0 4]);
%}
% print the sumrate
sumrate_i_heur = 0;
sumrate_j_heur = 0;
rb_total_heur = 0;
SE_heur = 0;

for n = 1 : max(U_i, U_j)
   if ~p_x(n)
       continue;
   end
   sumrate_i_heur = sumrate_i_heur + log2(1 + SINR_ij(n, p_x(n)));
   rb_total_heur = rb_total_heur + rb_alloc(n, p_x(n));
   SE_heur = SE_heur + SE_ij(n, p_x(n)) * 2 * rb_alloc(n, p_x(n));
end
for n = 1 : max(U_i, U_j)
   if ~p_y(n)                                                                                                                                                                                                                                                                            
       continue;
   end
   sumrate_j_heur = sumrate_j_heur + log2(1 + SINR_ji(n, p_y(n)));
end

sumrate_i_heur;
sumrate_j_heur;
sumrate_heur = sumrate_i_heur + sumrate_j_heur;
rb_total_heur;
SE_heur = SE_heur / (rb_total_heur * 2);
SE_td_heur = total_td / rb_total_heur;
%% sumrate comparison between different pairing schemes
if mode == mode_type(1)
    fig = fig + 1;
    figure(fig);
    clf;
    title('sumrate comparison', 'FontSize', 14);
    hold on;

    Y = [sumrate sumrate_bi sumrate_heur;sumrate_i sumrate_i_bi sumrate_i_heur;sumrate_j sumrate_j_bi sumrate_j_heur];
    X = categorical({'aggregation','i','j'});
    X = reordercats(X,{'aggregation','i','j'});
    b = bar(X, Y);
    l = cell(1, 3);
    l{1} = 'hungarian'; l{2} = 'bipartite';l{3} = 'heuristic';
    legend(b, l);
    hold off;

    sr = [sumrate;sumrate_bi;sumrate_heur]
    if sumrate ~= max(sr)
        sumrate 
    end
end
%% rb_alloc comparison between different pairing schemes
%{
fig = fig + 1;
figure(fig);
clf;
title('rb number comparison', 'FontSize', 14);
hold on;

Y = [rb_total; rb_total_bi; rb_total_random];
X = categorical({'hungarian','bipartite','random'});
X = reordercats(X,{'hungarian','bipartite','random'});
b = bar(X, Y);

stat_rb(1) = stat_rb(1) + rb_total;
stat_rb(2) = stat_rb(1) + rb_total_bi;
stat_rb(3) = stat_rb(1) + rb_total_random;

hold off;
%}

% test
%{
fig = fig + 1;
figure(fig)
clf;
title('RB test', 'FontSize', 14);
hold on;


Y = [rb_total;rb_total_random;rb_total_if];
X = categorical({'hungarian','random','interference free'});
X = reordercats(X,{'hungarian','random','interference free'});
b = bar(X, Y);
%}
stat_rb(1) = stat_rb(1) + rb_total;
stat_rb(2) = stat_rb(2) + rb_total_random;
stat_rb(3) = stat_rb(3) + rb_total_if;
stat_rb(4) = stat_rb(4) + rb_total_bi;
stat_rb(5) = stat_rb(5) + rb_total_heur;

stat_SE(1) = stat_SE(1) + SE_td;
stat_SE(2) = stat_SE(2) + SE_td_random;
stat_SE(3) = stat_SE(3) + SE_td_if;
stat_SE(4) = stat_SE(4) + SE_td_bi;
stat_SE(5) = stat_SE(5) + SE_td_heur;
%% SE comparison between different pairing schemes
%{
if mode == mode_type(3) % SE 
    fig = fig + 1;
    figure(fig);
    clf;
    title('SE comparison', 'FontSize', 14);
    hold on;
    %{
    Y = [SE; SE_bi; SE_heur; SE_random];

    X = categorical({'hungarian','bipartite','heuristic','random'});
    X = reordercats(X,{'hungarian','bipartite','heuristic','random'});
    %}
    
    Y = [SE; SE_bi; SE_random];

    X = categorical({'hungarian','bipartite','random'});
    X = reordercats(X,{'hungarian','bipartite','random'});
    
    b = bar(X, Y);
    hold off;
elseif mode == mode_type(2) % RB 
    fig = fig + 1;
    figure(fig);
    clf;
    title('RB comparison', 'FontSize', 14);
    hold on;

    Y = [rb_total; rb_total_bi; rb_total_random];

    X = categorical({'hungarian','bipartite','random'});
    X = reordercats(X,{'hungarian','bipartite','random'});
    b = bar(X, Y);
    hold off;
    
    fig = fig + 1;
    figure(fig);
    clf;
    title('SE comparison', 'FontSize', 14);
    hold on;
    
    Y = [SE; SE_bi; SE_random];

    X = categorical({'hungarian','bipartite','random'});
    X = reordercats(X,{'hungarian','bipartite','random'});
    b = bar(X, Y);
    hold off;
end
%}
%pause(1);
end

% rb
fig = fig + 1;
figure(fig)
clf;
title('RB number comparison stat', 'FontSize', 14);
hold on;

%Y = [rb_total; rb_total_bi; rb_total_random];
stat_rb = stat_rb / sim_times;
%Y = [stat_rb(1);stat_rb(2);stat_rb(3)];
Y = stat_rb;
X = categorical({'hungarian','random','interference free', 'bipartite', 'heuristic'});
X = reordercats(X,{'hungarian','random','interference free', 'bipartite', 'heuristic'});
b = bar(X, Y);

line_rb_h(para) = stat_rb(1);
line_rb_random(para) = stat_rb(2);
line_rb_if(para) = stat_rb(3);
line_rb_bi(para) = stat_rb(4);
line_rb_heur(para) = stat_rb(5);

% SE
fig = fig + 1;
figure(fig)
clf;
title('SE comparison stat', 'FontSize', 14);
hold on;

stat_SE = stat_SE / sim_times;
Y = stat_SE;
X = categorical({'hungarian','random','interference free', 'bipartite', 'heuristic'});
X = reordercats(X,{'hungarian','random','interference free', 'bipartite', 'heuristic'});
b = bar(X, Y);

line_SE_h(para) = stat_SE(1) / 500;
line_SE_random(para) = stat_SE(2) / 500;
line_SE_if(para) = stat_SE(3) / 500;
line_SE_bi(para) = stat_SE(4) / 500;
line_SE_heur(para) = stat_SE(5) / 500;

util_compare = (stat_rb(3) - stat_rb(1)) / stat_rb(3) * 100;
end
%{
x=1:1:5;
a=[203.024;113.857;256.259;244.888;293.376]; % y value
b=[334.4,143.2,297.4,487.2,596.2]; % y value
c =[]
plot(x,a,'-*b',x,b,'-or');
axis([0,6,0,700])  
set(gca,'XTick',[0:1:6]) 
set(gca,'YTick',[0:100:700]) 
%legend('Neo4j','MongoDB'); 
xlabel('') 
ylabel('')
%}

fig = fig + 1;
h_figure = figure(fig)
clf;
%title('SE comparison stat', 'FontSize', 14);
hold on;

x=10:10:50;
%x = categorical(x);
%a=[203.024;113.857;256.259;244.888;293.376]; % y value
%b=[334.4,143.2,297.4,487.2,596.2]; % y value
p = plot(x,line_SE_h,'-*b',x,line_SE_random,'-+r',x,line_SE_if, '--xg',x, line_SE_bi, '-*y',x, line_SE_heur, '-*c');
p(1).LineWidth = 2;
p(2).LineWidth = 2;
p(3).LineWidth = 2;
p(4).LineWidth = 2;
p(5).LineWidth = 2;
xlim([10, 50]);
set(gca,'XTick',10:10:50, 'FontSize', 24);
ylim([0, inf]);
set(gca, 'FontSize', 24);
xlabel('number of UEs','FontSize', 24) 
ylabel('average sum-rate (Mbps)','FontSize', 24)
%legend(['interference-aware',sprintf('\n'), '(opt pairing)'],['interference-aware',sprintf('\n'), '(random pairing)'],'interference free','FontSize', 14); 
legend('interference-aware(opt pairing)','interference-aware(random pairing)','interference free','interference-aware(threshold pairing)', 'interference-aware(heuristic pairing)'  ,'FontSize', 18); 
%h_figure = figure;
%{
set(h_figure, 'PaperPositionMode', 'manual');
set(h_figure, 'PaperUnits', 'inches');
set(h_figure, 'Units', 'inches');
set(h_figure, 'PaperPosition', [0, 0, 10, 10]);
set(h_figure, 'Position', [0, 0, 4*1.5 ,1.5*1.5]);
%}

fig = fig + 1;
h_figure = figure(fig)
clf;
%title('RB comparison stat', 'FontSize', 14);
hold on;

x=10:10:50;
%x = categorical(x);
%a=[203.024;113.857;256.259;244.888;293.376]; % y value
%b=[334.4,143.2,297.4,487.2,596.2]; % y value
p = plot(x,line_rb_h,'-*b',x,line_rb_random,'-+r',x,line_rb_if, '--xg',x,line_rb_bi, '-*y',x, line_rb_heur, '-*c');
p(1).LineWidth = 2;
p(2).LineWidth = 2;
p(3).LineWidth = 2;
p(4).LineWidth = 2;
p(5).LineWidth = 2;
%axis([10,50]);
xlim([10, 50]);
set(gca,'XTick',10:10:50, 'FontSize', 24);
ylim([0, inf]);
set(gca, 'FontSize', 24);
%set(gca,'YTick',10:10:50);
%ylim([0 500])
xlabel('number of UEs','FontSize', 24) 
ylabel('number of occupied RBs','FontSize', 24)
%legend(['interference-aware',sprintf('\n'), '(opt pairing)'],['interference-aware',sprintf('\n'), '(random pairing)'],'interference free','FontSize', 18); 
legend('interference-aware(opt pairing)','interference-aware(random pairing)','interference free','interference-aware(threshold pairing)', 'interference-aware(heuristic pairing)'  ,'FontSize', 18); 

hold off;

fig = fig + 1;
h_figure = figure(fig)
clf;
%title('avg RB comparison stat', 'FontSize', 14);
hold on;

x=10:10:50;

line_avg_rb_h = line_rb_h ./ x.';
line_avg_rb_random = line_rb_random ./ x.';
line_avg_rb_if = line_rb_if ./ x.';
line_avg_rb_bi = line_rb_bi ./ x.';
line_avg_rb_heur = line_rb_heur ./ x.';
%x = categorical(x);
%a=[203.024;113.857;256.259;244.888;293.376]; % y value
%b=[334.4,143.2,297.4,487.2,596.2]; % y value
p = plot(x,line_avg_rb_h,'-*b',x,line_avg_rb_random,'-+r',x,line_avg_rb_if, '--xg',x,line_avg_rb_bi, '-*y',x, line_avg_rb_heur, '-*c');
p(1).LineWidth = 2;
p(2).LineWidth = 2;
p(3).LineWidth = 2;
p(4).LineWidth = 2; 
p(5).LineWidth = 2;
%axis([10,50]);
xlim([10, 50]);
set(gca,'XTick',10:10:50, 'FontSize', 24);
ylim([0, inf]);
set(gca, 'FontSize', 24);
%set(gca,'YTick',10:10:50);
%ylim([0 500])
xlabel('number of UEs','FontSize', 24) 
ylabel('number of average occupied RBs','FontSize', 24)
%legend(['interference-aware',sprintf('\n'), '(opt pairing)'],['interference-aware',sprintf('\n'), '(random pairing)'],'interference free','FontSize', 18); 
legend('interference-aware(opt pairing)','interference-aware(random pairing)','interference free','interference-aware(threshold pairing)', 'interference-aware(heuristic pairing)' ,'FontSize', 18); 

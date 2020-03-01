% simulation for user pairing 
% heuristic algorithm

% from x and y's perspective, find the best user 

% input:  martix adj (adjacent)
% output: p_x: paired user v for each user u 
%         p_y: paired user u for each user v
%         pair indicates number of pairs

function [pair_x, pair_y, pair] = user_pairing_heuristic(weight)
    global w;
    global p_x;
    global p_y;
    iteration_time = 3;
    
    w = weight;
    min_val = min(w, [], 'all');
    if min_val < 0
        w = w - min_val;
    end
    p_x = zeros(iteration_time, size(w, 1));
    p_y = zeros(iteration_time, size(w, 2));  
    c = zeros(size(w)); % candidates for user x 
    weight_x = w;
    weight_y = w;
    
    
    % find the candidates
    for iter = 1 : iteration_time
        %p_x = zeros(iter, size(w, 1));
        %p_y = zeros(iter, size(w, 2));
        for i = 1 : size(w, 1)
            best_c = max(weight_x(i, :)); 
            idx = find(weight_x(i, :) == best_c); % best candidate index from x perspective
            c(i, idx) = 1;
            weight_x(i, idx) = 0;
        end
        for j = 1 : size(w, 2)
            best_c = max(weight_y(:, j)); 
            idx = find(weight_y(:, j) == best_c); % best candidate index from x perspective
            c(idx, j) = 1;
            weight_y(idx, j) = 0;
        end
        c;
        pair = user_allocation(c, iter);
        %pair_x = p_x;
        %pair_y = p_y;
    end
    sumweight = zeros(iteration_time, 1);
    max_iter = 1;
    for iter = 1 : iteration_time
        for i = 1 : size(w, 1)
           if ~p_x(iter, i)
               continue;
           end
           sumweight(iter) = sumweight(iter) + w(i, p_x(iter, i));
           if sumweight(iter) >= sumweight(max_iter)
               max_iter = iter;
           end
        end
    end
    pair_x = p_x(max_iter, :);
    pair_y = p_y(max_iter, :);
    pair = length(find(pair_x(:) ~= 0));
end
    % check if the number of candidate of all user x is sufficient
    
    % user allocation
function pair = user_allocation(c, iter) 
    global w;
    global p_x;
    global p_y;
    pair = 0;
    for it = 1 : min(size(w))
        c_num = zeros(size(w, 1), 1) + size(w, 2);
        for i = 1 : size(w, 1)
            if p_x(iter, i) ~= 0
                continue;
            end
            if isempty(find(c(i, :) == 1))
                continue;
            end
            c_num(i, 1) = length(find(c(i, :) == 1));
        end 
        least_c = min(c_num); 
        phi = find(c_num(: ,1) == least_c); 
        % tilde_phi need to be implement when multi-paired
        best_w = 0;
        best_c_x = 0;
        best_c_y = 0;
        for i = 1 : length(phi)
            x = phi(i);
            idx = find(c(x, :) == 1);
            for j = 1 : length(idx)
                y = idx(j);
                if p_y(iter, y) ~= 0
                    continue;
                end
                if w(x, y) > best_w
                    best_w = w(x, y);
                    best_c_x = x;
                    best_c_y = y;
                end
            end
        end
        %Z(best_c_x, best_c_y) = 1;
        if ~best_w
            break;
        end
        p_x(iter, best_c_x) = best_c_y;
        p_y(iter, best_c_y) = best_c_x;
        c(best_c_x, :) = 0;
        c(:, best_c_y) = 0;
        c;
        pair = pair + 1;
    end
end
   
    
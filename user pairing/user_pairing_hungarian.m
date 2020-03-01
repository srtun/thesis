% simulation for user pairing 
% hungarian algorithm
% find the minimum weight of matching


% input: matrix w indicates the weight(must be square matrix) 
% output: matrix z indicates the matching result
%         cost indicates the minimum cost

function [Z, cost] = user_pairing_hungarian(weight)
    global w;
    global check_row;   % use for label whether this row is in minimum zero coverage (1 indicates NOT within coverage)
    global check_col;   % use for label whether this column is in minimum zero coverage (1 indicates within coverage)
    w = weight;
    % each row element minus the min of this row
    for i = 1 : size(w, 1)
        min_val = min(w(i, :));
        w(i, :) = w(i, :) - min_val;
    end
    zero_row = zeros(1, size(w, 1));    %indicate this row is paired to which column
    zero_col = zeros(1, size(w, 2));    %indicate this column is paired to which row
    %{
    for i = 1 : size(w, 1)
        if length(find(w(i, :) == 0)) == 1
            zero_row(i) = find(w(i, :) == 0);
        end
    end
    zero_row;
    %}
    %zero_idx = find(w(:, :) == 0);
    
    %update matrix w until paired entirely
    while(1)
        adj = zeros(size(w));
        for i = 1 : size(w, 1)
            for j = 1 : size(w, 2)
                if ~w(i, j)
                    adj(i, j) = 1;
                end
            end
        end
        
        % use bipartite matching to choose the zeros
        [zero_row, zero_col, pair] = user_pairing_bipartite(adj);
        if pair == size(w, 1)
            break
        end
        check_row = zeros(size(zero_row));
        check_col = zeros(size(zero_col));

        for i = 1 : size(w, 1)
            if zero_row(i) == 0
                check(i, zero_col);
            end
        end
        
        %remaining element minus the minimum value of them
        min_val = min(w(find(check_row == 1), find(check_col == 0)), [], 'all');
        w(find(check_row == 1), :) = w(find(check_row == 1), :) - min_val;
        w(:, find(check_col == 1)) = w(:, find(check_col == 1)) + min_val;
    end
    cost = 0;
    Z = zeros(size(w));
    for i = 1 : size(w, 1)
        Z(i, zero_row(i)) = 1;
        cost = cost + weight(i, zero_row(i));
    end
end

% find the minimum cover of w
function check(i, zero_col)
    global check_row;
    global check_col;
    global w;
    check_row(i) = 1; 
    for j = 1 : size(check_col, 2)
        if w(i, j) == 0 && check_col(j) == 0
            check_col(j) = 1;
            if zero_col(j)
                check(zero_col(j), zero_col);
            end
        end
    end
end
    
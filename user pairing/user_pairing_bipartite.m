% simulation for user pairing 
% bipartite matching problem

% input:  martix adj (adjacent)
% output: p_x: paired user v for each user u 
%         p_y: paired user u for each user v
%         pair indicates number of pairs
function [p_x, p_y, pair] = user_pairing_bipartite(adjacent)
    global adj;
    global c_x;
    global c_y;
    global m_y;
    adj = adjacent;
    c_x = zeros(1, size(adj, 1));
    c_y = zeros(1, size(adj, 2));
    pair = 0;
    for i = 1:size(adj, 1)
       m_y = zeros(1, size(adj, 2));
       if(match(i))
           pair = pair + 1;
       end
    end
    p_x = c_x;
    p_y = c_y;
end
   
function [bool] = match(i)
    global adj;
    global c_x;
    global c_y;
    global m_y;
    for j = 1:size(adj, 2)
        if(adj(i, j) && ~m_y(j))
            m_y(j) = 1;
            if(~c_y(j) || match(c_y(j)))
               c_x(i) = j;
               c_y(j) = i;
               bool = 1;
               return;
            end
        end
    end
    bool = 0;
end
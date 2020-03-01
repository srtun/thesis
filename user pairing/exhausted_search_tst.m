% exhausted search
% find the optimal SE 

function [p_x, min_weight] = exhausted_search_tst(w)
    %p_x;
    min_weight = 0;
    len = max(size(w));
    p = 1 : len;
    t = 0;
    while 1
        t = t + 1;
        weight = 0;
        for n = 1 : len 
            weight = weight + w(n, p(n));
        end
        if weight < min_weight || min_weight == 0
            min_weight = weight;
            p_x = p;
        end
        p = next_permutation(p);
        if isempty(p)
            break;
        end
    end
    
function p_next = next_permutation(p)
    vec = [];
    ptr = length(p);
    
    while 1
        if isempty(p)
            break;
        elseif ~isempty(vec) && p(ptr) < max(vec)
            idx = find(vec > p(ptr));
            temp = min(vec(idx)); 
            %temp = p(ptr);
            vec(find(vec == temp)) = [];
            vec = [vec, p(ptr)];
            p(ptr) = [];
            p = [p, temp];
            break;
        else
            vec = [vec, p(ptr)]; 
            p(ptr) = [];
            ptr = ptr - 1;
        end
    end
    if isempty(p) 
        p_next = p;
    else
        vec = sort(vec);
        p(ptr+1:ptr + length(vec)) = vec;
        p_next = p;
    end

    
    
    
    

    
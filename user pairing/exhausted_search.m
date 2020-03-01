% exhausted search
% find the optimal SE 

function [p_x, SE_exhausted] = exhausted_search(SE_ij, rb_alloc)
    SE_exhausted = 0;
    %p_x;
    len = max(size(SE_ij));
    p = 1 : len;
    t = 0;
    while 1
        t = t + 1;
        SE = 0;
        rb = 0;
        for n = 1 : len 
            rb = rb + rb_alloc(n, p(n));
            SE = SE + SE_ij(n, p(n)) * 2 * rb_alloc(n, p(n));
        end
        SE = SE / (rb * 2);
        if SE > SE_exhausted
            SE_exhausted = SE;
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

    
    
    
    

    
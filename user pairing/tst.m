clearvars
clc

for sim = 1 : 2000
    U_i = 6;
    w = randi(100,U_i,U_i);
    [Z, cost] = user_pairing_hungarian(w);
    p_h = zeros(1, U_i);
    for i = 1 : U_i 
        for j = 1 : U_i
            if Z(i, j)
                p_h(i) = j;
            end
        end
    end
    err = 0;
    [p_x, min_weight] = exhausted_search_tst(w);
    if min_weight ~= cost 
        err = err + 1;
    end
    
end
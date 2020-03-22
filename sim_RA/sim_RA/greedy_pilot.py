from __future__ import print_function
from ortools.sat.python import cp_model
#from setting import _setting
import setting
import setting_SIC
import random
import xlrd
import math
import os

def _greedy_pilot(match, RB_needed, rate, rate_pair, rate_reduce_ij, rate_reduce_ji, num_pilot):
    # [ ] TODO: 3/3 itf user need to be added in single queue
    # [ ] TODO: 3/12 bug: if there are only two sc and RB_needed = 3, it won't be allocated 
    # [x] TODO: method which not be taken will waste the traffic demands
    # [x] TODO: better method may have wasted RB
    # [ ] TODO: pilot check
    # [ ] TODO: fairness 
    # [ ] TODO: benchmarking algo? baseline
        #random
        #round robin

    num_bs, num_subcarriers, num_time_slots, num_users, num_users_i = setting._setting()

    all_bs = range(num_bs)
    all_users = range(num_users)
    all_subcarriers = range(num_subcarriers)
    all_time_slots = range(num_time_slots)
    all_users_i = []
    for i in all_bs:
        all_users_i.append(range(num_users_i[i]))

    num_itf_users, itf_idx_i, rate_reduce_ij, rate_reduce_ji, SNR_reduce_ij, SNR_reduce_ji, rate_reduce, rate_pair = setting_SIC._setting_SIC()

    #algorithm start
    
    ## sorting single users by rate
    queue_single_i = []
    for i in all_bs:
        queue_single_i.append(sorted(range(len(rate[i]) - num_itf_users), key=lambda u: rate[i][u])) #sort user by rate using index
    #print(queue_single_i)
    
    ## sorting pair users by rate
    queue_pair = []
    for u in all_users_i[0]:
        if u not in itf_idx_i[0]:
            queue_pair.append(0)
        else:
            queue_pair.append(rate_pair[u][match[0, u]])
    #sort all user and delete single users
    queue_pair = sorted(range(len(queue_pair)), key=lambda u: queue_pair[u])
    queue_pair = queue_pair[len(queue_pair) - num_itf_users:]
    l = 0
    while l < len(queue_pair):
        min_rb = min(RB_needed[0][queue_pair[l]], RB_needed[1][match[0, queue_pair[l] ] ])
        if min_rb < num_pilot:
            del queue_pair[l]
        else:
            l += 1
    #print(queue_pair)    
    sumrate_i = [0 for i in all_bs]   
    alloc_RB_i = []
    for i in all_bs:
        alloc_RB_i.append([])

    ## each time slot choose the better side (single or pair)
    for t in all_time_slots:
        for i in all_bs:
            alloc_RB_i[i].append(['x' for f in all_subcarriers])
        #alloc_RB_i.append([])
        f = num_subcarriers
        #pilot = 2
        #print(RB_needed)
        pair_temp_stack = [] # save the pair users which have only 3 RB

        # deciding number of subcarriers this turn
        while(f):
            pilot = num_pilot  
            min_rb = 0
            if f < num_pilot:
                pilot = f
            else: 
                if queue_pair:
                    min_rb = min(RB_needed[0][queue_pair[-1]], RB_needed[1][match[0, queue_pair[-1] ] ])  
                    while min_rb > f and min_rb < num_pilot * 2 and f == num_pilot: # bug 
                        pair_temp_stack.append(queue_pair[-1])
                        queue_pair.pop()
                        if queue_pair:
                            min_rb = min(RB_needed[0][queue_pair[-1]], RB_needed[1][match[0, queue_pair[-1] ] ])  
                        elif pair_temp_stack:
                            min_rb = num_pilot
                            queue_pair.append(pair_temp_stack[0])
                            del pair_temp_stack[0]
                            break
                        else: 
                            min_rb = 0
                            break
                if min_rb > num_pilot and min_rb < num_pilot * 2:
                    pilot = min_rb

            sumrate_single_i = [0 for i in all_bs]      # sumrate of single users in this time slot
            sumrate_pair_i = [0 for i in all_bs]        # sumrate of pair users in this time slot
            single_alloc_RB_i = [['x' for f in range(pilot)] for i in all_bs]
            #single_sumrate_i = [0 for i in all_bs]
            pair_alloc_RB_i = [['x' for f in range(pilot)] for i in all_bs]
            #pair_sumrate_i = [0 for i in all_bs]
        
            single_RB_return = [[0 for u in all_users_i[j]] for j in all_bs ]
            single_temp_queue = [[] for i in all_bs]
        
            ## choosing best pairing users
            pair_RB_return = [[0 for u in all_users_i[j]] for j in all_bs ]
            pair_temp_queue = []
            #f = num_subcarriers
            p = pilot
            
            if f >= num_pilot and queue_pair:
                #min_rb = min(RB_needed[0][queue_pair[-1]], RB_needed[1][match[0, queue_pair[-1] ] ]) 
                #if min_rb == p:
                sumrate_pair_i[0] += (rate[0][queue_pair[-1]] - rate_reduce_ij[queue_pair[-1]][ match[0, queue_pair[-1] ]] ) * p
                sumrate_pair_i[1] += (rate[1][match[0, queue_pair[-1] ]] - rate_reduce_ji[ match[0, queue_pair[-1] ]][queue_pair[-1]] ) * p
                #RB_needed[0][ queue_pair[-1] ] -= p
                #RB_needed[1][ match[0, queue_pair[-1] ] ] -= p
                while(p):
                    p -= 1
                    pair_alloc_RB_i[0][p] = queue_pair[-1]
                    pair_alloc_RB_i[1][p] = match[0, queue_pair[-1]]
                    pair_RB_return[0][queue_pair[-1]] += 1
                    pair_RB_return[1][match[0, queue_pair[-1]]] += 1
                if min_rb == pilot:
                    pair_temp_queue.append(queue_pair[-1])
                    queue_pair.pop()
            while pair_temp_stack:
                queue_pair.append(pair_temp_stack[-1])
                pair_temp_stack.pop()
            #print('pair')
            #print(pair_alloc_RB_i)


            ## choosing best single user
            for i in all_bs:
                #f = num_subcarriers
                p = len(pair_alloc_RB_i[0])
                while(p):
                    if not queue_single_i[i]:
                        break
                    elif RB_needed[i][queue_single_i[i][-1]] <= p:
                        sumrate_single_i[i] += rate[i][queue_single_i[i][-1]] * RB_needed[i][queue_single_i[i][-1]]
                        #f -= RB_needed[queue_single_i[i][-1]]
                        for n in range(RB_needed[i][queue_single_i[i][-1]]):
                            p -= 1
                            single_alloc_RB_i[i][p] = queue_single_i[i][-1]
                            single_RB_return[i][queue_single_i[i][-1]] += 1
                        #RB_needed[i][queue_single_i[i][-1]] = 0
                        single_temp_queue[i].append(queue_single_i[i][-1])
                        queue_single_i[i].pop()
                    else:
                        sumrate_single_i[i] += rate[i][queue_single_i[i][-1]] * p
                        #RB_needed[i][queue_single_i[i][-1]] -= p
                        while(p):
                            p -= 1
                            single_alloc_RB_i[i][p] = queue_single_i[i][-1]
                            single_RB_return[i][queue_single_i[i][-1]] += 1
                        #f = 0
            ## comparison
            ## choose pair users to allcoate
            if sum(sumrate_pair_i) > sum(sumrate_single_i): 
                for i in all_bs:
                    for p in range(len(pair_alloc_RB_i[0])):
                        alloc_RB_i[i][t][f - 1 - p] = pair_alloc_RB_i[i][pilot - 1 - p]
                        if alloc_RB_i[i][t][f - 1 - p] != 'x':
                            RB_needed[i][alloc_RB_i[i][t][f - 1 - p]] -= 1
                    sumrate_i[i] += sumrate_pair_i[i] / 10000
                    # return the state of single user
                    while(single_temp_queue[i]):
                        queue_single_i[i].append(single_temp_queue[i][-1])
                        single_temp_queue[i].pop()
                    for u in all_users_i[i]:
                        #RB_needed[i][u] += single_RB_return[i][u]
                        pass
                

            ## choose single user to allocate              
            else:                                          
                for i in all_bs:
                    for p in range(len(single_alloc_RB_i[0])):
                        alloc_RB_i[i][t][f - 1 - p] = single_alloc_RB_i[i][len(single_alloc_RB_i[i]) - 1 - p]
                        if alloc_RB_i[i][t][f - 1 - p] != 'x':
                            RB_needed[i][alloc_RB_i[i][t][f - 1 - p]] -= 1
                    sumrate_i[i] += sumrate_single_i[i] / 10000
                # return the state of pair users
                while(pair_temp_queue):
                    queue_pair.append(pair_temp_queue[-1])
                    pair_temp_queue.pop()
                for i in all_bs:
                    for u in all_users_i[i]:
                        #RB_needed[i][u] += pair_RB_return[i][u]
                        pass
            
            #print(alloc_RB_i[0][t])
            #print(alloc_RB_i[1][t])
            #print(RB_needed)
            #print(queue_pair)
            f -= len(pair_alloc_RB_i[0])
            #print(sumrate_i)
            pass
    RB_used_i = [[0 for u in all_users_i[i]] for i in all_bs]
    #print(RB_used_i)
    for i in all_bs:
        for t in all_time_slots:
            for f in all_subcarriers:
                if alloc_RB_i[i][t][f] != 'x':
                    RB_used_i[i][ alloc_RB_i[i][t][f] ] += 1 
    #transpose alloc_RB_i[i][t][f] into alloc_RB_i[i][f][t]
    for i in all_bs:
        alloc_RB_i[i] = list(map(list, zip(*alloc_RB_i[i])))
        pass
    #a = 0
    return alloc_RB_i, sumrate_i, RB_used_i


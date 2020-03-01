from __future__ import print_function
from ortools.sat.python import cp_model
from setting import _setting
#from exhausted_search import _exhausted_search
import random
import xlrd
import math
import os

def _greedy(match, RB_needed, rate, rate_pair, rate_reduce_ij, rate_reduce_ji):
    # [ ] TODO: 2/27 for p: compare single and pair ??
    # [ ] TODO: 2/27 check wasted RB after all alloc??
    # [x] TODO: method which not be taken will waste the traffic demands
    # [x] TODO: better method may have wasted RB
    # [ ] TODO: pilot check
    # [ ] TODO: fairness (user fairness?? method fairness??)
        #by times (same method should't be taken more than x time slots consistently)
        #by weight (starving method increase the weight)
    # [ ] TODO: benchmarking algo? baseline
        #random
        #round robin

    num_bs, num_subcarriers, num_time_slots, num_users, num_users_i, num_itf_users, itf_idx_i = _setting()

    all_bs = range(num_bs)
    all_users = range(num_users)
    all_subcarriers = range(num_subcarriers)
    all_time_slots = range(num_time_slots)
    all_users_i = []
    for i in all_bs:
        all_users_i.append(range(num_users_i[i]))

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
    print(queue_pair)
    
   
    sumrate_i = [0 for i in all_bs]   
    alloc_RB_i = []
    for i in all_bs:
        alloc_RB_i.append([])

    ## each time slot choose the better side (single or pair)
    for t in all_time_slots:
        #alloc_RB_i.append([])
        sumrate_single_i = [0 for i in all_bs]      # sumrate of single users in this time slot
        sumrate_pair_i = [0 for i in all_bs]        # sumrate of pair users in this time slot
        #sumrate_pair = 0
        f = num_subcarriers
        single_alloc_RB_i = [['x' for f in all_subcarriers] for i in all_bs]
        #single_sumrate_i = [0 for i in all_bs]
        pair_alloc_RB_i = [['x' for f in all_subcarriers] for i in all_bs]
        #pair_sumrate_i = [0 for i in all_bs]
        
        single_RB_return = [[0 for u in all_users_i[j]] for j in all_bs ]
        single_temp_queue = [[] for i in all_bs]
        
        ## choosing best single user
        for i in all_bs:
            f = num_subcarriers
            while(f):
                if not queue_single_i[i]:
                    break
                elif RB_needed[i][queue_single_i[i][-1]] <= f:
                    sumrate_single_i[i] += rate[i][queue_single_i[i][-1]] * RB_needed[i][queue_single_i[i][-1]]
                    #f -= RB_needed[queue_single_i[i][-1]]
                    for n in range(RB_needed[i][queue_single_i[i][-1]]):
                        f -= 1
                        single_alloc_RB_i[i][f] = queue_single_i[i][-1]
                        single_RB_return[i][queue_single_i[i][-1]] += 1
                    RB_needed[i][queue_single_i[i][-1]] = 0
                    single_temp_queue[i].append(queue_single_i[i][-1])
                    queue_single_i[i].pop()
                else:
                    sumrate_single_i[i] += rate[i][queue_single_i[i][-1]] * f
                    RB_needed[i][queue_single_i[i][-1]] -= f
                    while(f):
                        f -= 1
                        single_alloc_RB_i[i][f] = queue_single_i[i][-1]
                        single_RB_return[i][queue_single_i[i][-1]] += 1
                    #f = 0
        
        ## choosing best pairing users
        pair_RB_return = [[0 for u in all_users_i[j]] for j in all_bs ]
        pair_temp_queue = []
        f = num_subcarriers
        while(f):
            if not queue_pair:
                break
            min_rb = min(RB_needed[0][queue_pair[-1]], RB_needed[1][match[0, queue_pair[-1] ] ]) 
            if min_rb <= f:
                #sumrate_pair += rate_pair[queue_pair[-1]][ match[0, queue_pair[-1] ] ] * min_rb
                sumrate_pair_i[0] += (rate[0][queue_pair[-1]] - rate_reduce_ij[queue_pair[-1]][ match[0, queue_pair[-1] ]] ) * min_rb
                sumrate_pair_i[1] += (rate[1][match[0, queue_pair[-1] ]] - rate_reduce_ji[ match[0, queue_pair[-1] ]][queue_pair[-1]] ) * min_rb
                #if sumrate_pair != sum(sumrate_pair_i):
                    #os.system('pause')
                #f -= min_rb
                for n in range(min_rb):
                        f -= 1
                        pair_alloc_RB_i[0][f] = queue_pair[-1]
                        pair_alloc_RB_i[1][f] = match[0, queue_pair[-1]]
                        pair_RB_return[0][queue_pair[-1]] += 1
                        pair_RB_return[1][match[0, queue_pair[-1]]] += 1
                RB_needed[0][ queue_pair[-1] ] -= min_rb
                RB_needed[1][ match[0, queue_pair[-1] ] ] -= min_rb
                pair_temp_queue.append(queue_pair[-1])
                queue_pair.pop()
            else:
                #sumrate_pair += rate_pair[queue_pair[-1]][ match[0, queue_pair[-1] ] ] * f
                sumrate_pair_i[0] += (rate[0][queue_pair[-1]] - rate_reduce_ij[queue_pair[-1]][ match[0, queue_pair[-1] ]] ) * f
                sumrate_pair_i[1] += (rate[1][match[0, queue_pair[-1] ]] - rate_reduce_ji[ match[0, queue_pair[-1] ]][queue_pair[-1]] ) * f
                RB_needed[0][ queue_pair[-1] ] -= f
                RB_needed[1][ match[0, queue_pair[-1] ] ] -= f
                while(f):
                        f -= 1
                        pair_alloc_RB_i[0][f] = queue_pair[-1]
                        pair_alloc_RB_i[1][f] = match[0, queue_pair[-1]]
                        pair_RB_return[0][queue_pair[-1]] += 1
                        pair_RB_return[1][match[0, queue_pair[-1]]] += 1
                #f = 0
        print('pair')
        print(pair_alloc_RB_i)

        ## comparison
        ## choose pair users to allcoate
        if sum(sumrate_pair_i) > sum(sumrate_single_i): 
            for i in all_bs:
                alloc_RB_i[i].append(pair_alloc_RB_i[i])
                sumrate_i[i] += sumrate_pair_i[i] / 10000
                # return the state of single user
                while(single_temp_queue[i]):
                    queue_single_i[i].append(single_temp_queue[i][-1])
                    single_temp_queue[i].pop()
                for u in all_users_i[i]:
                    RB_needed[i][u] += single_RB_return[i][u]
            # allocate wasted RB to single user
            wasted_RB = num_subcarriers - max(sum(pair_RB_return[0]), sum(pair_RB_return[1]))
            for i in all_bs:
                f = wasted_RB
                while(f):
                    if not queue_single_i[i]:
                        break
                    elif RB_needed[i][queue_single_i[i][-1]] <= f: 
                        sumrate_i[i] += rate[i][queue_single_i[i][-1]] * RB_needed[i][queue_single_i[i][-1]] / 10000
                        for n in range(RB_needed[i][queue_single_i[i][-1]]):
                            f -= 1
                            alloc_RB_i[i][t][f] = queue_single_i[i][-1]
                            #single_RB_return[i][queue_single_i[i][-1]] += 1
                        RB_needed[i][queue_single_i[i][-1]] = 0
                        queue_single_i[i].pop()
                    else: 
                        sumrate_i[i] += rate[i][queue_single_i[i][-1]] * f / 10000
                        RB_needed[i][queue_single_i[i][-1]] -= f
                        while(f):
                            f -= 1
                            alloc_RB_i[i][t][f] = queue_single_i[i][-1]
                            #single_RB_return[i][queue_single_i[i][-1]] += 1

        ## choose single user to allocate              
        else:                                          
            for i in all_bs:
                alloc_RB_i[i].append(single_alloc_RB_i[i])
                sumrate_i[i] += sumrate_single_i[i] / 10000
            # return the state of pair users
            while(pair_temp_queue):
                queue_pair.append(pair_temp_queue[-1])
                pair_temp_queue.pop()
            for i in all_bs:
                for u in all_users_i[i]:
                    RB_needed[i][u] += pair_RB_return[i][u]

            # allocate wasted RB to pair users
            wasted_RB = num_subcarriers - max(sum(single_RB_return[0]), sum(single_RB_return[1]))
            f = wasted_RB
            while(f):
                if not queue_pair:
                    break
                min_rb = min(RB_needed[0][queue_pair[-1]], RB_needed[1][match[0, queue_pair[-1] ] ]) 
                if min_rb <= f:
                    sumrate_i[0] += (rate[0][queue_pair[-1]] - rate_reduce_ij[queue_pair[-1]][ match[0, queue_pair[-1] ]] ) * min_rb / 10000
                    sumrate_i[1] += (rate[1][match[0, queue_pair[-1] ]] - rate_reduce_ji[ match[0, queue_pair[-1] ]][queue_pair[-1]] ) * min_rb / 10000
                    for n in range(min_rb):
                        f -= 1
                        alloc_RB_i[0][t][f] = queue_pair[-1]
                        alloc_RB_i[1][t][f] = match[0, queue_pair[-1]]
                        #pair_RB_return[0][queue_pair[-1]] += 1
                        #pair_RB_return[1][match[0, queue_pair[-1]]] += 1
                    RB_needed[0][ queue_pair[-1] ] -= min_rb
                    RB_needed[1][ match[0, queue_pair[-1] ] ] -= min_rb
                    #pair_temp_queue.append(queue_pair[-1])
                    queue_pair.pop()
                else:
                    sumrate_i[0] += (rate[0][queue_pair[-1]] - rate_reduce_ij[queue_pair[-1]][ match[0, queue_pair[-1] ]] ) * f / 10000
                    sumrate_i[1] += (rate[1][match[0, queue_pair[-1] ]] - rate_reduce_ji[ match[0, queue_pair[-1] ]][queue_pair[-1]] ) * f / 10000
                    RB_needed[0][ queue_pair[-1] ] -= f
                    RB_needed[1][ match[0, queue_pair[-1] ] ] -= f
                    while(f):
                            f -= 1
                            alloc_RB_i[0][t][f] = queue_pair[-1]
                            alloc_RB_i[1][t][f] = match[0, queue_pair[-1]]
                            #pair_RB_return[0][queue_pair[-1]] += 1
                            #pair_RB_return[1][match[0, queue_pair[-1]]] += 1

    RB_used_i = [[0 for u in all_users_i[i]] for i in all_bs]
    #print(RB_used_i)
    for i in all_bs:
        for t in all_time_slots:
            for f in all_subcarriers:
                if alloc_RB_i[i][t][f] != 'x':
                    RB_used_i[i][ alloc_RB_i[i][t][f] ] += 1 
               
    #a = 0
    return alloc_RB_i, sumrate_i, RB_used_i

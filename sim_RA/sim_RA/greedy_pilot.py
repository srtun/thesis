from __future__ import print_function
from ortools.sat.python import cp_model
from setting import _setting
import random
import xlrd
import math
import os

def _greedy_pilot(match, RB_needed, rate, rate_pair, rate_reduce_ij, rate_reduce_ji):
    # [ ] TODO: 2/27 check wasted RB after all alloc??
    # [ ] TODO: 3/2 with pilot number, pair user only choose 1 pair?
    # [ ] TODO: 3/3 itf user need to be added in single queue
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
        pilot = 2

        while(f):
            sumrate_single_i = [0 for i in all_bs]      # sumrate of single users in this time slot
            sumrate_pair_i = [0 for i in all_bs]        # sumrate of pair users in this time slot
            single_alloc_RB_i = [['x' for f in range(pilot)] for i in all_bs]
            #single_sumrate_i = [0 for i in all_bs]
            pair_alloc_RB_i = [['x' for f in range(pilot)] for i in all_bs]
            #pair_sumrate_i = [0 for i in all_bs]
        
            single_RB_return = [[0 for u in all_users_i[j]] for j in all_bs ]
            single_temp_queue = [[] for i in all_bs]

            ## choosing best single user
            for i in all_bs:
                #f = num_subcarriers
                p = pilot
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
                        RB_needed[i][queue_single_i[i][-1]] = 0
                        single_temp_queue[i].append(queue_single_i[i][-1])
                        queue_single_i[i].pop()
                    else:
                        sumrate_single_i[i] += rate[i][queue_single_i[i][-1]] * p
                        RB_needed[i][queue_single_i[i][-1]] -= p
                        while(p):
                            p -= 1
                            single_alloc_RB_i[i][p] = queue_single_i[i][-1]
                            single_RB_return[i][queue_single_i[i][-1]] += 1
                        #f = 0
        
            ## choosing best pairing users
            pair_RB_return = [[0 for u in all_users_i[j]] for j in all_bs ]
            pair_temp_queue = []
            #f = num_subcarriers
            p = pilot
            while(p):
                if not queue_pair:
                    break
                min_rb = min(RB_needed[0][queue_pair[-1]], RB_needed[1][match[0, queue_pair[-1] ] ]) 
                if min_rb <= p:
                    #sumrate_pair += rate_pair[queue_pair[-1]][ match[0, queue_pair[-1] ] ] * min_rb
                    sumrate_pair_i[0] += (rate[0][queue_pair[-1]] - rate_reduce_ij[queue_pair[-1]][ match[0, queue_pair[-1] ]] ) * min_rb
                    sumrate_pair_i[1] += (rate[1][match[0, queue_pair[-1] ]] - rate_reduce_ji[ match[0, queue_pair[-1] ]][queue_pair[-1]] ) * min_rb
                    #if sumrate_pair != sum(sumrate_pair_i):
                        #os.system('pause')
                    #f -= min_rb
                    for n in range(min_rb):
                            p -= 1
                            pair_alloc_RB_i[0][p] = queue_pair[-1]
                            pair_alloc_RB_i[1][p] = match[0, queue_pair[-1]]
                            pair_RB_return[0][queue_pair[-1]] += 1
                            pair_RB_return[1][match[0, queue_pair[-1]]] += 1
                    RB_needed[0][ queue_pair[-1] ] -= min_rb
                    RB_needed[1][ match[0, queue_pair[-1] ] ] -= min_rb
                    pair_temp_queue.append(queue_pair[-1])
                    queue_pair.pop()
                else:
                    #sumrate_pair += rate_pair[queue_pair[-1]][ match[0, queue_pair[-1] ] ] * f
                    sumrate_pair_i[0] += (rate[0][queue_pair[-1]] - rate_reduce_ij[queue_pair[-1]][ match[0, queue_pair[-1] ]] ) * p
                    sumrate_pair_i[1] += (rate[1][match[0, queue_pair[-1] ]] - rate_reduce_ji[ match[0, queue_pair[-1] ]][queue_pair[-1]] ) * p
                    RB_needed[0][ queue_pair[-1] ] -= p
                    RB_needed[1][ match[0, queue_pair[-1] ] ] -= p
                    while(p):
                            p -= 1
                            pair_alloc_RB_i[0][p] = queue_pair[-1]
                            pair_alloc_RB_i[1][p] = match[0, queue_pair[-1]]
                            pair_RB_return[0][queue_pair[-1]] += 1
                            pair_RB_return[1][match[0, queue_pair[-1]]] += 1
                    #f = 0
            #print('pair')
            #print(pair_alloc_RB_i)

            ## comparison
            ## choose pair users to allcoate
            if sum(sumrate_pair_i) > sum(sumrate_single_i): 
                for i in all_bs:
                    for p in range(pilot):
                        alloc_RB_i[i][t][f - 1 - p] = pair_alloc_RB_i[i][pilot - 1 - p]
                    sumrate_i[i] += sumrate_pair_i[i] / 10000
                    # return the state of single user
                    while(single_temp_queue[i]):
                        queue_single_i[i].append(single_temp_queue[i][-1])
                        single_temp_queue[i].pop()
                    for u in all_users_i[i]:
                        RB_needed[i][u] += single_RB_return[i][u]
                # allocate wasted RB to single user
                wasted_RB = pilot - max(sum(pair_RB_return[0]), sum(pair_RB_return[1]))
                for i in all_bs:
                    p = wasted_RB
                    while(p):
                        if not queue_single_i[i]:
                            break
                        elif RB_needed[i][queue_single_i[i][-1]] <= p: 
                            sumrate_i[i] += rate[i][queue_single_i[i][-1]] * RB_needed[i][queue_single_i[i][-1]] / 10000
                            for n in range(RB_needed[i][queue_single_i[i][-1]]):
                                p -= 1
                                alloc_RB_i[i][t][f - pilot + p] = queue_single_i[i][-1]
                                #single_RB_return[i][queue_single_i[i][-1]] += 1
                            RB_needed[i][queue_single_i[i][-1]] = 0
                            queue_single_i[i].pop()
                        else: 
                            sumrate_i[i] += rate[i][queue_single_i[i][-1]] * p / 10000
                            RB_needed[i][queue_single_i[i][-1]] -= p
                            while(p):
                                p -= 1
                                alloc_RB_i[i][t][f - pilot + p] = queue_single_i[i][-1]
                                #single_RB_return[i][queue_single_i[i][-1]] += 1

            ## choose single user to allocate              
            else:                                          
                for i in all_bs:
                    for p in range(pilot):
                        alloc_RB_i[i][t][f - 1 - p] = single_alloc_RB_i[i][pilot - 1 - p]
                    sumrate_i[i] += sumrate_single_i[i] / 10000
                # return the state of pair users
                while(pair_temp_queue):
                    queue_pair.append(pair_temp_queue[-1])
                    pair_temp_queue.pop()
                for i in all_bs:
                    for u in all_users_i[i]:
                        RB_needed[i][u] += pair_RB_return[i][u]

                # allocate wasted RB to pair users
                wasted_RB = pilot - max(sum(single_RB_return[0]), sum(single_RB_return[1]))
                p = wasted_RB
                while(p):
                    if not queue_pair:
                        break
                    min_rb = min(RB_needed[0][queue_pair[-1]], RB_needed[1][match[0, queue_pair[-1] ] ]) 
                    if min_rb <= p:
                        sumrate_i[0] += (rate[0][queue_pair[-1]] - rate_reduce_ij[queue_pair[-1]][ match[0, queue_pair[-1] ]] ) * min_rb / 10000
                        sumrate_i[1] += (rate[1][match[0, queue_pair[-1] ]] - rate_reduce_ji[ match[0, queue_pair[-1] ]][queue_pair[-1]] ) * min_rb / 10000
                        for n in range(min_rb):
                            p -= 1
                            alloc_RB_i[0][t][f - pilot + p] = queue_pair[-1]
                            alloc_RB_i[1][t][f - pilot + p] = match[0, queue_pair[-1]]
                            #pair_RB_return[0][queue_pair[-1]] += 1
                            #pair_RB_return[1][match[0, queue_pair[-1]]] += 1
                        RB_needed[0][ queue_pair[-1] ] -= min_rb
                        RB_needed[1][ match[0, queue_pair[-1] ] ] -= min_rb
                        #pair_temp_queue.append(queue_pair[-1])
                        queue_pair.pop()
                    else:
                        sumrate_i[0] += (rate[0][queue_pair[-1]] - rate_reduce_ij[queue_pair[-1]][ match[0, queue_pair[-1] ]] ) * p / 10000
                        sumrate_i[1] += (rate[1][match[0, queue_pair[-1] ]] - rate_reduce_ji[ match[0, queue_pair[-1] ]][queue_pair[-1]] ) * p / 10000
                        RB_needed[0][ queue_pair[-1] ] -= p
                        RB_needed[1][ match[0, queue_pair[-1] ] ] -= p
                        while(p):
                                p -= 1
                                alloc_RB_i[0][t][f - pilot + p] = queue_pair[-1]
                                alloc_RB_i[1][t][f - pilot + p] = match[0, queue_pair[-1]]
                                #pair_RB_return[0][queue_pair[-1]] += 1
                                #pair_RB_return[1][match[0, queue_pair[-1]]] += 1
            f -= pilot
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


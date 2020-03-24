from __future__ import print_function
from ortools.sat.python import cp_model
#from setting import _setting
import setting
import setting_SIC
import random
import xlrd
import math
import os

def _greedy_merge(match, RB_needed, rate, rate_pair, rate_reduce_ij, rate_reduce_ji):

    num_bs, num_subcarriers, num_time_slots, num_users, num_users_i = setting._setting()

    all_bs = range(num_bs)
    all_users = range(num_users)
    all_subcarriers = range(num_subcarriers)
    all_time_slots = range(num_time_slots)
    all_users_i = []
    for i in all_bs:
        all_users_i.append(range(num_users_i[i]))

    num_itf_users, itf_idx_i, rate_reduce_ij, rate_reduce_ji, SNR_reduce_ij, SNR_reduce_ji, rate_reduce, rate_pair = setting_SIC._setting_SIC()

    ##------------- algo start -------------------------------------
    queue_single_i = []
    queue_itf_i = []
    print(rate)
    #---- sorting single users by rate
    for i in all_bs:
        queue_single_i.append(sorted(range(len(rate[i]) - num_itf_users), key=lambda u: rate[i][u]))
    print(queue_single_i)

    #---- sorting interfering users by rate
    for i in all_bs:
        queue_itf_i.append(sorted(range(len(rate[i]) - num_itf_users, len(rate[i])), key=lambda u: rate[i][u]))
    print(queue_itf_i)

    alloc_RB_i = []
    for i in all_bs:
        alloc_RB_i.append([])

    RB_sufficient = False
    muting_RB_idx_i = [[ [] for u in all_users_i[i] ] for i in all_bs]
    #muting_RB_i = [ [0 for u in all_users_i[i]] for i in all_bs ]

    #------------- initial allocate
    for t in all_time_slots:
        for i in all_bs:
            alloc_RB_i[i].append(['x' for f in all_subcarriers])
        f = num_subcarriers 
        while f:
            sumrate_single = 0
            sumrate_itf = 0

            #-- calculate best sumrate of single users
            for i in all_bs:
                if queue_single_i[i]:
                    sumrate_single += rate[i][queue_single_i[i][-1]]
            #print(sumrate_single)

            #-- calculate best sumrate of interfering users
            max_sumrate_i = [0 for i in all_bs] 
            for i in all_bs:
                if queue_itf_i[i]:
                    max_sumrate_i[i] = rate[i][queue_itf_i[i][-1]]
            sumrate_itf = max(max_sumrate_i)
            #print(sumrate_itf)

            #-- no user to allocate
            if not sumrate_itf and not sumrate_single:
                RB_sufficient = True
                break
            #-- choose single user to allocate
            elif sumrate_single >= sumrate_itf:
                for i in all_bs:
                    if queue_single_i[i]:
                        alloc_RB_i[i][t][f - 1] = queue_single_i[i][-1]
                        RB_needed[i][queue_single_i[i][-1]] -= 1
                        if RB_needed[i][queue_single_i[i][-1]] == 0:
                            queue_single_i[i].pop()

            #-- choose interfering user to allocate
            else:
                i = max_sumrate_i.index(max(max_sumrate_i))
                alloc_RB_i[i][t][f - 1] = queue_itf_i[i][-1]
                RB_needed[i][queue_itf_i[i][-1]] -= 1
                #muting_RB_i[i][queue_itf_i[i][-1]] += 1
                muting_RB_idx_i[i][queue_itf_i[i][-1]].append(f - 1 + t * num_subcarriers)
                if RB_needed[i][queue_itf_i[i][-1]] == 0:
                    queue_itf_i[i].pop()
            f -= 1

    '''
    print(alloc_RB_i[0])
    print(alloc_RB_i[1])
    print(muting_RB_idx_i[0])
    print(muting_RB_idx_i[1])
    print()
    '''

    for i in all_bs:
        for u in all_users_i[i]:
            muting_RB_idx_i[i][u].sort()

    #---- sorting pairing user by reduce rate
    queue_reduce = sorted(range(len(rate[i]) - num_itf_users, len(rate[i])), key=lambda u: rate_reduce[u][match[0, u]], reverse = True)
    #print(rate_reduce)
    #print(queue_reduce)
    print('RB_needed')
    print(RB_needed)

    if not queue_itf_i and not queue_single_i:
        RB_sufficient = True
    
    #---------- do merging when RB is not sufficient
    while not RB_sufficient:
        #print(alloc_RB_i[0])
        #print(alloc_RB_i[1])
        for i in all_bs:
            print()
            for f in all_subcarriers:
                for t in all_time_slots:
                    print(alloc_RB_i[i][t][f],sep = '',end = '')
                print()

        print(muting_RB_idx_i[0])
        print(muting_RB_idx_i[1])
        
        #-- find the pairing user which will reduce least rate when merging
        merge_pair = -1
        for u in queue_reduce:
            if muting_RB_idx_i[0][u] and muting_RB_idx_i[1][match[0, u]]:
                merge_pair = u
                break

        if merge_pair != -1:
            RB_idx = [muting_RB_idx_i[0][merge_pair][-1] ,muting_RB_idx_i[1][ match[0, merge_pair]][-1] ]
            t = RB_idx[1] // num_subcarriers
            f = RB_idx[1] % num_subcarriers
            muting_RB_idx_i[0][merge_pair].pop()
            muting_RB_idx_i[1][match[0, merge_pair]].pop()

            print('merge_pair:')
            print(merge_pair)
            print('RB_idx:')
            print(RB_idx)
            #print('t:',t,'f:',f)

        sumrate_single = 0
        sumrate_itf = 0
        sumrate_pair = 0
        

        #-- calculate best sumrate of single users
        for i in all_bs:
            if queue_single_i[i]:
                sumrate_single += rate[i][queue_single_i[i][-1]]
        #print(sumrate_single)

        #----- calculate best sumrate of interfering users
        max_sumrate_i = [0 for i in all_bs] 
        for i in all_bs:
            while queue_itf_i[i] and RB_needed[i][queue_itf_i[i][-1]] == 0:
                queue_itf_i[i].pop()
            if queue_itf_i[i]:
                max_sumrate_i[i] = rate[i][queue_itf_i[i][-1]]
        sumrate_itf = max(max_sumrate_i)
        #print(sumrate_itf)

        #----- case addtion's rate
        # TODO: maybe can init
        addition_pair = -1
        for u in queue_reduce:
            sumrate_increase = 0
            if muting_RB_idx_i[0][u] and not muting_RB_idx_i[1][match[0, u]] and RB_needed[1][match[0, u]]:
                sumrate_increase = rate[1][match[0, u]] - rate_reduce[u][match[0, u]]
            elif not muting_RB_idx_i[0][u] and muting_RB_idx_i[1][match[0, u]] and RB_needed[0][u]:
                sumrate_increase = rate[0][u] - rate_reduce[u][match[0, u]]
            if sumrate_increase > sumrate_pair:
                sumrate_pair = sumrate_increase
                addition_pair = u
        if addition_pair != -1:
            print('addition:')
            print(addition_pair)


        print('case merge:')
        print('merge pair:', merge_pair)
        #print('RB_idx:', RB_idx[1])
        print('sumrate_single:', sumrate_single)
        print('sumrate_itf:',sumrate_itf)

        print('-----------------------------------------')

        print('case addition')
        print('addition:', addition_pair)
        #print('RB:', t * num_subcarriers + f )
        print('sumrate_pair:', sumrate_pair)

        #----- no more user to allocate
        if merge_pair == -1 and addition_pair == -1:
            break

        #----- case addition to allocate
        elif addition_pair != -1 and (merge_pair == -1 or sumrate_pair >= max(sumrate_itf, sumrate_single) - rate_reduce[merge_pair][ match[0, merge_pair] ]):
            print('Case addition')
            u = addition_pair
            if not muting_RB_idx_i[0][u]:
                t = muting_RB_idx_i[1][match[0, u]][-1] // num_subcarriers
                f = muting_RB_idx_i[1][match[0, u]][-1] % num_subcarriers 
                alloc_RB_i[0][t][f] = u
                RB_needed[0][u] -= 1
                muting_RB_idx_i[1][match[0, u]].pop()
                print('i: 0')
                print('u:', u) 
                print('RB:', t * num_subcarriers + f )
            elif not muting_RB_idx_i[1][match[0, u]]:
                t = muting_RB_idx_i[0][u][-1] // num_subcarriers
                f = muting_RB_idx_i[0][u][-1] % num_subcarriers 
                alloc_RB_i[1][t][f] = match[0, u]
                RB_needed[1][match[0, u]] -= 1
                muting_RB_idx_i[0][u].pop()
                print('i: 1')
                print('u:', match[0, u])
                print('RB:', t * num_subcarriers + f )

        #----- case merge to allocate
        elif merge_pair != -1:
            print('Case merge')
            #----- choose single user to allocate
            if sumrate_single >= sumrate_itf:
                for i in all_bs:
                    if queue_single_i[i]:
                        alloc_RB_i[i][t][f] = queue_single_i[i][-1]
                        RB_needed[i][queue_single_i[i][-1]] -= 1
                        if RB_needed[i][queue_single_i[i][-1]] == 0:
                            queue_single_i[i].pop()

            #----- choose interfering user to allocate
            else:
                i = max_sumrate_i.index(max(max_sumrate_i))
                alloc_RB_i[i][t][f] = queue_itf_i[i][-1]
                print('i:', i)
                print('u:', queue_itf_i[i][-1])
                RB_needed[i][queue_itf_i[i][-1]] -= 1
                muting_RB_idx_i[i][queue_itf_i[i][-1]].append(f + t * num_subcarriers)
                muting_RB_idx_i[i][queue_itf_i[i][-1]].sort()
                j = (i + 1) % 2
                alloc_RB_i[j][t][f] = 'x'
                if RB_needed[i][queue_itf_i[i][-1]] == 0:
                    queue_itf_i[i].pop()

            #-- merge the pairing user 
            t = RB_idx[0] // num_subcarriers
            f = RB_idx[0] % num_subcarriers 
            alloc_RB_i[1][t][f] = match[0, merge_pair]

    sumrate_i = [0 for i in all_bs]
    sumrate_RB_i = [[0 for r in range(num_subcarriers * num_time_slots)] for i in all_bs]
    sumrate_RB = [0 for r in range(num_subcarriers * num_time_slots)]
    for t in all_time_slots:
        for f in all_subcarriers:
            for i in all_bs:
                if alloc_RB_i[i][t][f] != 'x':
                    sumrate_RB_i[i][t * num_subcarriers + f] += rate[i][alloc_RB_i[i][t][f]] / 10000
                    #sumrate_i[i] += rate[i][alloc_RB_i[i][t][f]] / 10000
            if alloc_RB_i[0][t][f] != 'x' and alloc_RB_i[1][t][f] != 'x':
                sumrate_RB_i[0][t * num_subcarriers + f] -= rate_reduce_ij[alloc_RB_i[0][t][f]][alloc_RB_i[1][t][f]] / 10000
                sumrate_RB_i[1][t * num_subcarriers + f] -= rate_reduce_ji[alloc_RB_i[1][t][f]][alloc_RB_i[0][t][f]] / 10000

                #sumrate_i[0] -= rate_reduce_ij[alloc_RB_i[0][t][f]][alloc_RB_i[1][t][f]] / 10000
                #sumrate_i[1] -= rate_reduce_ji[alloc_RB_i[1][t][f]][alloc_RB_i[0][t][f]] / 10000

    ##-------- test if there is rate of pair user >= alloc 
    for r in range(num_subcarriers * num_time_slots):
        sumrate_RB[r] = sumrate_RB_i[0][r] + sumrate_RB_i[1][r]

    #----- sort pairing user by rate_pair 
    queue_pair = sorted(range(len(rate[i]) - num_itf_users, len(rate[i])), key=lambda u: rate_pair[u][match[0, u]], reverse = True)
    while True:
        print('sumrate_RB')
        print(sumrate_RB)
        for i in all_bs:
            print()
            for f in all_subcarriers:
                for t in all_time_slots:
                    print(alloc_RB_i[i][t][f],sep = '',end = '')
                print()
        u = -1
        for idx in range(len(queue_pair)):
            if RB_needed[0][queue_pair[idx]] and RB_needed[1][ match[0, queue_pair[idx]] ]:
                u = queue_pair[idx]
                break
        if u == -1:
            break
        sumrate_pair = rate_pair[u][match[0, u]] /10000
        sumrate_min = min(sumrate_RB)
        if sumrate_pair > sumrate_min:
            min_RB_idx = sumrate_RB.index(min(sumrate_RB))
            print('min_RB_idx:', min_RB_idx)
            print('u:', u)
            t = min_RB_idx // num_subcarriers
            f = min_RB_idx % num_subcarriers
            if alloc_RB_i[0][t][f] != 'x':
                RB_needed[0][alloc_RB_i[0][t][f]] += 1
            if alloc_RB_i[1][t][f] != 'x':
                RB_needed[1][alloc_RB_i[1][t][f]] += 1
            alloc_RB_i[0][t][f] = u
            alloc_RB_i[1][t][f] = match[0, u]
            RB_needed[0][u] -= 1
            RB_needed[1][match[0, u]] -= 1
            sumrate_RB_i[0][min_RB_idx] = (rate[0][u] - rate_reduce_ij[u][match[0, u]]) / 10000
            sumrate_RB_i[1][min_RB_idx] = (rate[1][match[0, u]] - rate_reduce_ji[match[0, u]][u]) / 10000
            sumrate_RB[min_RB_idx] = sumrate_RB_i[0][min_RB_idx] + sumrate_RB_i[1][min_RB_idx]
        else:
            break
    #print(rate_pair)
    #print(queue_pair)

    for i in all_bs:       
        sumrate_i[i] = sum(sumrate_RB_i[i])

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

    return alloc_RB_i, sumrate_i, RB_used_i
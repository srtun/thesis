from __future__ import print_function
from ortools.sat.python import cp_model
#from setting import _setting
import setting
import setting_SIC
import random
import xlrd
import math
import os

def _greedy_muting(RB_needed, rate):

    num_bs, num_subcarriers, num_time_slots, num_users, num_users_i = setting._setting()

    all_bs = range(num_bs)
    all_users = range(num_users)
    all_subcarriers = range(num_subcarriers)
    all_time_slots = range(num_time_slots)
    all_users_i = []
    for i in all_bs:
        all_users_i.append(range(num_users_i[i]))

    num_itf_users, itf_idx_i, rate_reduce_ij, rate_reduce_ji, SNR_reduce_ij, SNR_reduce_ji, rate_reduce, rate_pair = setting_SIC._setting_SIC()

    ##---- algo start -------------------------------------
    queue_single_i = []
    queue_itf_i = []
    print(rate)
    #-- sorting single users by rate
    for i in all_bs:
        queue_single_i.append(sorted(range(len(rate[i]) - num_itf_users), key=lambda u: rate[i][u]))
    print(queue_single_i)

    #-- sorting interfering users by rate
    for i in all_bs:
        queue_itf_i.append(sorted(range(len(rate[i]) - num_itf_users, len(rate[i])), key=lambda u: rate[i][u]))
    print(queue_itf_i)

    alloc_RB_i = []
    for i in all_bs:
        alloc_RB_i.append([])

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
                if RB_needed[i][queue_itf_i[i][-1]] == 0:
                    queue_itf_i[i].pop()
            f -= 1

    #print(alloc_RB_i[0])
    #print(alloc_RB_i[1])
    #print()
    RB_used_i = [[0 for u in all_users_i[i]] for i in all_bs]
    sumrate_i = [0 for i in all_bs]
    for i in all_bs:
        for t in all_time_slots:
            for f in all_subcarriers:
                if alloc_RB_i[i][t][f] != 'x':
                    RB_used_i[i][ alloc_RB_i[i][t][f] ] += 1 
                    sumrate_i[i] += rate[i][alloc_RB_i[i][t][f]] / 10000
    #transpose alloc_RB_i[i][t][f] into alloc_RB_i[i][f][t]
    for i in all_bs:
        alloc_RB_i[i] = list(map(list, zip(*alloc_RB_i[i])))


    return alloc_RB_i, sumrate_i, RB_used_i

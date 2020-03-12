from __future__ import print_function
import matplotlib.pyplot as plt
#from setting import _setting
import setting
import setting_SIC
import xlrd
import math
import os

def _print_RB(alloc_RB_i, RB_needed, rate, rate_reduce_ij, rate_reduce_ji, sumrate_i, algo_name):

    num_bs, num_subcarriers, num_time_slots, num_users, num_users_i = setting._setting()
    all_bs = range(num_bs)
    all_users = range(num_users)
    all_subcarriers = range(num_subcarriers)
    all_time_slots = range(num_time_slots)
    all_users_i = []
    for i in all_bs:
        all_users_i.append(range(num_users_i[i]))

    num_itf_users, itf_idx_i, rate_reduce_ij, rate_reduce_ji, SNR_reduce_ij, SNR_reduce_ji, rate_reduce, rate_pair = setting_SIC._setting_SIC()

    muting_RB_i = []
    unallocated_RB = 0
    RB_waste_i = [0 for i in all_bs]
    RB_used_i = [[0 for u in all_users_i[i]] for i in all_bs]
    for i in all_bs:
        muting_RB_i.append(0)
        print()
        print ('BS', i)
        print ('Total RB:',  num_subcarriers * num_time_slots)
        #print('sumrate:', sumrate_i[i])
        print()
        for f in all_subcarriers:
            for t in all_time_slots:
                j = (i + 1) % 2
                if alloc_RB_i[i][f][t] == 'x':
                    RB_waste_i[i] += 1
                else:
                    RB_used_i[i][alloc_RB_i[i][f][t]] += 1
                # count for unallocate RB
                if alloc_RB_i[i][f][t] == 'x' and alloc_RB_i[j][f][t] == 'x':
                    unallocated_RB += 1
                # count for muting RB
                if alloc_RB_i[i][f][t] == 'x' and alloc_RB_i[j][f][t] != 'x':
                    for u in itf_idx_i[j]:
                        if alloc_RB_i[j][f][t] == u:
                            muting_RB_i[i] += 1
                            alloc_RB_i[i][f][t] = 'm'
                            break
                print(alloc_RB_i[i][f][t],' ' , sep = '',end = '')
            print()
        print()
        unallocated_RB /= num_bs # r_{f,t} in different bs only count for 1 unallocated RB
        #print('RB wastes:', RB_waste_i[i])
        #print('muting RB:', muting_RB_i[i])
        print()
        for u in all_users_i[i]:
            if u in itf_idx_i[i]: #itf user
                break
            print('user', u, 'uses', RB_used_i[i][u], 'RB with rate', rate[i][u] / 10000, ',(', RB_used_i[i][u], '/', RB_needed[i][u], ')RB')
        j = (i + 1) % 2
        for u in itf_idx_i[i]:      #itf user
            print('user', u, 'uses', RB_used_i[i][u],  'RB ,(', RB_used_i[i][u], '/', RB_needed[i][u], ')RB')
            RB_SIC = 0
            pair_user_RB = [0 for v in all_users_i[j]] 
            for f in all_subcarriers:
                for t in all_time_slots:
                    if alloc_RB_i[i][f][t] == 'x' or alloc_RB_i[i][f][t] == 'm' or alloc_RB_i[i][f][t] != u:
                        continue
                    if alloc_RB_i[j][f][t] == 'x' or alloc_RB_i[j][f][t] == 'm':
                        continue
                    else:
                        v = alloc_RB_i[j][f][t]
                        pair_user_RB[v] += 1
            #print(pair_user_RB)
            for v in all_users_i[j]:
                if pair_user_RB[v] == 0:
                    continue
                if i == 0:
                    print(pair_user_RB[v], 'RB with rate', (rate[i][u] - rate_reduce_ij[u][v]) / 10000, ',(', pair_user_RB[v], '/', RB_used_i[i][u], ')RB (pair with user', v, ')')
                    #sumrate_i[i] -= rate_reduce_ij[u][v] * pair_user_RB[v] / 10000
                else:
                    print(pair_user_RB[v], 'RB with rate', (rate[i][u] - rate_reduce_ji[u][v]) / 10000, ',(', pair_user_RB[v], '/', RB_used_i[i][u], ')RB (pair with user', v, ')')
                    #sumrate_i[i] -= rate_reduce_ji[u][v] * pair_user_RB[v] / 10000
                #print(pair_user_RB[v], 'RB with rate', (rate[i][u] - rate_reduce[u][v] / 2) / 10000, ',(', pair_user_RB[v], '/', RB_used_i[i][u], ')RB (pair with user', v, ')')
                #sumrate_i[i] -= rate_reduce[u][v] / 2 * pair_user_RB[v] / 10000
            muting_RB = RB_used_i[i][u] - sum(pair_user_RB)
            if muting_RB != 0:
                print(muting_RB, 'RB with rate', (rate[i][u])/ 10000, ',(', muting_RB, '/', RB_used_i[i][u], ')RB (muting)')
            print()
        print('BS', i, 'sumrate:', round(sumrate_i[i], 4))
        
    print('sumrate', algo_name, '=', round(sum(sumrate_i), 4) )
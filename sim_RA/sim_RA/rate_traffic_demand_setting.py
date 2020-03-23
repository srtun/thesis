from __future__ import print_function
import matplotlib.pyplot as plt
from ortools.sat.python import cp_model
from setting import _setting
import random
import xlrd
import math
import os

# [ ] TODO: append RB_needed?

def _rate_traffic_demand_setting():
    # read mcs table file
    book = xlrd.open_workbook('CQI_index.xlsx')
    mcs_table = book.sheets()[0]
    
    num_bs, num_subcarriers, num_time_slots, num_users, num_users_i = _setting()
    #print(num_bs)
    
    all_bs = range(num_bs)
    all_users = range(num_users)
    all_subcarriers = range(num_subcarriers)
    all_time_slots = range(num_time_slots)
    all_users_i = []
    for i in all_bs:
        all_users_i.append(range(num_users_i[i]))

    traffic_demands = []
    for i in all_bs:
        traffic_demands.append([]) 
        for u in all_users_i[i]:
            traffic_demands[i].append(random.randint(500, 1000) * 10 // 4) 
    print('td:')
    print(traffic_demands)
    SNR = []  
    for i in all_bs:
        SNR.append([]) 
        for u in all_users_i[i]:
            SNR[i].append(random.randint(11, 90))
    #print(SNR)

    SNR_db = []
    for i in all_bs:
        SNR_db.append([]) 
        for u in all_users_i[i]:
            SNR_db[i].append(10 *  math.log(SNR[i][u], 10))

    rate = []
    for i in all_bs:
        rate.append([]) 
        for u in all_users_i[i]:
            r = round(math.log(1 + SNR[i][u],2), 4) * 10000
            rate[i].append(int(r))
    
    for i in all_bs:
        for u in all_users_i[i]:
            #rate[i][u] = random.randint(3, 6) * 10000
            rate[i][u] = 50000
            pass

    rate[0][2] = 30000
    rate[1][2] = 30000
    rate[0][3] = 50000
    rate[1][3] = 50000
    rate[0][4] = 50000
    rate[1][4] = 50000
    print('rate:')
    print(rate)
    print()
    rate_reduce_ij = []
    for u in all_users_i[0]:
        rate_reduce_ij.append([])
        for v in all_users_i[1]:
            reduce = 0
            if u in itf_idx_i[0] and v in itf_idx_i[1]:
                reduce = random.randint(5000 , 7500)
                reduce = 10000

            rate_reduce_ij[u].append(reduce)
    print('reduction_ij:')
    print(rate_reduce_ij)
    print()
    
    rate_reduce_ji = []
    for v in all_users_i[1]:
        rate_reduce_ji.append([])
        for u in all_users_i[0]:
            reduce = 0
            if u in itf_idx_i[0] and v in itf_idx_i[1]:
                reduce = random.randint(5000 , 7500)
                reduce = 10000

            rate_reduce_ji[v].append(reduce)
    print('reduction_ji:')
    print(rate_reduce_ji)
    print()

    print('SNR')
    print(SNR)
    print()

    SNR_reduce_ij = []
    for u in all_users_i[0]:
        SNR_reduce_ij.append([])
        for v in all_users_i[1]:
            #reduce = random.randint(5000 , 7500) / 1000
            multiple =  math.pow(2, rate_reduce_ij[u][v] / 10000)
            SNR_reduction = round(SNR[0][u] - ( (SNR[0][u] + 1) / multiple - 1), 4)
            SNR_reduce_ij[u].append(SNR_reduction)
    print('SNR_reduction_ij:')
    print(SNR_reduce_ij)
    print()
    
    SNR_reduce_ji = []
    for v in all_users_i[1]:
        SNR_reduce_ji.append([])
        for u in all_users_i[0]:
            multiple =  math.pow(2, rate_reduce_ji[v][u] / 10000)
            SNR_reduction = round(SNR[1][v] -( (SNR[1][v] + 1) / multiple - 1), 4)
            SNR_reduce_ji[v].append(SNR_reduction)
    print('SNR_reduction_ji:')
    print(SNR_reduce_ji)
    print()

    rate_reduce = []
    for u in all_users_i[0]:
        rate_reduce.append([])
        for v in all_users_i[1]:
            #reduce = 0
            #if u in itf_idx_i[0] and v in itf_idx_i[1]:
                #reduce = random.randint(5000 * 2 , 7500 * 2)
                #reduce = 20000
                #if u == v :
                    #reduce = random.randint(5000 * 2 , 7500 * 2)
            reduce = rate_reduce_ij[u][v] + rate_reduce_ji[v][u]
            rate_reduce[u].append(reduce)

    rate_pair = []
    for u in all_users_i[0]:
        rate_pair.append([])
        for v in all_users_i[1]:
            rate_pair[u].append(rate[0][u] + rate[1][v] - rate_reduce[u][v])
    
    print('rate_pair: ')
    print(rate_pair)
    print()


    return traffic_demands, SNR, SNR_db, rate, rate_reduce_ij, rate_reduce_ji, SNR_reduce_ij, SNR_reduce_ji, rate_reduce, rate_pair
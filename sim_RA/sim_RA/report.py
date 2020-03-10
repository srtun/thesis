from __future__ import print_function
from copy import deepcopy
import matplotlib.pyplot as plt
import numpy as np
from ortools.sat.python import cp_model
from setting import _setting
from rate_traffic_demand_setting import _rate_traffic_demand_setting
#from rtd_setting2 import _rtd_setting2
import rtd_setting2
import setting_SIC
from exhausted_search import _exhausted_search
from greedy_freq import _greedy_freq
from greedy_pilot import _greedy_pilot
from print_RB import _print_RB
from test import _test
import random
import xlrd
import math
import os
##[ ] TODO : traffic demands bug

def _report():

    # read mcs table file
    book = xlrd.open_workbook('CQI_index.xlsx')
    mcs_table = book.sheets()[0]
    #print (mcs_table.nrows)
    #print (mcs_table.ncols)
    #print (mcs_table.row_values(2))
    #print (mcs_table.cell(0,2).value)

    num_bs, num_subcarriers, num_time_slots, num_users, num_users_i = _setting()
    #print(num_bs)

    all_bs = range(num_bs)
    all_users = range(num_users)
    all_subcarriers = range(num_subcarriers)
    all_time_slots = range(num_time_slots)
    all_users_i = []
    for i in all_bs:
        all_users_i.append(range(num_users_i[i]))
    #rtd_setting2.init()
    traffic_demands, SNR, SNR_db, rate = rtd_setting2._rtd_setting2()
    num_itf_users, itf_idx_i, rate_reduce_ij, rate_reduce_ji, SNR_reduce_ij, SNR_reduce_ji, rate_reduce, rate_pair = setting_SIC._setting_SIC()

    # pairing matrix
    Z = [[1 for col in all_users_i[1]] for row in all_users_i[0]]
    #print (Z)
    for i in all_users_i[0]:
        #Z.append([])
        for j in all_users_i[1]:
            if i in itf_idx_i[0] or j in itf_idx_i[1]:
                Z[i][j] = 0
    
    Z_single = deepcopy(Z)

    for i in itf_idx_i[0]:
        for j in itf_idx_i[1]:
            if i == j:
                Z[i][j] = 1
    #print('Z:')
    #print(Z)

    #print('Z_single:')
    #print(Z_single)
    # record the matching pair user
    match = {}
    for i in all_users_i[0]:
        #Z.append([])
        for j in all_users_i[1]:
            if Z[i][j] == 1 and i in itf_idx_i[0] and j in itf_idx_i[1]:
                match[0, i] = j
                match[1, j] = i
    #print('match:')
    #print(match)
    # TODO: rb_needed may be sufficient(cause program stopping)
    
    RB_needed = []
    for i in all_bs:
        RB_needed.append([]) 
        for u in all_users_i[i]:
            reduce = 0
            if u in itf_idx_i[i]:
                v = match[i, u]
                if i == 0:
                    reduce =SNR_reduce_ij[u][v]
                else:
                    reduce =SNR_reduce_ji[u][v]
            snr = SNR[i][u] - reduce
            snr_db = 10 *  math.log(snr, 10)
            for idx in range(1, mcs_table.nrows):
                if snr_db < mcs_table.cell(idx, 4).value:
                    rb = traffic_demands[i][u] / (mcs_table.cell(idx - 1, 3).value * 84)
                    RB_needed[i].append(math.ceil(rb))
                    break
    #print('RB_needed: ')
    #print(RB_needed)       
    for i in all_bs:
        for u in all_users_i[i]:
            #RB_needed[i][u] = random.randint(3, 7)
            #RB_needed[i][u] = 4
            pass
    #RB_needed[0][3] = 5
    #RB_needed[1][3] = 5
    #RB_needed[0][4] = 5
    #RB_needed[1][4] = 5
    #print('RB_needed: ')
    #print(RB_needed)   
    

    ## exhausted search (opt)
    time_threshold = 1.0
    alloc_RB_i, RB_waste_i, RB_used_i, sumrate_i, sumrate_bit_i, objective_value, wall_time = _exhausted_search(Z, RB_needed, rate, rate_pair, rate_reduce_ij, rate_reduce_ji, traffic_demands, time_threshold)
    if round(sum(sumrate_i),4) != objective_value / 10000:
        print('objective function wrong!!')
    #print('exhausted')
    #print(alloc_RB_i)
    
    #_print_RB(alloc_RB_i, RB_needed, rate, rate_reduce_ij, rate_reduce_ji, sumrate_i, 'opt')
    
    ## exhausted search (singleton)
    single_alloc_RB_i, single_RB_waste_i, single_RB_used_i, single_sumrate_i, single_sumrate_bit_i, single_objective_value, single_wall_time = _exhausted_search(Z_single, RB_needed, rate, rate_pair, rate_reduce_ij, rate_reduce_ji, traffic_demands, time_threshold)
    #print('exhausted')
    #print(alloc_RB_i)
    
    ## exhausted search (pairing)
    pairing_traffic_demands = deepcopy(traffic_demands)
    pairing_rate = deepcopy(rate)
    pairing_RB_needed = deepcopy(RB_needed)
    for u in itf_idx_i[0]:
        v = match[0, u]
        pairing_rate[0][u] = rate_pair[u][v]
        pairing_RB_needed[0][u] = min(RB_needed[0][u], RB_needed[1][v])
        pairing_traffic_demands[0][u] += traffic_demands[1][v]
        pairing_rate[1][v] = 0
        pairing_RB_needed[1][v] = 0
        pairing_traffic_demands[1][v] = 0
    #print('pairing_rate')
    #print(pairing_rate)
    pairing_alloc_RB_i, pairing_RB_waste_i, pairing_RB_used_i, pairing_sumrate_i, pairing_sumrate_bit_i, pairing_objective_value, pairing_wall_time = _exhausted_search(Z_single, pairing_RB_needed, pairing_rate, rate_pair, rate_reduce_ij, rate_reduce_ji, pairing_traffic_demands, time_threshold)
    #print('exhausted')
    #print(alloc_RB_i)
    

    #_print_RB(single_alloc_RB_i, RB_needed, rate, rate_reduce_ij, rate_reduce_ji, single_sumrate_i, 'singleton')
    value = [round(sum(sumrate_i, 2)) / num_time_slots , 
             round(sum(single_sumrate_i, 2)) / num_time_slots, 
             round(sum(pairing_sumrate_i, 2)) / num_time_slots]
    bit = [sum(sumrate_bit_i), sum(single_sumrate_bit_i), sum(pairing_sumrate_bit_i)]
    ## plot
    '''
    algo = ['opt', 'singleton']
    value = [round(sum(sumrate_i, 2)), round(sum(single_sumrate_i, 2))]
    plt.scatter(algo, value)
    plt.ylim(0, max(value) + 5)
    plt.show()
    print()
    '''
    return value, bit

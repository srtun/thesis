from __future__ import print_function
from copy import deepcopy
import matplotlib.pyplot as plt
import numpy as np
from ortools.sat.python import cp_model
#from setting import _setting
import setting
import rtd_setting2
import setting_SIC
from rate_traffic_demand_setting import _rate_traffic_demand_setting
from exhausted_search import _exhausted_search
from greedy_freq import _greedy_freq
from greedy_pilot import _greedy_pilot
from print_RB import _print_RB
#from test import _test
import test
from report import _report
import random
import xlrd
import math
import os

def main(): 
    # [x] TODO: ob function bug
    # [x] TODO: rb_needed bug // fix: rb_needed are decided by pair SNR
    # [ ] TODO: num_itf_users may be different

    # [ ] TODO: minimum pilot
    # [ ] TODO: different freq, different rate
    # [ ] TODO: real sim deployment
    
    #_test()

    # read mcs table file
    book = xlrd.open_workbook('CQI_index.xlsx')
    mcs_table = book.sheets()[0]
    #print (mcs_table.nrows)
    #print (mcs_table.ncols)
    #print (mcs_table.row_values(2))
    #print (mcs_table.cell(0,2).value)

    num_bs, num_subcarriers, num_time_slots, num_users, num_users_i = setting._setting()
    #print(num_bs)
    
    all_bs = range(num_bs)
    all_users = range(num_users)
    all_subcarriers = range(num_subcarriers)
    all_time_slots = range(num_time_slots)
    all_users_i = []
    for i in all_bs:
        all_users_i.append(range(num_users_i[i]))
    
    traffic_demands, SNR, SNR_db, rate, rate_reduce_ij, rate_reduce_ji, SNR_reduce_ij, SNR_reduce_ji, rate_reduce, rate_pair = _rate_traffic_demand_setting()


    # pairing matrix
    Z = [[1 for col in all_users_i[1]] for row in all_users_i[0]]
    #print (Z)
    for i in all_users_i[0]:
        #Z.append([])
        for j in all_users_i[1]:
            if i in itf_idx_i[0] or j in itf_idx_i[1]:
                Z[i][j] = 0

    for i in itf_idx_i[0]:
        for j in itf_idx_i[1]:
            if i == j:
                Z[i][j] = 1
    print('Z:')
    print(Z)

    # record the matching pair user
    # TODO: itf_idx_i
    match = {}
    for i in all_users_i[0]:
        #Z.append([])
        for j in all_users_i[1]:
            if Z[i][j] == 1 and i in itf_idx_i[0] and j in itf_idx_i[1]:
                match[0, i] = j
                match[1, j] = i
    print('match:')
    print(match)

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
    print('RB_needed: ')
    print(RB_needed)   
    

    ## exhausted search
    time_threshold = 30.0
    alloc_RB_i, RB_waste_i, RB_used_i, sumrate_i, objective_value, wall_time = _exhausted_search(Z, RB_needed, rate, rate_pair, rate_reduce_ij, rate_reduce_ji, traffic_demands, time_threshold)
    if round(sum(sumrate_i),4) != objective_value / 10000:
        print('objective function wrong!!')
    #print('exhausted')
    #print(alloc_RB_i)
    
    _print_RB(alloc_RB_i, RB_needed, rate, rate_reduce_ij, rate_reduce_ji, sumrate_i, 'exhausted search')
    
    ## greedy algorithm (pilot)
    RB_needed_cp = deepcopy(RB_needed)
    pilot = 2
    greedy_alloc_RB_i, greedy_sumrate_i, greedy_RB_used_i = _greedy_pilot(match, RB_needed_cp, rate, rate_pair, rate_reduce_ij, rate_reduce_ji, pilot)
    _print_RB(greedy_alloc_RB_i, RB_needed, rate, rate_reduce_ij, rate_reduce_ji, greedy_sumrate_i, 'greedy_pilot')

    #print('greedy:')
    #print(greedy_alloc_RB_i)


    ## greedy algorithm (freq)
    RB_needed_cp = deepcopy(RB_needed)
    greedy_f_alloc_RB_i, greedy_f_sumrate_i, greedy_f_RB_used_i = _greedy_freq(match, RB_needed_cp, rate, rate_pair, rate_reduce_ij, rate_reduce_ji)
    _print_RB(greedy_f_alloc_RB_i, RB_needed, rate, rate_reduce_ij, rate_reduce_ji, greedy_f_sumrate_i, 'greedy_freq')

    ## Comparison between different RA algorithm
    print()
    print('Comparison')
    for i in all_bs:
        print()
        print('BS', i, 'sumrate')
        #print('Exhausted search:', round(sumrate_i[i], 4))
        print('Greedy_pilot:', round(greedy_sumrate_i[i], 4))
        print('Greedy_freq:', round(greedy_f_sumrate_i[i], 4))

    print()
    print('total sumrate')
    #print('Exhausted search:', round(sum(sumrate_i), 4))
    print('Greedy_pilot:', round(sum(greedy_sumrate_i), 4))
    print('Greedy_freq:', round(sum(greedy_f_sumrate_i), 4))
    print()
    #print('Wall time:', round(wall_time))
    #os.system('pause')

    ## plot
    '''
    algo = ['exhausted', 'greedy_pilot', 'greedy_freq']
    value = [round(sum(sumrate_i, 2)), round(sum(greedy_sumrate_i, 2)), round(sum(greedy_f_sumrate_i, 2))]
    plt.scatter(algo, value)
    plt.ylim(0, max(value) + 5)
    plt.show()
    print()
    '''

if __name__ == '__main__':
    #setting.init()
    #main()
    sumrate = [0 for i in range(5)] 
    single_sumrate = [0 for i in range(5)] 
    pairing_sumrate = [0 for i in range(5)] 
    sumrate_bit = [0 for i in range(5)] 
    single_sumrate_bit = [0 for i in range(5)] 
    pairing_sumrate_bit = [0 for i in range(5)] 
    
    sim_times = 20
    itf_percent = 0
    t = 0 

    while t < sim_times:
        t += 1
        print(t)
        itf_percent = 0
        rtd_setting2.init()
        while itf_percent < 5:
            itf_percent += 1
            print('itf_percent:', itf_percent * 20)
            setting_SIC.set_itf_users(itf_percent)
            value, bit = _report()
            sumrate[itf_percent - 1] += value[0]
            single_sumrate[itf_percent - 1] += value[1]
            pairing_sumrate[itf_percent - 1] += value[2]
            sumrate_bit[itf_percent - 1] += bit[0]
            single_sumrate_bit[itf_percent - 1] += bit[1]
            pairing_sumrate_bit[itf_percent - 1] += bit[2]
        os.system('cls')
    
    for i in range(len(sumrate)):
        sumrate[i] /= sim_times
        single_sumrate[i] /= sim_times
        pairing_sumrate[i] /= sim_times
        sumrate[i] *= 0.18 
        single_sumrate[i] *= 0.18 
        pairing_sumrate[i] *= 0.18 
        sumrate_bit[i] /= sim_times * 1000 * 1.5
        single_sumrate_bit[i] /= sim_times * 1000 * 1.5
        pairing_sumrate_bit[i] /= sim_times * 1000 * 1.5
    

    algo = ['opt', 'singleton', 'pairing']
    #value = [round(sum(sumrate_i, 2)), round(sum(single_sumrate_i, 2))]
    x = ['20','40','60','80','100']
    plt.plot(x, sumrate, label = 'opt', color = 'blue', marker = '^')
    plt.plot(x, single_sumrate, label = 'singleton', color = 'red', marker = 'o')
    plt.plot(x, pairing_sumrate, label = 'pairing', color = 'green', marker = 's')
    plt.ylabel('sumrate (Mbps)', fontsize = 20)
    plt.xlabel('percentage of interfering UEs(%)', fontsize = 20)
    plt.ylim(ymin = 0)
    plt.xticks(fontsize = 20)
    plt.yticks(fontsize = 20)
    #plt.scatter(algo, sumrate)
    #plt.ylim(0, max(sumrate) + 2)
    plt.legend(fontsize = 20 )
    plt.show()

    '''
    algo = ['opt', 'singleton', 'pairing']
    #value = [round(sum(sumrate_i, 2)), round(sum(single_sumrate_i, 2))]
    x = ['20','40','60','80','100']
    plt.plot(x, sumrate_bit, label = 'opt', color = 'blue', marker = '^')
    plt.plot(x, single_sumrate_bit, label = 'singleton', color = 'red', marker = 'o')
    plt.plot(x, pairing_sumrate_bit, label = 'pairing', color = 'green', marker = 's')
    plt.ylabel('sumrate (Mbps)', fontsize = 20)
    plt.xlabel('percentage of interfering UEs(%)', fontsize = 20)
    plt.ylim(ymin = 0)
    plt.xticks(fontsize = 20)
    plt.yticks(fontsize = 20)
    #plt.scatter(algo, sumrate)
    #plt.ylim(0, max(sumrate) + 2)
    plt.legend(fontsize = 20 )
    plt.show()
    '''
    print()
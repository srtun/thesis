from __future__ import print_function
from copy import deepcopy
import matplotlib.pyplot as plt
from ortools.sat.python import cp_model
from setting import _setting
from exhausted_search import _exhausted_search
from greedy_freq import _greedy_freq
from greedy_pilot import _greedy_pilot
from print_RB import _print_RB
from test import _test
import random
import xlrd
import math
import os

def main(): 
    # [ ] TODO: independent funtion of random parameter 
    # [x] TODO: ob function bug
    # [x] TODO: rb_needed bug // fix: rb_needed are decided by pair SNR
    # [ ] TODO: num_itf_users may be different

    # [ ] TODO: minimum pilot
    # [ ] TODO: different freq, different rate
    # [ ] TODO: real sim deployment
    # [ ] TODO: generalize??
    
    
    _test()

    # read mcs table file
    book = xlrd.open_workbook('CQI_index.xlsx')
    mcs_table = book.sheets()[0]
    #print (mcs_table.nrows)
    #print (mcs_table.ncols)
    #print (mcs_table.row_values(2))
    #print (mcs_table.cell(0,2).value)

    num_bs, num_subcarriers, num_time_slots, num_users, num_users_i, num_itf_users, itf_idx_i = _setting()
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
            traffic_demands[i].append(random.randint(500, 1000) * 10 // 8) 

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
            #rate[i][u] = 50000
            pass
    #rate[0][3] = 50000
    #rate[1][3] = 50000
    #rate[0][4] = 50000
    #rate[1][4] = 50000
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
                #reduce = 10000

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
                #reduce = 10000

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

    '''
    RB_needed_old = []
    for i in all_bs:
        RB_needed_old.append([]) 
        for u in all_users_i[i]:
            for idx in range(1, mcs_table.nrows):
                if SNR_db[i][u] < mcs_table.cell(idx, 4).value:
                    rb = traffic_demands[i][u] / (mcs_table.cell(idx - 1, 3).value * 84)
                    RB_needed_old[i].append(math.ceil(rb))
                    break
    print('RB_needed_old: ')
    print(RB_needed_old)      
    '''
    
    time_threshold = 10.0
    alloc_RB_i, RB_waste_i, RB_used_i, sumrate_i, objective_value, wall_time = _exhausted_search(Z, RB_needed, rate, rate_pair, rate_reduce_ij, rate_reduce_ji, time_threshold)
    if round(sum(sumrate_i),4) != objective_value / 10000:
        print('objective function wrong!!')
    #print('exhausted')
    #print(alloc_RB_i)
    
    _print_RB(alloc_RB_i, RB_needed, rate, rate_reduce_ij, rate_reduce_ji, sumrate_i, 'exhausted search')

    # Statistics.
    '''
    print()
    print('Statistics')
    print('  - sumrate = %f' % (objective_value / 10000), '(out of', num_bs * num_subcarriers * num_time_slots, 'RBs)')
    print('  - RB waste = %i' % (sum(RB_waste_i)))
    print('  - RB utilization = %f' % (100 - sum(RB_waste_i) / (num_bs * num_subcarriers * num_time_slots) * 100 ), '%')
    print('  - wall time       : %f s' % wall_time)
    print('unallocated RB:', unallocated_RB)
    #os.system('pause')
    '''
    
    # greedy
    RB_needed_cp = deepcopy(RB_needed)
    greedy_alloc_RB_i, greedy_sumrate_i, greedy_RB_used_i = _greedy_pilot(match, RB_needed_cp, rate, rate_pair, rate_reduce_ij, rate_reduce_ji)
    _print_RB(greedy_alloc_RB_i, RB_needed, rate, rate_reduce_ij, rate_reduce_ji, sumrate_i, 'greedy_pilot')

    #print('greedy:')
    #print(greedy_alloc_RB_i)
    
    print()
    print('Comparison')
    for i in all_bs:
        print()
        print('BS', i, 'sumrate')
        print('Exhausted search:', round(sumrate_i[i], 4))
        print('Greedy:', round(greedy_sumrate_i[i], 4))
    print()
    print('total sumrate')
    print('Exhausted search:', round(sum(sumrate_i), 4))
    print('Greedy:', round(sum(greedy_sumrate_i), 4))
    #os.system('pause')
if __name__ == '__main__':
    main()
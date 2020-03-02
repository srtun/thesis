from __future__ import print_function
import xlrd
import random
import math
import os


def _setting():
    book = xlrd.open_workbook('CQI_index.xlsx')
    mcs_table = book.sheets()[0]
    
    num_bs = 2;
    all_bs = range(num_bs)

    num_users = 10
    #num_users_i = num_users // 2
    #num_users_j = num_users - num_users_i
    num_users_i = []
    num_users_i.append(num_users // 2)
    #num_users_i.append(4)
    num_users_i.append(num_users - num_users_i[0])
    
    itf_idx_i = []
    #num_itf_users = num_users // 4
    num_itf_users = 2
    for i in all_bs:
        itf_idx_i.append([])
        for u in range(num_itf_users):
            itf_idx_i[i].append(num_users_i[i] - 1 - u)
        itf_idx_i[i].sort();

    #print(itf_idx_i)

    num_subcarriers = 6
    num_time_slots = 2
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
            pass
    #print('rate:')
    #print(rate)
    #print()

    rate_reduce_ij = []
    for u in all_users_i[0]:
        rate_reduce_ij.append([])
        for v in all_users_i[1]:
            reduce = 0
            if u in itf_idx_i[0] and v in itf_idx_i[1]:
                reduce = random.randint(5000 , 7500)
                #reduce = 5000

            rate_reduce_ij[u].append(reduce)
    #print('reduction_ij:')
    #print(rate_reduce_ij)
    #print()
    
    rate_reduce_ji = []
    for v in all_users_i[1]:
        rate_reduce_ji.append([])
        for u in all_users_i[0]:
            reduce = 0
            if u in itf_idx_i[0] and v in itf_idx_i[1]:
                reduce = random.randint(5000 , 7500)
                #reduce = 6000

            rate_reduce_ji[v].append(reduce)
    #print('reduction_ji:')
    #print(rate_reduce_ji)
    #print()

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
    
    #print('pair: ')
    #print(rate_pair)
    #print()

    # TODO: rb_needed may be sufficient(cause program stopping)
    RB_needed = []
    for i in all_bs:
        RB_needed.append([]) 
        for u in all_users_i[i]:
            for idx in range(1, mcs_table.nrows):
                if SNR_db[i][u] < mcs_table.cell(idx, 4).value:
                    rb = traffic_demands[i][u] / (mcs_table.cell(idx - 1, 3).value * 84)
                    RB_needed[i].append(math.ceil(rb))
                    break
    #print('RB_needed: ')
    #print(RB_needed)       
    for i in all_bs:
        for u in all_users_i[i]:
            #RB_needed[i][u] = random.randint(3, 7)
            pass
    #print('RB_needed: ')
    #print(RB_needed)   
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
    #print('Z:')
    #print(Z)

    return num_bs, num_subcarriers, num_time_slots, num_users, num_users_i, num_itf_users, itf_idx_i

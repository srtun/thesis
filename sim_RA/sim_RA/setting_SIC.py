from __future__ import print_function
import matplotlib.pyplot as plt
from ortools.sat.python import cp_model
from setting import _setting
import rtd_setting2
import random
import xlrd
import math
import os

def set_itf_users(num_itf):
    global num_itf_users
    num_itf_users = num_itf

def _setting_SIC():
    # read mcs table file
    book = xlrd.open_workbook('CQI_index.xlsx')
    mcs_table = book.sheets()[0]
    
    num_bs, num_subcarriers, num_time_slots, num_users, num_users_i = _setting()
    all_bs = range(num_bs)
    all_users = range(num_users)
    all_subcarriers = range(num_subcarriers)
    all_time_slots = range(num_time_slots)
    all_users_i = []

    for i in all_bs:
        all_users_i.append(range(num_users_i[i]))

    itf_idx_i = []
    for i in all_bs:
        itf_idx_i.append([])
        for u in range(num_itf_users):
            itf_idx_i[i].append(num_users_i[i] - 1 - u)
        itf_idx_i[i].sort()

    #print(itf_idx_i)
    traffic_demands, SNR, SNR_db, rate = rtd_setting2._rtd_setting2()

    rate_reduce_ij = []
    for u in all_users_i[0]:
        rate_reduce_ij.append([])
        for v in all_users_i[1]:
            reduce = 0
            if u in itf_idx_i[0] and v in itf_idx_i[1]:
                reduce = random.randint(5000 , 7500)
                reduce = 5000
                if u == v:
                    reduce = random.randint(4000, 5000)
                    reduce = 5000
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
                reduce = 5000
                if u == v:
                    reduce = random.randint(4000, 5000)
                    reduce = 5000
            rate_reduce_ji[v].append(reduce)
    #print('reduction_ji:')
    #print(rate_reduce_ji)
    #print()

    #print('SNR')
    #print(SNR)
    #print()

    SNR_reduce_ij = []
    for u in all_users_i[0]:
        SNR_reduce_ij.append([])
        for v in all_users_i[1]:
            #reduce = random.randint(5000 , 7500) / 1000
            multiple =  math.pow(2, rate_reduce_ij[u][v] / 10000)
            SNR_reduction = round(SNR[0][u] - ( (SNR[0][u] + 1) / multiple - 1), 4)
            SNR_reduce_ij[u].append(SNR_reduction)
    #print('SNR_reduction_ij:')
    #print(SNR_reduce_ij)
    #print()
    
    SNR_reduce_ji = []
    for v in all_users_i[1]:
        SNR_reduce_ji.append([])
        for u in all_users_i[0]:
            multiple =  math.pow(2, rate_reduce_ji[v][u] / 10000)
            SNR_reduction = round(SNR[1][v] -( (SNR[1][v] + 1) / multiple - 1), 4)
            SNR_reduce_ji[v].append(SNR_reduction)
    #print('SNR_reduction_ji:')
    #print(SNR_reduce_ji)
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
    
    #print('rate_pair: ')
    #print(rate_pair)
    #print()

    return num_itf_users, itf_idx_i, rate_reduce_ij, rate_reduce_ji, SNR_reduce_ij, SNR_reduce_ji, rate_reduce, rate_pair





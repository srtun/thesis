from __future__ import print_function
import matplotlib.pyplot as plt
from ortools.sat.python import cp_model
import numpy as np
from setting import _setting
import random
import xlrd
import math
import os

# [ ] 3/26 TODO: separate td and rate 
def set_traffic_demand(mean, lo):
    global traffic_demands
    
    book = xlrd.open_workbook('CQI_index.xlsx')
    mcs_table = book.sheets()[0]
    
    #num_bs, num_subcarriers, num_time_slots, num_users, num_users_i, num_itf_users, itf_idx_i = _setting()
    num_bs, num_subcarriers, num_time_slots, num_users, num_users_i = _setting()

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
            td = random.randint(300, 1500) * 10 // 12
            #mean = 1000 
            #std = 100
            sigma = (mean - lo) / 3
            td = np.random.normal(mean, sigma) 
            #td = 1100
            traffic_demands[i].append(td) 

def set_rate():
    global SNR, SNR_db, rate
    
    book = xlrd.open_workbook('CQI_index.xlsx')
    mcs_table = book.sheets()[0]
    
    #num_bs, num_subcarriers, num_time_slots, num_users, num_users_i, num_itf_users, itf_idx_i = _setting()
    num_bs, num_subcarriers, num_time_slots, num_users, num_users_i = _setting()

    all_bs = range(num_bs)
    all_users = range(num_users)
    all_subcarriers = range(num_subcarriers)
    all_time_slots = range(num_time_slots)
    all_users_i = []
    
    for i in all_bs:
        all_users_i.append(range(num_users_i[i]))


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
    '''
    rate[0][0] = 70000
    rate[1][0] = 40000
    rate[0][1] = 70000
    rate[1][1] = 60000
    rate[0][2] = 70000
    rate[1][2] = 50000
    rate[0][3] = 70000
    rate[1][3] = 30000
    rate[0][4] = 70000
    rate[1][4] = 30000
    '''
    #print('rate:')
    #print(rate)
    #print()


def _rtd_setting2():

    return traffic_demands, SNR, SNR_db, rate

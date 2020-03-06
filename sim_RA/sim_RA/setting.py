from __future__ import print_function
import xlrd
import random
import math
import os

def init():
    global num_itf
    num_itf = 2

def _setting():
    book = xlrd.open_workbook('CQI_index.xlsx')
    mcs_table = book.sheets()[0]
    
    num_bs = 2

    num_users = 10

    num_itf_users = num_itf
    #num_itf_users = num_users // 4

    num_subcarriers = 6
    num_time_slots = 3
    
    num_users_i = []
    num_users_i.append(num_users // 2)
    #num_users_i.append(4)
    num_users_i.append(num_users - num_users_i[0])
    
    itf_idx_i = []
    
    all_bs = range(num_bs)
    all_users = range(num_users)
    all_subcarriers = range(num_subcarriers)
    all_time_slots = range(num_time_slots)
    all_users_i = []
    for i in all_bs:
        all_users_i.append(range(num_users_i[i]))

    for i in all_bs:
        itf_idx_i.append([])
        for u in range(num_itf_users):
            itf_idx_i[i].append(num_users_i[i] - 1 - u)
        itf_idx_i[i].sort();

    #print(itf_idx_i)
    
    return num_bs, num_subcarriers, num_time_slots, num_users, num_users_i, num_itf_users, itf_idx_i

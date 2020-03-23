from __future__ import print_function
from ortools.sat.python import cp_model
from setting import _setting
import setting_SIC
import random
import xlrd
import math
import os

def _exhausted_search(Z, RB_needed, rate, rate_pair, rate_reduce_ij, rate_reduce_ji, traffic_demands, time_threshold, optimal):

    num_bs, num_subcarriers, num_time_slots, num_users, num_users_i = _setting()
    num_itf_users, itf_idx_i, rate_reduce_ij, rate_reduce_ji, SNR_reduce_ij, SNR_reduce_ji, rate_reduce, rate_pair = setting_SIC._setting_SIC()
    all_bs = range(num_bs)
    all_users = range(num_users)
    all_subcarriers = range(num_subcarriers)
    all_time_slots = range(num_time_slots)
    all_users_i = []
    for i in all_bs:
        all_users_i.append(range(num_users_i[i]))

    # Creates the model
    model = cp_model.CpModel()
    # Creates RB variables.
    # RB[(u
    # , t, f)]: user u is allocated RB_{f,t}
    RB = {}
    for i in all_bs:
        for u in all_users_i[i]:
            for t in all_time_slots:
                for f in all_subcarriers:
                    RB[(i, u, t, f)] = model.NewBoolVar('RB_i%iu%it%if%i' % (i, u, t, f))
    X = {}
    for u in all_users_i[0]:
        for v in all_users_i[1]:
            for t in all_time_slots:
                for f in all_subcarriers:
                    X[(u, v, t, f)] = model.NewBoolVar('X_u%iv%it%if%i' % (u, v, t, f))

    # constraints 1,2
    # allocated RB should not exceed the total RB
    for i in all_bs:
        model.Add(sum(RB[i, u, t, f] for u in all_users_i[i] for t in all_time_slots for f in all_subcarriers) <= num_subcarriers * num_time_slots)
                
    # constraints 3,4
    # Each RB_{f,t} is allocated to no more than one user u 
    for i in all_bs:
        for t in all_time_slots:
            for f in all_subcarriers:
                model.Add(sum(RB[(i, u, t, f)] for u in all_users_i[i]) <= 1)
            
     # constraints: allocated RB <= needed RB (traffic demand)
    for i in all_bs:
        for u in all_users_i[i]:
            model.Add(sum(RB[(i, u, t, f)] for t in all_time_slots for f in all_subcarriers) <= RB_needed[i][u])

    # constraints: for interference users I_{i,u,t,f} + I_{j,v,t,f} <= Z_{u, v} + 1
    for u in all_users_i[0]:
        for v in all_users_i[1]:
            for t in all_time_slots:
                for f in all_subcarriers:
                    model.Add(RB[(0, u, t, f)] + RB[(1, v, t, f)] <= Z[u][v] + 1)
    # old one
    # constraints: x_{u,v,f,t} <= I_{i,u,f,t} && x_{u,v,f,t} <= I_{j,v,f,t} (wrong)
    for u in all_users_i[0]:
        for v in all_users_i[1]:
            for t in all_time_slots:
                for f in all_subcarriers:
                    #model.Add(X[(u, v, t, f)] <= RB[0, u, t, f])
                    #model.Add(X[(u, v, t, f)] <= RB[1, v ,t ,f])
                    #model.AddBoolOr([RB[(0, u, t, f)].Not(), RB[(1, v, t, f)].Not(), X[(u, v, t, f)]])
                    pass
     
    # constraits: I_{i,u,f,t} + i_{j,v,f,t} <= X_{u,v,f,t} + 1
    for u in all_users_i[0]:
        for v in all_users_i[1]:
            for t in all_time_slots:
                for f in all_subcarriers:
                    model.Add(RB[(0, u, t, f)] + RB[(1, v, t, f)] <= X[(u, v, t, f)] + 1)
    
    # objective function
    #model.Maximize(sum(rate[i][u] * RB[(i, u, t, f)] - sum(RB[(1, v, t, f)] * rate_reduce[u][v] for v in all_users_i[1]) for i in all_bs for u in all_users_i[i] for t in all_time_slots for f in all_subcarriers))
    model.Maximize(
                    sum(
                     sum(rate[0][u] * RB[(0, u, t, f)] for u in all_users_i[0])
                   + sum(rate[1][v] * RB[(1, v, t, f)] for v in all_users_i[1])
                   #+ sum (X[(u ,v ,t, f)] * (rate_reduce[u][v])
                   + sum(X[(u ,v ,t, f)] * (rate_pair[u][v] - rate[0][u] - rate[1][v])
                    for u in all_users_i[0] for v in all_users_i[1])
                    for t in all_time_slots for f in all_subcarriers) 
                   )
    # Creates the solver and solve.
   
    solver = cp_model.CpSolver()
    #solver.Solve(model)
    if not optimal:
        solver.parameters.max_time_in_seconds = time_threshold

    
    status = solver.Solve(model)
    stat = ''
    if status == cp_model.OPTIMAL:
        #print('optimal')
        stat = 'optimal'
    if status == cp_model.FEASIBLE:
        #print('feasible')
        stat = 'feasible'
    if status == cp_model.INFEASIBLE:
        #print('infeasible')
        stat = 'infeasible'
    if status == cp_model.MODEL_INVALID:
        #print('model invalid')
        stat = 'model invalid'
    if status == cp_model.UNKNOWN:
        #print('unknown')
        stat = 'unknown'

    if 1:
    #if status == cp_model.FEASIBLE:
        alloc_RB_i = []
        RB_waste_i = []
        RB_used_i = []
        sumrate_i = []
        muting_RB_i = []
        sumrate_bit_i = []

        for i in all_bs:
            # print('BS', i)
            alloc_RB_i.append([])
            RB_waste_i.append(0)
            RB_used_i.append([0 for u in all_users_i[i]])
            sumrate = 0
            sumrate_bit = 0
            for f in all_subcarriers:
                #print('time slot', t)
                alloc_RB_i[i].append([])
                for t in all_time_slots:
                    for u in all_users_i[i]:
                        if solver.Value(RB[(i, u, t, f)]) == 1:
                            #print('User', u + i * num_users_i[0], 'is allocated RB',t, f, 'by rate ', rate[i][u] / 10000)
                            sumrate = sumrate + rate[i][u] / 10000
                            sumrate_bit = sumrate_bit + traffic_demands[i][u] / RB_needed[i][u]
                            alloc_RB_i[i][f].append(u)
                            RB_used_i[i][u] =  RB_used_i[i][u] + 1
                            break
                    if len(alloc_RB_i[i][f]) <= t:
                        alloc_RB_i[i][f].append('x')
                        RB_waste_i[i] = RB_waste_i[i] + 1
                #print()
            #print('BS', i,'sumrate :', round(sumrate, 4))
            #print()
            sumrate_i.append(round(sumrate, 4))
            sumrate_bit_i.append(sumrate_bit)
        for f in all_subcarriers:
            for t in all_time_slots:
                #j = (i + 1) % 2
                if alloc_RB_i[0][f][t] != 'x' and alloc_RB_i[1][f][t] != 'x':
                    sumrate_i[0] -= rate_reduce_ij[alloc_RB_i[0][f][t]][alloc_RB_i[1][f][t]] / 10000
                    sumrate_i[1] -= rate_reduce_ji[alloc_RB_i[1][f][t]][alloc_RB_i[0][f][t]] / 10000
        '''
        # find X 
        x_RB_i = []
        x_RB_j = []
        for f in all_subcarriers:
            x_RB_i.append([])
            x_RB_j.append([])
            for t in all_time_slots:
                for u in all_users_i[0]:
                    for v in all_users_i[1]:
                        if solver.Value(X[(u, v, t, f)]) == 1 :
                            #print()
                            x_RB_i[f].append(u)
                            x_RB_j[f].append(v)
                            break
                    if len(x_RB_i[f]) > t:
                        break
                if len(x_RB_i[f]) == t:
                    x_RB_i.append('x')
                    x_RB_j.append('x')

        for f in all_subcarriers:
            for t in all_time_slots: 
                print(x_RB_i[f][t],' ' , sep = '',end = '')
                #print()
            print()
        print()
        for f in all_subcarriers:
            for t in all_time_slots: 
                print(x_RB_j[f][t],' ' , sep = '',end = '')
                #print()
            print()

        for f in all_subcarriers:
            for t in all_time_slots:
                for u in all_users_i[0]:
                    for v in all_users_i[1]:
                        print(solver.Value(X[(u, v, t, f)]), ' ', sep = '', end = '')
                    print()
                print()
            print()
        '''
            
        '''
        print('Statistics')
        print('  - sumrate = %f' % (solver.ObjectiveValue() / 10000), '(out of', num_bs * num_subcarriers * num_time_slots, 'RBs)')
        print('  - RB waste = %i' % (sum(RB_waste_i)))
        print('  - RB utilization = %f' % (100 - sum(RB_waste_i) / (num_bs * num_subcarriers * num_time_slots) * 100 ), '%')
        print('  - wall time       : %f s' % solver.WallTime())
        #print('unallocated RB:', unallocated_RB)
        '''
        objective_value = solver.ObjectiveValue()
        wall_time = solver.WallTime()
    return alloc_RB_i, RB_waste_i, RB_used_i, sumrate_i, sumrate_bit_i, objective_value, wall_time, stat
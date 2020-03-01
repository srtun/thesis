from __future__ import print_function
from ortools.sat.python import cp_model
import random

def main():
    # This program tries to find an optimal assignment of nurses to shifts
    # (3 shifts per day, for 7 days), subject to some constraints (see below).
    # Each nurse can request to be assigned to specific shifts.
    # The optimal assignment maximizes the number of fulfilled shift requests.
    num_users = 5
    num_subcarriers = 3
    num_time_slots = 7
    all_users = range(num_users)
    all_subcarriers = range(num_subcarriers)
    all_time_slots = range(num_time_slots)

    traffic_demands = []
    for u in all_users:
        traffic_demands.append(random.randint(500, 1000))
    
    RB_needed = []
    for u in all_users:
        RB_needed.append(random.randint(1, 10))
    while sum(RB_needed) < num_subcarriers * num_time_slots:
        for u in all_users:
            RB_needed[u] = random.randint(1, 10)
    print(RB_needed)
    SNR = []
    for u in all_users:
        SNR.append(random.randint(2, 6))

    rate = []
    for u in all_users:
        rate.append(random.randint(2, 6))

    # Creates the model.
    model = cp_model.CpModel()

    # Creates RB variables.
    # RB[(u, t, f)]: user u is allocated RB_{f,t}
    RB = {}
    for u in all_users:
        for t in all_time_slots:
            for f in all_subcarriers:
                RB[(u, t, f)] = model.NewBoolVar('RB_n%id%is%i' % (u, t, f))

    # constraints 1,2
    # allocated RB should not exceed the total RB
    model.Add(sum(RB[u, t, f] for u in all_users for t in all_time_slots for f in all_subcarriers) <= num_subcarriers * num_time_slots)
                
    # constraints 3,4
    # Each RB_{f,t} is allocated to exactly one user u 
    for t in all_time_slots:
        for f in all_subcarriers:
            model.Add(sum(RB[(u, t, f)] for u in all_users) == 1)
            
     # constraints allocated RB <= needed RB
    for u in all_users:
         model.Add(sum(RB[(u, t, f)] for t in all_time_slots for f in all_subcarriers) <= RB_needed[u])

    # min_shifts_assigned is the largest integer such that every nurse can be
    # assigned at least that number of shifts.
    #min_RB_per_user = (num_subcarriers * num_time_slots) // num_users
    #max_RB_per_user = min_RB_per_user + 1
    #for u in all_users:
    #    num_RB_allocated = sum(RB[(u, t, f)] for t in all_time_slots for f in all_subcarriers)
    #    model.Add(min_RB_per_user <= num_RB_allocated)
    #    model.Add(num_RB_allocated <= max_RB_per_user)

    
    # srtun1217 : of sum(rate * RB) // RB: I
    # objective function
    model.Maximize(sum(rate[u] * RB[(u, t, f)] for u in all_users for t in all_time_slots for f in all_subcarriers))
    # Creates the solver and solve.
    solver = cp_model.CpSolver()
    solver.Solve(model)
    for t in all_time_slots:
        #print('time slot', t)
        for f in all_subcarriers:
            for u in all_users:
                if solver.Value(RB[(u, t, f)]) == 1:
                    print('User', u, 'is allocated RB',t, f, 'by rate ', rate[u])
        print()

    # Statistics.
    print()
    print('Statistics')
    print('  - sumrate = %i' % solver.ObjectiveValue(),
          '(out of', num_subcarriers * num_time_slots, 'RBs)')
    print('  - wall time       : %f s' % solver.WallTime())


if __name__ == '__main__':
    main()

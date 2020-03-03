from __future__ import print_function
from ortools.sat.python import cp_model
import random
import xlrd
import math
import os

def _test(): 
    l = [[1,2,3],[4,5,6],[7,8,9]]
    #map(list, zip(*l))
    r = list(map(list, zip(*l)))
    print(r)
    print()
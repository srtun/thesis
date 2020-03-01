from __future__ import print_function
from ortools.sat.python import cp_model
import random
import xlrd
import math
import os

def _test(): 
    s = [6, 3, 1, 4, 5]
    s2 = sorted(range(len(s)), key=lambda x: s[x])
    print(s2)
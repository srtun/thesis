from __future__ import print_function
from ortools.sat.python import cp_model
import matplotlib.pyplot as plt
import numpy as np
import random
import xlrd
import math
import os

def init():
    global tt
    tt = 2

def _test(): 
    tst = tt
    print(tst)
    y = [2,4,6,10,8]
    #value = [round(sum(sumrate_i, 2)), round(sum(single_sumrate_i, 2))]
    x = [i + 1 for i in range(5)]
    plt.plot(x, y)
    #plt.scatter(algo, sumrate)
    #plt.ylim(0, max(sumrate) + 2)
    plt.show()
    
    
    
    names = ['es', 'gp', 'gf']
    index = [i for i in range(3)]
    values = [10, 20, 30]
    #plt.plot([1, 2, 3])
    plt.scatter(names, values)
    plt.ylim(ymin = 0)
    #plt.ylabel('some numbers')
    #plt.axis([0, 2, 0, 35])
    #x_axis = np.arange(0, 3, 1)
    #plt.xticks(x_axis)
    plt.show()
    
    x = np.linspace(0, 10, 1000)
    y = np.sin(x)
    #z = np.cos(x**2)
    plt.figure(figsize=(8,4))
    plt.plot(x,y,label="$sin(x)$",color="red",linewidth=2)
    #plt.plot(x,z,"b--",label="$cos(x^2)$")
    plt.xlabel("Time(s)")
    plt.ylabel("Volt")
    plt.title("PyPlot First Example")
    plt.ylim(-1.2,1.2)
    plt.legend()
    plt.show()

    x = np.arange(0, 5, 0.1)
    plt.plot(x, x*x) 
    plt.show()

    print()
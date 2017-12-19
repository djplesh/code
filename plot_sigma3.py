# -*- coding: utf-8 -*-
"""
Created on Wed Mar 08 17:27:01 2017

read in timestamp files from get_timestamps, sum over boxes if desired
in 2ms time bins, plot histogram of values above various sigma

@author: DJ Pleshinger
"""


#import cPickle
import numpy as np
import matplotlib.pyplot as plt
from datetime import date
from datetime import timedelta
import time

from get_lightning import nearby_strikes
import tools as tool


##############################################################################
##############################################################################    


def bin_data(data, ave_counts, sig_counts):
    """take in a set of histogrammed data its average and stddev
    return the bin counts for each sigma level
    """
    
    above = data - ave_counts
    above[above < 0] = 0
    sig = above / sig_counts
    sig = np.floor(sig).astype(np.int32)
    sig = sig[sig >= 0]
    bins = np.bincount(sig)
    
    return bins
##############################################################################
##############################################################################        
##############################################################################
##############################################################################        
##############################################################################        
def get_sig(box_num, start_date, duration=1, source = 'wwlln', path0 = None):
    """search bgo data for candidate events above user defined threshold"""
    
    start_time = time.time()
    
    start_d = int(start_date[8:10])
    start_m = int(start_date[5:7])
    start_y = int(start_date[0:4])
    start_day = date(start_y, start_m, start_d)
    
    near_data = []
    far_data = []
    all_data = []
    sum_data = []
    loop_day = start_day
    loc = tool.loc_name(box_num)
    for loop_day in [start_day + timedelta(x) for x in range(duration)]:

        date_str = tool.ints_to_date(loop_day.day, loop_day.month, loop_day.year)      
        folder = date_str[:4] + '_' + date_str[5:7] + '/' 

        if not path0: 
            path = 'Y:/' + box_num + '/' + folder
        else:
            path = path0 + box_num + '/' + folder
            
        ts_file = path + 'ts_' + date_str[8:] + '.npz'
        try:
            ts_data = np.load(ts_file)
        except IOError:
            sys.exit()
        sum_data = []
        for key in ts_data.keys():
            for line in ts_data[key]:
                sum_data.append(line)
        bins_num = np.linspace(0, 86400, 3600*500*24 + 1, dtype = np.float64) 
        total, bins = np.histogram(sum_data,bins_num, density=True)
        strikes_8km, strikes = nearby_strikes(loc, date_str, source)
        for i in range(len(bins) - 1):
            try:
                x = tool.get_nearest(strikes_8km, bins[i])
            except ValueError:
                far_data.append(total[i])
            if np.abs(bins[i] - strikes_8km[x]) < 5:
                near_data.append(total[i])
            else:
                far_data.append(total[i])
            all_data.append(total[i])
    ave_counts = np.average(all_data)
    sig_counts = np.std(all_data)
    far_data = np.array(far_data)
    
    near_bin = bin_data(near_data, ave_counts, sig_counts)
    far_bin = bin_data(far_data, ave_counts, sig_counts)
    all_bin = bin_data(all_data, ave_counts, sig_counts)   
    far_bin = far_bin * len(near_data)/len(far_data)   
    all_bin = all_bin * len(near_data)/len(all_data)    

    print time.time() - start_time
    return far_bin, near_bin, all_bin
    
    
def plot_sig(far, near, all):

    plt.plot(far, lw = 0, marker = 'o', color = 'r')
    plt.yscale('log', noposy = 'clip')
    plt.plot(near, lw = 0, marker = 'o', color = 'b')
    plt.plot(all, lw = 0, marker = 'o', color = 'y')
    plt.show()

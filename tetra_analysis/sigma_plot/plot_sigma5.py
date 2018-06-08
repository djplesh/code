# -*- coding: utf-8 -*-
"""
Created on Wed Mar 08 17:27:01 2017

read in timestamp files from get_timestamps, sum over boxes if desired
in 2ms time bins, plot histogram of values above various sigma

@author: DJ Pleshinger
"""


import numpy as np
import matplotlib.pyplot as plt
from datetime import date
from datetime import timedelta
import datetime as dt
import time
import os
import sys
import csv

from tetra_analysis.ec_search.lightning import nearby
import tetra_tools.tools as tool


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
       
def get_sig(box_num, d_str, source = 'wwlln', bin_size = .002):
    """search bgo data for candidate events above user defined threshold"""

    start_time = time.time()  
    d = dt.date(int(d_str[0:4]),int(d_str[5:7]),int(d_str[8:10]))
    
    near_data = []
    loc = tool.loc_name(box_num[0])
    strikes_8km = nearby(loc, d, source)
    if len(strikes_8km[0]) == 0: sys.exit()
    timestamps = np.array([])
    for b in box_num:
        fp = 'Y:/' + b + '/' + str(d.year) + '_' + str(d.month) + '/ts_' + str(d.day) + '.npz'
        if not os.path.exists(fp): continue
        ts_file = np.load(fp)
        for key in ts_file.keys():
            timestamps = np.concatenate([timestamps, ts_file[key]])
     
    if bin_size < .1:
        all_counts = np.array([])
        all_bins = np.array([])
        for i in range(24):
            ts_1hr = timestamps[np.where(np.logical_and(timestamps < 3600 * (i+1), timestamps > 3600 * i))[0]]
            bins = np.linspace(0, 3600, 3600/bin_size + 1) + 3600 * i
            counts = np.histogram(ts_1hr, bins)[0]
            all_counts = np.concatenate([all_counts, counts])
            if i != 23:
                all_bins = np.concatenate([all_bins, bins[:-1]])
            else:
                all_bins = np.concatenate([all_bins, bins[:]])
    else:
        all_bins = np.linspace(0, 86400, (86400/bin_size) + 1)
        all_counts = np.histogram(timestamps, all_bins)[0]
    bin_mid = all_bins[:-1] + bin_size/2
    print time.time() - start_time 
    for i in range(len(bin_mid) - 1):
        try:
            x = tool.get_nearest(strikes_8km[0], bin_mid[i])
        except ValueError:
            continue
        if np.abs(bin_mid[i] - strikes_8km[0][x]) < 5:
            near_data.append(all_counts[i])
    print time.time() - start_time    
    ave_counts = np.average(all_counts)
    sig_counts = np.std(all_counts)
    
    near_bin = bin_data(near_data, ave_counts, sig_counts)
    all_bin = bin_data(all_counts, ave_counts, sig_counts)   
    all_bin = all_bin * float(len(near_data))/float(len(all_counts))
    
    if len(all_bin) < len(near_bin):
        all_bin.resize(near_bin.shape)
    else:
        near_bin.resize(all_bin.shape)
    test3 = np.array(list(zip(near_bin, all_bin)))
    
    
    storm_time_hrs = round(len(near_data)*.002/3600,5)
    fileheader = str(storm_time_hrs) + ' hours ' + source
    if len(box_num) == 1:
        box_name = box_num[0]
    else:
        box_name = loc
    #fileout = box_name + '-' + date_str + source[0]
    #np.savetxt('C:/Users/tetra/analysis/freq_sig/' + fileout  + '.csv',test3,delimiter=',', fmt = '%.5f', header = fileheader)
    
    print time.time() - start_time
    return near_bin, all_bin


    
def plot_sig():

    file_list = tool.path_files('C:/Users/tetra/analysis/freq_sig/')
    total_time = 0
    n_sum = np.array([])
    a_sum = np.array([])

    for f in file_list:
        if f[-3:] == 'csv':
            n = []
            a = []
            with open(f) as infile:
                reader = csv.reader(infile)
                for row in reader:
                    if row[0].startswith('#'):
                        h = float(row[0][2:9])
                        total_time = total_time + h
                    else:
                        n.append(float(row[0]))
                        a.append(float(row[1]))
                a = np.array(a)
                n = np.array(n)
                if len(n) < len(n_sum):
                    n.resize(n_sum.shape)
                else:
                    n_sum.resize(n.shape)
                n_sum = n_sum + n
                if len(a) < len(a_sum):
                    a.resize(a_sum.shape)
                else:
                    a_sum.resize(a.shape)
                a_sum = a_sum + a    
    x1 = np.arange(len(n_sum))+1
    plt.bar(x1,n_sum, color = 'w', edgecolor = 'purple', width = .8, log = True, hatch = '/')
    plt.bar(x1,a_sum, color = 'w', edgecolor = 'g', width = .8, log = True, hatch = '/')
    plt.xlim([0,50])
    plt.ylim([0.01,1e7])
    plt.title('6 events, background normalized to 5 hours')
    plt.ylabel('# of events')
    plt.xlabel('Sigma')
    #plt.savefig('C:/Users/tetra/analysis/freq_sig/freq_sig.pdf')
    plt.show()
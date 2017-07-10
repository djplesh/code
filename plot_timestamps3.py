# -*- coding: utf-8 -*-
"""
Created on Wed Mar 08 17:27:01 2017

same as plot_timestamps.py just with ability to sum data from multiple boxes

@author: DJ Pleshinger
"""


import numpy as np
import matplotlib.pyplot as plt
import time


##############################################################################
##############################################################################    
def get_bins(c, min_bin):    
    """return bins with at least min threshold counts"""

    b2a = np.where(c > min_bin)
    b2b = np.where(c < 500)  #eliminates periodic noise trigger ~900
    b2c = np.intersect1d(b2a, b2b)    
    return b2c

def get_nearest(array, value):    
    '''find the nearest value in an array'''
    
    idx = (np.abs(array - value)).argmin()
    return idx

def get_focus(data, mi, ma):    
    """obtain data between a min and max value or time"""
    
    focus = []
    for line in data:
        if line > mi and line < ma:
            focus.append(line)            
    return focus
       
##############################################################################
##############################################################################        
##############################################################################
##############################################################################        
##############################################################################        
def rates(box_num, date_str, threshold = 30, path0 = None):
    """search bgo data for candidate events above user defined threshold"""
    
    start_time = time.time()
    if not threshold: threshold = 30
    folder = date_str[5:7] + '_' + date_str[0:4] + '/'
    
    total_data = []
    for box in box_num:
        
        if not path0: 
            path = 'D:/rates/' + box + '/' + folder
        else:
            path = path0 + box + '/' + folder
        dev1_file =  path + 'dev1_' + date_str[8:]+'.npy'
        dev2_file =  path + 'dev2_' + date_str[8:]+'.npy' 
        hist_file = path + 'hist_' + date_str[8:]+'.npy'
        
        
        hist_data = np.load(hist_file)
        
         
        
        ave = np.sum(hist_data, axis=0)[1]/43200000
        std = np.sqrt((np.sum((hist_data-ave)**2, axis = 0)[1] \
        + (43200000 - len(hist_data))*ave**2)/(43200000-1))

    
        above = hist_data[:,1] - ave
        above[above < 0] = 0
        bin_sig = above / std
        bin_sig = np.floor(bin_sig).astype(np.int32)
        bin_sig = bin_sig[bin_sig >= 0] 
        x = np.where(bin_sig >= threshold)[0]
        bgo_triggers = x
        
        
        
        
    if len(bgo_triggers) > 0:
        for trig in bgo_triggers:
            print hist_data[trig][1]
            print trig
            trig_ts = hist_data[:,0][trig]
            xmin_bin = trig_ts - 0.5
            xmax_bin = trig_ts + 0.5
            xmi = get_nearest(hist_data[:,0], xmin_bin)
            xma = get_nearest(hist_data[:,0], xmax_bin)
            fig1,ax1 = plt.subplots(1)
            ax1.bar(hist_data[:,0][xmi:xma],hist_data[:,1][xmi:xma],
            width = .002)
            title_string = str(sum(hist_data[:,1][xmi:xma])) \
            + ' total counts on: ' + date_str
            ax1.set_title(title_string)
            plt.xlim([hist_data[:,0][xmi],hist_data[:,0][xma]+.002])
            
            temp=[]
            xmin_bin = trig_ts - 5*.002
            xmax_bin = trig_ts + 6*.002
            xmi = get_nearest(hist_data[:,0], xmin_bin)
            xma = get_nearest(hist_data[:,0], xmax_bin)
            
            dev1_data = np.load(dev1_file)
            dev2_data = np.load(dev2_file)
            total_data = dev1_data[0] + dev1_data[1] + dev1_data[2] \
            + dev2_data[0] + dev2_data[1] + dev2_data[2]
            for line in total_data:
                if line < hist_data[:,0][xma] and line > hist_data[:,0][xmi]:
                    temp.append(line)
            bins_needed = np.ceil((xma - xmi) * .002 / .00002)
            bins_focus = np.linspace(hist_data[:,0][xmi], hist_data[:,0][xma], 
                                     bins_needed + 1, dtype=np.float64)
            bgo_focus, bins_focus = np.histogram(temp, bins = bins_focus)
            fig2, ax2 = plt.subplots(1)
            ax2.bar(bins_focus[:-1], bgo_focus, width = .00002)
            title_string2 = str(sum(bgo_focus)) + ' total counts on: ' + date_str
            ax2.set_title(title_string2)

            
            
    print time.time() - start_time
                               

def daily_rates(box_num, date_str, path0 = None):
    
    start_time = time.time()

    folder = date_str[5:7] + '_' + date_str[0:4] + '/'
               
    if not path0: 
        path = 'D:/rates/' + box_num + '/' + folder
    else:
        path = path0 + box_num + '/' + folder
    dev1_file =  path + 'dev1_' + date_str[8:]+'.npy'
    dev2_file =  path + 'dev2_' + date_str[8:]+'.npy' 
    
    dev1_data = np.load(dev1_file)
    dev2_data = np.load(dev2_file)
    total_data = dev1_data[0] + dev1_data[1] + dev1_data[2] + dev2_data[0] \
    + dev2_data[1] + dev2_data[2]
    
    bins_num=np.linspace(0,86400,60*24+1,dtype=np.float64)

    bgo, bins = np.histogram(total_data, bins_num)
    print time.time() - start_time
    
    fig, ax = plt.subplots(1)
    ax.plot(bins[:-1],bgo, lw = 0, marker = ',')
    title_string2 = date_str
    ax.set_title(title_string2)
    
    print time.time() - start_time
    
#    return total_data, bgo, bins, dev1_data, dev2_data
    
    


        


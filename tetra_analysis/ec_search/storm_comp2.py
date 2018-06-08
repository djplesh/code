# -*- coding: utf-8 -*-
"""
Created on Wed Mar 08 17:27:01 2017

same as plot_timestamps.py just with ability to sum data from multiple boxes

@author: DJ Pleshinger
"""


import numpy as np
import matplotlib.pyplot as plt
import time
from datetime import date
from datetime import timedelta
import os

from get_lightning import recent_strikes
from get_lightning import nearby_strikes
import tetra_tools.tools as tool

import tetra_analysis.ec_search.lightning as light

##############################################################################
##############################################################################

def get_bins(c, min_bin):    
    """return bins with at least min threshold counts"""

    b2a = np.where(c > min_bin)
    b2b = np.where(c < 500)  #eliminates periodic noise trigger ~900
    b2c = np.intersect1d(b2a, b2b)    
    return b2c

def get_focus(data, mi, ma):    
    """obtain data between a min and max value or time"""
    
    focus = []
    for line in data:
        if line > mi and line < ma:
            focus.append(line)            
    return focus

def zoom_data(box_list, date_str, xmin, xmax):
    folder = date_str[:4] + '_' + date_str[5:7] + '/'
    
    total_data = []
    for box in box_list:
        path = 'Y:/' + box + '/' + folder
        ts_file = path + 'ts_' + date_str[8:] + '.npz'
        if not os.path.exists(ts_file):
            continue
        ts_data = np.load(ts_file)
        for key in ts_data.keys():
            total_data = np.concatenate([total_data, ts_data[key]])
        #total_data = np.concatenate([total_data, ts_data['bgo1'], ts_data['bgo2'], ts_data['bgo3'],ts_data['bgo4'], ts_data['bgo5'], ts_data['bgo6']])
    zoom_data = []
    for ts in total_data:
        if xmin < ts < xmax:
            zoom_data.append(ts)
    bgo, bins = np.histogram(zoom_data, 200, (xmin, xmax))
    return bgo, bins

def add_boxes(box_list, date_str):
            
    folder = date_str[:4] + '_' + date_str[5:7] + '/'
    
    total_data = []
    for box in box_list:
        path = 'Y:/' + box + '/' + folder
        ts_file = path + 'ts_' + date_str[8:] + '.npz'
        if not os.path.exists(ts_file):
            continue
        ts_data = np.load(ts_file)
        for key in ts_data.keys():
            total_data = np.concatenate([total_data, ts_data[key]])
        #total_data = np.concatenate([total_data, ts_data['bgo1'], ts_data['bgo2'], ts_data['bgo3'], ts_data['bgo4'], ts_data['bgo5'], ts_data['bgo6']])
    
    bgo, bins = np.histogram(total_data, 43200000, (0, 86400))
    return bgo
##############################################################################
##############################################################################        
##############################################################################
##############################################################################        
##############################################################################        
def event_search(box_num, start_date, time_window = 5, duration = 1, bin_size = .002, threshold = 20, source = 'wwlln'):
    """search bgo data for candidate events above user defined threshold
    time_window is number of seconds before and after event to search for lighting
    default is 5 seconds
    """   
    
    start_d = int(start_date[8:10])
    start_m = int(start_date[5:7])
    start_y = int(start_date[0:4])
    start_day = date(start_y, start_m, start_d)
    
    start_time = time.time()
    if not threshold: threshold = 30
    loop_day = start_day
    n = duration/np.abs(duration)
    
    for loop_day in [loop_day + timedelta(x) for x in range(0, duration, n)]:
        loc = tool.loc_name(box_num[0])
        date_str = tool.ints_to_date(loop_day.day, loop_day.month, loop_day.year)
        if len(box_num) == 1:
            
            folder = date_str[:4] + '_' + date_str[5:7] + '/'
            
            total_data = []

            path = 'D:/rates/' + box_num[0] + '/' + folder
            path = 'Y:/' + box_num[0] + '/' + folder
           
            ts_file =  path + 'ts_' + date_str[8:]+'.npz'
            ts = np.load(ts_file)
            for key in ts.keys():
                timestamps = np.concatenate([total_data, ts[key]])
                        
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
            
            ave = np.average(all_counts)
            std = np.std(all_counts)
            min_counts = np.ceil(ave + std * threshold)
            ec = np.where(np.array(all_counts) > min_counts)[0]
            print len(ec)
            print min_counts
            if min_counts < 6:
                continue
            above = all_counts - ave
            above[above < 0] = 0
            bin_sig = above / std
            bin_sig = np.floor(bin_sig).astype(np.int32)
            bin_sig = bin_sig[bin_sig >= 0] 
            x = np.where(bin_sig >= threshold)[0]
            bgo_triggers = x
            
            
            
            
        elif len(box_num) > 1:
            #check on if there was lightning first, quicker than looping through boxes
            a, b = nearby_strikes(loc, date_str, source, True)
            if a == 0:
                continue
            bin_info = np.linspace(0,43200000, 43200001)
            hist_data = add_boxes(box_num, date_str)
            ave = np.average(hist_data)
            std = np.std(hist_data)
            above = hist_data - ave
            above[above < 0] = 0
            bin_sig = above / std
            bin_sig = np.floor(bin_sig).astype(np.int32)
            bin_sig = bin_sig[bin_sig >= 0] 
            x = np.where(bin_sig >= threshold)[0]
            bgo_triggers = x
            hist_data2 = np.array(zip(bin_info*.002, hist_data))
            
        if len(bgo_triggers) > 0 and len(bgo_triggers) < 10000:

            #strikes_8km, strikes_all = nearby_strikes(loc, date_str, source) 
            strikes_8km = light.nearby(loc, date_str, source)
            if len(strikes_8km) == 0:
                continue
            print str(len(bgo_triggers)) + ' events over threshold on ' + date_str
            print str(len(strikes_8km[0])) + ' lightning strikes within 8km on ' + date_str
            for trig in bgo_triggers:
                print trig

                #strikes_8km_5s, dists_8km_5s = recent_strikes(strikes_8km, strikes_all, hist_data2[trig][0], time_window)
                strikes_8km_5s, dists_8km_5s = light.recent(strikes_8km, hist_data2[trig][0], time_window)
                if len(strikes_8km_5s) == 0:
                    continue
                trig_ts = hist_data2[:,0][trig]
                xmin_bin = trig_ts - time_window
                xmax_bin = trig_ts + time_window
                xmi = tool.get_nearest(hist_data2[:,0], xmin_bin)
                xma = tool.get_nearest(hist_data2[:,0], xmax_bin)
                plot_s = []
                plot_d = []
                
                
                for i in range(len(strikes_8km_5s)):
                    if strikes_8km_5s[i] < hist_data2[xma][0] and strikes_8km_5s[i] > hist_data2[xmi][0]:
                        plot_s.append(strikes_8km_5s[i])
                        plot_d.append(dists_8km_5s[i])
                    i = i + 1
                if len(plot_s) == 0: continue
                print len(plot_s)
                print str(len(strikes_8km_5s)) + 'strikes in time window'
                #fig1, ax1 = plt.subplots(1)
                f, axarr = plt.subplots(2)
                axarr[1].bar(hist_data2[:,0][xmi:xma],hist_data2[:,1][xmi:xma],
                width = .002)
                axarr[1].set_ylabel('counts per 2ms')
                title_string = loc + ' on ' + date_str 
                #axarr[0].set_title(title_string)
                axarr[1].set_xlabel('time (s)')
                
                if len(plot_s) > 0:
                    ax2 = axarr[1].twinx()
                    ax2.plot(plot_s, plot_d, lw = 0, marker = 'd', color = 'green', label = 'lightning strike')
                    ax2.set_ylabel('distance to lightning (km)', color = 'g')
                    ax2.tick_params('y', colors = 'g')
                    a = ax2.axis()
                    ax2.axis([a[0], a[1], 0, 8])   
                    #print np.abs(plot_s - hist_data2[trig][0])
                    #print min(plot_d)
                
                #plt.xlim([hist_data2[:,0][xmi],hist_data2[:,0][xma]+.002])
                axarr[1].set_xlim([hist_data2[:,0][xmi],hist_data2[:,0][xma]+.002])    
                axarr[0].set_xlim([hist_data2[:,0][trig]-.002,hist_data2[:,0][trig]+.004])               
                
                #this part is only needed for 20usec bins
                xmin_bin = trig_ts - .002
                xmax_bin = trig_ts + .002
                xmi = tool.get_nearest(hist_data2[:,0], xmin_bin)
                xma = tool.get_nearest(hist_data2[:,0], xmax_bin)
                zoom_counts, zoom_bins = zoom_data(box_num, date_str, xmin_bin, xmax_bin)
                # if sum(zoom_counts) < 7:
                    # plt.close()
                    # continue
                hist_dataz = np.array(zip(zoom_bins, zoom_counts))
                #print sum(zoom_counts)
                #fig2, ax2 = plt.subplots(1)
                axarr[0].bar(hist_dataz[:,0],hist_dataz[:,1],color = 'black', width = .00002)
                axarr[0].set_ylabel('counts per 20us')
                title_string = loc + ' on ' + date_str + ': ' + str(sum(zoom_counts))
                axarr[0].set_title(title_string)
                axarr[0].set_xlabel('time (s)')
                #axarr[0].set_xlim([hist_data2[:,0][xmi],hist_data2[:,0][xma]+.002])
                
                #f.subplots_adjust(hspace=0.3)
                plt.tight_layout()
                plt.show()                
    #print time.time() - start_time     

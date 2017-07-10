# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 19:36:37 2017

@author: DJ Pleshinger
"""

import os
import glob
import datetime
import numpy as np
from datetime import timedelta

from pyTDMS4 import read


##########################################################################
def get_filelist(path, loop_day, time_diff, file_type):      
    """select specific files in a given path from a given day"""
    
    day, month, year = loop_day.day, loop_day.month, loop_day.year
    file_list = []
    for file in glob.glob(os.path.join(path,file_type)):
        statinfo = os.stat(file)                
        timestamp = statinfo.st_mtime
        if time_diff == None:
            date = datetime.datetime.fromtimestamp(timestamp)
        else:
            date2 = datetime.datetime.fromtimestamp(timestamp)
            date = date2 + timedelta(hours = time_diff)
        if date.day == day and date.month == month and date.year == year:
            if (date.hour == 0 and date.minute >= 10) or date.hour > 0:
                file_list.append(file)
        d = datetime.date(year, month, day)
        tom = d + datetime.timedelta(days = 1)
        if date.day == tom.day and date.month == tom.month \
        and date.year == tom.year:
            if date.hour == 0 and date.minute < 10:
                file_list.append(file)            
    return file_list

def day_files_tz(path_name, file_type, loop_day):   
    """select .tdms files from any timezone for a day in a given path"""
    
    current_hour = datetime.datetime.now().hour
    current_utchour = datetime.datetime.utcnow().hour
    time_diff = current_hour - current_utchour
    path = path_name + file_type + '/'   
    file_list = get_filelist(path, loop_day, time_diff, '*tdms')            
    return file_list

def day_files(path_name, file_type, loop_day):    
    """select .tdms files from UTC computer for a day in a given path"""    
    
    path = path_name + file_type + '/'    
    file_list = get_filelist(path, loop_day, None, '*tdms')           
    return file_list



##########################################################################
##########################################################################
def find_nearest(array, value):    
    """find the closest value in an array to the called value"""
    
    x = np.searchsorted(array, value)-1
    if x == -1:
        x = 0        
    return x

def first_pps(ctr1):    
    """find the first pps in the ctr1 file"""
    
    for k in range(100):        
        d = ctr1[(k + 1):(k + 200)] - ctr1[k]
        b = find_nearest(d, 20000000)
        if np.abs(20000000 - d[b]) < 500:            
            return k

def get_pps(ctr1_file):    
    """from the ctr1 file obtain the position of all pps and the clk rates"""
    
    ctr = get_ctr(ctr1_file)    
    ctr1_full = ctr_rollover(ctr)   
    pos = []
    ctr1_full = np.array(ctr1_full)
    
    a = first_pps(ctr1_full)
    if not a: 
        pos = None
        pps_ctrs = []
        clks = []
        return pos, pps_ctrs,clks
    pos.append(a)    
    
    for k in range(600):
        diffs = []
        diffs = ctr1_full[(a + 1):] - ctr1_full[a]
        diffs = np.array(diffs)
        b = find_nearest(diffs, 20000000)
        if diffs[b] < 19999000:
            break   # reached end of file before 600 pps
        pos.append(b + a + 1)
        a = b + 1 + a
        if a > len(ctr1_full) - 2:
            break   # reached end of file, do not look for another pps  
            
    pps_ctrs = []    
    for k in pos:
        pps_ctrs.append(ctr1_full[k])
    pps_arr = np.array(pps_ctrs)
    clks = np.ediff1d(pps_arr)
    return pos, pps_ctrs, clks

##########################################################################
##########################################################################
def start_times(start_time):    
    """find the time a file started from the hhmmss notation in file name"""
#    print start_time
    hh = start_time[0:2]
    mm = start_time[2:4]
    ss = start_time[4:6]
    if hh == '':
        time = 0
    else:
        second = int(ss)   
        minute = int(mm)
        hour = int(hh)   
        time = hour*3600 + minute*60 + float(second)          
    return time

def ctr_to_times(ctr_data, pps_ctrs, clks, ctr_file, i):        
    """converts the ctr tic data to times"""
    

    file_time = [x.strip() for x in ctr_file.split(',')][1][:6]
    start_time = start_times(file_time)
    if i == 0:
        start_time = start_time - 86400
    time_data = []
    c = 0
    sec = 0   
    for ctr in ctr_data:
        if sec < len(pps_ctrs):
            if ctr - pps_ctrs[sec] > 0:
                sec = sec + 1
                c = sec - 1
                if c == len(clks):
                    c = c - 1
        if sec == 0:    
            time_to_add = float(ctr) / float(clks[c]) + float(start_time)
        else:
            time_to_add = (float(ctr) - float(pps_ctrs[sec - 1]))  \
                            /float(clks[c]) + float(start_time) + sec
        time_data.append(time_to_add)        
    return time_data

def ctr_rollover(ctr):    
    """adjust ctr values for roll over at 2^32 tics"""
    if len(ctr) < 100:
        return ctr
    
    v = 0
    ctr_full = []
    ctr_full.append(ctr[0])
    for k in range(1, len(ctr)):
        if ctr[k] < ctr[k - 1]:
            v = v + 1
        ctr_full.append(ctr[k] + (2**32)*v)        
    return ctr_full

def get_ctr(file_name):
    '''read in ctr data'''
    
    data_raw = read(file_name)
    data = data_raw[1][data_raw[1].keys()[0]]
    data = list(data)    
    
    data2 = ctr_rollover(data)
    return data2

def get_times(file_name, pps_ctr1, clks, i):     
    """read in ctr data and call to convert to times""" 
    
    data = get_ctr(file_name)
    times = ctr_to_times(data, pps_ctr1, clks, file_name, i)      
    return times

##########################################################################
########################################################################## 
def get_bgo(ctr1_file, ctr2_file, ctr3_file, ctr1_pps_idx):
    
    both = []
    bgo1 = []
    bgo2 = []
    bgo3 = []
#    print ctr1_file
    ctr1 = np.array(get_ctr(ctr1_file))
    ctr2 = np.array(get_ctr(ctr2_file))
    ctr3 = np.array(get_ctr(ctr3_file))
    
    c= 0
    for x in ctr1:
        if len(ctr2) != 0 and len(ctr3) != 0 and (np.abs(ctr2 - x)).min() < 3 \
        and (np.abs(ctr3 - x)).min() < 3:
            both.append(x)
        elif len(ctr2) != 0 and (np.abs(ctr2 - x)).min < 3:
            bgo2.append(x)
        elif len(ctr3) != 0 and (np.abs(ctr3 - x)).min < 3:
            bgo3.append(x)
        elif x == ctr1[ctr1_pps_idx[c]]:
            c += 1
            if c == len(ctr1_pps_idx): c = c-1
        else:
            bgo1.append(x)
            
    return bgo1, bgo2, bgo3
    


  
def get_idx(timestamps, ctr1_pps_idx):     
    """compare ctr2 and ctr3 to ctr1 to create an idx file for ctr1 triggers"""
    
    idx = []
    j = 0
    count = 0
    ctr1_times_arr = np.array(timestamps[0])    
    ctr2_times_arr = np.array(timestamps[1])
    ctr3_times_arr = np.array(timestamps[2])
       
    for line in ctr1_times_arr:
        if count == ctr1_pps_idx[j]:
            idx.append('pps')
            j = j + 1
            if j > len(ctr1_pps_idx) - 1:
                j = j - 1
            count = count + 1
            continue
        ctr2_diff = np.abs(ctr2_times_arr - line)
        ctr3_diff = np.abs(ctr3_times_arr - line)
        ctr2_matches = np.where(ctr2_diff <= 0.0000002)[0]
        ctr3_matches = np.where(ctr3_diff <= 0.0000002)[0]
        n2_matches = len(ctr2_matches)
        n3_matches = len(ctr3_matches)
        if n2_matches == n3_matches == 1:
            idx.append('both')
        elif n2_matches != 0:
            idx.append('bgo2')
        elif n3_matches != 0:
            idx.append('bgo3')
        elif n2_matches == n3_matches == 0:
            idx.append('bgo1')
        count = count + 1
    bgo1 = []
    c = 0 
    for line in idx:
        if line == 'bgo1':
            bgo1.append(ctr1_times_arr[c])
            c = c + 1
        else: 
            c = c + 1
    del ctr1_times_arr
    del ctr2_times_arr
    del ctr3_times_arr
    return idx, bgo1

##########################################################################
########################################################################## 
def fix_num(n):    
    """convert integer to string, add 0 if single digit"""
    
    if n < 10: n_s = '0' + str(n)
    else:
        n_s = str(n)
    return n_s

def ints_to_date(d, m, y):    
    """from integers for day month and year return date string,
    format yyyy_mm_dd"""
    
    m_s = fix_num(m)
    d_s = fix_num(d)
    y_s = str(y)
    date_s = y_s + '_' + m_s + '_' + d_s   
    return date_s

def date_to_ints(date):    
    """from date in string format yyyy_mm_dd 
    return integer values for day month and year"""
    
    d = int(date[8:10])
    m = int(date[5:7])
    y = int(date[0:4])        
    return d, m, y  
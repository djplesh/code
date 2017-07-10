# -*- coding: utf-8 -*-
"""
Created on Tue Jan 24 14:46:55 2017

make energy plots from single file from a day

needs work

@author: DJ Pleshinger
"""


import numpy as np
import datetime

import ctr_to_timestamp2 as get

##############################################################################


def get_idx(ctr1_times, ctr2_times, ctr3_times, ctr1_pps_idx):

    idx = []
    j = 0
    count = 0
    ctr1_times_arr = np.array(ctr1_times)
    ctr2_times_arr = np.array(ctr2_times)
    ctr3_times_arr = np.array(ctr3_times)

    for line in ctr1_times_arr:
        if count == ctr1_pps_idx[j]:
            idx.append('pps')
            j = j + 1
            if j > len(ctr1_pps_idx) - 1:
                j = j - 1
            count=count + 1
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
    j = 0
    bgo1 = []
    for line in idx:
        if line == 'bgo1':
            bgo1.append(ctr1_times_arr[j])
            j = j + 1 
        else:
            j = j + 1 
    return idx, bgo1 



def get_times(files):
    ctr_times = [[], [], []]
    pps_idx, pps_ctr1, clks = get.get_pps(files[0])
    ctr_times[1] = get.get_times(files[1], pps_ctr1, clks, 1)
    ctr_times[2] = get.get_times(files[2], pps_ctr1, clks, 1)
    ctr_times[0] = get.get_times(files[0], pps_ctr1, clks, 1)

    return ctr_times, pps_idx


def get_filename(path0, date_str, time_sec, dev):
    files = []

    d, m, y = get.date_to_ints(date_str)
    date = datetime.date(y, m, d)

    path = path0 + dev + '/'
    file_type = ['ctr1', 'ctr2', 'ctr3', 'analog']
    file_list = [[],[],[],[]]
    for x in file_type:
        file_list = get.day_files(path, x, date)
        file_names = []
        for f in file_list:
            file_name = f[f.rfind('\\'):]
            file_time = file_name.split(',')[1]
            try:
                file_time = 3600*int(file_time[0:2]) + 60*int(file_time[2:4]) + int(file_time[4:6])
            except ValueError as e:
                continue
            if file_time < time_sec:
                good_file = f
            else:
                break
        files.append(good_file)

    return files

##############################################################################
##############################################################################
##############################################################################


def energy(box_num, date_str, time_sec, path0):
    #to do:
    #get file lists for that day, pick out correct one based on time
    if not path0: path0 = 'C:/Users/tetra/data/' + box_num + '/'
    folder = date_str[5:7] + '_' + date_str[0:4] + '/'
    path = path0 + folder
    dev1_files = get_filename(path, date_str, time_sec, 'Dev1')
    dev2_files = get_filename(path, date_str, time_sec, 'Dev2')
    print dev1_files[0]

    #convert ctr files to times and make index file
    dev1_times, pps_idx1 = get_times(dev1_files)
    dev2_times, pps_idx2 = get_times(dev2_files)
    
    idx1, bgo1_1 = get_idx(dev1_times[0], dev1_times[1], dev1_times[2], pps_idx1)
    idx2, bgo1_2 = get_idx(dev2_times[0], dev2_times[1], dev2_times[2], pps_idx2)
    
    idx1_arr = np.array(idx1)
    idx2_arr = np.array(idx2)
    
    print len(dev1_times[1]) - (idx1_arr == 'bgo2').sum()
    print len(dev1_times[2]) - (idx1_arr == 'bgo3').sum()
    print len(dev2_times[2]) - (idx2_arr == 'bgo3').sum()
    print len(dev2_times[1]) - (idx2_arr == 'bgo2').sum()
    
    print len(bgo1_1) + len(dev1_times[1]) + len(dev1_times[2])
    print len(dev1_times[0])
    print len(bgo1_2) + len(dev2_times[1]) + len(dev2_times[2])
    print len(dev2_times[0])

    

    # idx_arr=np.array(idx1)
    # pps_idx_len=(idx_arr == 'pps').sum()
    # bgo1_idx_len=(idx_arr == 'bgo1').sum()
    # bgo2_idx_len=(idx_arr == 'bgo2').sum()
    # bgo3_idx_len=(idx_arr == 'bgo3').sum()
    # both_idx_len=(idx_arr == 'both').sum()

    return idx1, idx2

    #align ctr1 with analog
    
    #select triggers within smaller range in adc file
    #convert adc values to energies using calibration values
    #plot













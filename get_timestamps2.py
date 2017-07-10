# -*- coding: utf-8 -*-
"""
Created on Fri Jun 24 18:21:15 2016

-reads in all TETRAII files for a single day and saves two files
    one file for each device containing each ctr converted to timestamps
-uses analog and ctr1 files to find pps and determine clock
-uses clock to convert counters into times
-finds ctr2 and ctr3 ungated rates
-finds ctr1 gated rates

remember: the bgo for each ctr1 cannot give a good rate estimate
    should be gated with 13usec delay


@author: DJ Pleshinger
"""

import ctr_to_timestamp2 as get

import os
import numpy as np
from datetime import date
from datetime import timedelta

##############################################################################
def trim_lists(file_list):
    """used to collect only matching files if there are different number
    of files in each folder for a given day
    """

    adc_file_path = file_list[3][0][:file_list[3][0].rfind('\\')]
    ctr1_file_path = file_list[0][0][:file_list[0][0].rfind('\\')]
    ctr2_file_path = file_list[1][0][:file_list[1][0].rfind('\\')]
    ctr3_file_path = file_list[2][0][:file_list[2][0].rfind('\\')]

    new_list = np.intersect1d(np.intersect1d(np.intersect1d( \
                    np.array([s.split("\\")[-1] for s in file_list[0]]), \
                    np.array([s.split("\\")[-1] for s in file_list[1]])), \
                    np.array([s.split("\\")[-1] for s in file_list[2]])), \
                    np.array([s.split("\\")[-1] for s in file_list[3]]))
    file_list = [[],[],[],[]]

    for line in new_list:
        file_list[3].append(adc_file_path + '/' + line)
        file_list[0].append(ctr1_file_path + '/'  +line)
        file_list[1].append(ctr2_file_path + '/' + line)
        file_list[2].append(ctr3_file_path + '/' + line)
    num_files = len(new_list)
    return file_list, num_files

def array_name(box_num):
    """convert box name string to string of folder on home computer"""

    if box_num[0:3] == 'LSU':
        array = 'lsu'
    elif box_num[0:3] == 'UAH':
        array = 'uah'
    elif box_num[0:3] == 'PAN':
        array = 'pan'
    elif box_num[0:2] == 'PR':
        array = 'pr'
    return array

def check_cals(date_str, box_num):
    """check to make sure calibrations were not done on the day of interest"""

    x = None
    array = array_name(box_num)
    cal_file_dates = 'C:/Users/tetra/calibrations/' + array + '/cal_dates.txt'
    with open(cal_file_dates) as infile:
        for line in infile:
            if line[0:10] == date_str[0:10]:
                x = True
                return x
    return x


##############################################################################
def get_data(dev, loop_day, path0):
    """runs for a given device to convert the ctr data to timestamps"""

    data_full = [[],[],[]]
    file_type = ['ctr1', 'ctr2', 'ctr3', 'analog']
#   get file lists and check number of each
    path = path0 + dev + '/'
    file_list = [[],[],[],[]]
    for i in range(4):
        file_list[i] = get.day_files(path, file_type[i], loop_day)
    if len(file_list[0]) == len(file_list[1]) == len(file_list[2]) \
    == len(file_list[3]):
        num_files = len(file_list[0])
    else:
        file_list, num_files = trim_lists(file_list)
#   begin looping thru files, count is number of files used in analysis
    count = 0
    for i in range(num_files):
#        check for gps lock
        gps_lock = True
        for j in range(4):
            file_name = file_list[j][i][file_list[j][i].rfind('\\'):]
            if len(file_name) == 1:
                file_name = file_list[j][i][file_list[j][i].rfind('/'):]
            if len(file_name) < 50:
                gps_lock = None
                break
        if  not gps_lock: continue
#        check ctr1 size
        ctr1_data = get.get_ctr(file_list[0][i])
        if len(ctr1_data) < 100:
            continue
        del ctr1_data
#        get pps and clks
        pps_idx, pps_ctr1, clks = get.get_pps(file_list[0][i])
        if not pps_idx: continue
        count = count + 1
#       get data and convert to times
        dev_data = [[],[],[]]
        for j in range(3):
            dev_data[j].extend(get.get_times(file_list[j][i], pps_ctr1,
            clks, i))        
            # if j != 0:
                # for line in dev_data[j]: data_full[j].append(line)
                
        idx, bgo1 = get.get_idx(dev_data, pps_ctr1)
        idx = np.array(idx)
        if (idx == 'bgo2').sum() == 0: dev_data[1] = []
        if (idx == 'bgo3').sum() == 0: dev_data[2] = []
        # for line in bgo1: data_full[0].append(line)
        
        for j in range(3):
            if j == 0:
                for line in bgo1: data_full[0].append(line)
            if j != 0:
                for line in dev_data[j]: data_full[j].append(line)


    return data_full


##############################################################################
def run_data(box_num, start_date, end_date = None):
    """call the box number and date range to convert the ctr files to two saved
    files of lists containing the timestamp information
    """

    if end_date == None or end_date == '': end_date = start_date
    path0 = 'C:/Users/tetra/data/' + box_num + '/'
    start_day, start_month, start_year = get.date_to_ints(start_date)
    end_day, end_month, end_year = get.date_to_ints(end_date)
    loop_day = date(start_year, start_month, start_day)
    loop_end = date(end_year, end_month, end_day)

    while loop_day < loop_end + timedelta(1):

        date_str = get.ints_to_date(loop_day.day, loop_day.month, loop_day.year)
        folder = date_str[5:7] + '_' + date_str[0:4] + '/'
        output_path = 'D:/rates/' + box_num + '/' + folder
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        if not os.path.isfile(output_path + 'hist_' + date_str[8:] + '.npy'):

            cal=check_cals(date_str, box_num)
            if not cal:
                path = path0 + folder
                
                #added this if statement to deal with 2016 data not in month folders
                if loop_day.year == 2016 and loop_day.month != 8 and loop_day.year != 9:
                    path = path0
                try:
                    dev1_data = get_data('Dev1', loop_day, path)
                    dev2_data = get_data('Dev2', loop_day, path)
                except NameError as e:
                    with open('C:/Users/tetra/data/errors.txt', 'a') as f:
                        f.write(box_num + ' ' + date_str + ': ' + str(e) + '\n')
                        loop_day = loop_day + timedelta(1)
                        continue
                        
            else:
                dev1_data = 'calibration day'
                dev2_data = 'calibration day'


            np.save(output_path + 'Dev1_' + date_str[8:], dev1_data)
            np.save(output_path + 'Dev2_' + date_str[8:], dev2_data)

            sum_data = dev1_data[0] + dev1_data[1] + dev1_data[2] + dev2_data[0] + dev2_data[1] + dev2_data[2]
            bins_num=np.linspace(0,86400,3600*500*24+1,dtype=np.float64)
            bgo, bins = np.histogram(sum_data, bins_num)
            
            for i in range(len(bgo)):
                if bgo[i] > 500:
                    bgo[i] = 0
            
            
            non_zero = np.where(bgo != 0)
            store = []
            for line in non_zero[0]:
                store.append([line * .002, bgo[line]])
            q = output_path + 'hist_' + date_str[8:]
            np.save(q, store)
            
            del bgo, bins, store, non_zero, dev1_data, dev2_data
            


        loop_day = loop_day + timedelta(1)

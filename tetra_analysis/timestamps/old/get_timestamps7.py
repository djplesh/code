# -*- coding: utf-8 -*-
"""
Created on Fri Jun 24 18:21:15 2016

-reads in all TETRAII files for a single day and saves two files
    one file for each device containing each ctr converted to timestamps
-uses ctr1 files to find pps and determine clock
-uses clock to convert counters into times
-finds ctr2 and ctr3 ungated rates
-finds ctr1 gated rates

remember: the bgo for each ctr1 cannot give a good rate estimate
    should be gated with 13usec delay
modified date handling
removed creation of hist.py 

@author: DJ Pleshinger
"""

import ctr_to_timestamp3 as get
import tetra_tools.tools as tool

import os
import numpy as np
from datetime import date
from datetime import timedelta
from datetime import datetime
import time


##############################################################################
def trim_lists(file_list):
    """used to collect only matching files if there are different number
    of files in each folder for a given day
    """

    ctr1_file_path = file_list[0][0][:file_list[0][0].rfind('\\')]
    ctr2_file_path = file_list[1][0][:file_list[1][0].rfind('\\')]
    ctr3_file_path = file_list[2][0][:file_list[2][0].rfind('\\')]

    new_list = np.intersect1d(np.intersect1d(np.intersect1d( \
                    np.array([s.split("\\")[-1] for s in file_list[0]]), \
                    np.array([s.split("\\")[-1] for s in file_list[1]])), \
                    np.array([s.split("\\")[-1] for s in file_list[2]])))
    file_list = [[],[],[],[]]

    for line in new_list:
        file_list[0].append(ctr1_file_path + '/'  +line)
        file_list[1].append(ctr2_file_path + '/' + line)
        file_list[2].append(ctr3_file_path + '/' + line)
    num_files = len(new_list)
    return file_list, num_files


def check_cals(date_str, box_num):
    """check to make sure calibrations were not done on the day of interest"""

    x = None
    loc = tool.loc_name(box_num)
    cal_file_dates = 'C:/Users/tetra/calibrations/' + loc + '/cal_dates.txt'
    with open(cal_file_dates) as infile:
        for line in infile:
            if line[0:10] == date_str[0:10]:
                x = True
                return x
    return x


##############################################################################
def get_data(dev, d, path0):
    """runs for a given device to convert the ctr data to timestamps"""
    x = True
    data_full = [[],[],[]]
    file_type = ['ctr1', 'ctr2', 'ctr3']
#   get file lists and check number of each
    path = path0 + dev + '/'
    file_list = [[],[],[],[]]
    for i in range(3):
        file_list[i] = get.day_files(path, file_type[i], d)
    if len(file_list[0]) == len(file_list[1]) == len(file_list[2]):
        num_files = len(file_list[0])
    else:
        file_list, num_files = trim_lists(file_list)
    if num_files == 0:
        return False
#   begin looping thru files
    for i in range(num_files):
#        check for gps lock
        try:
            gps_test = file_list[0][i][file_list[0][i].rfind('/'):]
            if len(gps_test) < 60:
                continue
            
            # gps_lock = True
            # for j in range(3):
                # file_name = file_list[j][i][file_list[j][i].rfind('/'):]
                # if len(file_name) < 60:
                    # gps_lock = None
                    # break
            # if  not gps_lock: continue
            
    #        get pps and clks, check for length of ctr1
            pps_idx, pps_ctr1, clks = get.get_pps(file_list[0][i])
            if not pps_idx or pps_idx == []: continue
    #       get data and convert to times
            dev_data = [[],[],[]]
            for j in range(3):
                dev_data[j].extend(get.get_times(file_list[j][i], pps_ctr1, clks, i))
            idx, bgo1 = get.get_idx(dev_data, pps_idx)
            idx = np.array(idx)
            if (idx == 2).sum() == 0: dev_data[1] = []
            if (idx == 3).sum() == 0: dev_data[2] = []
            data_full[0].extend(bgo1)
            data_full[1].extend(dev_data[1])
            data_full[2].extend(dev_data[2])

        except NameError as e:
                with open('C:/Users/tetra/errors.txt', 'a') as f:
                    f.write(str(e) + ': ' + file_list[0][i] + '\n')
                x = False
    if not x:
        return False
    return data_full


def run_data(d, box_num):
    """for a given day and box, create npz files for each bgo timestamps and 
    hist the data in 2ms timebins
    """
    path0 = 'E:/' + box_num + '/'
    output_path = 'Y:/' + box_num + '/' + d.strftime("%Y_%m") + '/'
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    output_file = output_path + 'ts_' + d.strftime("%d")
    if not os.path.isfile(output_file + '.npz'):

        cal = check_cals(d.strftime("%Y_%m_%d"), box_num)
        if not cal:
            path = path0 + d.strftime("%Y_%m") + '/'

            #added this if statement to deal with 2016 data not in month folders
            if d.year == 2016 and d.month != 8 and box_num[:3] == 'LSU':
                path = path0
            if d.year == 2016 and d.month != 9 and box_num[:2] == 'PR':
                path = path0
            if d.year == 2016 and box_num[:3] == 'UAH':
                path = path0
            try:
                dev1_data = get_data('Dev1', d, path)
                if not dev1_data:
                        with open('C:/Users/tetra/errors.txt', 'a') as f:
                            f.write(str(d) + ' Dev1' + '\n' + '\n')
                dev2_data = get_data('Dev2', d, path)
                if not dev2_data:
                        with open('C:/Users/tetra/errors.txt', 'a') as f:
                            f.write(str(d) + ' Dev2' + '\n' + '\n')
                bgo4 = np.array(dev1_data[0])
                bgo5 = np.array(dev1_data[1])
                bgo6 = np.array(dev1_data[2])
                bgo1 = np.array(dev2_data[0])
                bgo2 = np.array(dev2_data[1])
                bgo3 = np.array(dev2_data[2])

                if len(dev1_data[0]) > 0 or len(dev2_data[0]) > 0:
                    np.savez(output_file, bgo1=bgo1, bgo2=bgo2, bgo3=bgo3, bgo4=bgo4, bgo5=bgo5, bgo6=bgo6)
            except IndexError as e:
                with open('C:/Users/tetra/errors.txt', 'a') as f:
                    f.write(box_num + ' ' + str(d) + ': ' + str(e) + '\n')


##############################################################################
def loop_days(box_num, start_date, end_date = None):
    """call run_data for a box and a range of dates
    give dates as dt.date objects
    """
    # start_time = time.time()
    if end_date == None: 
        end_date = start_date
    else:
        end_date = datetime.strptime(end_date, "%Y_%m_%d")

    while start_date < end_date + timedelta(1):
        x = run_data(start_date, box_num)
        start_date = start_date + timedelta(1)


def loop_boxes(boxes = 'all', start_date = 'yesterday', end_date = None):
    """call run_data for a set of boxes and a range of dates
    give dates as strings YYYY_MM_DD
    """
    boxes = tool.box_list(boxes)
    if start_date == 'yesterday':
        start_date = date.today() - timedelta(1)
    else:
        start_date = datetime.strptime(start_date, "%Y_%m_%d")
           
    for box in boxes:
        loop_days(box, start_date, end_date)


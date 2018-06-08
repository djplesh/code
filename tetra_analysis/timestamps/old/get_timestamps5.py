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
def get_data(dev, loop_day, path0):
    """runs for a given device to convert the ctr data to timestamps"""
    x = True
    data_full = [[],[],[]]
    file_type = ['ctr1', 'ctr2', 'ctr3', 'analog']
#   get file lists and check number of each
    path = path0 + dev + '/'
    file_list = [[],[],[],[]]
    for i in range(4):
        file_list[i] = get.day_files(path, file_type[i], loop_day)
    if len(file_list[0]) == len(file_list[1]) == len(file_list[2]) == len(file_list[3]):
        num_files = len(file_list[0])
    else:
        file_list, num_files = trim_lists(file_list)
    if num_files == 0:
        return False
#   begin looping thru files
    for i in range(num_files):
#        check for gps lock
        try:
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
            try:
                ctr1_data = get.get_ctr(file_list[0][i])
                if len(ctr1_data) < 100:
                    continue
            except IndexError:
                continue
            del ctr1_data
    #        get pps and clks
            pps_idx, pps_ctr1, clks = get.get_pps(file_list[0][i])
            if not pps_idx: continue
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


def run_data(loop_day, loc, box_num, path0):
    """for a given day and box, create npz files for each bgo timestamps and 
    hist the data in 2ms timebins
    """
    
    date_str = tool.ints_to_date(loop_day.day, loop_day.month, loop_day.year)
    folder = date_str[:4] + '_' + date_str[5:7] + '/'
    output_path = 'Y:/' + box_num + '/' + folder
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    if not os.path.isfile(output_path + 'histb_' + date_str[8:] + '.npz'):

        cal = check_cals(date_str, box_num)
        if not cal:
            path = path0 + folder

            #added this if statement to deal with 2016 data not in month folders
            if loop_day.year == 2016 and loop_day.month != 8 and loc == 'LSU':
                path = path0
            if loop_day.year == 2016 and loop_day.month != 9 and loc == 'PR':
                path = path0
            if loop_day.year == 2016 and loc == 'UAH':
                path = path0
            try:
                dev1_data = get_data('Dev1', loop_day, path)
                if not dev1_data:
                        with open('C:/Users/tetra/errors.txt', 'a') as f:
                            f.write(date_str + ' Dev1' + '\n' + '\n')
                            return False

                dev2_data = get_data('Dev2', loop_day, path)
                if not dev2_data:
                        with open('C:/Users/tetra/errors.txt', 'a') as f:
                            f.write(date_str + ' Dev2' + '\n' + '\n')
                            return False

                bgo4 = np.array(dev1_data[0])
                bgo5 = np.array(dev1_data[1])
                bgo6 = np.array(dev1_data[2])
                bgo1 = np.array(dev2_data[0])
                bgo2 = np.array(dev2_data[1])
                bgo3 = np.array(dev2_data[2])

                file_ts = output_path + 'ts_' + date_str[8:10]
                if len(dev1_data[0]) > 0 or len(dev2_data[0]) > 0:
                    np.savez(file_ts, bgo1=bgo1, bgo2=bgo2, bgo3=bgo3, bgo4=bgo4, bgo5=bgo5, bgo6=bgo6)

            except IndexError as e:
                with open('C:/Users/tetra/errors.txt', 'a') as f:
                    f.write(box_num + ' ' + date_str + ': ' + str(e) + '\n')
                    loop_day = loop_day + timedelta(1)
                    return False

        else:
            # dev1_data = 'calibration day'
            # dev2_data = 'calibration day'
            return
        if len(dev2_data[0]) > 0 or len(dev1_data[0]) > 0:
            sum_data = dev1_data[0] + dev1_data[1] + dev1_data[2] + dev2_data[0] + dev2_data[1] + dev2_data[2]
            bgo, bins0 = np.histogram(sum_data, 43200000, (0, 86400))
            non_zero = np.where(bgo != 0)
            bins = []
            counts = []
            for line in non_zero[0]:
                if bgo[line] < 500: #deals with noisy bins with ~900 counts
                    bins.append(np.int32(line))
                    counts.append(np.int16(bgo[line]))
            bins = np.array(bins)
            counts = np.array(counts)
            new_hist = output_path + 'hist_' + date_str[8:10]
            np.savez(new_hist, bins=bins, counts=counts)
    return True

##############################################################################
def loop_days(box_num, start_date, end_date = None):
    """call run_data for a box and a range of dates
    """
    # start_time = time.time()
    if end_date == None or end_date == '': end_date = start_date
    path0 = 'E:/' + box_num + '/'
    start_day, start_month, start_year = tool.date_to_ints(start_date)
    end_day, end_month, end_year = tool.date_to_ints(end_date)
    loop_day = date(start_year, start_month, start_day)
    loop_end = date(end_year, end_month, end_day)
    loc = tool.loc_name(box_num)

    while loop_day < loop_end + timedelta(1):
        x = run_data(loop_day, loc, box_num, path0)
        loop_day = loop_day + timedelta(1)


def loop_boxes(box_list = None, start_date = 'yesterday', end_date = None):
    """call run_data for a set of boxes and a range of dates
    """
    lsu = ['LSU_01', 'LSU_02']
    pan = ['PAN_01', 'PAN_02', 'PAN_03', 'PAN_04', 'PAN_05']
    pr = ['PR_01', 'PR_02', 'PR_03', 'PR_04', 'PR_05', 'PR_06', 'PR_07',
        'PR_08', 'PR_09', 'PR_10']
    uah = ['UAH_01', 'UAH_02']
    if box_list == None or box_list == '':
        box_list = lsu + pan + pr + uah
    if box_list == 'LSU':
        box_list = lsu
    if box_list == 'PAN':
        box_list = pan
    if box_list == 'PR':
        box_list = pr
    if box_list == 'UAH':
        box_list = uah

    if start_date == 'yesterday':
        yest = datetime.today() - timedelta(1)
        start_date = str(yest.year) + '_' + str(tool.fix_num(yest.month)) + '_' + str(tool.fix_num(yest.day))
    
    for box_num in box_list:
        loop_days(box_num, start_date, end_date)


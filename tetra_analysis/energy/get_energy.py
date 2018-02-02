# -*- coding: utf-8 -*-
"""
Created on Tue Jan 24 14:46:55 2017

make energy plots from single file from a day

needs work

@author: DJ Pleshinger
"""


import numpy as np
import datetime
import numpy.ma as ma

import tetra_analysis.timestamps.ctr_to_timestamp3 as get
from tetra_tools.pyTDMS4 import read
import tools as tool
from numba import jit
from scipy.stats.mstats import gmean
import csv
##############################################################################
def get_pmt(file_name,pmt):
    """read in the data for a specific column in the analog file"""
    
    if pmt == 'gps': pmt = 6
    data_raw=read(file_name)
    keys1=data_raw[1].keys()
    for key in keys1:
        if str(key[-2]) == str(pmt):
            data=data_raw[1].get(key)
    return data

def get_gmean(pmt_a, pmt_b):     
    """take geometric mean of each pair in two lists"""
    
    bgo = []
    for i in range(len(pmt_a) - 1):
        pmts = []
        if pmt_a[i] > 0 and pmt_b[i] > 0:
            pmts.append(pmt_a[i])
            pmts.append(pmt_b[i])
            bgo.append(gmean(pmts))            
    return bgo
    
def get_analog(filename):
    
    adc_data = [[],[],[],[],[],[],[]]
    for i in range(7):
        adc_data[i] = get_pmt(filename, i)
    pmts = [list(a) for a in zip(adc_data[0], adc_data[1], adc_data[2], adc_data[3], adc_data[4], adc_data[5])]
    gps_adc = adc_data[6]
    return pmts, gps_adc
        


#@jit(nopython=True)
def get_match(ctr1, ctr2, ctr3, ctr1_pps_idx):

    ctr1 = np.array(ctr1)
    ctr2 = np.array(ctr2)
    ctr3 = np.array(ctr3)
    idx = np.zeros(len(ctr1))
    j = 0
    count = 0
    for line in ctr1:
        if count == ctr1_pps_idx[j]:
            idx[count] = 9
            j = j + 1
            if j > len(ctr1_pps_idx) - 1:
                j = j - 1
            count = count + 1
            continue
        ctr2_diff = np.abs(ctr2 - line)
        ctr3_diff = np.abs(ctr3 - line)        
        ctr2_matches = np.where(ctr2_diff <= 0.0000002)[0]
        ctr3_matches = np.where(ctr3_diff <= 0.0000002)[0]
        n2_matches = len(ctr2_matches)
        n3_matches = len(ctr3_matches)
        if n2_matches == n3_matches == 1:
            idx[count] = 23
        elif n2_matches != 0:
            idx[count] = 2
        elif n3_matches != 0:
            idx[count] = 3
        elif n2_matches == n3_matches == 0:
            idx[count] = 1
        count = count + 1
    idx = np.array(idx)
    return idx
    
    

def get_times2(files):
    ctr_times = [[], [], []]
    pps_idx, pps_ctr1, clks = get.get_pps(files[0])
    ctr_times[1] = get.get_times(files[1], pps_ctr1, clks, 1)
    ctr_times[2] = get.get_times(files[2], pps_ctr1, clks, 1)
    ctr_times[0] = get.get_times(files[0], pps_ctr1, clks, 1)
    ctr1_clean = []
    ctr1_clean.append(ctr_times[0][0])
    for i in range(1,len(ctr_times[0])):
        if ctr_times[0][i] - ctr1_clean[-1] > .000013:
            ctr1_clean.append(ctr_times[0][i])
    # print len(ctr1_clean)
    # print len(ctr_times[0])
    ctr_times[0] = ctr1_clean
    return ctr_times, pps_idx


def get_filename(path0, date_str, time_sec, dev):
    files = []

    d, m, y = tool.date_to_ints(date_str)
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
                file_time = 3600*int(file_time[0:2]) + 60*int(file_time[2:4]) \
                + int(file_time[4:6])
            except ValueError as e:
                continue
            if file_time < time_sec:
                good_file = f
            else:
                break
        files.append(good_file)

    return files
###############################################################################
###############################################################################    
'''    
def comp(filenames):


    gps = get_pmt(filenames[3], 'gps')
    gps_pos = np.where(np.array(gps) > 2500)
    gps_new = gps[gps_pos[0][0]:]
    gps_new_pos = np.where(np.array(gps_new) > 2500)

    
    pos, pps_ctrs, clks = get.get_pps(filenames[0])
    ctr1_times = get.get_times(filenames[0], pps_ctrs, clks, 1)
    ctr1_times_new = ctr1_times[pos[0]:]
    
    times_clean = np.array(ctr1_times_new)
    
    test1 = []
    for x in range(len(pos)):
        test1.append(np.where(times_clean == ctr1_times[pos[x]]))
    clean_pos=[]
    for x in test1:
        clean_pos.append(x[0][0])
    clean_pos2 = clean_pos[:-1]
    
    gps_pos = np.array(gps_pos)
    gps_new_pos = np.array(gps_new_pos[0])

    if len(clean_pos2) != len(gps_new_pos):
        clean_pos2 = clean_pos2[:599]
        gps_new_pos = gps_new_pos[:599]
    diff2 = clean_pos2 - gps_new_pos
    
    return  diff2 #this is the difference between pps in ctr1 and analog if both files start at first pps
    
    
def align(diff, c1times, adc_file, pps_idx, idx):
    
    pmts, gps_adc = get_analog(adc_file)
    gps_pos = np.where(np.array(gps_adc) > 2500)
    gps_new = gps_adc[gps_pos[0][0]:]
    pmts_new = pmts[gps_pos[0][0]:]
    gps_new_pos = np.where(np.array(gps_new) > 2500)[0]
    
    c1times = c1times[pps_idx[0]:]
    idx = idx[pps_idx[0]:]
    pps_idx = np.array(pps_idx) - pps_idx[0]
    idx = idx.tolist()
    

    #mpmts = ma.array(pmts_new, mask = [0 for i in range(len(pmts_new))])
    mpmts = ma.array(pmts_new, mask = False)
    midx = ma.array(idx, mask = [0 for i in range(len(idx))])
    mtimes = ma.array(c1times, mask = [0 for i in range(len(c1times))])
    mgps = ma.array(gps_new, mask = [0 for i in range(len(gps_new))])
    
    c = 0
    d = 0
    for i in range(len(diff)):
        if diff[i] == c:
            continue
        c = diff[i]
        d = c - d

        mtimes[pps_idx[i-1]+1:pps_idx[i]] = ma.masked
        midx[pps_idx[i-1]+1:pps_idx[i]] = ma.masked
        
        mgps[gps_new_pos[i-1]+1:gps_new_pos[i]] = ma.masked
        mpmts[gps_new_pos[i-1]+1:gps_new_pos[i]] = ma.masked
        
    c1times = mtimes.compressed()
    idx = midx.compressed()
    gps_new = mgps.compressed()
    pmts_new = mpmts.compressed()
    
    pmts_new = np.reshape(pmts_new,(len(pmts_new)/6,6))
    
    c1times = c1times[:len(gps_new)]
    idx = idx[:len(gps_new)]
    return c1times, pmts_new, gps_new, idx
    
def event_info(d, event_time, duration):

    event_ts = np.where(np.abs(np.array(d[0]) - (event_time + duration)) <= .005)[0]
    
    if len(event_ts) != 0:
        min_ts = event_ts[0]
        max_ts = event_ts[-1]+1
        
        d_new = [d[0][min_ts:max_ts], d[1][min_ts:max_ts], d[2][min_ts:max_ts], d[3][min_ts:max_ts]]
    else:
        d_new = [0]
    return d_new
'''
###############################################################################    
###############################################################################
    
def trim(c1times, adc_file, pps_idx, idx, event_time, duration, box_num, dev):

    pmts, gps_adc = get_analog(adc_file)
    gps_pos = np.where(np.array(gps_adc) > 2500)
    gps_new = gps_adc[gps_pos[0][0]:]
    pmts_new = pmts[gps_pos[0][0]:]
    gps_new_pos = np.where(np.array(gps_new) > 2500)[0]
    c1times = c1times[pps_idx[0]:]
    idx = idx[pps_idx[0]:]
    pps_idx = np.array(pps_idx) - pps_idx[0]
    idx = idx.tolist()
    
    x = np.where(np.array(c1times) == np.floor(event_time))[0][0]
    second_in_file = int(c1times[x] - c1times[0]) #number of seconds passed in file, use to find pps in analog
    y = np.where(np.array(c1times) == np.ceil(event_time))[0][0]
    c1times = c1times[x:y+1]
    idx = idx[x:y+1]
    
        
    gps_new_pos = gps_new_pos[second_in_file:second_in_file+2]
    
    pmts_new = pmts_new[gps_new_pos[0]:gps_new_pos[1]+1]
    gps_new = gps_new[gps_new_pos[0]:gps_new_pos[1]+1]


    c = 0
    event_times = []
    event_idx = []
    event_pmts = []
    event_gps = []
    #print event_time
    for t in c1times:
        #print t
        if t < (event_time + duration) and t > (event_time):
            event_times.append(t)
            event_idx.append(idx[c])
            event_pmts.append(pmts_new[c])
            event_gps.append(gps_new[c])
            c0 = c + 1
        c = c + 1
    for x in range(len(pmts_new) - len(c1times)):
        event_pmts.append(pmts_new[c0])
        event_gps.append(gps_new[c0])
        c0 = c0 + 1

    event = [event_times, event_idx, event_pmts, event_gps]
    trig = trigs(event[0], event[1], event[2], box_num, dev)
    return trig
    
    
def trigs(times, idx, pmts, box_num, dev):
    
    c = 0
    trig_times = []
    trig_pmts = []
    trig_idx = []  #eliminate gps index
    for x in idx:
        if x == 1:
            trig_pmts.append([pmts[c][0], pmts[c][1]])
        if x == 2:
            trig_pmts.append([pmts[c][2], pmts[c][3]])
        if x == 3:
            trig_pmts.append([pmts[c][4], pmts[c][5]])
        if x == 23:
            trig_pmts.append([pmts[c][2], pmts[c][3]])
            trig_pmts.append([pmts[c][4], pmts[c][5]])
        if x != 9 and x != 23:
            trig_idx.append(x)
            trig_times.append(times[c])
        if x != 9 and x == 23:
            trig_idx.append(2.0)
            trig_idx.append(3.0)
            trig_times.append(times[c])
            trig_times.append(times[c])
        c = c + 1
    trig_bgo = adc_to_energy(trig_pmts, box_num, trig_idx, dev)
    trig = [trig_times, trig_idx, trig_bgo]
    return trig

def get_cals():

    slopes = []
    y_ints = []
    cal_file = 'C:/Users/tetra/calibrations/cal_eqns.csv'
    with open(cal_file, 'r') as infile:
        for line in infile:
            csv_input = csv.reader(infile, delimiter = ',')
            for cols in csv_input:
                slopes.append(float(cols[0]))
                y_ints.append(float(cols[1]))
    return slopes, y_ints
    
    
def adc_to_energy(pmts, box_num, idx, dev):

    # bgo = []
    # for p in pmts:
        # bgo.append(gmean(p))
    # return bgo
    
    g = lambda x: m*x + b
    
    lookup = {'LSU_01':0, 'LSU_02':1, 'PAN_01':2, 'PAN_02':3, 'PAN_03':4, 'PAN_04':5, 'PAN_05':6,
    'PR_01':7, 'PR_02':8, 'PR_03':9, 'PR_04':10, 'PR_05':11, 'PR_06':12, 'PR_07':13,
    'PR_08':14, 'PR_09':15, 'PR_10':16, 'UAH_01':17, 'UAH_18':18}
    box = lookup[box_num]
    
    if dev == 'Dev1':
        lookup_idx = {1:0, 2:1, 3:2}
    if dev == 'Dev2':
        lookup_idx = {1:3, 2:4, 3:5}
    
    f = np.zeros(shape = (19, 6, 2))
        
    slopes, y_ints = get_cals()


    c = 0
    for i in range(19):
        for j in range(6):
            f[i][j][0] = slopes[c]
            f[i][j][1] = y_ints[c]
            c = c + 1
    bgo = []
    c = 0
    for x in idx:

        m = f[box][lookup_idx[x]][0]
        b = f[box][lookup_idx[x]][1]
        pmt1 = g(pmts[c][0])
        pmt2 = g(pmts[c][1])
        bgo.append(gmean([pmt1,pmt2]))
        c = c + 1
    return bgo
##############################################################################
##############################################################################
##############################################################################


def energy(box_num, date_str, time_sec, duration, path0=None):
    #to do:
    #get file lists for that day, pick out correct one based on time
    if not path0: path0 = 'E:/' + box_num + '/'
    folder = date_str[:4] + '_' + date_str[5:7] + '/'
    path = path0 + folder
    
    try:
        d1_files = get_filename(path, date_str, time_sec, 'Dev1')
        d1_times, pps_idx1 = get_times2(d1_files)
        idx1 = get_match(d1_times[0], d1_times[1], d1_times[2], pps_idx1)
        d1_event = trim(d1_times[0], d1_files[3], pps_idx1, idx1, time_sec, duration, box_num, 'Dev1')
    except IndexError as e:
        d1_event = [[],[],[]]
    
    try:
        d2_files = get_filename(path, date_str, time_sec, 'Dev2')
        d2_times, pps_idx2 = get_times2(d2_files)
        idx2 = get_match(d2_times[0], d2_times[1], d2_times[2], pps_idx2)
        d2_event = trim(d2_times[0], d2_files[3], pps_idx2, idx2, time_sec, duration, box_num, 'Dev2')
    except IndexError as e:
        d2_event = [[],[],[]]

    
    event = []
    c = 0
    for x in d1_event[1]:
        if x == 1.0:
            d1_event[1][c] = 4.0
        if x == 2.0:
            d1_event[1][c] = 5.0
        if x == 3.0:
            d1_event[1][c] = 6.0
        c = c + 1
    event = [d1_event[0] + d2_event[0], d1_event[1] + d2_event[1], d1_event[2] + d2_event[2]]
    #dev1_diff = comp(dev1_files)
    #dev2_diff = comp(dev2_files)
    #d1t, d1p, d1g, d1i = align(dev1_diff, dev1_times[0], dev1_files[3], pps_idx1, idx1)
    #d2t, d2p, d2g, d2i = align(dev2_diff, dev2_times[0], dev2_files[3], pps_idx2, idx2)
    #dev1 = [d1t, d1p, d1g, d1i]
    #dev2 = [d2t, d2p, d2g, d2i]
    #return dev1, dev2
    #dev1_event = event_info(dev1, time_sec, duration)
    #dev2_event = event_info(dev2, time_sec, duration)
    return event
    return d1_event, d2_event




    
def loop_energy(box_list, date_str, time_sec, duration, path0=None):

    boxes = [list() for _ in range(len(box_list))]
    
    b = 0
    for box in box_list:
        boxes[b] = energy(box, date_str, time_sec, duration, path0)
        b = b + 1
    return boxes
    













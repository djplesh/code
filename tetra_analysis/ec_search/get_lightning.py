# -*- coding: utf-8 -*-
"""
Created on Thu Mar 02 14:44:56 2017

searches specified lightning set for strikes within 8km and 5sec
can read in USPLN, WWLLN, ENTLN, or NLDN(text file from Huntsville)

@author: DJ Pleshinger
"""

from geopy.distance import vincenty 
import os
import datetime
import numpy as np
import gzip
import csv

import tetra_tools.tools as tool


def next_day(date):    
    """from date in string get string for next day, format yyyy_mm_dd"""
    
    tom = datetime.datetime(int(date[0:4]), int(date[5:7]), int(date[8:10])) \
    + datetime.timedelta(1)  
    date_s = str(tom.year) + '_' + tool.fix_num(tom.month) + '_' + tool.fix_num(tom.day)    
    return date_s


def det_location(location):
    '''get location of detector'''
    
    if location == 'LSU':
        det_pos = [30.412603, -91.178733]
    elif location == 'PR':
        det_pos = [18.254166, -66.721110]
    elif location == 'PAN':
        det_pos = [9.000914, -79.584843]
    elif location == 'UAH':
        det_pos = [34.725031, -86.646313]    
    return det_pos
   

def get_dists(lats, lons, det_pos):
    
    lats = [float(i) for i in lats]
    lons = [float(i) for i in lons]
    dists = []

    c = 0
    for i in range(0, len(lats)):
        pos=[lats[c], lons[c]]
        try:
            dists.append(vincenty(pos, det_pos).km)
        except ValueError:
            c = c + 1 
            continue
        c = c + 1  
    del lats, lons
    return dists

def wwlln_dists(lats, lons, times):
    
    lats = [float(i) for i in lats]
    lons = [float(i) for i in lons]
    locs = [det_location('LSU'), det_location('PAN'), det_location('PR'), det_location('UAH')]
    strikes = [[], [], [], []]
    
    c = 0
    for i in range(0, len(times)):
        pos=[lats[c], lons[c]]
        try:
            for i in range(4):
                d = vincenty(pos, locs[i]).km
                if d < 8:
                    strikes[i].append([times[c], lats[c], lons[c]])
        except ValueError:
            c = c + 1 
            continue
        c = c + 1  
    del lats, lons
    return strikes   
    

def get_times(times_str):
    times = []
    for line in times_str:
        h, m, s = line.split(':')
        x = int(h)*3600 + int(m)*60 + float(s)
        times.append(x)
    
    return times
    

###############################################################
###############################################################


def uspln(date, loc):
    
    det_pos = det_location(loc)
    if date[0:4] == '2016':
        path0 = 'C:/Users/tetra/lightning/USPLN/' + loc + '/2016/' + date + '/'
    else:
        path0 = 'C:/Users/tetra/lightning/USPLN/' + loc + '/' + date + '/'
    if not os.path.exists(path0):
        return None
    file_list = tool.path_files(path0)
    
    date2 = next_day(date)
    if date2[0:4] == '2016':
        path1 = 'C:/Users/tetra/lightning/USPLN/' + loc +'/2016/' + date2 + '/'
    else:
        path1 = 'C:/Users/tetra/lightning/USPLN/' + loc + '/' + date2 + '/'
    if not os.path.exists(path1):
        return None
    file_list.extend(tool.path_files(path1))
      
    strikes = []
    for file in file_list:
        with open(file) as infile:
            next(infile)
            for line in infile:
                if line[5:7] == date[5:7] and line[8:10] == date[8:10]:
                    strikes.append(line)
    
    lats = []
    lons = []
    times_str = []
    for line in strikes:      
        lats.append(line.split(',')[1])
        lons.append(line.split(',')[2])
        times_str.append(line[11:23])
    dists = get_dists(lats, lons, det_pos)
    times = get_times(times_str)
    strikes = [times, dists]    
    
    return strikes
    
    
def entln(date, loc):

    folder = 'C:/Users/tetra/lightning/ENTLN/' + loc + '/'
    date_int = int(date[0:4] + date[5:7] + date[8:10])
    date_str = date[0:4] + '-' + date[5:7] + '-' + date[8:10]
    det_pos = det_location(loc)
    
    #include this due to filename change after March 2017
 
    
    lats = []
    lons = []
    times_str = []

    for f in os.listdir(folder):
        print f
        if date_int > int(f[0:8]) and date_int < int(f[12:20]):
            filename = folder + f
            with open(filename, 'rb') as infile:
                temp = csv.reader(infile)
                for row in temp:
                    if row[1] == 'timestamp':
                        continue
                    if row[1][0:10] == date_str:
                        lats.append(row[2])
                        lons.append(row[3])
                        times_str.append(row[1][11:])
                        
    dists = get_dists(lats, lons, det_pos)
    times = get_times(times_str)
    strikes = [times, dists]             
    return strikes
    

def wwlln(date, loc):

    filename0 = 'C:/Users/tetra/lightning/WWLLN/'
    folder = date[0:4] + '_' + date[5:7]
    date_str = date[0:4] + date[5:7] + date[8:10]
    filename = filename0 + folder + '/AE' + date_str + '.loc'
    if not os.path.isfile(filename):
        filename = filename0 + folder + '/A' + date_str + '.loc'
    if not os.path.isfile(filename):
        return None
    det_pos = det_location(loc)
    
    try:
        f = open(filename)
    except NameError:
        return None
    except IOError:
        return None
    strikes_raw = []
    for line in f:
        strikes_raw.append(line)
    f.close()
    
    lats = []
    lons = []
    times_str = []
    for s in strikes_raw:
        lats.append(float(s.split(',')[2]))
        lons.append(float(s.split(',')[3]))
        times_str.append(s.split(',')[1])
    dists = get_dists(lats, lons, det_pos)
    times = get_times(times_str)
    strikes = [times, dists]
    return strikes



def nldn_text(date, loc, event_time):
    """NEEDS WORK TO CLEAN UP, DEPENDS ON HOW TEXT FILE IS ORGANIZED"""
    det_pos = det_location(loc) 
    path0='C:/Users/tetra/NLDN/' + loc + '/lightning/nldn/' + date + '/'
    file_list = tool.path_files(path0, 'lightning')
    
    dates = []
    times_str = []
    lats = []
    lons = []
    for file in file_list:
        with open(file) as infile:
            for line in infile:
                dates.append(line.split()[0])
                times_str.append(line.split()[1])
                lats.append(line.split()[2])
                lons.append(line.split()[3])
    dists = get_dists(lats,lons,det_pos)
    times=get_times(times_str)
    strikes = [times, dists]   
    return strikes


###############################################################
###############################################################

def nearby_strikes(loc, date, source, number = None):
    """returns a list of timestamps in seconds for a day of lightning strikes
    within 8kms of an array location
    If number is set to True, will return the number of nearby and total strikes
    """

    if source == 'wwlln':
        strikes = wwlln(date, loc)
        
    if source == 'entln':
        strikes = entln(date, loc)
        
    if loc == 'LSU' and source == 'uspln':
        strikes = uspln(date, loc)
    if strikes == None:
        strikes_8km =[]
        strikes = []
        return strikes_8km, strikes
    strikes_8km = []
    for i in range(len(strikes[1])):
        if strikes[1][i] < 8:
            strikes_8km.append(strikes[0][i])
    if number:
        return len(strikes_8km), len(strikes[0])
    return strikes_8km, strikes


def recent_strikes(strikes_8km, strikes_all, time_sec, time_window=5):
    """returns a list of timestamps and distances for lightning strikes from list
    within 5 seconds of given time
    modified, now searches for strikes in time_window of seconds, default is 5
    """
    strikes_8km = np.array(strikes_8km)
   
    strikes_8km_5s = []
    for s in strikes_8km:
        if np.abs(s-time_sec) < time_window:
            strikes_8km_5s.append(s)
    strike_dist = []
    for s in strikes_8km_5s:
        x = np.where(strikes_all[0] == s)
        y = x[0][0]
        strike_dist.append(strikes_all[1][y]) 
    
    return strikes_8km_5s, strike_dist


def find_strikes(box_num, date, time_sec, source = 'wwlln'):
    """calls both nearby and recent strikes"""
    
    loc = tool.loc_name(box_num)
    strikes_8km, strikes_all = nearby_strikes(loc, date, source)
    strikes_8km_5s, strike_dist = recent_strikes(strikes_8km, strikes_all, time_sec)       
    
    return strikes_8km_5s, strike_dist
    
    
def num_strikes(date, duration = 1, locations = None, source = 'both'):
    """print out how many strikes were detected vs how many were nearby for 
    a given date and location from various sources,
    NOTE: WWLLN has strikes worldwide and ENTLN has strikes within some range of location
    """
    if locations == None: locations = ['LSU', 'PAN', 'PR', 'UAH']
    
    start_d = int(date[8:10])
    start_m = int(date[5:7])
    start_y = int(date[0:4])
    start_day = datetime.date(start_y, start_m, start_d)
    
    loop_day = start_day
    n = duration/np.abs(duration)
    
    for loop_day in [loop_day + datetime.timedelta(x) for x in range(0, duration, n)]:
        
        for loc in locations:
            date = tool.ints_to_date(loop_day.day, loop_day.month, loop_day.year)
            print '\n' + loc + ' on ' + date
            if source == 'both' or source == 'wwlln':
                nearby, total = nearby_strikes(loc, date, 'wwlln')
                if len(total) > 0:
                    print str(len(nearby)) + ' out of ' + str(len(total[0])) + ' WWLLN strikes were within 8km'
                else:
                    print 'no data from WWLLN'
            if source == 'both' or source == 'entln':
                nearby, total = nearby_strikes(loc, date, 'entln')
                if len(total[0]) != 0:
                    print str(len(nearby)) + ' out of ' + str(len(total[0])) + ' ENTLN strikes were within 8km'     
                else:
                    print 'No data from ENTLN'

    


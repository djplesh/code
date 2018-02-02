from geopy.distance import vincenty 
import os
import datetime
import numpy as np
import gzip
import csv

import tetra_tools.tools as tool


def get_times(times_str):
    times = []
    for line in times_str:
        h, m, s = line.split(':')
        x = int(h)*3600 + int(m)*60 + float(s)
        times.append(x)
    times = np.array(times)
    return times

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
    dists = np.array(dists)
    return dists

def wwlln(date, loc):

    filename0 = 'C:/Users/tetra/lightning/WWLLN/'
    folder = date[0:4] + '_' + date[5:7]
    date_str = date[0:4] + date[5:7] + date[8:10]
    filename = filename0 + folder + '/AE' + date_str + '.loc'
    if not os.path.isfile(filename):
        filename = filename0 + folder + '/A' + date_str + '.loc'
    if not os.path.isfile(filename):
        return None
    det_pos = tool.det_location(loc)
    
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
    strikes = [np.array(times), np.array(dists)]
    return strikes
    
def entln(date, loc):

    folder = 'C:/Users/tetra/lightning/ENTLN/' + loc + '/'
    date_int = int(date[0:4] + date[5:7] + date[8:10])
    date_str = date[0:4] + '-' + date[5:7] + '-' + date[8:10]
    det_pos = tool.det_location(loc)
    
    lats = []
    lons = []
    times_str = []
  
    for f in os.listdir(folder):
        if date_int > int(f[0:8]) and date_int < int(f[12:20]):
            filename = folder + f
            with open(filename, 'rb') as infile:
                temp = csv.reader(infile)
                for row in temp:
                    if row[1] == 'timestamp':
                        continue
                    # sp included because in some files there is an extra space 
                    # before the date
                    sp = 0
                    if row[1][0] == ' ': sp = 1
                    if row[1][0 + sp:10 + sp] == date_str:
                        lats.append(row[2])
                        lons.append(row[3])
                        times_str.append(row[1][12:])
    dists = get_dists(lats, lons, det_pos)
    times = get_times(times_str)
    strikes = [np.array(times), np.array(dists)]             
    return strikes
    
    
    
def nearby(loc, date, source):
    """returns a list of timestamps in seconds for a day of lightning strikes
    within 8kms of an array location
    If number is set to True, will return the number of nearby and total strikes
    """

    if source == 'wwlln':
        strikes = wwlln(date, tool.fix_loc(loc))
        
    if source == 'entln':
        strikes = entln(date, tool.fix_loc(loc))
        
    if strikes == None:
        strikes_8km =[]
        strikes = []
        return strikes_8km, strikes
    light_dists = np.array([])
    light_times = np.array([])
    for i in range(len(strikes[1])):
        if strikes[1][i] < 8:
            light_times = np.append(light_times, strikes[0][i])
            light_dists = np.append(light_dists, strikes[1][i])
    strikes_8km = [light_times, light_dists]

    return strikes_8km


def recent(strikes_8km, time_sec, time_window=5):
    """returns a list of timestamps and distances for lightning strikes from list
    within 5 seconds of given time
    modified, now searches for strikes in time_window of seconds, default is 5
    """

    time_diffs = np.abs(strikes_8km[0] - time_sec)
    close_strikes = np.where(time_diffs < time_window)[0]
    ec_strike_times = strikes_8km[0][close_strikes]
    ec_strike_dists = strikes_8km[1][close_strikes]
    
    return ec_strike_times, ec_strike_dists
        
    
    
def lightning_search(loc, date, source, time_sec, time_window=5):

    strikes_8km, strikes_all = nearby(loc, date, source)
    ec_nearby_strikes = recent(strikes_8km, strikes_all, time_sec, time_window)
    
    return ec_nearby_strikes
    
    
    
    
    
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

    for i, j in zip(lats, lons):
        pos=[i, j]
        try:
            dists.append(vincenty(pos, det_pos).km)
        except ValueError:
            continue
    dists = np.array(dists)
    return dists

def boltek(d, loc):
    
    
    fname = d.strftime("%Y%m%d")
    fpath = 'C:/Users/tetra/lightning/BOLTEK/{0}/{1}.txt'.format(loc, fname)
    
    times, xs, ys = [], [], []
    with open(fpath, 'r') as f:
        r = csv.reader(f, delimiter='\t')
        for row in r:
            times.append(float(row[0]))
            xs.append(float(row[1])/1000.)
            ys.append(float(row[2])/1000.)
    dists = np.sqrt(np.array(xs)**2 + np.array(ys)**2)
    strikes = [np.array(times), np.array(dists)]
    return strikes
    
def wwlln(d, loc, nearby=False):

    folder = d.strftime("%Y_%m")
    d_str = d.strftime("%Y%m%d")
    fname = 'C:/Users/tetra/lightning/WWLLN/{0}/AE{1}.loc'.format(folder, d_str)
    if not os.path.isfile(fname):
        fname = 'C:/Users/tetra/lightning/WWLLN/{0}/A{1}.loc'.format(folder, d_str)
    if not os.path.isfile(fname):
        return None
    det_pos = tool.det_location(loc)
    
    try:
        f = open(fname)
    except NameError:
        return None
    except IOError:
        return None
    strikes_raw = []
    for line in f:
        strikes_raw.append(line)
    f.close()
    
    lats, lons, times_str = [], [], []

    for s in strikes_raw:
        lat = float(s.split(',')[2])
        lon = float(s.split(',')[3])
        if np.abs(lat - det_pos[0]) <= 2 and np.abs(lon - det_pos[1]) <= 2:
            lats.append(lat)
            lons.append(lon)
            times_str.append(s.split(',')[1])
    dists = get_dists(lats, lons, det_pos)
    times = get_times(times_str)
    strikes = [np.array(times), np.array(dists)]
    if nearby:
        strikes = get_near(strikes)
        
    return strikes
    
def entln(d, loc, nearby=True):

    folder = 'C:/Users/tetra/lightning/ENTLN/{0}/'.format(loc)
    d_int = int(d.strftime("%Y%m%d"))
    d_str = d.strftime("%Y-%m-%d")
    det_pos = tool.det_location(loc)
    
    lats, lons, times_str = [], [], []

    for f in os.listdir(folder):
        if d_int > int(f[0:8]) and d_int < int(f[12:20]):
            fname = folder + f
            with open(fname, 'rb') as infile:
                temp = csv.reader(infile)
                for row in temp:
                    if row[1] == 'timestamp':
                        continue
                    # sp included because in some files there is an extra space 
                    # before the date
                    sp = 0
                    if row[1][0] == ' ': sp = 1
                    if row[1][0 + sp:10 + sp] == d_str:
                        lats.append(row[2])
                        lons.append(row[3])
                        times_str.append(row[1][11+sp:])
    dists = get_dists(lats, lons, det_pos)
    times = get_times(times_str)
    strikes = [np.array(times), np.array(dists)]

    return strikes


def nearby(loc, d, source):
    """returns a list of timestamps in seconds for a day of lightning strikes
    within 8kms of an array location
    
    d is a datetime object
    """

    if source == 'wwlln': strikes = wwlln(d, tool.fix_loc(loc))
    if source == 'entln': strikes = entln(d, tool.fix_loc(loc))
    if source == 'boltek': strikes = boltek(d, tool.fix_loc(loc))

    
    if strikes == None:
        strikes_8km =[[],[]]
        return strikes_8km

    light_dists, light_times = [], []
    for i in range(len(strikes[1])):
        if strikes[1][i] < 8:
            light_times.append(strikes[0][i])
            light_dists.append(strikes[1][i])
    strikes_8km = [np.array(light_times), np.array(light_dists)]
    return strikes_8km


def recent(strikes_8km, time_sec, time_window=5):
    """returns list of timestamps and distances for lightning strikes from list
    searches for strikes in time_window of seconds, default is 5
    """

    time_diffs = np.abs(strikes_8km[0] - time_sec)
    close_strikes = np.where(time_diffs < time_window)[0]
    ec_strike_times = strikes_8km[0][close_strikes]
    ec_strike_dists = strikes_8km[1][close_strikes]
    
    return ec_strike_times, ec_strike_dists
    
def lightning_search(loc, d, source, time_sec, time_window=5):
    """d is a datetime object"""
    
    strikes_8km, strikes_all = nearby(loc, d, source)
    ec_nearby_strikes = recent(strikes_8km, strikes_all, time_sec, time_window)
    
    return ec_nearby_strikes
    
    
    
    
    
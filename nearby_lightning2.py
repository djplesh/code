# -*- coding: utf-8 -*-
"""
Created on Thu Mar 02 14:44:56 2017

uspln:
this takes in the daily files from uspln here at lsu


lightning_text:
this takes in a text file from P. Bitzer that contains lighting data
pulls out strikes within 5 miles and 5 seconds of chosen time and location
columns of text file are:
date,time,lat,lon,est peak current,(ignore),semimajor axis,semiminor axis, 
axis ratio, angle of ellipse, chi squared, num sensors, type

output has same columns with the distance (in miles) after the lat lon values

@author: DJ Pleshinger
"""

from geopy.distance import vincenty 
import os
import datetime


def fix_num(n):    
    """convert integer to string, add 0 if single digit"""
    
    if n < 10: n_s = '0' + str(n)
    else:
        n_s = str(n)
    return n_s

def next_day(date):    
    """from date in string get string for next day, format yyyy_mm_dd"""
    
    y=int(date[0:4])
    m=int(date[5:7])
    d=int(date[8:10])
    tom = datetime.datetime(y, m, d) + datetime.timedelta(1)
    
    year = tom.year
    year_s = str(year)
    month = tom.month 
    month_s = fix_num(month)
    day = tom.day
    day_s = fix_num(day)        
    date_s = year_s + '_' + month_s + '_' + day_s    
    return date_s

def path_files(path):    
    """select all files in a given path independent of day"""
    
    file_list = []
    for file in os.listdir(path):
        file_list.append(path + file)        
    return file_list

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

def det_location(location):
    '''get location of detector'''
    
    if location == 'lsu':
        lat_box = 30.412603
        lon_box = -91.178733
    elif location == 'pr':
        lat_box = 18.254166
        lon_box = -66.721110
    elif location == 'pan':
        lat_box = 9.000914
        lon_box = -79.584843
#    elif location == 'uah':
#        lat_box = 
#        lon_box =
    det_pos = [lat_box, lon_box]
    
    return det_pos
   

def get_dists(lats,lons,det_pos):
    
    lats = [float(i) for i in lats]
    lons = [float(i) for i in lons]
    dists=[]

    c=0
    for i in range(0,len(lats)):
        pos=[lats[c],lons[c]]
        dists.append(vincenty(pos,det_pos).miles)
        c=c+1  
    del lats,lons
    return dists


def get_times(times_str):
    times=[]
    for line in times_str:
        h, m, s=line.split(':')
        x = int(h)*3600 + int(m)*60 + float(s)
        times.append(x)
    
    return times
    

###############################################################
###############################################################


def uspln(date,array):
    
    det_pos = det_location(array) 
    path0='C:/Users/tetra/data/lightning/lsu/uspln/'+date+'/'
    file_list = path_files(path0)
    
    date2=next_day(date)
    path1='C:/Users/tetra/data/lightning/lsu/uspln/'+date2+'/'
    file_list.extend(path_files(path1))
      
    strikes =[]
    for file in file_list:
        with open(file) as infile:
            next(infile)
            for line in infile:
                if line[5:7]==date[5:7] and line[8:10]==date[8:10]:
                    strikes.append(line)
    
    lats=[]
    lons=[]
    for line in strikes:      
        lats.append(line.split(',')[1])
        lons.append(line.split(',')[2])
    
    dists = get_dists(lats,lons,det_pos)
    
    times_str=[]
    for line in strikes:
        times_str.append(line[11:23])
    times=get_times(times_str)
   
    strikes = [times, dists]       
    return strikes
    
    
###############################################################
###############################################################    



def lightning_text(date,array,event_time):
    det_pos = det_location(array) 
    path0='C:/Users/tetra/array/'+array+'/lightning/nldn/'+date+'/'
    file_list=path_files(path0,'lightning')
    
    dates=[]
    times_str=[]
    lats=[]
    lons=[]
#    misc=[]
    for file in file_list:
        with open(file) as infile:
            for line in infile:
                dates.append(line.split()[0])
                times_str.append(line.split()[1])
                lats.append(line.split()[2])
                lons.append(line.split()[3])
#                misc.append(line.split()[4:])
            
    
    dists = get_dists(lats,lons,det_pos)
            

    times=get_times(times_str)

    
    return dists, times




###############################################################
###############################################################

def nearby_lightning(box_num, date):
    """returns a list of timestamps in seconds for a day of lightning strikes
    within 5 miles of an array location
    """
    array = array_name(box_num)
    if array == 'lsu':
        strikes = uspln(date,array)
        strikes_5mi=[]
        for i in range(len(strikes[1])):
            if strikes[1][i]<5:
                strikes_5mi.append(strikes[0][i])
        return strikes_5mi

    


    



    

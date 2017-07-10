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

import matplotlib.pyplot as plt
from geopy.distance import vincenty 
import numpy as np
from date_info import ints_to_date
from date_info import next_day
from date_info import time_to_seconds

from get_info import path_files



###############################################################
###############################################################  


def det_location(location):
    '''get location of detector'''
    if location == 'lsu':
        lat_box = 30.412603
        lon_box = -91.178733
    elif location =='pr':
        lat_box = 18.254166
        lon_box = -66.721110
    elif location == 'pan':
        lat_box = 9.000914
        lon_box = -79.584843
#    elif location == 'uah':
#        lat_box = 
#        lon_box =
    det_pos=[lat_box,lon_box]
    
    return det_pos

###############################################################
###############################################################    


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

###############################################################
###############################################################


def get_times(times_str):
    times=[]
    for line in times_str:
        hh,mm,ss=line.split(':')
        times.append(time_to_seconds(hh,mm,ss))
    
    return times
    

###############################################################
###############################################################


def uspln(date,array,event_time):
    
    det_pos = det_location(array) 
    path0='C:/Users/tetra/array/lsu/lightning/uspln/'+date+'/'
    file_list = path_files(path0,'lightning')
    
    date2=next_day(date)
    path1='C:/Users/tetra/array/lsu/lightning/uspln/'+date2+'/'
    file_list.extend(path_files(path1,'lightning'))
    
    strikes =[]
    for file in file_list:
        with open(file) as infile:
            c=0
            for line in infile:
                if c > 0 and line[0:4]==date[0:4] and line[5:7]==date[5:7] \
                and line[8:10]==date[8:10]:
                
                    strikes.append(line)
                    c=c+1
                else:
                    c=c+1
    strikes=strikes[1:]
    
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
       

    
    
    
    return dists, times
    
    
    
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

def nearby_lightning(day,month,year,array,data_type):
    
      
    #event time in UTC, comment out if no event
    #hour=21
    #minute=02
    #second=28.644
    
    
    
    #account for days with no event of note
    try: hour
    except NameError: hour = None
    if hour is None:
        event_time = 'no event'
    else:
        event_time=time_to_seconds(hour,minute,second)
        del hour,minute,second
       
    date=ints_to_date(day,month,year)
      
      
    
    
    if data_type=='uspln':
        dists, times = uspln(date,array,event_time)
        
    nearby=[]
    for i in range(len(dists)):
        if dists[i]<5:
            nearby.append(times[i])
    del i
    bin_num=np.linspace(0,86400,86401)
    
    
    
    fig,(ax1,ax2)= plt.subplots(2,1)
    
    scat = ax1.scatter(times,dists,color='black',marker='.')
    #ax1.title(date+' strikes seen by: '+data_type)
    ax1.set_xlim(0,86400)
    ax1.set_ylim(0,100)
    ax1.set_title(array+'  '+date+'  from: '+data_type)
    if len(dists)==0:
        ax1.annotate('no strikes within 100 miles',xy=(0,0),xytext=(30000,50))
    
    
    histo = ax2.hist(nearby,bins=bin_num,histtype='step',color='black')
    ax2.set_xlim(0,86400)
    if len(nearby)==0:
        ax2.set_ylim(0,10)
        ax2.annotate('no strikes within 5 miles',xy=(0,0),xytext=(30000,5))
    
    
    plt.show()

    



    

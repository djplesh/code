import numpy as np
import os
import datetime

def get_nearest(array, value):    
    '''find the nearest value in an array'''
    
    idx = (np.abs(array - value)).argmin()
    return idx
    
def fix_loc(loc):
    '''convert user given location to correct form for code'''

    if loc == 'pr' or loc == 3 or loc == 'PR': loc = 'PR'
    if loc == 'pan' or loc == 2 or loc == 'PAN': loc = 'PAN'
    if loc == 'lsu' or loc == 1 or loc == 'LSU': loc = 'LSU'
    if loc == 'uah' or loc == 4 or loc == 'UAH': loc = 'UAH'
    return loc

def box_numbers(loc):
    '''return a list of the number of boxes at a location'''
    
    if loc == 'LSU' or loc == 'UAH':
        boxes = range(1, 3)
    if loc == 'PAN':
        boxes = range(1, 6)
    if loc == 'PR':
        boxes = range(1, 11)
    return boxes
    
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
    
def fix_num(n):    
    """convert integer to string, add 0 if single digit"""
    
    if n < 10: n_s = '0' + str(n)
    else:
        n_s = str(n)
    return n_s

def ints_to_date(d, m, y):    
    """from integers for day month and year return date string,
    format yyyy_mm_dd"""
    
    m_s = fix_num(m)
    d_s = fix_num(d)
    y_s = str(y)
    date_s = y_s + '_' + m_s + '_' + d_s   
    return date_s

def date_to_ints(date):    
    """from date in string format yyyy_mm_dd 
    return integer values for day month and year"""
    
    d = int(date[8:10])
    m = int(date[5:7])
    y = int(date[0:4])        
    return d, m, y  
    
def loc_name(box_num):    
    """convert box name string to string of folder on home computer"""
    
    if box_num[0:3] == 'LSU':
        loc = 'LSU'
    elif box_num[0:3] == 'UAH':
        loc = 'UAH'
    elif box_num[0:3] == 'PAN':
        loc = 'PAN'
    elif box_num[0:2] == 'PR':
        loc = 'PR'        
    return loc
    
def path_files(path):    
    """select all files in a given path """
    
    file_list = []
    for file in os.listdir(path):
        file_list.append(path + file)        
    return file_list
    
def sec_to_hr(sec):
    """given a time in seconds return the hh:mm:ss"""
    
    return str(datetime.timedelta(seconds = sec)
    
def day_of_yr(d, m, y):
    """give a day month and year return what day of the year it is"""
    
    return (datetime.date(y, m, d) - datetime.date(y, 1, 1)).days + 1
    
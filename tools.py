import numpy as np


def get_nearest(array, value):    
    '''find the nearest value in an array'''
    
    idx = (np.abs(array - value)).argmin()
    return idx
    
def fix_loc(loc):

    if loc == 'pr' or loc == 3: loc = 'PR'
    if loc == 'pan' or loc == 2: loc = 'PAN'
    if loc == 'lsu' or loc == 1: loc = 'LSU'
    if loc == 'uah' or loc == 4: loc = 'UAH'\
    
    return loc
    
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
    """select all files in a given path independent of day"""
    
    file_list = []
    for file in os.listdir(path):
        file_list.append(path + file)        
    return file_list
    
    
def folder_rename(box_list):
    """used to rename folder in directory from MM_YYYY to YYYY_MM"""
    
    for box in box_list:
        f = 'E:/' + box + '/'
        for folder in os.listdir(f):
            if folder != 'calibrations':
                os.rename(f+folder, f_folder[3:]+'_'+folder[:2])
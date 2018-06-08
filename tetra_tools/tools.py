import numpy as np
import os
import datetime
import math


def get_nearest(array,value):
    idx = np.searchsorted(array, value, side="left")
    if idx > 0 and (idx == len(array) or math.fabs(value - array[idx-1]) < \
    math.fabs(value - array[idx])):
        return idx-1
    else:
        return idx


def box_list(loc):

    lsu = ['LSU_01', 'LSU_02']
    pan = ['PAN_01', 'PAN_02', 'PAN_03', 'PAN_04', 'PAN_05']
    pr = ['PR_01', 'PR_02', 'PR_03', 'PR_04', 'PR_05', 'PR_06', 'PR_07',
        'PR_08', 'PR_09', 'PR_10']
    uah = ['UAH_01', 'UAH_02']
    if loc == 'all': boxes = lsu + pan + pr + uah
    if loc == 'LSU': boxes = lsu
    if loc == 'PAN': boxes = pan
    if loc == 'PR': boxes = pr
    if loc == 'UAH': boxes = uah
    return boxes


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
    d_str = '{0}_{1}_{2}'.format(y_s, m_s, d_s)
    return d_str

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

    return str(datetime.timedelta(seconds = sec))

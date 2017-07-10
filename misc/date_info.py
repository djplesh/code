# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 20:19:08 2017

@author: DJ Pleshinger
"""

from datetime import date
from datetime import timedelta
import datetime


def fix_num(n):    
    """convert integer to string, add 0 if single digit"""
    
    if n < 10: n_s = '0' + str(n)
    else:
        n_s = str(n)
    return n_s

def get_date(d):    
    """get today as string and integers for day, month, year
    able to call 'tomorrow' or 'yesterday' as well"""
    
    today = date.today()
    if d == 'tomorrow': today = date.today() + timedelta(1)
    if d == 'yesterday': today = date.today() - timedelta(1)
    
    year = today.year
    year_s = str(year)        
    month = today.month 
    month_s = fix_num(month)    
    day = today.day
    day_s = fix_num(day)
    date_s = year_s + '_' + month_s + '_' + day_s
    
    return date_s, day, month, year
#########################################################################
def next_day(date):    
    """from date in string get string for next day, format yyyy_mm_dd"""
    
    y=int(date[0:4])
    m=int(date[5:7])
    d=int(date[8:10])
    tom = datetime.datetime(y, m, d) + timedelta(1)
    
    year = tom.year
    year_s = str(year)
    month = tom.month 
    month_s = fix_num(month)
    day = tom.day
    day_s = fix_num(day)        
    date_s = year_s + '_' + month_s + '_' + day_s    
    return date_s

def previous_day(date):    
    """from date in string get string for previous day, format yyyy_mm_dd"""
    
    yy = int(date[0:4])
    mm = int(date[5:7])
    dd = int(date[8:10])
    yest = datetime.datetime(yy,mm,dd) - timedelta(1)
    
    year = yest.year
    year_s = str(year)
    month = yest.month 
    month_s = fix_num(month)
    day = yest.day
    day_s = fix_num(day)        
    date_s = year_s + '_' + month_s + '_' + day_s    
    return date_s
#########################################################################
def ints_to_datetime(d, m, y):    
    """from integers for day month and year return datetime date"""
    
    date_return = date(y, m, d)
    return date_return

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

def time_to_seconds(h, m, s):    
    """convert hour minute second integers to number of seconds"""
    
    return int(h)*3600 + int(m)*60 + float(s) 
   
    


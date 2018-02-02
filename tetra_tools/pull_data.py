import subprocess as sp
from datetime import timedelta
from datetime import datetime
import urllib
import os
from tetra_tools.tools import fix_num


#sp.Popen('robocopy Z:\LSU_01\ E:/LSU_01//09_2017/ *.* /MAXAGE:20170901 /MINAGE:20171001 /E')

def get_tetra2(d = 0):
    box_list = ['LSU_01', 'LSU_02', 'PAN_01', 'PAN_02', 'PAN_03', 'PAN_04', 'PAN_05', 
    'UAH_01', 'UAH_02', 'PR_01', 'PR_02', 'PR_03', 'PR_04', 'PR_05', 'PR_06',
    'PR_07', 'PR_08',' PR_09', 'PR_10']
    
    date = datetime.today() - timedelta(d)
    if date.day == 1: date = datetime.today() - timedelta(1)
    
    year =date.year
    year2 = year
    cur_month = date.month
    next_month = (cur_month + 1) % 12
    if next_month == 0: next_month = 12
    if next_month == 1: year2 = year + 1
    cur_month = fix_num(cur_month)
    next_month = fix_num(next_month)

    oldest = str(year) + cur_month + '01'
    newest = str(year2) + next_month + '01'

    month_dir = '/' + str(year) + '_' + cur_month + '/'

    for box in box_list:
        x = sp.Popen('robocopy Z:\\' + box + '\\ ' + ' E:/' + box + month_dir + ' *.* ' + '/MAXAGE:' + oldest + ' /MINAGE:' + newest + ' /E')
        x.wait() #wait for each box to complete before starting next




def get_wwlln(year = None, month = None, day = None):
    
    if day == None:
        #default is one week prior, files are uploaded a week delayed
        day = datetime.today() - timedelta(7)
        day_str = str(day.year) + fix_num(day.month) + fix_num(day.day)
        folder = str(day.year) + '_' + fix_num(day.month)
    else:
        day_str = str(year) + fix_num(month) + fix_num(day)
        folder = str(year) + '_' + fix_num(month)
    
    output_path = 'C:/Users/tetra/lightning/WWLLN/' + folder
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    url = 'http://LSU:deirdreWWLLN17@wwlln.net/hostdata/A' + day_str + '.loc'
    path = output_path + '/A' + day_str + '.loc'    
    urllib.urlretrieve(url, filename = path)

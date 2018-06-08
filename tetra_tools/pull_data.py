import subprocess as sp
from datetime import timedelta
from datetime import datetime
from datetime import date
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
        d = date.today() - timedelta(7)
        folder = d.strftime("%Y_%m")
    else:
        d = date(year, month, day)
        folder = d.strftime("%Y_%m")
    output_path = 'C:/Users/tetra/lightning/WWLLN/' + folder
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    for i in range(1, d.day+1):
        x = date(d.year, d.month, i)
        path = output_path + '/A' + x.strftime("%Y%m%d") + '.loc'
        if not os.path.isfile(path):
            url = 'http://LSU:deirdreWWLLN17@wwlln.net/hostdata/A' + x.strftime("%Y%m%d") + '.loc'
            urllib.urlretrieve(url, filename = path)

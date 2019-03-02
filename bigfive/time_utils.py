# -*- coding: utf-8 -*-

import time
import datetime

def today():
    return time.strftime('%Y-%m-%d', time.localtime(time.time()))

def now():
    return time.strftime('%H:%M:%S', time.localtime(time.time()))

def date2datestr(date):
    return date.strftime('%Y-%m-%d')

def unix2hadoop_date(ts):
    return time.strftime('%Y_%m_%d', time.localtime(ts))

def ts2date(ts):
    return time.strftime('%Y-%m-%d', time.localtime(ts))

def ts2datetime(ts):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts))

def date2ts(date):
    return int(time.mktime(time.strptime(date, '%Y-%m-%d')))

def datetime2ts(date):
    return int(time.mktime(time.strptime(date, '%Y-%m-%d %H:%M:%S')))

def window2time(window, size=24*60*60):
    return window*size

def datestr2ts(date):
    return time.mktime(time.strptime(date, '%Y-%m-%d'))

def nowts():
    return int(time.time())

def get_datelist(year1,month1,day1,year2,month2,day2):
    date_list = []
    begin_date = datetime.datetime.strptime(str(year1)+'-'+str(month1)+'-'+str(day1), "%Y-%m-%d")
    end_date = datetime.datetime.strptime(str(year2)+'-'+str(month2)+'-'+str(day2), "%Y-%m-%d")
    while begin_date <= end_date:
        date_str = begin_date.strftime("%Y-%m-%d")
        date_list.append(date_str)
        begin_date += datetime.timedelta(days=1)   #输出时间列表的函数
    return date_list

DAY = 24*3600
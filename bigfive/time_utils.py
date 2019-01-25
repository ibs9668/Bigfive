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

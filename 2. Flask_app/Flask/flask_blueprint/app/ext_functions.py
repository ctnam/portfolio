import datetime
import time

def monthconverted_fromstr(month=str()):
    monthslist = ['January','February','March','April','May','June','July','August','September','October','November','December']
    for i in monthslist:
        if month.lower() == i.lower():
            r = monthslist.index(i)+1
    return r

def monthconverted_fromint(month=int()):
    monthslist = ['January','February','March','April','May','June','July','August','September','October','November','December']
    r = monthslist[month-1]
    return r

def currenttimepoint():
    struct_time = time.localtime()
    now = datetime(struct_time.tm_year, struct_time.tm_mon, struct_time.tm_mday, struct_time.tm_hour, struct_time.tm_min, struct_time.tm_sec, 0)
    return now

def currentyear():
    struct_time = time.localtime()
    r = struct_time.tm_year
    return r

def currentmonth():
    struct_time = time.localtime()
    r = struct_time.tm_mon
    return r

def today():
    today = datetime.date.today()
    return today

def fullmonth(month=str()):
    for m in ['January','February','March','April','May','June','July','August','September','October','November','December']:
        if month.lower() in m.lower():
            r=m
            return r

def fullday(day=str()):
    for d in ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']:
        if day.lower() in d.lower():
            r=d
            return r

print('Hello World, this message comes from ext_functions.py')

host = "http://127.0.0.1:5000"
# /files/DSC_1891__d02de562bc6c468792dbb142634da700.jpg
def getfilename(url=str()):
    r = url.split('/')[-1]
    return r
def getfullurl(url=str()):
    r = host + url
    return r
#print(getfilename("/files/DSC_1891__d02de562bc6c468792dbb142634da700.jpg"))
#print(getfullurl("/files/DSC_1891__d02de562bc6c468792dbb142634da700.jpg"))

def strdatetime_todatetime(d=str()):
    # '2021-10-20 11:58:00'
    year = int(d.split('-')[0])
    month = int(d.split('-')[1].split('-')[0])
    day = int(d.split('-')[2].split(' ')[0])
    hour = int(d.split(' ')[1].split(':')[0])
    minute = int(d.split(' ')[1].split(':')[1].split(':')[0])
    second = 0
    return datetime.datetime(year,month,day,hour,minute,second)

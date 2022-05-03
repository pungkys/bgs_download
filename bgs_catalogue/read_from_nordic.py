#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr  1 12:08:53 2022

@author: psuroyo
"""
"""Functions to read Nordic data format 
input: 
    - Nordic files downloaded from BGS ftp ftp://seiswav.bgs.ac.uk/events 
    - path of nordic file 
    - nordic filename 
    - station informations 
output:
    a. Event details 
    continuous_day -> Id of continuous records (julian date)
    eventid -> id of events
    lat -> latitude of event
    lon -> longitude of event
    dep -> focal depth
    nsta -> number of stations which record the event
    mag -> magnitude
    magtype -> type of magnitude
    otime -> event origin time 
    
    b. waveform details
    sta -> station id
    cha -> channel id
    phase -> arrival phase
    time -> arrival time 

    """

import datetime
import time
from datetime import timedelta
from obspy.io.nordic.core import read_nordic


def fix_second(datetime_str):
    nofrag, frag = datetime_str.split('.')
    nofrag_dt = time.strptime(nofrag, "%Y-%m-%dT%H:%M:%S")
    ts = datetime.datetime.fromtimestamp(time.mktime(nofrag_dt))
    dt = ts.replace(microsecond=int(frag)*10000)
    return dt

def read_event_file(path: str):
    list_sta_diff =['PNR3','PNR0','PPV0']
    catalog = read_nordic(path, return_wavnames=False)
    str_cat = str(catalog[0])
    cat_header = str_cat.split('\t')[1].strip().split('|')
    str_cat = str(catalog[0])
    cat_header = str_cat.split('\t')[1].strip().split('|')
    
    str_event = cat_header[0].strip()
    eventid = datetime.datetime.strptime(str_event, '%Y-%m-%dT%H:%M:%S.%fZ')
    day_of_year = eventid.date().timetuple().tm_yday
    day_of_year ="{0:0=3d}".format(day_of_year)
    continuous_day = str(eventid.date().year)+"."+day_of_year
    mag = cat_header[2].strip().split(" ")[0]
    magtype = cat_header[2].strip().split(" ")[1]
    latlon = cat_header[1].split(",")
    lat = latlon[0].strip().replace('+','')
    lon = latlon[1].strip()
    waveforms =[]
    header = None
    with open(path, 'r') as fp:
        for i, line in enumerate(fp):
            if i == 0:
                head = [u for u in line.strip().split(" ")]
                event =[u for u in head if u.strip()]
                year = event[0].strip()
                if len(event[1].strip())>2 :
                    n= 1
                    if len(event[1].strip())== 3:
                        month = event[1].strip()[0]
                        day = event[2-n].strip()[1:3]
                    if len(event[1].strip())== 4:
                        month = event[1].strip()[0:2]
                        day = event[2-n].strip()[2:4]
                else:
                    n=0
                    month = event[1].strip()
                    day = event [2-n].strip()

                if len (event[3-n]) < 4:
                    hh = event[3-n].strip()[0]
                    mm = event[3-n].strip()[1:3]
                else:
                    hh = event[3-n].strip()[0:2]
                    mm = event[3-n].strip()[2:4]   
                sec = event[4-n].strip()
                sec = "".join([i for i in sec if not i.isalpha()])
                dep = event[7-n].strip()
                dep = "".join([i for i in dep if not i.isalpha()])
                nsta= event[9-n].strip()

                date_time_str = year+'-'+month+"-"+day+"T"+hh+":"+mm+":"+sec
                if float(sec) > 59.0:
                    otime = fix_second(date_time_str)
                else:
                    otime = datetime.datetime.strptime(date_time_str, '%Y-%m-%dT%H:%M:%S.%f')
                event = (continuous_day, eventid, lat, lon, dep, nsta, mag, magtype, otime)

            if i < 3:
                continue
            if i == 3:
                if len ([" " + u for u in line.strip().split(" ")]) != 18:
                    continue
                else:
                    header = [" " + u for u in line.strip().split(" ")]
                    continue

            if i == 4:
                if header == None:
                    if len ([" " + u for u in line.strip().split(" ")]) != 18:
                        continue
                    else:
                        header = [" " + u for u in line.strip().split(" ")]
                        continue
            if i == 5:
                if header == None:
                    if len ([" " + u for u in line.strip().split(" ")]) != 18:
                        continue
                    else:
                        header = [" " + u for u in line.strip().split(" ")]
                        continue
            if i == 6:
                if header == None:
                    if len ([" " + u for u in line.strip().split(" ")]) != 18:
                        continue
                    else:
                        header = [" " + u for u in line.strip().split(" ")]
                        continue
            if i == 7:
                if header == None:
                    header = [" " + u for u in line.strip().split(" ")]
                continue

            if not line.strip():
                continue

            start, end = 0, len(header[0])
            sta = line[start: end].strip()
            if sta in list_sta_diff:
                sta = line[start: end+1].strip()
            start = end
            end += len(header[1])
            cha = line[start: end].strip()
            if len(cha)> 2:
                cha = cha[-2:]
            start = end
            end += len(header[2])
            phase = line[start: end].strip()
            start = end
            end += len(header[3])
            start = end
            end += len(header[4])
            hm = line[start: end].strip()
            start = end
            end += len(header[5])
            sec = line[start: end].strip()
            time = timedelta(hours=int(hm[:-2]), minutes=int(hm[-2:]), seconds=float(sec))
            waveforms.append((sta, cha, phase, time))
    return event, waveforms 
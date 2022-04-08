#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr  1 12:36:48 2022

@author: psuroyo
"""

"""Functions to store event and station details  
other important modules to run 
- read_from_nordic.py

input: 
    - Path to nordic file
    - Station informations
output:
    Event catalogue 
    List of missing informations

    """

import numpy as np
import pandas as pd
from read_from_nordic import read_event_file
from search_station_info import search_sta_info_nonet,search_sta_info_add

def store_event_nordic(path):
    event, waveforms=read_event_file(path)
    ev_missing=[]
    sta_missing=[]
    continuous_id = []
    eventid = [] 
    lat = []
    lon = []
    dep = []
    nsta = []
    mag = []
    magtype = []
    otime = []
    sta = []
    cha = []
    net=[]
    slat=[]
    slon=[]
    selv=[]
    qphase= []
    phase = []
    time =[]
    for i in range (len(waveforms)):
        channel = waveforms[i][1]
        s = waveforms[i][0]
        c = channel[0]+"H"+channel[1]
        id_sta_tr = s+".."+c
        station= search_sta_info_nonet ("/Volumes/Samsung_T5/Secondment_GFZ/", 'stn-info.txt', id_sta_tr)
        if station != None: # if missing station info, then skip
            s_lat =station[0]
            s_lon =station[1]
            s_elv =station[2]
            network = station [3]
        else:
            station = search_sta_info_add ("/Volumes/Samsung_T5/Secondment_GFZ/", "stn-info-add_v2.csv", id_sta_tr)
            if station != None: # if missing station info, then skip
                s_lat =station[0]
                s_lon =station[1]
                s_elv =station[2]
                network = station [3]
            else:
                ev_missing.append(event [1])
                sta_missing.append(id_sta_tr)
                s_lat = np.NaN
                s_lon = np.NaN
                s_elv = np.NaN
                network = " "
        sta.append(s)
        cha.append(c)
        net.append(network)
        slat.append(s_lat)
        slon.append(s_lon)
        selv.append(s_elv)
        qphase.append(waveforms[i][2][0])
        phase.append(waveforms[i][2][1:len(waveforms[i][2])])
        time.append(waveforms[i][3])
#         continuous_day.append(event [0])
        continuous_id.append(str(network)+'.'+s+".00."+c+".D."+event [0])
        eventid.append(event [1])
        lat.append(event [2])
        lon.append(event [3])
        dep.append(event [4])
        nsta.append(event [5])
        mag.append(event [6])
        magtype.append(event [7])
        otime.append(event [8])

    df = pd.DataFrame({'continuous id': continuous_id,"eventid": eventid,
                       "elat":lat, "elon": lon, "edep": dep, "nsta" :nsta,
                       "emag" : mag, "emagtype": magtype, "otime": otime, 
                       "network": net, "station" : sta, "channel" : cha,
                       "slat": slat,"slon": slon, "selv": selv, "qphase": qphase,
                       "phase" : phase, "arrival time" : time })
    
    de = pd.DataFrame({"station missing": sta_missing, "event missing" : ev_missing})
    return df, de
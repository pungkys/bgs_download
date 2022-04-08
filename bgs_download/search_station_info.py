#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr  1 18:57:38 2022

@author: psuroyo
"""
"""Functions to store station details  
other important modules to run 
- read_from_nordic.py

input: 
    - Path to station information file
        a. stn-info.txt
        b. stn-info-add_v2.csv
output:
   - network
   - station id 
   -station latitude
   -station longitude
   -station elevation

    """
import os
import pandas as pd
import numpy as np

def search_sta_info_nonet (path, filename :str, id_sta_tr: str):
    
    ds=pd.read_fwf(os.path.join(path,filename),header=None)
    
    ds['sta_id'] = ds[0] # new row to take station id
    ds['sta_net'] = ds[1] # new row to take network


    elv_chan=[s.split(' ') for s in ds[3]] # since the DataFrame in column 3 reading 2 variables, we seperate them
    schan_ =[s[1].split('"') for s in elv_chan] # get rid unnecessary part
    schan = [s[1] for s in schan_] # get channel


    ds['ID'] = ds['sta_id']+".."+schan
    
    # find location wheren the network, station, and channel of the traces is matched
    mask = np.column_stack([ds[col].str.contains(id_sta_tr, na=False) for col in ds])
    any_sta=ds.iloc[mask.any(axis=1)]
    
    if len(any_sta)== 0: 
#         print('station '+id_sta_tr+' is not found!')
        return None # nothing match
    
    elif len(any_sta)>1: # if more than 1 station matched, take the latest station information
        # store the most updated station information -> last row/ higher index
        latlon= [s.split(' ') for s in any_sta[2]][-1]
        slat  = latlon[0]
        slon  = latlon[1]
        elv_chan = [s.split(' ') for s in any_sta[3]][-1]
        selv = elv_chan[0][0]
        net = [s.split(' ') for s in any_sta[1]][-1][0]
        return slat, slon, selv, net
    
    elif len(any_sta)==1:# if only 1 station matched, stored
        latlon= [s.split(' ') for s in any_sta[2]][0]
        slat  = latlon[0]
        slon  = latlon[1]
        elv_chan = [s.split(' ') for s in any_sta[3]]
        selv = elv_chan[0][0]
        net = [s.split(' ') for s in any_sta[1]][0][0]
        return slat, slon, selv, net
    
def search_sta_info_add (path: str, filename: str, id_str: str):
    d = pd.read_csv(os.path.join(path, filename), encoding= 'unicode_escape')
    sta = id_str.split('..')[0] 
    mask = np.column_stack([d['Sta'].str.contains(sta, na=False)])
    any_sta=d.iloc[mask.any(axis=1)]

    if any_sta is not None:
        dsta = any_sta[any_sta['Sta'] == sta]
        if len(dsta) != 0:
            slat = dsta['slat'].values
            slon = dsta['slon'].values
            selv = dsta['selv'].values
            net = dsta['net'].values
            
            return float(slat), float(slon), float(selv), net.item()
    else:
        return None
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr  1 19:09:45 2022

@author: psuroyo
"""

"""Script to store event catalogue

    modules:
        -store.py
        -read_from_nordic.py
        -search_station_info.py
        
    input file:
        Nordic file "./events"
    output files:
        Catalog.csv
        List of missing station
    """
import os 
from store import store_event_nordic
import pandas as pd

direc    = '/Volumes/Samsung_T5/Secondment_GFZ/events'

list_year = [f for f in os.listdir(direc) if not f.startswith('.')]
# list_year= ["2018"]
store=[]
list_missing=[]
for yearfile in list_year:
    list_month = [f for f in os.listdir(os.path.join(direc,yearfile)) if not f.startswith('.')]
    for monthfile in list_month:
        list_file =[f for f in os.listdir(os.path.join(direc,yearfile,monthfile)) if not f.startswith('.')]
        list_file = [f for f in list_file if not f.endswith('swp')]
        
        for file in list_file:
            df,de = store_event_nordic(os.path.join(direc,yearfile,monthfile,file))
            store.append(df)
            list_missing.append(de)
result = pd.concat(store,ignore_index=True)
missing = pd.concat(list_missing,ignore_index=True)
result.to_csv(os.path.join('/Volumes/Samsung_T5/Secondment_GFZ/',"Catalog_v2.csv"),header=True, index=True)
missing.to_csv(os.path.join('/Volumes/Samsung_T5/Secondment_GFZ/',"missing_stations_v3.csv"),header=True, index=True) 
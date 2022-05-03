#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  4 19:26:21 2022

@author: psuroyo
"""

""" Function to read arrival  of P and S waves from catalogue file 
and estimate arrival time when it is not provided in the catalog file """
import pandas as pd
import datetime
import numpy as np
from obspy.taup import TauPyModel
from obspy.geodetics.base import gps2dist_azimuth

def pick_arrival(dcatalog, phase):
    dnew= dcatalog[dcatalog['phase'] == phase]
    if not dnew.empty:
        atime = pd.to_timedelta(dnew['arrival time'])
        year = pd.DatetimeIndex(dnew['eventid']).year
        month = pd.DatetimeIndex(dnew['eventid']).month
        day = pd.DatetimeIndex(dnew['eventid']).day
        str_datetime= str(year[0])+'-'+str(month[0])+"-"+str(day[0])
        arrival = datetime.datetime.strptime(str_datetime, '%Y-%m-%d')+ atime
        return pd.to_datetime(arrival.iloc[0])
    else:
        arrival = taupy_arrival(dcatalog, phase)
        return arrival

def taupy_arrival(dcatalog, phase):
    TauPy_model = TauPyModel('ak135')
    dnew =dcatalog.iloc[0]
    # theoretical backazimuth and distance
    baz = gps2dist_azimuth(dnew['elat'], dnew['elon'],
                           dnew['slat'], dnew['slon'])
    arrival = TauPy_model.get_travel_times(distance_in_degree=0.001 * baz[0] / 111.11,
                                            source_depth_in_km=dnew['edep'],
                                           phase_list=phase)[0]
    timedelta_arrival = pd.to_timedelta(arrival.time, unit='S')
    return pd.to_datetime(dnew['otime'])+timedelta_arrival

def distances(dcatalog):
    dnew =dcatalog.iloc[0]
    baz = gps2dist_azimuth(dnew['elat'], dnew['elon'],
                           dnew['slat'], dnew['slon'])
    repi_km = baz[0]/1000
    rhyp_km = np.sqrt((dnew['edep']+(float(dnew['selv'])/1000))**2+repi_km**2)
    return repi_km, rhyp_km
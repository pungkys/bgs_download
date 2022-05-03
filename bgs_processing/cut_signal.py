#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  5 10:11:23 2022

@author: psuroyo
"""

""" Function to cut and trim the signal"""
from scipy.integrate import cumtrapz
import numpy as np 

def link_window_to_trace(tr, start, end):
    tr.stats['wstart'] = start
    tr.stats['wend'] = end


def get_sta_shift(sta, sta_shift):
    """
    sta_shift must be a dictionary containing the station name to be shifted
    and the time shift in seconds e.g. {'STA':0.5}.
    """
    if sta in sta_shift.keys():
        return sta_shift[sta]
    else:
        return 0

def get_arias(tr):
        """
        Performs calculation of arias intensity.
        Returns:
            arias_intensities.
        """

        trace= tr.copy()
        dt = trace.stats["delta"]
        
        if trace.stats.output == 'DISP':
            trace.differentiate 
        elif trace.stats.output == 'ACC':
            trace.integrate
        # Calculate Arias Intensity
        arias_intensity =np.pi / (2 * 9.81) * cumtrapz(trace.data ** 2, dx=dt, initial=0)
        return arias_intensity

def calc_cav(tr):
    """
    Calculates the Cumulative Absolute velocity

    ref:
    Electrical Power Research Institute. Standardization of the Cumulative
    Absolute Velocity. 1991. EPRI TR-100082-1'2, Palo Alto, California.
    """
    
    trace=tr.copy()
    if trace.stats.output == 'DISP':
        trace.integrate 
    elif trace.stats.output == 'ACC':
        trace.differentiate
        
    abs_tr = np.abs(trace.data)
    return cumtrapz(abs_tr, dx=trace.stats.delta, initial=0)

def calc_tend(tr, percentage, method='cav'):
    trace= tr.copy()
    if method =='cav':
        cav = calc_cav (trace)
        cum_cav = cav / max(cav)
        ind= np.where(cum_cav > percentage)
        firstabove = ind[0][0]
        return trace.stats.starttime +trace.times()[firstabove]
    
    elif method =='ariasintensity':
        ai = get_arias(trace)
        cum_ai = ai / max(ai)
        ind= np.where(cum_ai > percentage)
        firstabove = ind[0][0]
        return trace.stats.starttime +trace.times()[firstabove]
    else:
        return print("Select your method (arias intensity or CAV)!")

def cut_p(st, bf=2, raf=0.8, sta_shift=dict()):
    """
    Function to cut a p wave window from an Obspy trace obeject

    bf (int/float) time shift in seconds before the P-wave arrival time

    raf (int/float) ratio of p-s time to fix the end of the P-window

    sta_shift (dict) dictionary of station names and station specific time shifts in seconds
    """

    stas=0

    for tr in st:

        stas = get_sta_shift(tr.stats.station, sta_shift)
        relps = tr.stats['s_time'] - tr.stats['p_time']
        p_start = tr.stats['p_time']-bf+stas
        p_end = tr.stats['p_time']+relps*raf

        link_window_to_trace(tr, p_start, p_end)
        tr.trim(p_start, p_end)


def cut_s(st, bf=2, rafp=0.8, tafs=2.3, time_after='absolute_time', sta_shift=dict()):
    """
    Function to cut a s wave window from an Obspy trace obeject.

    bf (int/float) time shift in seconds before the P-wave arrival time

    rafp (int/float) ratio of p-s time to fix the start the of S-window

    tafs (int/float) window length in seconds or scaling factor of relative p-s time

    time_after (str) can be set to 'absolute_time' or 'relative_ps'

        if time_after == 'absolute_time' the window length is given as a value in seconds

        if time_after == 'relative_ps' the value should be some number that scales with the p-s differential time

    sta_shift (dict) dictionary of station names and station specific time shifts in seconds

    Modified by Pungky Suroyo.
    """
    stas=0

    for tr in st:

        stas = get_sta_shift(tr.stats.station, sta_shift)
        relps = tr.stats['s_time'] - tr.stats['p_time']
        s_start = tr.stats['s_time'] - bf + stas

        if time_after == 'absolute_time':
            s_end = s_start + tafs

        if time_after == 'relative_ps':
            s_end = s_start + tafs*relps*rafp + stas

        if s_end > tr.stats['endtime']:
            s_end= tr.stats['endtime']

        link_window_to_trace(tr, s_start, s_end)
        tr.trim(s_start, s_end)

def pad_traces(st, pad_len=1, pad_val=0):

    """
    Util to pad waveforms with zeros before and after the start and endtime of trace.
    """

    for tr in st:
        tr.trim(tr.stats.starttime-pad_len, tr.stats.endtime+pad_len, pad=True, fill_value=pad_val)



def cut_c(st, bf=2, raf=0.8, tafp=2.3, percentage= None, sta_shift=dict()):

    """

    Function to cut a coda wave window from an Obspy trace object

    Written by Pungky Suroyo.

    """

    stas=0

    for tr in st:

        stas = get_sta_shift(tr.stats.station, sta_shift)

        relps = tr.stats['s_time'] - tr.stats['p_time']

        s_start = tr.stats['p_time'] + relps*raf + stas

        c_start = s_start + tafp*relps
        
        if c_start < (s_start+ relps*raf + stas):
            c_start = s_start+ relps*raf + stas
            
        if percentage is not None:
            c_end = tend_cav(tr, percentage)
        else:
            c_end =tr.stats['endtime']
        
        if c_end < c_start:
            st.remove(tr)
        else:
            link_window_to_trace(tr, c_start, c_end)

            tr.trim(c_start, c_end)
            
def define_noise(tr, Dtarget, Ds, bf=2):
    ParamDmin = 0.5
    
    wN1 = [(tr.stats['p_time']-0.1)- max([ParamDmin,Dtarget]), tr.stats['starttime']]
    iIN1= [max(wN1), tr.stats['p_time']-bf]
    DN1 =  iIN1[1]- iIN1[0]
    wN2 = [tr.stats['endtime'] - max([ParamDmin , DN1]), tr.stats['s_time']+Ds]
    iIN2= [max(wN2), tr.stats['endtime']]
    wN3 = [tr.stats['endtime']-max([ParamDmin,DN1,Dtarget]) , tr.stats['s_time']+Ds]
    iIN3= [max(wN3), tr.stats['endtime']]
    DN2 =  iIN2[1]- iIN2[0]
    DN3 = iIN3[1]- iIN3[0]
    
    return [DN1,iIN1,Dtarget,iIN2,iIN3,DN2,DN3]

def noise(tr, Dtarget, Ds, noisetype: str):
    noise = define_noise(tr, Dtarget, Ds)
    if noisetype == 'pre':
        start = min(noise[1])
        end = max(noise[1])
    if noisetype == 'post':
        start = min(noise[3])
        end = max(noise[3])
    return start, end
        
def get_signal(st, func, **kwargs):
    stc = st.copy()
    func(stc, **kwargs)
    return stc

def get_noise_s(st, swave, noisetype: str, bf=2):
    stc=st.copy()
    for tr, trs in zip(stc, swave):
        durs = trs.stats['wend']-trs.stats['wstart']
        start, end = noise(tr, durs, durs, noisetype)
        if end >= tr.stats['p_time']:
            dt= end - tr.stats['p_time']
            end= tr.stats['p_time'] - (dt + bf)
        link_window_to_trace(tr, start, end)
        tr.trim(start, end)
    return stc
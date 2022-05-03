#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 14 16:43:34 2022

@author: psuroyo
"""

""" Calculate peak ground acceleration, peak ground velocity a
nd maximum amplitude of wood-Anderson"""

from obspy.signal.invsim import simulate_seismometer as seisSim
def peak_ground(data):
    if abs(max(data)) >= abs(min(data)):
        pg = abs(max(data))
    else:
        pg = abs(min(data))
    return pg

def pgav(tr):
    trace= tr.copy()

    if trace.stats.output == 'DISP':
        trace.differentiate()
        pgv = peak_ground(trace.data)
        trace2=trace.copy()
        trace2.differentiate()
        pga = peak_ground(trace2.data)   
    elif trace.stats.output == 'VEL':
        pgv = peak_ground(trace.data)
        trace2=trace.copy()
        trace2.differentiate()
        pga = peak_ground(trace2.data)   
    elif trace.stats.output == 'ACC':
        pga = peak_ground(trace.data)
        trace2 = trace.copy()
        trace2.integrate()
        pgv = peak_ground(trace2.data)
        
    return pga, pgv
    
def maxwn(tr, PAZ=None, water_level=60):
    # Sensitivity is 2080 according to:
    # Bormann, P. (ed.) (2002). IASPEI New Manual of Seismological Observatory
    # Practice (NMSOP), GeoForschungsZentrum Potsdam, ISBN: 3-9808780-0-7,
    # IASPEI Chapter 3, page 24
    # (PITSA has 2800)
    WOODANDERSON = {'poles': [-6.283 + 4.7124j, -6.283 - 4.7124j],
                    'zeros': [0 + 0j], 'gain': 1.0, 'sensitivity': 2080}
    trace = tr.copy()
    
    # De-trend data
    trace.detrend('simple')
    # Simulate Wood Anderson
    if PAZ:
        trace.data=seisSim(trace.data, trace.stats.sampling_rate, paz_remove=PAZ,
                           paz_simulate=WOODANDERSON, water_level=water_level,
                           remove_sensitivity=True)
    else:
        trace.data=seisSim(trace.data, trace.stats.sampling_rate, paz_remove=None,
                            paz_simulate=WOODANDERSON, water_level=water_level,
                            remove_sensitivity=True)

    if abs(max(trace.data)) >= abs(min(trace.data)):
        maxwn = abs(max(trace.data))
    else:
        maxwn = abs(min(trace.data))

    return maxwn
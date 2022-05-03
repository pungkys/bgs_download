#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  5 10:14:35 2022

@author: psuroyo
"""
""" Function to calculate spectra"""

import numpy as np
# from mtspec import mtspec
import multitaper.mtspec as mtspec

def calc_spectra(tr, **kwargs):
#     psd, freq = mtspec(tr.data, tr.stats['delta'], 3)
    a = mtspec.MTSpec(tr.data, nw=4, kspec=3, dt=tr.stats.delta, nfft=len(tr.data))
    psd = a.rspec()[1]
    freq = a.rspec()[0]
    amp = psd_to_amp(tr, psd)
    return amp, freq

def psd_to_amp(tr, psd):
    """
    Converts Power Spectral Density (PSD) to spectral amplitude.
    amp = [PSD*fs*len(PSD)]^0.5
    fs is sampling rate in Hz
    """
    amp = np.sqrt(
        (psd*len(psd))/tr.stats['sampling_rate'])
    return amp

def amp_to_psd(tr, amp):
    """
    Converts Power Spectral Density (PSD) to spectral amplitude.
    amp = [PSD*fs*len(PSD)]^0.5
    fs is sampling rate in Hz
    """
    psd = np.power(amp, 2) / (
        tr.stats['sampling_rate']* len(amp))
    return psd
    
def integrate(amp, freq):
    newamp = amp/ (2*np.pi*freq)
    return newamp

def differentiate(amp, freq):
    newamp = amp* (2*np.pi*freq)
    return newamp

def bin_spectrum(amp, freq, smin=0.001, smax=200, bins=101):
    # define the range of bins to use to average amplitudes and smooth spectrum
    space = np.logspace(np.log10(smin), np.log10(smax), bins)
    # initialise numpy arrays
    bamps = np.zeros(int(len(space)-1)); bfreqs = np.zeros(int(len(space)-1));
    # iterate through bins to find mean log-amplitude and bin center (log space)
    for i, bbb in enumerate(zip(space[:-1], space[1:])):
        bb, bf = bbb
        a = 10**np.log10(amp[(freq>=bb)&(freq<=bf)]).mean()
        bamps[i] = a;
        bfreqs[i] = 10**(np.mean([np.log10(bb), np.log10(bf)]))

    # remove nan values
    bfreq = bfreqs[np.logical_not(np.isnan(bamps))]
    bamp = bamps[np.logical_not(np.isnan(bamps))]
    return bamp, bfreq

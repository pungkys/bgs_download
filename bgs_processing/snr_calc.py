#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  5 10:43:40 2022

@author: psuroyo
"""

""" Function to calculate snr and frequency bands of SNR> snr_tolerance"""


BIN_PARS = {"smin": 0.001, "smax": 200, "bins": 151}
ROT_PARS = {'inc': 0.05, 'space': [1e-3, 1+1e-3]}

import numpy as np
from spectra import bin_spectrum

def scale_noise_parseval(namp, amp):
    # if noise is shorter than signal - scale with np.sqrt(len(signal)/len(noise))
    namp *= np.sqrt(len(amp)/len(namp))
    return namp 

def interp_noise_to_signal(namp, nfreq, amp, freq):
    namp = np.interp(freq, nfreq, namp)
    #self.noise.diff_freq = self.noise.freq[np.where(self.noise.freq <= self.signal.freq.min())]
    nfreq = freq.copy()
    return bin_spectrum(namp, nfreq,**BIN_PARS) # need to recalc bins after interp.


def calc_bsnr(namp, nfreq, samp, sfreq, ROTATE_NOISE=True):
    bnamp, bnfreq = bin_spectrum(namp, nfreq, **BIN_PARS)
    sbamp, sbfreq = bin_spectrum(samp, sfreq, **BIN_PARS)
    bnamp = scale_noise_parseval(bnamp, sbamp)
    bnamp, bnfreq = interp_noise_to_signal(bnamp, bnfreq, sbamp, sbfreq)
    if ROTATE_NOISE:
        rot = non_lin_boost_noise_func(sbamp.copy(),
            bnamp, sbamp, **ROT_PARS)

        bnamp *= rot

        namp *= np.interp(nfreq, bnfreq, rot)
        # set bsnr to the object
    return sbamp/bnamp
    
def non_lin_boost_noise_func(xn, yn, ys, inc, space):

    nb = 0; max_its = 1000; it=0;
    # determin low and high freqs with respect to centroid freq
    inds_b = xn <= get_centroid_freq(xn, ys) # indices of 'low' freqs
    inds_f = ~inds_b # indices of 'high' freqs

    sample_no = np.interp(xn, [xn.min(), xn.max()], space)
    # 'rotate' the low frequencies to signal
    while it < max_its:

        tmp_n_b = yn / sample_no ** nb

        nb += inc
        it += 1
        # break condition looks for any low freq that is greater than signal
        if np.any(tmp_n_b[inds_b] >= ys[inds_b]):
            break


    sample_no_f = sample_no[::-1]
    nf = 0; max_its = 1000; it=0;

    while it < max_its:

        tmp_n_f = yn / sample_no_f ** nf

        nf += inc
        it += 1

        if np.any(tmp_n_f[inds_f] >= ys[inds_f]):
            break

    return np.maximum(tmp_n_b, tmp_n_f) / yn

def get_centroid_freq(f, a):
    # Calc the center freq of spectrum
    return np.sum(f*a) / np.sum(a)

def find_freq_limit(sfreq,snr,fbands,snr_tol):
    # get freq and ratio function
    f = sfreq; a = snr

    #get freq and snr between min/max freq considered
    minf = fbands[0]
    maxf = fbands[1] 
    if min(f) < minf:
        start = np.where(f>minf)[0][0]
    else:
        start = np.where(f==min(f))[0][0]

    if max(f) > maxf:
        end = np.where(f<maxf)[0][-1]
    else:
        end = np.where(f==max(f))[0][0]

    f= f[start:end]; a= a[start:end]

    # get index of freqs > peak bsnr  and < peak bsnr
    indsgt = np.where(f>f[a==a.max()])
    indslt = np.where(f<f[a==a.max()])
    # get those freqs
    fh = f[indsgt]; fl = f[indslt]
    frange_tol = 10; 


    if (len(indslt[0])!=0) and (len(indsgt[0]) !=0 ):
        afl= a[np.where(a[indslt]-snr_tol<=0)[0]+1]
        ffl = f[np.where(a[indslt]-snr_tol<=0)[0]+1]
        indl= np.where(afl-snr_tol>0)[0]
        ia = -1

        if len (indl)+ia > 0:
            if indl[ia] -  indl[ia-1] <= 3:
                ia = ia-1

        if len(indl) != 0:
            lfl = ffl [indl[ia]]
        else:
            lfl= np.array([])

        nh=0     
        if len((np.where(a[indsgt]-snr_tol<=0)[0]-1)) != 0:
            ind = (np.where(a[indsgt]-snr_tol<=0)[0]-1)[0]
            for ih in range (indsgt[0][ind], (indsgt[0]).max()+1):
                if a[ih] < snr_tol:
                    nh+= f[ih]-f[ih-1]
                else:
                    nh=0

                if nh <= frange_tol:
                    if ih == (indsgt[0]).max():
                        #ufl = f[ih -nh]
                        ufl = fh[np.where(a[indsgt]-snr_tol<=0)[0]-1][0]
                elif nh > frange_tol:
                    if ih == (indsgt[0]).max():
                        ufl = fh[np.where(a[indsgt]-snr_tol<=0)[0]-1][0]
                    else:
                        ufl = f [ih]
                    break
        else:
            ufl = fh[-1]

    else:
        lfl= np.array([])
        ufl= np.array([])


    return lfl, ufl

    

       
        

    
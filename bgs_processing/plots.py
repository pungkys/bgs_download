#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  5 10:09:20 2022

@author: psuroyo
"""

""" Function to plot traces and seismic phase windows """

import obspy
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['ps.fonttype'] = 42
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['svg.fonttype'] = 'none'
from matplotlib.dates import num2date
import numpy as np


def plot_traces(st, plot_theoreticals=False, plot_windows=False, conv=1e-9,
                    bft=1, aftt=180, sig=None, noise=None, save=None):

    sharey=False
    stc = stream_distance_sort(st)
    if conv is None:
        conv=1
        stc.normalize()
        sharey=True

    if sig is not None and noise is not None:
        sig = stream_distance_sort(sig)
        noise = stream_distance_sort(noise)

    fig, ax = plt.subplots(len(stc), 1, sharex=True, sharey=sharey, figsize=(14,len(stc)*3))
    if len(stc) > 1:
        ax = ax.flatten()
    else:
        ax=[ax]
    for i, tr in enumerate(stc):

        if plot_windows:
            # get window start and end times
            sts = sig[i].stats['wstart'], sig[i].stats['wend']
            nts = noise[i].stats['wstart'], noise[i].stats['wend']

            tr.trim(nts[0]-bft, sts[1]+aftt)

            for ts, tn in zip(sts, nts):
                ts, tn = num2date(ts.matplotlib_date), num2date(tn.matplotlib_date)
                ax[i].vlines(ts,tr.data.min()*conv,tr.data.max()*conv,color='k')
                ax[i].vlines(tn,tr.data.min()*conv,tr.data.max()*conv,color='blue')

        if plot_theoreticals:

            try:

#                 if not plot_windows:
#                     # we should trim it down to some time before and after the p arrival (assuming we trust it)
#                     tr.trim(tr.stats['p_time']-bft, tr.stats['p_time']+aftt)

                p = num2date(tr.stats['p_time'].matplotlib_date)
                s = num2date(tr.stats['s_time'].matplotlib_date)
                ax[i].vlines(p, tr.data.min()*conv, tr.data.max()*conv,
                    linestyles='dashed', color='blue', label='Pg')
                ax[i].vlines(s, tr.data.min()*conv, tr.data.max()*conv,
                    linestyles='dashed', color='red', label='Sg')
            except KeyError:
                pass

        time = num2date(np.array([
            (tr.stats.starttime+(tr.stats.delta*(
                i+1))).matplotlib_date for i in range(len(tr.data))]))

        ax[i].plot(time, tr.data*conv, color='grey', label=tr.id, zorder=1)
        try:
            ax[i].set_title("Repi: {:.2f} km, Rhyp: {:.2f} km".format(
                tr.stats['repi'], tr.stats['rhyp']),fontsize = 8)
        except KeyError:
            pass
        ax[i].legend(loc='upper right')
    ax[-1].set_xlabel('Time (UTC)')
    fig.suptitle(str(st[0].stats.otime))
    fig.tight_layout()
    if save is not None:
        assert type(save) is str
        fig.savefig(save)
        fig.clear()
        plt.close(fig)
        print("deleted td fig")

def plot_windows(st, conv=1e-9, bft=1, aftt=60, pwave= None, swave=None,
                 cwave= None, noise=None, save=None):
    style = dict(size=10, color='gray')
    sharey=False
    stc = stream_distance_sort(st)
    if conv is None:
        conv=1
        stc.normalize()
        sharey=True

    if st is not None and noise is not None:
        st = stream_distance_sort(st)
        noise = stream_distance_sort(noise)
    if pwave is not None and swave is not None and cwave is not None:
        pwave = stream_distance_sort(pwave)
        swave = stream_distance_sort(swave)
        cwave = stream_distance_sort(cwave)
        
    fig, ax = plt.subplots(len(stc), 1, sharex=True, sharey=sharey, figsize=(14,len(stc)*3))
    if len(stc) > 1:
        ax = ax.flatten()
    else:
        ax=[ax]
    for i, tr in enumerate(stc):


        # get window start and end times
        sts = st[i].stats['wstart'], st[i].stats['wend']
        nts = noise[i].stats['wstart'], noise[i].stats['wend']
        pwts = pwave[i].stats['wstart'], pwave[i].stats['wend']
        swts = swave[i].stats['wstart'], swave[i].stats['wend']
        cwts = cwave[i].stats['wstart'], cwave[i].stats['wend']

        tr.trim(nts[0]-bft, sts[1]+aftt)

        for ts, tn, tpw, tsw, tcw in zip(sts, nts, pwts, swts, cwts):
            ts, tn = num2date(ts.matplotlib_date), num2date(tn.matplotlib_date)
            tpw, tsw = num2date(tpw.matplotlib_date), num2date(tsw.matplotlib_date)
            tcw = num2date(tcw.matplotlib_date)
            ax[i].vlines(tn,tr.data.min()*conv,tr.data.max()*conv,color='grey')
            ax[i].vlines(tpw,tr.data.min()*conv,tr.data.max()*conv,color='blue')
            ax[i].vlines(tsw,tr.data.min()*conv,tr.data.max()*conv,color='r')
            ax[i].vlines(tcw,tr.data.min()*conv,tr.data.max()*conv,color='purple')
        
        ax[i].text(nts[0], tr.data.max()*conv, 'noise',ha='center', **style)
        ax[i].text(pwts[0], tr.data.max()*conv, 'tp',ha='center', **style)
        ax[i].text(swts[0], tr.data.max()*conv,'ts',ha='center', **style)
        ax[i].text(cwts[0], tr.data.max()*conv, 'tc',ha='center', **style)

        time = num2date(np.array([
            (tr.stats.starttime+(tr.stats.delta*(
                i+1))).matplotlib_date for i in range(len(tr.data))]))

        ax[i].plot(time, tr.data*conv, color='grey', label=tr.id, zorder=1)
        try:
            ax[i].set_title("Repi: {:.2f} km, Rhyp: {:.2f} km".format(
                tr.stats['repi'], tr.stats['rhyp']),fontsize = 8)
        except KeyError:
            pass
        ax[i].legend(loc='upper right')
    ax[-1].set_xlabel('Time (UTC)')
    fig.suptitle(str(st[0].stats.otime))
    fig.tight_layout()
    if save is not None:
        assert type(save) is str
        fig.savefig(save)
        fig.clear()
        plt.close(fig)
        print("deleted td fig")

def stream_distance_sort(st, dist_met='repi'):
    """
    Sorted makes a copy so you must save it back to rhe stream
    then force the user to save a new copy. NOT INPLACE!!!
    """
    try:
        st = obspy.Stream(sorted(st, key=lambda x: x.stats[dist_met]))
    except KeyError:
        print('WARNING: No distance info, stream not sorted by distance.')

    return st.copy()
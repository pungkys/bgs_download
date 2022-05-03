#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 16 22:02:30 2022

@author: psuroyo
"""
import os
import pandas as pd
from obspy import read
from connect import connect_bgs, list_bgs, read_bgs

path ="/Volumes/Samsung_T5/Secondment_GFZ/Catalog.csv"
df = pd.read_csv(path, header=0)
local_path = "/Volumes/Samsung_T5/Secondment_GFZ/"
continuous_id = df['continuous id']
with connect_bgs() as ftp:
    print('connect to  bgs ftp')
    for i in range (len(continuous_id)):
        filename = df['continuous id'][i].split(".")
        net = filename [0]
        sta = filename [1]
        cha = filename [3]
        year = filename [5]
        day = filename [6]
        name = df['continuous id'][i]
        event = df['eventid'][i]
        if year !="2018" :
            ftp_year = os.path.join (year)
            list_sta = list_bgs(ftp, ftp_year)
            ftp.cwd("..")
            ftp.cwd("..")
            if any(ext in sta for ext in list_sta):
                ftp_sta = os.path.join (year, sta)
                list_cha = list_bgs(ftp, ftp_sta)
                ftp.cwd("..")
                ftp.cwd("..")
                ftp.cwd("..")
                print("cur here",cha,ftp.pwd())
                if any(ext in cha+".D" for ext in list_cha):
                    ftp_path = os.path.join (year,sta,cha+".D")
                    list_events = list_bgs(ftp, ftp_path)
                    print("before evnts",ftp.pwd())
                    if any(ext in name for ext in list_events):
                        print(ftp.pwd())
                        print("any ", name)
                        wave_path = os.path.join('/',ftp_path,name)
                        bio_st = read_bgs(ftp, wave_path)
                        if bio_st != None: # some of the file is hanging in the ftp -> broken file, so skip
                            if len( bio_st.getvalue())!=0 : # some of the file contains 0 bytes, then skip
                                st = read (bio_st, format='mseed')
                                for tr in st:
                                    new_path = os.path.join(local_path,"continuous",year,net,sta)
                                    filename = net+"."+sta+".00."+cha+event
                                    save = os.path.join(new_path, filename)
                                    if not os.path.exists(os.path.dirname(save)):
                                        os.makedirs(os.path.dirname(save))
                                        os.chdir(os.path.dirname(save))
                                    tr.write(save,format="MSEED")
                                    print("loc after save", ftp.pwd())
                                    print(i)
                ftp.cwd("..")
                ftp.cwd("..")
                ftp.cwd("..")
    #if there is a path than store


path ="/Volumes/Samsung_T5/Secondment_GFZ/missing_stations.csv"
de = pd.read_csv(path, header=0)
a=[]
for i in range(len(de['station missing'])):
    sta = de['station missing'][i].split("..")
    sta = sta[0]
    if sta not in a:
        a.append(sta)

list_missing_sta= pd.DataFrame({'missing sta': a})
list_missing_sta.to_csv(os.path.join('/Volumes/Samsung_T5/Secondment_GFZ/',"list_missing_sta.csv"),header=True, index=True)
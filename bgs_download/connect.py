#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  4 15:12:58 2022

@author: psuroyo
"""
from ftplib import FTP
from io import BytesIO
from contextlib import contextmanager
import os

@contextmanager
def connect_bgs() -> FTP:
    try:
        ftp = FTP('seiswav.bgs.ac.uk')
        ftp.connect()
        ftp.login()
        yield ftp
    finally:
        print("quit")
        ftp.quit()

def list_bgs(ftp_con: FTP, folder_name: str):
    ftp_con.cwd(folder_name)
    return ftp_con.nlst()


def return_folder_bgs (ftp_con: FTP):
    for i in range (len(ftp_con.pwd())):
        ftp_con.cwd("..")
    return ftp_con.cwd("/")
    

def read_bgs(ftp_con: FTP, wave_path: str):
    try:
        bio = BytesIO()
        ftp_con.retrbinary(f'RETR {os.path.basename(wave_path)}', bio.write)
        bio.seek(0) 
        return bio
    except:
        print("File not available:",os.path.basename(wave_path) )
        return None
    
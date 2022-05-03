#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 14 16:52:33 2022

@author: psuroyo
"""
import h5py
import os
import pickle

def write_hdf(path, filename, data_matrix):
    # Write data to HDF5
    filepath = os.path.join(path,filename)
    with h5py.File(filepath, "w") as data_file:
        data_file.create_dataset("group_name", data=data_matrix)
    return data_file

def read_hdf(path, filename):
    filepath = os.path.join(path,filename)
    with h5py.File(filepath, "r") as f:
        # List all groups
        a_group_key = list(f.keys())[0]

        # Get the data
        data = list(f[a_group_key])
    return data

def write_methods(path, thing, method):
    """
    write_methods function has all of necesary commands to write objects in
    number of formats.
    """
    
    if method.lower() == 'pickle':
        with open(path, 'wb') as f:
                pickle.dump(thing, f)
    else:
        raise TypeError("{} method is not currently supported".format(method.lower()))


def read_methods(path, method):
    """
    write_methods function has all of necesary commands to write objects in
    number of formats.
    """

    if method.lower() == 'pickle':
        with open(path, 'rb') as f:
            obj = pickle.load(f)
        return obj
    else:
        raise TypeError("{} method is not currently supported".format(method.lower()))

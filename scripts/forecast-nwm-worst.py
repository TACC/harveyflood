# create worst scenario NWM channel_rt forecast netcdf from NWM forecasts
# Yan Y. Liu <yanliu@illinois.edu>
# 02/02/2017

# This is a modified version by TACC on Sep 1 2017
# Si Liu, Cyrus Proctor, Niall Gaffney, Xing Zheng

import sys, os, string, time, re, getopt, glob, shutil, math
import osr
import netCDF4
import numpy as np
from osgeo import gdal
from osgeo import ogr
import pandas as pd
import xarray as xr
from datetime import datetime
import csv
#import pytz

# open one nwm nc file and update comidlist and Qlist with larger Qs
def updateMax(ncdir = '', ncfile = '', comidlist = [], Qlist = [], tlist = [], h = {}):
    f = ncdir + "/" + ncfile
    t = float(ncfile.split(".")[-3][1:])
    # open nwm netcdf file
    rootgrp = netCDF4.Dataset(f, 'r')
    intype='channel_rt'
    metadata_dims = ['feature_id']
    dimsize = len(rootgrp.dimensions[metadata_dims[0]]) # num rows
    # create attr data for COMID and flowstream attr
    comids_ref = rootgrp.variables['feature_id']
    Qs_ref = rootgrp.variables['streamflow']
    comids = np.copy(comids_ref) 
    Qs = np.copy(Qs_ref)
    # close netcdf file
    rootgrp.close()

    # scan Qs and update 
    num_updated = 0
    num_new = 0
    for i in range(dimsize):
        comid = comids[i]
        Q = Qs[i]
        if not comid in h: # new comid
            if Q <= 0.0:
                continue
            comidlist.append(comid)
            Qlist.append(Q)
            tlist.append(t)
            h[comid] =  len(comidlist) - 1
            num_new += 1
        else: # update
            index = h[comid]
            if Q > Qlist[index]:
                Qlist[index] = Q
                tlist[index] = t
                num_updated += 1
    print datetime.now().strftime("%Y-%m-%d %H:%M:%S : calcMax ") + ncfile + " stations:" + str(dimsize) +  " new:" + str(num_new) +  " updated:" + str(num_updated) 
    sys.stdout.flush()

# open files and calc the max Q for each comid seen
def calcMax(ncdir = '', nclist = None, comidlist = [], Qlist = [], tlist = []):
    h = {} # hash for COMID and array index
    # create max data in memory
    for ncfile in nclist:
        print datetime.now().strftime("%Y-%m-%d %H:%M:%S : calcMax ") + ncfile + " hashs:" + str(len(h)) +  " comids:" + str(len(comidlist)) +  " Qs:" + str(len(Qlist)) 
        sys.stdout.flush()
        updateMax(ncdir, ncfile, comidlist, Qlist, tlist, h)
    h = None

# save as netcdf
def saveWorstFC(of = '', comidlist = [], Qlist = [], tlist = [], samplefile = ''):
    # get attributes to keep from one input nc file
    rootgrp = netCDF4.Dataset(samplefile, 'r')
    global_attrs={att:val for att,val in rootgrp.__dict__.iteritems()}
    timestamp_str=global_attrs['model_output_valid_time']
    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d_%H:%M:%S') # read
    init_timestamp_str=global_attrs['model_initialization_time']
    init_timestamp = datetime.strptime(init_timestamp_str, '%Y-%m-%d_%H:%M:%S') # read
    init_t = init_timestamp.strftime('%Y%m%d_%H%M%S') # reformat timestampe output
    rootgrp.close() # close netcdf file to save memory
    # create output data
    xds = xr.Dataset({
        'station_id': (['station'], comidlist),
        'streamflow': (['station'], Qlist),
        'max_time_step': (['station'], tlist)
    })
    xds.attrs = {
        'NFIESubject': 'worst-scenario forecast calculated from NOAA NWM',
        'model_initialization_time': init_timestamp_str,
        'model_output_valid_time': timestamp_str,
        'Description': 'For one nwm forecast that has n forecast timestamps, calculate the max streamflow for each COMID and save it as worst scenario forecast.'
    }
    xds['station_id'].attrs = { 'units': 'station', 'long_name': 'Station id'}
    xds['streamflow'].attrs = { 'units': 'meter^3 / sec', 'long_name': 'River Flow'}
    xds['max_time_step'].attrs = { 'units': 'hour', 'long_name': 'Peak Time'}
    # save
    print datetime.now().strftime("%Y-%m-%d %H:%M:%S : ") + "Writing netcdf output " + of
    sys.stdout.flush()
    xds.to_netcdf(of)
    print datetime.now().strftime("%Y-%m-%d %H:%M:%S : ") + "netcdf written."
    sys.stdout.flush()
        

## create worst-scenario nwm forecast for all the forcast time slots
## in one NOAA forcase initialization timestamp
# input 1: list of nwm forecast netcdf files
# input 2: output nc file path

# This is a modified version by TACC on Sep 1 2017
# Si Liu, Cyrus Proctor, Niall Gaffney, Xing Zheng

#python /work/projects/TexasFlood/scripts/forecast-nwm-worst.py  /work/projects/TexasFlood/data/para/nwm.20170901/short_range    "nwm.t16z.short_range.channel_rt.f016.conus.nc nwm.t16z.short_range.channel_rt.f017.conus.nc nwm.t16z.short_range.channel_rt.f018.conus.nc" /work/projects/TexasFlood/outputs-1/firsttry.nc

if __name__ == '__main__':
    ncdir = sys.argv[1] # dir of the nwm nc files
    nclist = sys.argv[2].split() # list of nwm nc files, separated by space
    of = sys.argv[3] # output nc file path

    for f in nclist:
        if not os.path.isfile(ncdir + '/' + f) :
            print "Input nc file does not exist: " + f
            sys.exit(1)

    print datetime.now().strftime("%Y-%m-%d %H:%M:%S : ") + " Input has " + str(len(nclist)) + " forecasts."
    sys.stdout.flush()
    comidlist = []
    Qlist = []
    tlist = []
    calcMax(ncdir, nclist, comidlist, Qlist, tlist)
    saveWorstFC(of, comidlist, Qlist, tlist, ncdir + '/' + nclist[len(nclist)-1]) # use last nc timestamp as fc timestamp

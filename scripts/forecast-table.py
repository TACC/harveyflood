# This is a modified version by TACC on Sep 1 2017
# Si Liu, Cyrus Proctor, Niall Gaffney, Xing Zheng

import sys, os, string, time, re, getopt, glob, shutil, math
import osr
import numpy as np
import netCDF4
import gdal
import ogr
import pandas as pd
import xarray as xr
from datetime import datetime
import csv
#import pytz

## create flood forecast table for all the COMIDs on CONUS
# input 1: the list of hydro property lookup table for each HUC6 code
# input 2: NOAA NWM forecast data, one timestamp
# input 3: NHDPlus MR geodb, for creating georeferenced anomaly shp files
# output: an inundation table for all the COMIDs on CONUS as netcdf and csv

# read input NOAA NWM netcdf file
def readForecast(in_nc = None):
    global comids
    global Qs
    global h
    # open netcdf file
    rootgrp = netCDF4.Dataset(in_nc, 'r')
    metadata_dims = ['station']
    dimsize = len(rootgrp.dimensions[metadata_dims[0]]) # num rows
    # create attr data for COMID and flowstream attr
    comids_ref = rootgrp.variables['station_id']
    Qs_ref = rootgrp.variables['streamflow']
    comids = np.copy(comids_ref) 
    Qs = np.copy(Qs_ref)

    rootgrp.close() # close netcdf file to save memory
    
    # check for invalid Qfc
    negCount = 0
    for i in range(Qs.size):
        if Qs[i] < 0.0:
            negCount += 1
    print "readForecast(): Warning: read " + str(negCount) + " forecasts with negative value. Will skip these COMIDs."

    # create hash table
    h = dict.fromkeys(comids)
    for i in range(0, len(comids)):
        h[comids[i]] = i
    sys.stdout.flush()


# interpolate H forecast from the static H and Q table dervied from HAND
# assuming the ascending order to stage heights for a COMID in CSV table
def Hinterpolate(Qfc = 0.0, Hlist = [], Qlist = [], count = 0, comid = 0):
    if Qfc <= 0:
        return -9999.0
    Q1 = None
    Q1i = 0
    Q2 = None
    Q2i = 0
    for i in range(0, count): # find two Qs that can interpolate H forecast
        if Qlist[i] < Qfc: # implicitly Q1 increases
            Q1 = Qlist[i]
            Q1i = i
        if Qlist[i] >= Qfc:
            Q2 = Qlist[i]
            Q2i = i
            break
    # linear interpolation
    if Q1 is None: # Qfc falls below the range of Qs
        return Hlist[0]
    if Q2 is None: # Qfc falls beyond the range of Qs
        Q1 = Qlist[count - 2]
        Q1i = count - 2 # count has to be >=2
        Q2 = Qlist[count - 1]
        Q2i = count - 1
    if Qlist[Q2i] < 0.00000001: # stage table is wrong
        return -9999.0 # can't predict
    if abs(Q2 - Q1) < 0.000001:
        print "WARNING: discharge data flat: count=" + str(count) + " Q1="+str(Q1)+" Q2="+str(Q2) + " Qfc=" + str(Qfc)
        return Hlist[Q2i]
    
    Hfc =  (Qfc - Q1) * (Hlist[Q2i] - Hlist[Q1i]) / (Q2 - Q1) + Hlist[Q1i]
    if Hfc > 25.0: # debug
        print "DEBUG: irregular Hfc: comid=" + str(comid) + " Hfc=" + str(Hfc) + " Qfc=" + str(Qfc) + " Q1=" + str(Q1) + " Q2=" + str(Q2) + " H1=" +str(Hlist[Q1i]) + " H2=" +str(Hlist[Q2i]) + " Q1i=" + str(Q1i) + " Q2i=" + str(Q2i)
    return Hfc


def updateH(comid = 0, fccount = 0, count = 0, numHeights = 83, h = None, Qs = None, Hlist = None, Qlist = None, comidlist = None, Hfclist = None, Qfclist = None):
    if count != numHeights:
        print "Warning: COMID " + str(comid) + " has <" + str(numHeights) + " rows on hydroprop table"
    j = h[comid]
    Qfc = Qs[j]
    if Qfc > 0.0:
        Hfc = Hinterpolate(Qfc, Hlist, Qlist, count, comid)
        if Hfc > 0.0:
            comidlist[fccount] = comid
            Hfclist[fccount] = Hfc
            Qfclist[fccount] = Qfc
            return 1
    return 0

def forecastH (tablelist = None, numHeights = 83, odir = None, ofilename = 'inun-hq-table'):
    global comids
    global Qs
    global h
    global comidlist 
    global Qfclist
    global Hfclist
    global fccount

    comidlist = np.zeros(len(comids), dtype='int64')
    Hfclist = np.zeros(len(comids), dtype='float64')
    Qfclist = np.zeros(len(comids), dtype='float64')
    fccount = 0
    missings = 0 # in hydro table but not in station hash
    nulls = 0 # null values that are not interpolated
    catchcount = 0 # count of catchments in hydro table
    for i in range(0, len(tablelist)): # scan each HUC's hydro prop table
        hpfile = tablelist[i]
        hpdata = None
        colcatchid = None # memory to store CatchId column
        colH = None # memory to store Stage column
        colQ = None # memory to store Discharge (m3s-1)/Discharge column
        filetype = hpfile.split('.')[-1]
        print hpfile + "   +++++++   " + filetype
        if filetype == 'csv':
            hpdata = pd.read_csv(hpfile)
            colcatchid = np.copy(hpdata['CatchId'])
            colH = np.copy(hpdata['Stage'])
            colQ = np.copy(hpdata['Discharge (m3s-1)'])
        elif filetype == 'nc':
            hpdata = netCDF4.Dataset(hpfile, 'r')
            colcatchid = np.copy(hpdata.variables['CatchId'])
            colH = np.copy(hpdata.variables['Stage'])
            colQ = np.copy(hpdata.variables['Discharge'])
        #TODO: error handling on unsupported file formats
        catchcount += (colcatchid.size / numHeights )
        print datetime.now().strftime("%Y-%m-%d %H:%M:%S : ") + hpfile + " : " + str(colcatchid.size) + " rows "
        sys.stdout.flush()
        comid = None
        count = 0
        Hlist = np.zeros(numHeights, dtype = 'float64')
        Qlist = np.zeros(numHeights, dtype = 'float64')
        #for index, row in csvdata.iterrows(): # loop each row of the table
        for i in range(colcatchid.size):
            catchid = int(colcatchid[i]) # get comid
            if not catchid in h: # hydro table doesn't have info for this comid
                missings += 1
                continue
            if comid is None:
                comid = catchid
            if comid != catchid : # time to interpolate
                if count < numHeights:
                    print "Warning: COMID " + str(comid) + " has <" + str(numHeights) + " rows on hydroprop table"
                j = h[comid]
                Qfc = Qs[j]
                if Qfc > 0.0:
                    Hfc = Hinterpolate(Qfc, Hlist, Qlist, count, comid)
                    if Hfc > 0.0:
                        comidlist[fccount] = comid
                        Hfclist[fccount] = Hfc
                        Qfclist[fccount] = Qfc
                        fccount += 1
                count = 0
                comid = catchid
                Hlist.fill(0)
                Qlist.fill(0)
            Hlist[count] = colH[i]
            Qlist[count] = colQ[i]
            count += 1
                # update the last comid
        if comid > 0:
            updated = updateH(comid, fccount, count, numHeights, h, Qs, Hlist, Qlist, comidlist, Hfclist, Qfclist)
            if updated == 1:
                fccount += 1
            else:
                nulls += 1
    print datetime.now().strftime("%Y-%m-%d %H:%M:%S : ") + "Read " + str(len(comids)) + " stations from NWM, " + str(catchcount) + " catchments from hydro table. " + str(missings) + " comids in hydro table but not in NWM. " + " generated " + str(fccount) + " forecasts"
    sys.stdout.flush()

    # save forecast output
    saveForecast(odir, ofilename) 


def saveForecast(odir = None, ofilename = 'inun-hq-table'):
    global comidlist 
    global Qfclist
    global Hfclist
    global fccount
    # save to netcdf
    xds = xr.Dataset({
        'COMID': (['index'], comidlist[:fccount]),
#        'Time': (['index'], [timestr for i in range(fccount)]),
        'H': (['index'], Hfclist[:fccount]),
        'Q': (['index'], Qfclist[:fccount])
    })
    xds.attrs = {
        'Subject': 'Inundation table derived from HAND and NOAA NWM for CONUS',
        'Initialization_Timestamp': '2017-08-24_12:00:00',
        'Timestamp': '2017-08-24_12:00:00',
        'Description': 'Inundation lookup table for all the COMIDs in CONUS through the aggregation of HUC6-level hydro property tables and NOAA NWM forecast netcdf on channel_rt'
    }
    xds['COMID'].attrs = { 'units': 'index', 'long_name': 'Catchment ID (COMID)'}
    xds['H'].attrs = { 'units': 'm', 'long_name': 'Inundation height forecast'}
    xds['Q'].attrs = { 'units': 'm3s-1', 'long_name': 'Inundation discharge forecast'}
    ofilenetcdf = odir + '/' + ofilename + '.nc'
    ofilecsv = odir + '/' + ofilename + '.csv'
    print datetime.now().strftime("%Y-%m-%d %H:%M:%S : ") + "Writing netcdf output " + ofilenetcdf 
    sys.stdout.flush()
    xds.to_netcdf(ofilenetcdf)
    print datetime.now().strftime("%Y-%m-%d %H:%M:%S : ") + "Writing csv output " + ofilecsv
    sys.stdout.flush()
    with open(ofilecsv, 'wb') as ofcsv:
        ow = csv.writer(ofcsv, delimiter = ',')
#        ow.writerow(['COMID', 'Time', 'H', 'Q']) # header
        ow.writerow(['COMID', 'H', 'Q']) # header
        for i in range(fccount):
#            ow.writerow([comidlist[i], timestr, Hfclist[i], Qfclist[i]])
            ow.writerow([comidlist[i], Hfclist[i], Qfclist[i]])

    print datetime.now().strftime("%Y-%m-%d %H:%M:%S : ") + "DONE"
    sys.stdout.flush()

# global variables
comids = None # COMID list from NWM forecast table
Qs = None # Q forecast list (discharge) from NWM
h = None # hash table for Q forecast lookup, indexed by COMID (station id)
comidlist = None # COMID list, intersection of NWM forecast and hydroprop
Qfclist = None # Q forecast
Hfclist = None # H forecast
fccount = 0 # length of the above three arrays

# python /projects/nfie/nfie-floodmap/test/forecast-table.py /gpfs_scratch/nfie/users/hydroprop/hydroprop-fulltable.nc /gpfs_scratch/nfie/users/yanliu/forecast/nwm.t00z.short_range.channel_rt.f001.conus.nc /gpfs_scratch/nfie/users/hydroprop
# python /projects/nfie/nfie-floodmap/test/forecast-table.py /gpfs_scratch/nfie/users/HUC6 /gpfs_scratch/nfie/users/yanliu/forecast/nwm.t00z.short_range.channel_rt.f001.conus.nc /gpfs_scratch/nfie/users/hydroprop
## forecast table test:
# python /projects/nfie/nfie-floodmap/test/forecast-table.py /gpfs_scratch/nfie/users/yanliu/forecast/test /gpfs_scratch/nfie/users/yanliu/forecast/nwm.t00z.short_range.channel_rt.f001.conus.nc /gpfs_scratch/nfie/users/yanliu/forecast/test
## anomaly map shp test:
# python /projects/nfie/nfie-floodmap/test/forecast-table.py /gpfs_scratch/nfie/users/yanliu/forecast/test /gpfs_scratch/nfie/users/yanliu/forecast/nwm.t10z.short_range.channel_rt.f010.conus.nc /gpfs_scratch/nfie/users/yanliu/forecast/test/anomaly /gpfs_scratch/usgs/nhd/NFIEGeoNational.gdb
if __name__ == '__main__':
    hpinput = sys.argv[1] # hydro property file root dir
    qfile = sys.argv[2] # NOAA NWM forecast netcdf path
    odir = sys.argv[3] # output netcdf path, directory must exist
    ofilename = qfile[:-4]
    readForecast(qfile) # read forecast, set up hash table
    huclist = []
    tablelist = []
    if os.path.isdir(hpinput):
        tabledir = hpinput
        # read dir list
        wildcard = os.path.join(tabledir, '*')
        dlist = glob.glob(wildcard)
        count = 0
        for d in dlist:
            if not os.path.isdir(d):
                continue
            hucid = os.path.basename(d)
            csvfile = d+'/'+'hydroprop-fulltable-'+hucid+'.csv'
            if not os.path.isfile(csvfile):
                continue
            tablelist += [ csvfile ]
            huclist += [ hucid ]
            count +=1
    else: # single netcdf file
        tablelist += [hpinput]
        count = 1
    print str(count) + " hydro property tables will be read."
    sys.stdout.flush()
    forecastH(tablelist, 83, odir, ofilename = os.path.basename(qfile)[:-4])

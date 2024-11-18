#!/u/robert.grumbine/env3.10/bin/python3
# python system
import os
import sys
import copy
from math import *
import datetime

# env libraries
import numpy as np
import numpy.ma as ma
import netCDF4 as nc
import pygrib

import pyproj

# shared
from match import *
from filtering import *
from tools import *
# mmablib
from utility import *

if (len(sys.argv) == 2):
    tmp = parse_8digits(int(sys.argv[1]) )
    start = tmp
    end   = tmp
    del tmp
elif (len(sys.argv) == 3):
    start = parse_8digits(int(sys.argv[1]) )
    end   = parse_8digits(int(sys.argv[2]) )
else:
    start = datetime.datetime(2024,1,3)
    end   = datetime.datetime(2024,2,29)

dt = datetime.timedelta(1)


#RG: Update to run if files present, alt: if desired output not present
tag = start
while (tag <= end): 
  tag8 = tag.strftime("%Y%m%d")
  tagj = tag.strftime("%Y%j")
  yy=tagj[0:4]
  print("date info:",tag8, tagj, yy, flush=True)
  #debug: exit(0)

  #---------------------------------------------------------------
  #---------------------------------------------------------------
  #                     Data Acquisition
  #---------------------------------------------------------------
  # Read in the ice fixed file (for distance to land, posteriori filter, ..)
  # ice_distance, ice_land, ice_post, ice_latitude, ice_longitude
  # Needs seaice_fixed_fields.nc in cwd
  
  #--
  fname='seaice_fixed_fields.nc'
  icefix = nc.Dataset(fname, 'r', format='NETCDF4')
  
  nlats = len(icefix.dimensions["nlats"])
  nlons = len(icefix.dimensions["nlons"])
  #debug: print("nlon nlat ",nlons, nlats, flush=True)
  
  ice_distance = np.zeros((nlats, nlons),dtype="float")
  ice_land = np.zeros((nlats, nlons))
  ice_post = np.zeros((nlats, nlons))
  
  ice_land      = icefix.variables["land"]     [:,:]
  ice_post      = icefix.variables["posteriori"][:,:]
  
  ice_distance  = icefix.variables["distance_to_land"][:,:]
  ice_distance /= 1000.   #Convert to km

  #debug: 
  """
  ice_longitude = np.zeros((nlats, nlons),dtype="double")
  ice_latitude = np.zeros((nlats, nlons),dtype="double")
  ice_longitude = icefix.variables["longitude"][:,:]
  ice_latitude  = icefix.variables["latitude"] [:,:]
  """
  #debug: print("ice_longitude shape ",ice_longitude.shape )
  #debug: print("read lon max ",ice_longitude.max(), flush=True )
  #debug: exit(0) 

  post_use_vals = [165, 173, 174]
  
  #---------------------------------------------------------------
  # Read in the satellite obs to matchup -- satobs class in match file
  # use icefix to filter vs. ice_post
  
  #tb_lr = np.zeros((amsr2_lr.ntb))
  #tb_hr = np.zeros((amsr2_hr.ntb))
  #sat_lr = amsr2_lr()
  #tmp = match(sat_lr)
  tb_lr = np.zeros((match.amsr2_lr.ntb))
  tb_hr = np.zeros((match.amsr2_hr.ntb))
  sat_lr = match.amsr2_lr()
  
  x = amsr2_lr(satid = 0, latitude = 0., longitude = 0.)
  tmp = match.match(x)
  
  allmatches = []
  #read in sat obs (text file, from scan of bufr)
  basedir='/u/robert.grumbine/noscrub/filter/txt/'
  ftmp='amsr2_'+tag8+'.txt.0'
  try:
      fin = open(basedir+ftmp,"r")
  except:
      print("failed to open matchups file ",basedir+ftmp)
      exit(1)
  k = int(0)
  for line in fin:
    if ("lr" in line):
      k += int(1)
      #debug: if (k%1000 == 0):
      #debug:   print("k/1000 = ",k/1000, flush=True)
      #RG: more efficient to work w. tmp directly? tmp.obs.read(line)
      x.read(line)
      tmp = match.match(x)
  
      # (j,i) = rg12th(self.obs.latitude, self.obs.longitude)
      # if ice_post[j,i] in post_use_vals
      #   append
      # else:
      #   nothing
      allmatches.append(tmp)
      allmatches[k-1] = copy.deepcopy(tmp)
      #debug: if (k > 30000): break
      #debug: allmatches[k-1].show()
  
  print(len(allmatches), "lr satellite obs")
  del x,tmp
  fin.close()

  #---------------------------------------------------------------
  # Add ice fixed info to matchups (ice_land, ice_post, ice_distance)
  #debug: print("zzzzzzzzzzzzzzzzzz icefix zzzzzzzzzzzzzzzzzzzz")
  for i in range(0,len(allmatches)):
    allmatches[i].add_icefix(ice_land, ice_post, ice_distance)
    #debug: allmatches[i].show()
  del ice_land, ice_post, ice_distance
  
  #---------------------------------------------------------------
  # Read ice analysis, add to matchup (icec)
  analy_base='/u/robert.grumbine/noscrub/sice/sice.'+tag8+'/'
  fname=analy_base+'seaice.t00z.5min.grb.grib2'
  try:
      grbs = pygrib.open(fname)
  except:
      print("failed to open grib2 analysis ",fname)
      exit(1)
  for x in grbs:
    #debug: print(x.shortName, x.name, x.level, x.typeOfLevel, x.paramId, x.forecastTime, flush=True)
    #debug: print(x, flush=True)
    #placeholder: 
    print(x.values.max(), x.values.min(), flush=True )
  icec = x.values
  
  #debug: print("zzzzzzzzzzzzzzzzzzzzzzzzzzz  icec zzzzzzzzzzzzzzzzzzzzzzzzzz")
  for i in range(0,len(allmatches)):
     allmatches[i].add_icec(icec)
     #debug:  if (i%1000 == 0):
     #debug:    allmatches[i].show()
  del x, grbs
  
  #debug: exit(0)
  
  #---------------------------------------------------------------
  # Read in IMS analysis, add to NH matchups
  
  # IMS Map projection from projection:proj4 in netcdf header
  proj4 = "+proj=stere +lat_0=90 +lat_ts=60 +lon_0=-80 +k=1 +x_0=0 +y_0=0 +a=6378137 +b=6356257 +units=m +no_defs" 
  
  ims_base='/u/robert.grumbine/noscrub/imstmp/'
  #subdirs: fname=ims_base+yy+'/ims'+tagj+'_4km_v1.3.nc'
  fname=ims_base+'/ims'+tagj+'_4km_v1.3.nc'
  
  try:
    ims = nc.Dataset(fname, 'r', format='NETCDF4')
  except:
    print("failed to open ims file ",fname)
    exit(1)
  
  nx = len(ims.dimensions["x"])
  ny = len(ims.dimensions["y"])
  #debug: print("nx ny ",nx, ny, flush=True)
  
  ims_x = np.zeros((nx),dtype="float")
  ims_y = np.zeros((ny),dtype="float")
  ims_value = np.zeros((ny, nx),dtype="byte")
  
  ims_x     = ims.variables["x"]     [:]
  ims_y     = ims.variables["y"]     [:]
  ims_value = ims.variables["IMS_Surface_Values"]  [0,:,:]
  
  pims = pyproj.Proj(proj4)
  
  def ims_invlocate(proj, latitude, longitude):
    (x,y) = proj(longitude, latitude)
    fi = x/4000. + 6144./2.
    fj = y/4000. + 6144./2.
    i = int(fi+0.5)
    j = int(fj+0.5)
    return (i,j)
  
  def is_land(ims, i, j, pm = 0):
    return (ims[j,i] == 2 or ims[j,i] == 4)
  
  # Add IMS to matchups
  # Loop over observations, find nearest IMS point, append i+-1, j+-1 ims (5 total values)
  # define an 'is ice' function, or 'partial ice'
  
  #debug: print("zzzzzzzzzzzzzzzzzzzzzzzzzzz  ims  zzzzzzzzzzzzzzzzzzzzzzzzzz")
  for i in range(0,len(allmatches)):
    allmatches[i].add_ims(ims_value, pims)
    #debug: allmatches[i].show()
  #debug: exit(0)
  
  
  #---------------------------------------------------------------
  # Use SST from qdoi v2, including its sea ice cover
  # Read sst analysis, add sst and analysis' ice conc to match (sst, ice_sst)
  sstbase='/u/robert.grumbine/static/oiv2/'
  fname=sstbase+'oisst-avhrr-v02r01.'+tag8+'.nc'
  
  try:
    sstgrid = nc.Dataset(fname, 'r', format='NETCDF4')
  except:
    print("failed to open sst file ",fname)
    exit(1)

  sst_nlats = len(sstgrid.dimensions["lat"])
  sst_nlons = len(sstgrid.dimensions["lon"])
  
  sst = np.zeros((sst_nlats, sst_nlons))
  ice_sst = np.zeros((sst_nlats, sst_nlons))
  #anom = np.zeros((sst_nlats, sst_nlons))
  #err  = np.zeros((sst_nlats, sst_nlons))
  
  sst   = sstgrid.variables["sst"][0,0,:,:]
  ice_sst   = sstgrid.variables["ice"][0,0,:,:]
  #anom  = sstgrid.variables["anom"] [0,0,:,:]
  #err   = sstgrid.variables["err"][0,0,:,:]
  
  #debug: print("zzzzzzzzzzzzzzzzzzzzzzzzzzz  sst  zzzzzzzzzzzzzzzzzzzzzzzzzz")
  for k in range(0,len(allmatches)):
    allmatches[k].add_oiv2(sst, ice_sst)
  
  #debug: print("done adding in sst, max = ",sst.max(), flush=True)
  #debug: exit(0)
  
  #---------------------------------------------------------------
  #  Now have all data in hand --- write it out
  try:
    fout = open("matched_"+tag8+".txt","w")
  except:
    print("failed to open output file ","matched_"+tag8+".txt")
    exit(1)
  
  # Bring in thinning from quick_thin.py
  for k in range(0,len(allmatches)):
      # if ice_post[j,i] in post_use_vals and ice.land, ice.post, ice.dist all ok 
      #   write out to fout
      # else:
      #   nothing
    allmatches[k].show(fout)
  fout.close()
  #---------------------------------------------------------------

  tag += dt


#!/usr/bin/env python3
import argparse
import glob
import os
import sys
import copy
import datetime

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import netCDF4 as nc
import pygrib

import cartopy.crs as ccrs
import cartopy.feature as cfeature

matplotlib.use('agg')

#PlateCaree
#LambertConformal
#LambertCylindrical
#NorthPolarStereo

def plot_map(lons, lats, data, lonrange, latrange, tag, fn):
    vmin = max(-1., np.nanmin(data))
    vmax = min( 1., np.nanmax(data))

    proj = ccrs.PlateCarree()
    #proj = ccrs.LambertConformal(central_longitude=-170, central_latitude=60., cutoff=25.)
    #proj = ccrs.NorthPolarStereo(true_scale_latitude=60.)
    #proj = ccrs.Stereographic(central_longitude=+170, central_latitude=60. )

    ax = plt.axes(projection = proj)
    fig = plt.figure(figsize=(640/50,480/50))
    #fig = plt.figure( )
    ax = fig.add_subplot(1, 1, 1, projection = proj)

    #ax.set_extent([-100, 100, 30, 90], crs = proj)
    ax.set_extent((lonrange[0],lonrange[1], latrange[0], latrange[1]), crs=ccrs.PlateCarree())

    xlocs = np.arange(min(lonrange[0],lonrange[1]), max(lonrange[0],lonrange[1]), 5.)
    ylocs = np.arange(min(latrange[0],latrange[1]), max(latrange[0],latrange[1]), 5.)
    ax.gridlines(crs=ccrs.PlateCarree(), xlocs=xlocs , ylocs=ylocs )

    #'natural earth' -- coast only -- ax.coastlines(resolution='10m')
    ax.add_feature(cfeature.GSHHSFeature(levels=[1], scale="c") )
    ax.add_feature(cfeature.GSHHSFeature(levels=[2,3,4], scale="l") )

    cbarlabel = '%s' % ("ice concentration")
    plttitle = 'Plot of %s' % (tag)
    plt.title(plttitle)

    #Establish the color bar
    #colors=matplotlib.colormaps.get_cmap('jet')
    #colors=matplotlib.colormaps.get_cmap('gray')
    colors=matplotlib.colormaps.get_cmap('terrain')

    cs = ax.pcolormesh(lons, lats, data,vmin=vmin,vmax=1.0,cmap=colors, transform=ccrs.PlateCarree() )
    cb = plt.colorbar(cs, extend='both', orientation='horizontal', shrink=0.5, pad=.04)
    cb.set_label(cbarlabel, fontsize=12)

    plt.savefig(fn+".png")

    plt.close('all')

#----------------------------------------------------------------
# Plot from sea ice grib analysis
dl = 1./12.
lons = np.arange(dl/2., 360., dl)
lats = np.arange(90-dl/2, -90., -dl)

# newfilter:
newbase="/u/robert.grumbine/noscrub/com/seaice_analysis/v4.6.0/seaice_analysis."
# oldfilter
#oldbase="/u/robert.grumbine/noscrub/sice/sice."
oldbase="/u/robert.grumbine/noscrub/sice/seaice_analysis."

dt = datetime.timedelta(1)
#start = datetime.datetime(2022,1,20)
#end   = datetime.datetime(2022,2,5)
#start = datetime.datetime(2022,3,3)
#end   = datetime.datetime(2022,3,23)
start = datetime.datetime(2023,3,11)
end   = datetime.datetime(2023,3,31)
working = start

while (working <= end):
  dtag = working.strftime("%Y%m%d")

  if (not os.path.exists(newbase+dtag+"/seaice.t00z.5min.grb.grib2") ):
    print("don't have ",newbase+dtag+"/seaice.t00z.5min.grb.grib2")
  else:
    grbs = pygrib.open(newbase+dtag+"/seaice.t00z.5min.grb.grib2")
    k = 0
    for x in grbs:
      k += 1
    newicec = x.values
  
    grbs = pygrib.open(oldbase+dtag+"/seaice.t00z.5min.grb.grib2")
    for x in grbs:
      k += 1
    oldicec = x.values
  
    delta = copy.deepcopy(oldicec)
    delta -= newicec
  
    #Newfoundland:
    region = "newf"
    lonrange = (-70., -30.)
    latrange = (35., 60.)
    plot_map(lons, lats, oldicec, lonrange, latrange, "oldfilter "+dtag, "old_"+region+"_"+dtag)
    plot_map(lons, lats, newicec, lonrange, latrange, "newfilter "+dtag, "new_"+region+"_"+dtag)
    plot_map(lons, lats, delta, lonrange, latrange, "delta old-new "+dtag, "delta_"+region+"_"+dtag)
    
    #Kuriles
    region = "kurile"
    lonrange = (135., 180.)
    latrange = (40., 65.)
    plot_map(lons, lats, oldicec, lonrange, latrange, "oldfilter "+dtag, "old_"+region+"_"+dtag)
    plot_map(lons, lats, newicec, lonrange, latrange, "newfilter "+dtag, "new_"+region+"_"+dtag)
    plot_map(lons, lats, delta, lonrange, latrange, "delta old-new "+dtag, "delta_"+region+"_"+dtag)
    
    #Drake Passage
    region = "drake"
    lonrange = (-80., -30.)
    latrange = (-80., -45.)
    plot_map(lons, lats, oldicec, lonrange, latrange, "oldfilter "+dtag, "old_"+region+"_"+dtag)
    plot_map(lons, lats, newicec, lonrange, latrange, "newfilter "+dtag, "new_"+region+"_"+dtag)
    plot_map(lons, lats, delta, lonrange, latrange, "delta old-new "+dtag, "delta_"+region+"_"+dtag)

  working += dt
  print(working, end, flush=True)



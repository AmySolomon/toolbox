#!/usr/bin/env python3
import argparse
import glob
import os

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import netCDF4 as nc

import cartopy.crs as ccrs
import cartopy.feature as cfeature

matplotlib.use('agg')

#PlateCaree
#LambertConformal
#LambertCylindrical
#NorthPolarStereo

def plot_world_map(lons, lats, data):
    vmin = np.nanmin(data)
    vmax = np.nanmax(data)

    proj = ccrs.LambertConformal(central_longitude=-170, central_latitude=60., cutoff=25.)
    #proj = ccrs.NorthPolarStereo(true_scale_latitude=60.)
    #proj = ccrs.Stereographic(central_longitude=+170, central_latitude=60. )

    ax  = plt.axes(projection = proj)
    fig = plt.figure(figsize=(640/50,480/50))
    ax  = fig.add_subplot(1, 1, 1, projection = proj)

    ax.set_extent((-220,-120, 40, 90), crs=ccrs.PlateCarree())
    ax.gridlines(crs=ccrs.PlateCarree(), 
                 xlocs=[-180, -170, -150, -120], 
                 ylocs=[40,50,60,66.6,70,80] )

    #'natural earth' -- coast only -- ax.coastlines(resolution='10m')
    ax.add_feature(cfeature.GSHHSFeature(levels=[1,2,3,4], scale="l") )

    plttitle = 'Plot of variable %s' % ("hello2")
    plt.title(plttitle)

    #Establish the color bar
    #colors=matplotlib.cm.get_cmap('jet')
    colors=matplotlib.cm.get_cmap('gray')
    colors=matplotlib.cm.get_cmap('terrain')

    #cs = ax.pcolormesh(lons, lats, data,vmin=vmin,vmax=vmax,cmap=colors, transform=ccrs.PlateCarree() )
    cs = ax.pcolormesh(lons, lats, data,vmin=30.,vmax=vmax,cmap=colors, transform=ccrs.PlateCarree() )
    cb = plt.colorbar(cs, extend='both', orientation='horizontal', shrink=0.5, pad=.04)
    cbarlabel = '%s' % ("hello1")
    cb.set_label(cbarlabel, fontsize=12)

    plt.savefig("hello3.png")

    plt.close('all')

#----------------------------------------------------------------
lons = range(-360,360)
lats = range(-90,90)
data = np.zeros((len(lats),len(lons)))

for i in range(-360,360):
  data[:,i] = lats[:] 

plot_world_map(lons, lats, data)

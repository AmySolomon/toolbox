import sys
import os
import datetime

from math import *
import numpy as np
import numpy.ma as ma

import netCDF4
from netCDF4 import Dataset

import networkx as netx

# User-written
from functions import *
from graphics import *

#--------------------------------------------------------
base = os.environ['base']

#tag = datetime.datetime(2022,4,1)
#debug: print("args ",sys.argv, flush=True)
tag = datetime.datetime(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]) )

#debug -- set up a bogus line to see where it starts to fail to be plotted:
tlons = np.arange(-170., -75., 0.1)
tlats = np.linspace(60, 80, len(tlons))
pseudo_length = 5000
#debug: show(tlats, tlons, tag, hours = 0, cost = pseudo_length)
#debug: exit(0)

#dname = tag.strftime("%Y%m%d")
fname = "REB2."+tag.strftime("%Y-%m-%d") + ".nc"
#fname = "REB2.2024-11-14.nc"
if (not os.path.exists(base+'/'+"/"+fname) ):
  print("could not open ",base+'/'+"/"+fname, flush=True)
  exit(1)

fin = Dataset(base+'/'+"/"+fname, "r")
nx = len(fin.dimensions["ni"])
ny = len(fin.dimensions["nj"])
lons = fin.variables["TLON"][:,:]
lats = fin.variables["TLAT"][:,:]
tarea = fin.variables["tarea"][:,:]

#debug: show(tlats, tlons, tag, hours = 300, cost = pseudo_length)
#debug: exit(0)

for tstep in range(0,40):
#debug: for tstep in range(0,2):
  aice = fin.variables["aice_h"][tstep,:,:]
  hs   = fin.variables["hs_h"][tstep,:,:]
  hi   = fin.variables["hi_h"][tstep,:,:]
  uvel = fin.variables["uvel_h"][tstep,:,:]
  vvel = fin.variables["vvel_h"][tstep,:,:]
  tsfc = fin.variables["Tsfc_h"][tstep,:,:]
  uatm = fin.variables["uatm_h"][tstep,:,:]
  vatm = fin.variables["vatm_h"][tstep,:,:]
  sst  = fin.variables["sst_h"][tstep,:,:]
  sss  = fin.variables["sss_h"][tstep,:,:]
  tair = fin.variables["Tair_h"][tstep,:,:]
  aice = fin.variables["aice_h"][tstep,:,:]
  aice = fin.variables["aice_h"][tstep,:,:]

  #debug: print("sample for tstep ",tstep,aice.max(), aice.min(), 
  #debug:                tsfc.max(), sst.max(), tair.max() )

  # One may/must treat these fields as masked, as in masked arrays
  indices = tair.nonzero()
  #debug: print(len(indices), len(indices[0]), flush=True )

# flag is 1 = land, 0 = not-land
  land = np.zeros((ny,nx))
  land.fill(1)
  for k in range(0,len(indices[0]) ):
    j = indices[0][k]
    i = indices[1][k]
    land[j,i] = 0.0 

  #--------------------------------------------------------
  # define a subset to search within for paths
  # NWP Domain:
  latmin = 64.0
  latmax = 82.0
  lonmin = 185.0
  lonmax = 290.0

  # Construct nodes -- brute force looping over all grid points:
  # RG: Rtofs does this more elegantly, using masked arrays.
  #     The coarser and regional cafs grid doesn't demand this the way 
  #       the global, higher resolution RTOFS does
  offmap = 0
  nodemap = np.full((ny,nx),int(offmap), dtype="int")
 
  #debug:  show(tlats, tlons, tag, hours = 400+tstep, cost = pseudo_length)
  #debug:  exit(0)

  #Not a directed graph
  G = netx.Graph()
  
  #1 -> steps in i,j space
  #2 -> meters
  #3 -> weighted by polar class
  #4 -> weight by 1./(1.1-aice)
  cost_type = 4
  
  k = int(1)
  for i in range(0,nx):
    for j in range(0,ny):
      #debug: if (k%1000 == 0):
        #debug: print("adding nodes, i = ",i, flush=True)
      if (lats[j,i] > latmin and lats[j,i] < latmax and
          lons[j,i] > lonmin and lons[j,i] < lonmax     ):
        if (land[j,i] == 0):
          nodemap[j,i] = int(k)
          G.add_node(k, i = i, j =j, lat = lats[j,i], lon = lons[j,i],  aice=aice[j,i], hi = hi[j,i])
          k += int(1)
  #debug: print("Done adding nodes, k=",k, flush=True)
  
  # Construct edges between nodes
  k = 0
  for j in range(0,ny):
    jp = j + 1
    jm = j - 1
    for i in range(0,nx):
      ip = i+1
      im = i-1
      if (not (lats[j,i] > latmin and lats[j,i] < latmax and
               lons[j,i] > lonmin and lons[j,i] < lonmax     )    ):
        continue
      n = nodemap[j,i]
      if (n == 0):
        continue
  
      if (im >= 0):
        if (nodemap[j,im] != offmap):
          weight = cost(cost_type, lat1 = lats[j,i], lon1 = lons[j,i], lat2 = lats[j,im], lon2 = lons[j,im], aice = aice[j,i])
          G.add_edge(n, nodemap[j,im], weight= weight)
          k += 1
  
      if (ip < nx):
        if (nodemap[j,ip] != offmap):
          weight = cost(cost_type, lat1 = lats[j,i], lon1 = lons[j,i], lat2 = lats[j,ip], lon2 = lons[j,ip], aice = aice[j,i])
          G.add_edge(n, nodemap[j,ip], weight = weight)
          k += 1
  
      if (jp < ny ):
        if (nodemap[jp,i] != offmap):
          weight = cost(cost_type, lat1 = lats[j,i], lon1 = lons[j,i], lat2 = lats[jp,i], lon2 = lons[jp,i], aice = aice[j,i])
          G.add_edge(n, nodemap[jp,i], weight = weight)
          k += 1
        if (im >= 0):
          if (nodemap[jp,im] != offmap):
            weight = cost(cost_type, lat1 = lats[j,i], lon1 = lons[j,i], lat2 = lats[jp,im], lon2 = lons[jp,im], aice = aice[j,i])
            G.add_edge(n, nodemap[jp,im], weight = weight)
            k += 1
        if (ip < nx):
          if (nodemap[jp,ip] != offmap):
            weight = cost(cost_type, lat1 = lats[j,i], lon1 = lons[j,i], lat2 = lats[jp,ip], lon2 = lons[jp,ip], aice = aice[j,i])
            G.add_edge(n, nodemap[jp,ip], weight = weight)
            k += 1
  
      if (jm >= 0 ):
        if (nodemap[jm,i] != offmap):
          weight = cost(cost_type, lat1 = lats[j,i], lon1 = lons[j,i], lat2 = lats[jm,i], lon2 = lons[jm,i], aice = aice[j,i])
          G.add_edge(n, nodemap[jm,i], weight = weight)
          k += 1
        if (im >= 0):
          if (nodemap[jm,im] != offmap):
            weight = cost(cost_type, lat1 = lats[j,i], lon1 = lons[j,i], lat2 = lats[jm,im], lon2 = lons[jm,im], aice = aice[j,i])
            G.add_edge(n, nodemap[jm,im], weight = weight)
            k += 1
        if (ip < nx):
          if (nodemap[jm,ip] != offmap):
            weight = cost(cost_type, lat1 = lats[j,i], lon1 = lons[j,i], lat2 = lats[jm,ip], lon2 = lons[jm,ip], aice = aice[j,i])
            G.add_edge(n, nodemap[jm,ip], weight = weight)
            k += 1

  #debug: print("Have constructed graph, number of edges =",k, len(G.edges), flush=True)
  #debug: exit(0)

  #--------------------------------------------------------
  #    Select start and finish points
  
  ##start in Bering strait
  ##Lat = 65.68, Lon = -168.59
  #i_start = int(0.5 + (360. - 168.59)*12.)
  #j_start = int(0.5 + (90.0 -  65.68)*12.)
  ##finish in ... Baffin Bay
  ##Lat = 74.0 N, -78.0
  #i_finish = int(0.5 + (360. - 78.0)*12.)
  #j_finish = int(0.5 + (90.0 - 74.0)*12.)
  
  #for j in range(0,ny):
  #  for i in range(0, nx):
  #      print(i, j, nodemap[j,i])
  
  #exit(0)
  
  # cafs grid is different
  #RG: Need a findij function (65.68 N, -168.59), (64.0, -78.0) 
  #RG: is baffin bay insize cafs domain?
  i_start = int(287)
  j_start = int(67)
  #i_finish = int(415)
  #j_finish = int(420)
  i_finish = int(396) 
  j_finish = int(344) 
  #debug: print("start: ",lons[j_start, i_start], lats[j_start, i_start] )
  #debug: print("finis: ",lons[j_finish, i_finish], lats[j_finish, i_finish] )
  
  # Quick check to see whether there are _any_ paths:
  start  = nodemap[j_start, i_start]
  finish = nodemap[j_finish, i_finish]
  #debug: print("start node ",G.nodes[start])
  #debug: print("finish node ",G.nodes[finish])
  #debug: print(i_start, j_start, i_finish, j_finish, start, finish)
  print("Is there a path from start to finish? ",netx.has_path(G,start,finish ), flush=True )
  if (not netx.has_path(G,start,finish )):
    exit(1)

  #debug:  show(tlats, tlons, tag, hours = 500+tstep, cost = pseudo_length)
  #debug:  exit(0)

  #------------------------------------------------
  path = netx.dijkstra_path(G,start, finish)
  print("dijkstra length and score ", len(path), 
         netx.dijkstra_path_length(G, start, finish), flush=True)
  pseudo_length = netx.dijkstra_path_length(G, start, finish)
  
  graphic_lats = np.zeros((len(path)))
  graphic_lons = np.zeros((len(path)))
  for k in range(0,len(path)):
    print(k,G.nodes[path[k]])
    graphic_lats[k] = G.nodes[path[k]]['lat']
    graphic_lons[k] = G.nodes[path[k]]['lon']
    #print(k,
    #      G.nodes[path[k]]['i'], G.nodes[path[k]]['j'],
    #      G.nodes[path[k]]['lon'], G.nodes[path[k]]['lat'],
    #      G.nodes[path[k]]['aice'], G.nodes[path[k]]['hi'],
    #      flush=True )
  print("",flush=True)
  
#----------- kml output ---------------------------------
  kmlout_path("path_"+tag.strftime("%Y%m%d")+"_"+"{:d}".format((tstep+1)*6)+".kml", G, path)

#----------- Graphics ---------------------------------
  #debug:  show(tlats, tlons, tag, hours = 600+tstep, cost = pseudo_length)
  #debug:  exit(0)

  show(graphic_lats, graphic_lons, tag, hours = (tstep+1)*6, cost = pseudo_length)
  del graphic_lats, graphic_lons
  #debug:  exit(0)

#-----------------------------------------------------


"""
Reference:
USCG Healy
maximum speed = 31 km/h
cruising      = 26 km/h
1.4 m ice     =  5.6 km/h

At cruising speed, 2965 km = 114 hours; about 5 days vs. the 10 of CAFS model lead time
"""

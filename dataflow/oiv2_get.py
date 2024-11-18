#!/usr/bin/python3

#Python3 -- important to add urllib.request, decode
import os
import re

#--------------------------------
import datetime
from datetime import date
from datetime import timedelta

dt = datetime.timedelta(1)
today = date.today()
startdate = today
startdate -= 15*dt
#startdate = datetime.date(2024,3,6)


# First date of OIv2
#enddate = datetime.date(1981,9,1)
# current from here back:
enddate = datetime.date(2024,3,1)

#---------------------------------------------------------
import urllib
import urllib.request
baseurl='https://www.ncei.noaa.gov/data/sea-surface-temperature-optimum-interpolation/v2.1/access/avhrr/'
tdate = startdate

#run back in time from 'today'
while (tdate >= enddate):
  #while (tdate < datetime.datetime(1990,9,1) ):
  ym=tdate.strftime("%Y%m")
  ymd=tdate.strftime("%Y%m%d")
  #print(tdate, ym, ymd)
  #print(baseurl+ym+'/oisst-avhrr-v02r01.'+ymd+'.nc')
  oname = 'oisst-avhrr-v02r01.'+ymd+'.nc'
  if (not os.path.exists(oname)):
    print("getting ",oname)
    print(baseurl+ym+'/oisst-avhrr-v02r01.'+ymd+'.nc', flush=True)

    try:
      web = urllib.request.urlopen(baseurl+ym+'/oisst-avhrr-v02r01.'+ymd+'.nc')
      data = web.read()
  
      outfile = open('oisst-avhrr-v02r01.'+ymd+'.nc','w+b')
      outfile.write(data)
      outfile.close()
      web.close()
    except:
      print("could not get ",oname, flush=True)

  #else:
  #  print("have ",oname)

  #run back in time from 'today'
  tdate -= dt

#---------------------------------------------------------
print("run back to ",tdate)

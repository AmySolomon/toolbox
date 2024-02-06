import numpy as np
import numpy.ma as ma

from filtering import *


#----------------------------------------------------------
# Read in data, customized for each different sort of scan/match
# Later, read in from the standardized 'match' class
fin = open(sys.argv[1], "r")
allmatch = []
for line in fin:
  words = line.split()
  if ("lr" in line):

    icec  = int(words[0])
    land_frac = 1. - float(words[5]) # original has 0 == full land

    satid = int(words[2])
    lat   = float(words[3])
    lon   = float(words[4])
    x = amsr2_lr(satid = satid, latitude = lat, longitude = lon)
    for i in range(0,x.ntb):
      tb_lr[i] = float(words[6+i])
    x.add_tb(tb_lr)
    
    tmp = match(x, land = land_frac, icec = icec)
    #tmp.show()
    allmatch.append(tmp)
fin.close()

npts = len(allmatch)

#----------------------------------------------------------
# RG: better to have a set of masks, rather than specified names in specified orders
# RG: might want to exclude 'coast' in computing %ages

(icemask, landmask, watermask, known) = makemasks(allmatch)

stats = mask_stats(npts, landmask, icemask, watermask, known)
print(stats,flush=True)
#print(icemask[5], flush=True)
#exit(0)

#---------------------------------------------------------------------
fout = open("perfect1","w")

tbfilters = []
chobs = np.zeros((npts))

for channel in range(0,amsr2_lr.ntb):
  tag = "ch"+"{:d}".format(channel)
  for i in range(0,npts):
    chobs[i] = allmatch[i].obs.tb[channel]
  print("channel ",channel,"stats ",chobs.max(), chobs.min(), chobs.mean(), flush=True )
  
  for tc in range(50, 285):
    thot = float(tc)
    tmp  = bayes(chobs, thot, tag, npts, stats, landmask, icemask, watermask, channel)
    filter.add(tbfilters, tmp)

print("len of tbfilters: ",len(tbfilters), flush=True)
perfect = 0
for i in range(0, len(tbfilters)):
    if (tbfilters[i].perfect()):
      tbfilters[i].show(fout)
      perfect += 1

fout.close()
print("found ",perfect," perfect filters", flush=True)
#return perfect

#---------------------------------------------------------------------

fname = "maybe_ice_match"
fout = open(fname,"w")
fcount = 0
tcount = 0
bstats = np.zeros((3))
#if any of these are true, icec == 0
f22 = filter("ch0", "hot", 251., bstats, chan = 0)
f1  = filter("ch2", "hot", 256., bstats, chan = 2) 
f21 = filter("ch4", "hot", 252., bstats, chan = 4)
f2  = filter("ch6", "hot", 258., bstats, chan = 6) 
f4  = filter("ch7", "hot", 271., bstats, chan = 7) 
f3  = filter("ch8", "hot", 265., bstats, chan = 8) 
f5  = filter("ch9", "hot", 272., bstats, chan = 9) 
f6  = filter("ch10", "hot", 267., bstats, chan = 10) 
f7  = filter("ch11", "hot", 272., bstats, chan = 11) 
f23 = filter("dr29", "hot", -0.0021, bstats, chan = [2, 9])
f24 = filter("dr48", "cold", -0.2646, bstats, chan = [4,8])

print("applying filters ",flush=True)
for i in range(0, len(allmatch)):
    if (
          f1.apply(allmatch[i]) or
          f2.apply(allmatch[i]) or
          f3.apply(allmatch[i]) or
          f4.apply(allmatch[i]) or
          f5.apply(allmatch[i]) or
          f6.apply(allmatch[i]) or
          f7.apply(allmatch[i]) or 
         f21.apply(allmatch[i]) or f22.apply(allmatch[i])
      or f23.apply(allmatch[i]) or f24.apply(allmatch[i])
       ):
      tcount += 1
      known[i] == True
    else:
      fcount += 1
      allmatch[i].show(fout)
fout.close()

print("true ",tcount, "false ",fcount)

del allmatch
del tbfilters
del chobs

#----------------------------------------------------------
# Restart with result of last write:
fin = open(fname, "r")
allmatch = []
for line in fin:
  x = amsr2_lr()
  x.read(line)

  words = line.split()
  icec      = float(words[15])
  land_frac = float(words[16]) 

  tmp = match(x, land = land_frac, icec = icec)
  del x 
  allmatch.append(tmp)
fin.close()

npts = len(allmatch)
print("found ",npts," matchups")

# Re-masking -------------------------------------------------------------
(icemask, landmask, watermask, known) = makemasks(allmatch, known)
stats = mask_stats(npts, landmask, icemask, watermask, known)
print(stats,flush=True)

#---------------------------------------------------------------------
#while (find_perfect(allmatch) != 0):
#  
foutp = open("perfect2","w")
foute = open("all2","w")

tbfilters = []
c1obs = np.zeros((npts))
c2obs = np.zeros((npts))

for c1 in range(0, amsr2_lr.ntb):
  for i in range(0,npts):
    c1obs[i] = allmatch[i].obs.tb[c1]
  for c2 in range (c1+1, amsr2_lr.ntb):
    if (c1 != c2):
      for i in range(0,npts):
        c2obs[i] = allmatch[i].obs.tb[c2]

      tag = "dr"+"{:d}".format(c1)+"{:d}".format(c2)
      channel = [c1,c2]  
      tmp = dr(c1obs, c2obs, c1, c2, tag, npts, stats, landmask, icemask, watermask,
               granularity = 100)
      filter.add(tbfilters, tmp)

print("len of dr tbfilters: ",len(tbfilters), flush=True)
perfect = 0
for i in range(0, len(tbfilters)):
    tbfilters[i].show(foute)
    if (tbfilters[i].perfect()):
      tbfilters[i].show(foutp)
      perfect += 1

foutp.close()
foute.close()
print("round2 found ",perfect," perfect filters", flush=True)

#exit(0)

if (perfect > 0):
  fname = "maybe_ice_match2"
  fout = open(fname,"w")
  fcount = 0
  tcount = 0
  bstats = np.zeros((3))
  # here, 'hot' filters are this is not ice, almost certainly land
  #       'cold' are this is not ice, almost certainly water
  f21 = filter("dr29", "hot", -0.0021, bstats, chan = [2, 9])
  f22 = filter("dr48", "cold", -0.2646, bstats, chan = [4,8])
  for i in range(0, len(allmatch)):

    if ( f21.apply(allmatch[i]) or f22.apply(allmatch[i])
       ):
      tcount += 1
    else:
      fcount += 1
      allmatch[i].show(fout)
fout.close()

print("true ",tcount, "false ",fcount)

del allmatch
del tbfilters
del c1obs, c2obs

exit(0)
# return
# --- round3 ----
# read
# makemasks
# try filters
# close and delete

fin = open(fname, "r")
allmatch = []
for line in fin:
  x = amsr2_lr()
  x.read(line)

  words = line.split()
  icec      = float(words[15])
  land_frac = float(words[16]) 

  tmp = match(x, land = land_frac, icec = icec)
  del x 
  allmatch.append(tmp)
fin.close()

npts = len(allmatch)
print("found ",npts," matchups")

# Re-masking -------------------------------------------------------------
(icemask, landmask, watermask, known) = makemasks(allmatch, known)
stats = mask_stats(npts, landmask, icemask, watermask, known)
print(stats,flush=True)

#---------------------------------------------------------------------
#while (find_perfect(allmatch) != 0):
#  
foutp = open("perfect3","w")
foute = open("all3","w")

tbfilters = []
chobs = np.zeros((npts))

for channel in range(0,amsr2_lr.ntb):
  tag = "ch"+"{:d}".format(channel)
  for i in range(0,npts):
    chobs[i] = allmatch[i].obs.tb[channel]
  print("channel ",channel,"stats ",chobs.max(), chobs.min(), chobs.mean(), flush=True )
  
  for tc in range(50, 285, 1):
    thot = float(tc)
    tmp  = bayes(chobs, thot, tag, npts, stats, landmask, icemask, watermask, channel)
    filter.add(tbfilters, tmp)

print("len of tbfilters: ",len(tbfilters), flush=True)
perfect = 0
for i in range(0, len(tbfilters)):
    tbfilters[i].show(foute)
    if (tbfilters[i].perfect()):
      tbfilters[i].show(foutp)
      perfect += 1

foutp.close()
foute.close()
print("round3 found ",perfect," perfect filters", flush=True)

exit(0)


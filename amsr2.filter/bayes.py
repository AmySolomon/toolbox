# python system
import os
import sys
import copy
from math import *
import datetime

# shared
from match import *
from filtering import *
from tools import *


"""
Read in f01, f10 files, and f11, f00 files
compute bulk P(11, 10, 01, 00)
for each of ntb brightness temperatures, compute P_ij(Tb) Tb in [50:300], by 1
  (ij = 11, 10, 01, 00)

Bayes 
P(A|B) = P(B|A)*P(A)/P(B)
or, here:
P(bogus | Tb_k) = P(Tb_k | bogus) * P(bogus) / P(Tb_k )

here, Tb_k refers to logical function of Tb_k (e.g. Tb_k > Tcrit)

same thing applies to fns of T_k, T_l (k,l = channel numbers), such as the delta ratio
and delta squared ratio

n.b.: With 12 channels, and a fundamental symmetry between f(i,j) and f(j,i) (i,j denoting channel numbers), there are 1/2*k*(k-1), or 66 binary combinations for each

"""

x = amsr2_lr(satid = 0, latitude = 0., longitude = 0.)
tmp = match.match(x)

tmin =  70.0
tmax = 285.0

match11 = []
match10 = []
match01 = []
match00 = []
counts  = np.zeros((int(tmax),x.ntb), dtype=np.int64)
count11 = np.zeros((int(tmax),x.ntb), dtype=np.int64)
count10 = np.zeros((int(tmax),x.ntb), dtype=np.int64)
count01 = np.zeros((int(tmax),x.ntb), dtype=np.int64)
count00 = np.zeros((int(tmax),x.ntb), dtype=np.int64)


f11 = open("f11", "r")
f00 = open("f00", "r")
f10 = open("f10", "r")
f01 = open("f01", "r")

k = int(0)
for line in f11:
  tmp.lr_read(line)
  match11.append(tmp)
  match11[k] = copy.deepcopy(tmp)
  k += 1

k = int(0)
for line in f00:
  tmp.lr_read(line)
  match00.append(tmp)
  match00[k] = copy.deepcopy(tmp)
  k += 1

k = int(0)
for line in f10:
  tmp.lr_read(line)
  match10.append(tmp)
  match10[k] = copy.deepcopy(tmp)
  k += 1

k = int(0)
for line in f01:
  tmp.lr_read(line)
  match01.append(tmp)
  match01[k] = copy.deepcopy(tmp)
  k += 1

f11.close()
f10.close()
f01.close()
f00.close()

print("final counts = ", len(match11), len(match00), len(match01), len(match10) )
total  = len(match11) + len(match10) + len(match01) + len(match00)
pbogus = float(len(match10)) / float(total)
print("total, pbogus ",total,pbogus, flush=True)

#---------------------------------------------------------------

def pdf(matches, counts):

  for k in range(int(0),int(len(matches)) ):
    if (k%10000 == 0):
      print("k = ",k, flush=True)

    for tchannel in range (int(0),matches[0].obs.ntb ):

      for tcrit in range(int(tmin),int(tmax)):
  
        #if (int(matches[k].obs.tb[tchannel]+0.5) > tcrit):  
        if ( matches[k].obs.tb[tchannel] > tcrit):  
          counts[ tcrit  ,tchannel] += int(1)

#---------------------------------------------------------------

pdf(match11, count11)
pdf(match10, count10)
pdf(match01, count01)
pdf(match00, count00)

counts += count11
counts += count10
counts += count00
counts += count01

for k in range(int(tmin), int(tmax)):
  print("total ",k, counts[k,:])
  print("c11 ",k, count11[k,:])
  print("c01 ",k, count01[k,:])
  print("c10 ",k, count10[k,:])
  print("c00 ",k, count00[k,:])


#P(A|B) = P(B|A)*P(A)/P(B)
#  A = bogus
#  B = Tb_k (channel k Tb is greater than tcrit)
#
#P(bogus | Tb_k) = P(Tb_k | bogus) * P(bogus) / P(Tb_k )
#
#total = len(match11) + len(match10) + len(match01) + len(match00)
#pbogus = float(len(match10)) / float(total)
#p(tb_k) = sum(countIJ[tb,k) / float(total)
#p(tb_k | bogus) = count10[tb,k] / float(total)
for tchan in range(int(0), match11[0].obs.ntb):
  for tb in range(int(tmin), int(tmax)):
    sumtc    = float( counts[tb, tchan]) / float(total)
    sumgiven = float(count10[tb, tchan]) / float(len(match10) )
    if (sumtc > 0.):
      print("tchan, tb_crit ",tchan, tb, sumgiven * pbogus / sumtc, sumgiven, pbogus, sumtc, flush=True)
  

#---------------------------------------------------------------


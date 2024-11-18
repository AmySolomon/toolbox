#!/bin/bash --login
#PBS -N filtget
#PBS -o filtget
#PBS -j oe
#PBS -A XFER-DEV
#PBS -q dev_transfer
#PBS -l walltime=6:00:00
#PBS -l select=1:ncpus=1

set -x

cd /u/robert.grumbine/noscrub/

#export base=/NCEPDEV/emc-climate/5year/Robert.Grumbine/
#hsi mget $base/ncep_ice/sice/sice.20230[1-5].tar
#
#export base=/NCEPDEV/emc-climate/1year/Robert.Grumbine/
#export base=/NCEPDEV/emc-marine/1year/Robert.Grumbine/

export base=/NCEPDEV/emc-marine/5year/Robert.Grumbine/
cd filter/dirs
hsi mget $base/filter/*.20220[1234].tar

#yy=2022
#for mm in 06 05
#do
#  hsi get $base/filter/*.${yy}${mm}.tar
#done

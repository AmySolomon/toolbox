#!/bin/bash


base=$HOME/noscrub/filter/
cd $base

# for dumpjb (getting the bufr inputs)
source $HOME/rgdev/rg.analy/ecf/jobcards
export DCOMROOT=~/noscrub/satellites/prod/
export TMPDIR=/lfs/h2/emc/ptmp/wx21rg/dumpjb

module load bufr_dump
module load bufr
set +xe

tag=20240305
#tag=20230701
#while [ $tag -ge 20220601 ]
while [ $tag -ge 20220101 ]
do
  echo checking $tag
  
# check filter archive:
  if [ ! -f txt/amsr2_$tag.txt.0 ] ; then
    if [ -f dirs/amsr2.$tag/amsr2.$tag ] ; then
      echo zzz_tomv mv dirs/amsr2.$tag/amsr2.$tag bin/
    fi
  fi

# create the text files from bin -- ~ 1 min/day
  if [ ! -f txt/amsr2_${tag}.txt.0 -a -f ${base}/bin/amsr2.${tag} ] ; then
    echo zzz_totext ./seaice_totext ${base}/bin/amsr2.${tag} txt/amsr2_${tag}.txt
  fi

# bufr to bin -- ~8 min/day
  if [ ! -f txt/amsr2_${tag}.txt.0 -a ! -f ${base}/bin/amsr2.${tag} -a -f bufr/amsr2.$tag ] ; then
#    ln -s bufr/amsr2.$tag fort.11
#    time ./seaice_amsrbufr 
    echo zzz_seaice_amsrbufr mv fort.52 bin/amsr2.$tag
#    rm fort.11 fort.51
  fi

# get bufr -- dumpjb from my archive -- ~8 min/day
  if [ ! -f txt/amsr2_${tag}.txt.0 -a ! -f ${base}/bin/amsr2.${tag} -a ! -f bufr/amsr2.$tag ] ; then
     echo zzz_dumpjb $DUMPJB ${tag}00 12 amsr2
#    echo zzz_dumpjb mv amsr2.ibm bufr/amsr2.${tag}
  fi

  tag=`expr $tag - 1`
  tag=`$HOME/bin/dtgfix3 $tag`
done

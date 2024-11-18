#!/bin/bash


base=$HOME/noscrub/filter/
cd $base

# for dumpjb (getting the bufr inputs)
source $HOME/rgdev/rg.analy/ecf/jobcards
export DCOMROOT=~/noscrub/satellites/prod/
export TMPDIR=/lfs/h2/emc/ptmp/wx21rg/dumpjb

set +xe

tag=20240229
#tag=20230701
while [ $tag -ge 20220601 ]
#while [ $tag -ge 20240101 ]
do
  echo checking $tag
  
# bufr to bin
  if [ ! -f txt/amsr2_${tag}.txt.0 -a ! -f ${base}/bin/amsr2.${tag} -a -f bufr/amsr2.$tag ] ; then
    ln -s bufr/amsr2.$tag fort.11
    time ./seaice_amsrbufr 
    mv fort.52 bin/amsr2.$tag
    rm fort.11 fort.51
  fi

  tag=`expr $tag - 1`
  tag=`$HOME/bin/dtgfix3 $tag`
done

#!/bin/bash


base=$HOME/noscrub/filter/
cd $base

# for dumpjb (getting the bufr inputs)
source $HOME/rgdev/rg.analy/ecf/jobcards
export DCOMROOT=~/noscrub/satellites/prod/
export TMPDIR=/lfs/h2/emc/ptmp/wx21rg/dumpjb

set +xe

module load bufr_dump
module load bufr
module list
which $DUMPJB
#exit

tag=20240306
while [ $tag -ge 20220101 ]
do
  echo checking $tag
  
# get bufr -- dumpjb from my archive:
  if [ ! -f txt/amsr2_${tag}.txt.0 -a ! -f ${base}/bin/amsr2.${tag} -a ! -f bufr/amsr2.$tag ] ; then
    $DUMPJB ${tag}00 12 amsr2
    mv amsr2.ibm bufr/amsr2.${tag}
  fi

  tag=`expr $tag - 1`
  tag=`$HOME/bin/dtgfix3 $tag`
done

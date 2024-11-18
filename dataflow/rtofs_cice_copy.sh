#!/bin/bash 
#PBS -N rtofsget
#PBS -o rtofsget
#PBS -j oe
#PBS -A XFER-DEV
#PBS -q dev_transfer
#PBS -l walltime=6:00:00
#PBS -l select=1:ncpus=1

#env > ~/rtofs.env.1

echo zzz entered rtofs_cice_copy.sh 

set -x
echo zzz source modules
source /usr/share/lmod/lmod/init/bash

echo zzz try to load prod_envir
module purge
module reset

export MODULEPATH_ROOT=/usr/share/modulefiles
module load prod_envir
echo zzz done trying to load prod_envir

ops=$COMROOT/rtofs/v2.4/
echo zzz ops = $ops

cd $ops
base=$HOME/noscrub/model_intercompare/rtofs_cice/
tag=20240920
end=`date +"%Y%m%d"`
end=`expr $end - 1`
end=`$HOME/bin/dtgfix3 $end`

while [ $tag -lt $end ]
do
  if [ ! -d ${base}/rtofs.$tag ] ; then
    if [ -d rtofs.$tag ] ; then
      find rtofs.$tag -name '*cice_inst*' | cpio -pamdv $base
    else
      echo no rtofs for $tag
    fi
  else
    echo already have $tag
  fi

  tag=`expr $tag + 1`
  tag=`$HOME/bin/dtgfix3 $tag`
done

echo zzz leaving rtofs_cice_copy.sh 
#env > ~/rtofs.env.2

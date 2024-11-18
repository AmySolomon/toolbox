#!/bin/sh

source $HOME/rgdev/rg.analy/ecf/jobcards
export DCOMROOT=~/noscrub/satellites/prod/
export TMPDIR=/lfs/h2/emc/ptmp/wx21rg/

tag=20231231
while [ $tag -ge 20231101 ]
do
  /apps/ops/prod/nco/intel/19.1.3.304/bufr_dump.v1.1.2/install/ush/dumpjb ${tag}00 12 amsr2
  mv amsr2.ibm amsr2.${tag}

  tag=`expr $tag - 1`
  tag=`$HOME/bin/dtgfix3 $tag`
done

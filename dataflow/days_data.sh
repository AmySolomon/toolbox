#!/bin/bash

#General retrieval of data sets for the day, in approximate order of increasing size
# Robert Grumbine 26 September 2022
#

export EXDIR=$HOME/rgdev/toolbox/dataflow
if [ $? -ne 0 ] ; then
	echo could not cd to dataflow directory
	exit 1
fi
#env > env.initial

time $EXDIR/cislakes.sh #-- kb/wk
time $EXDIR/nic_edge.sh #-- kb/day

#iabp
time $EXDIR/iabp_dcomdev #-- 500 Mb/day
time $EXDIR/iabp.wget    #-- can be up to a few Gb, but updates only monthly

time $EXDIR/osisaf      # --  76 Mb/day
time $EXDIR/ims.wget    # -- 0.5 Mb/day, but may get several months at a time
time $EXDIR/nsidc       # updates only about quarterly

time $EXDIR/get_cafs.sh # -- 500 Mb/day

#submit jobs that reference hpss to q so that data transfer nodes+queues can be used
echo zzz set up modules
source /usr/share/lmod/lmod/init/bash
module list
echo zzz preceding was list of modules from days_data.sh

/opt/pbs/bin/qsub $EXDIR/reget.2yr.sh # -- 2Gb/day, ssmi-s, amsr2

/opt/pbs/bin/qsub $EXDIR/gefs_get.sh   #  ./gefs_thin.sh, ./gefs_clean.sh -- 1 Gb/day
time   $EXDIR/gefs_thin.sh   # this winds up cleaning yesterday and before, 
                        # since the queue won't respond instantly

#/opt/pbs/bin/qsub $EXDIR/sice.reget.sh   # 5-10 Gb/day, opnl sea ice analysis

#While large volumes, these are disk to disk copy from com to my space
time $EXDIR/riops.sh           # --  6.5 Gb/day
time $EXDIR/gofs.sh            # -- 13.3 Gb/day
time $EXDIR/giops.sh           # -- 28 Gb/day 

#/opt/pbs/bin/qsub ./rtofs_cice_copy.sh # -- 27 Gb/day

#viirs -- 32 Gb/day

#env > env.final

#!/bin/bash 
#PBS -N sicereget
#PBS -o sicereget
#PBS -j oe
#PBS -A XFER-DEV
#PBS -q dev_transfer
#PBS -l walltime=6:00:00
#PBS -l select=1:ncpus=1

set -x

#Go back to this date, ensuring all are present:
end_date=20240601

#Start from this date -- back up 2 days for archive process/delay
start_date=`date +"%Y%m%d"`
##start_date=`sh finddate.sh $start_date d-1`
##start_date=`sh finddate.sh $start_date d-1`

start_date=`expr $start_date - 1`
start_date=`$HOME/bin/dtgfix3 $start_date`
start_date=`expr $start_date - 1`
start_date=`$HOME/bin/dtgfix3 $start_date`

#start_date=20210831

base=$HOME/noscrub/sice/
if [ ! -d $base ] ; then
  mkdir -p $base
fi

set -x
date=$start_date
while [ $date -ge $end_date ]; do

  dirout=${base}/sice.$date

  if [ ! -d $dirout ] ; then 

    [ -d ${base}/$date ] || mkdir -p ${base}/$date
  
    echo $date
    yr=`echo $date | cut -c1-4`
    yrmo=`echo $date | cut -c1-6`

    if [ $date -ge 20220627 ] ; then
      ice_archive=/NCEPPROD/hpssprod/runhistory/rh${yr}/${yrmo}/${date}/com_seaice_analysis_v4.5_seaice_analysis.${date}.tar
    elif [ $date -ge 20200101 ] ; then
      ice_archive=/NCEPPROD/hpssprod/runhistory/rh${yr}/${yrmo}/${date}/com_omb_prod_sice.${date}.tar
    elif [ $date -ge 20190612 ] ; then
      ice_archive=/NCEPPROD/hpssprod/runhistory/rh${yr}/${yrmo}/${date}/gpfs_dell1_nco_ops_com_omb_prod_sice.${date}.tar
    elif [ $date -ge 20161031 ] ; then
      ice_archive=/NCEPPROD/hpssprod/runhistory/rh${yr}/${yrmo}/${date}/com2_omb_prod_sice.${date}.tar
    else
      ice_archive=/NCEPPROD/hpssprod/runhistory/rh${yr}/${yrmo}/${date}/com_omb_prod_sice.${date}.tar
    fi

    cd ${base}/$date
    htar xvf $ice_archive
    cd ..
    mv $date sice.$date

  fi

  #date=`sh finddate.sh $date d-1`
  date=`expr $date - 1`
  date=`$HOME/bin/dtgfix3 $date`
done



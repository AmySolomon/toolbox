#!/bin/bash 
#PBS -N gefsget
#PBS -o outname
#PBS -j oe
#PBS -A XFER-DEV
#PBS -q dev_transfer
#PBS -l walltime=6:00:00
#PBS -l select=1:ncpus=1

echo zzz entered gefs_get.sh

if [ ! -d $HOME/noscrub/gefs/ ] ; then
	mkdir -p $HOME/noscrub/gefs
fi
cd $HOME/noscrub/gefs/

set -x

tag=20240601
#end=20220905
end=`date +"%Y%m%d"`
base=`pwd`
j=0


#Up to 07/##/2018
#pathbase=com_gens_prod_gefs
#Afterwards, up to 2020/02/25
#pathbase=gpfs_hps_nco_ops_com_naefs_prod_gefs
#After 2020/02/25
#pathbase=com_naefs_prod_gefs
#2022/06/27 -- 2023/12/03
#pathbase=com_naefs_v6.1_gefs
#
#2023/12/04 -- present
pathbase=com_naefs_v7.0_gefs


# 75 is ~2 Tb for .5 GEFS
#while [ $j -lt 75 -a \( $tag -le $end \) ]
while [ $tag -le $end ]
#for tag in 20170910 20171012 20171013 20171027 20171108 20171109 20171110 20180119 20180612 20180613   
do
  yy=`echo $tag | cut -c1-4`
  mo=`echo $tag | cut -c5-6`
  dd=`echo $tag | cut -c7-8`
  for hh in 00 
  do

    if [ ! -d gefs.${tag}/${hh} -a \( ! -f winds.${tag}.tar \) ] ; then
      hsi get /NCEPPROD/2year/hpssprod/runhistory/rh${yy}/${yy}${mo}/${yy}${mo}${dd}/${pathbase}.${tag}_${hh}.pgrb2ap5_bc.tar

      if [ -f ${pathbase}.${tag}_${hh}.pgrb2ap5_bc.tar ] ; then
        mkdir -p gefs.${tag}/${hh}
        cd gefs.${tag}/${hh}
        tar xf ${base}/${pathbase}.${tag}_${hh}.pgrb2ap5_bc.tar
        cd $base
        rm ${pathbase}.${tag}_${hh}.pgrb2ap5_bc.tar
      fi
     else
      echo already have $tag
    fi

  done

  j=`expr $j + 1`
  tag=`expr $tag + 1`
  tag=`dtgfix3 $tag`
done

echo zzz leaving gefs_get.sh

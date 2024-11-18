#!/bin/sh

echo entered get_cafs.sh

models=$HOME/noscrub/model_intercompare/
if [ ! -d $models/cafs ] ; then
	mkdir $models/cafs
fi
cd $models/cafs


base=`pwd`
tag=20240401
while [ $tag -lt `date +"%Y%m%d"` ]
do

  if [ ! -d $tag ] ; then

    mkdir $tag
    cd $tag
  
    YYYY=`echo $tag | cut -c1-4`
    MM=`echo $tag | cut -c5-6`
    DD=`echo $tag | cut -c7-8`
  
    wget -q ftp://ftp1.esrl.noaa.gov/RASM-ESRL/ModelOutput/*$YYYY-$MM-$DD*

  fi
  cd $base
  tag=`expr $tag + 1`
  tag=`/u/robert.grumbine/bin/dtgfix3 $tag`
done

echo leaving get_cafs.sh


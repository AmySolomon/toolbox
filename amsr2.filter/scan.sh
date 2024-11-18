#!/bin/sh
#

source ./nest

tag=20240303
while [ $tag -ge 20220101 ]
do
  echo zzz $tag
  if [ ! -f matched_$tag.txt ] ; then
    echo zzz making matched_$tag.txt 
    time python3 ./runup.py $tag
  fi

  yy=`echo $tag | cut -c1-4`
  d=`echo $tag | cut -c5-8`
  if [ ! -d $yy/$d ] ; then
    mkdir -p $yy/$d
  fi

  if [ ! -f $yy/$d/f10 ] ; then
    echo zzz making quick_thin for $tag
    time python3 quick_thin.py matched_$tag.txt
    mv f[01][01] $yy/$d
  fi

  tag=`expr $tag - 1`
  tag=`$HOME/bin/dtgfix3 $tag`
done

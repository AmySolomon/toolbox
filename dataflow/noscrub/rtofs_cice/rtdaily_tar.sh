#!/bin/sh

tag=20240201
while [ $tag -le 20240702 ]
do
  echo $tag
  if [ -d rtofs.$tag ] ; then
    tar cf ../rtofs.${tag}.tar rtofs.$tag
  fi

  tag=`expr $tag + 1`
  tag=`$HOME/bin/dtgfix3 $tag`
done

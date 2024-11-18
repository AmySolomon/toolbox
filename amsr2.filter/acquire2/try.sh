#!/bin/sh
#
source ~/rgdev/toolbox/amsr2.filter/nest

tag=20240101
while [ $tag -le 20240303 ]
do
  yy=`echo $tag | cut -c1-4`
  d=`echo $tag | cut -c5-8`
  if [ -d ../$yy/$d ] ; then
    ln -sf ../$yy/$d/f11 .
    ln -sf ../$yy/$d/f00 .
    ln -sf ../$yy/$d/f01 .
    ln -sf ../$yy/$d/f10 .
    # rerun whole bayes -- ~ 90 minutes
    #python3 noodle.py > tchan.$d
    
    # run filter, ~ 5 min
    if [ ! -f $yy/filt.out.$d ] ; then
      echo need $tag
      time python3 filter.py tchan > $yy/filt.out.$d
    fi
  fi

  tag=`expr $tag + 1`
  tag=`$HOME/bin/dtgfix3 $tag`
done

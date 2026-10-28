#!/bin/bash
# usage: pipe.sh P key subj outname [key subj outname ...]
P=$1; shift; D=/home/claude/v24; cd $D
while [ $# -ge 3 ]; do
  k=$1; s=$2; o=$3; shift 3
  until [ -f $D/$k/body.ok ]; do sleep 20; done
  [ -s p$P/kin_$k.mp4 ] || python3 kinetic.py p$P/kin_$k.json p$P/kin_$k.mp4 > p$P/kin_$k.log 2>&1 || echo "$k KIN FAIL"
  ./runX.sh $k $s $o $P
done

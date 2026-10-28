#!/bin/bash
D=/home/claude/v24; cd $D
while pgrep -f "all.sh" >/dev/null; do sleep 15; done
for spec in "ibrahima 2 TCF_Tache2_P11_Ibrahima_Progresser_francais 11" "karim 4 TCF_Tache2_P11_Karim_Promenade_ville 11" "fatou 5 TCF_Tache2_P11_Fatou_Benevolat 11" "patrick 1 TCF_Tache2_P10_Patrick_Garde_enfants 10"; do
  set -- $spec; rm -f $1/body.ok $1/body.mp4
  ./runX.sh $1 $2 $3 $4 2>&1 | grep -E "DONE|FAIL"
done
echo FIXDONE

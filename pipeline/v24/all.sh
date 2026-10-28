#!/bin/bash
cd /home/claude/v24
./bodyq.sh karim fatou patrick nadia abdou divya mariam > bodyq_r.log 2>&1 &
./pipe.sh 11 ibrahima 2 TCF_Tache2_P11_Ibrahima_Progresser_francais priya 3 TCF_Tache2_P11_Priya_Activite_artistique karim 4 TCF_Tache2_P11_Karim_Promenade_ville fatou 5 TCF_Tache2_P11_Fatou_Benevolat > pipe11_r.log 2>&1 &
./pipe.sh 10 patrick 1 TCF_Tache2_P10_Patrick_Garde_enfants nadia 2 TCF_Tache2_P10_Nadia_Adopter_animal abdou 3 TCF_Tache2_P10_Abdou_Weekend_famille divya 4 TCF_Tache2_P10_Divya_Activite_loisir mariam 5 TCF_Tache2_P10_Mariam_Formation_pro > pipe10_r.log 2>&1 &
wait
echo ALLDONE

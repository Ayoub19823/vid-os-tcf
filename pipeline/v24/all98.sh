#!/bin/bash
cd /home/claude/v24
./bodyq.sh amine aissatou christian leila serge kenza mamadou anjali oumar bintou > bodyq98.log 2>&1 &
./pipe.sh 9 amine 1 TCF_Tache2_P9_Amine_Chambre_hotes aissatou 2 TCF_Tache2_P9_Aissatou_Poste_vendeuse christian 3 TCF_Tache2_P9_Christian_Centre_sportif leila 4 TCF_Tache2_P9_Leila_Acheter_ordinateur serge 5 TCF_Tache2_P9_Serge_Evenements_culturels > pipe98.log 2>&1
./pipe.sh 8 kenza 1 TCF_Tache2_P8_Kenza_Jeux_societe mamadou 2 TCF_Tache2_P8_Mamadou_Fete_retraite anjali 3 TCF_Tache2_P8_Anjali_Cours_jardinage oumar 4 TCF_Tache2_P8_Oumar_Bibliotheque bintou 5 TCF_Tache2_P8_Bintou_Cours_natation >> pipe98.log 2>&1
wait
for s in "9 amine TCF_Tache2_P9_Amine_Chambre_hotes CHAMBRE|D'HÔTES" "9 aissatou TCF_Tache2_P9_Aissatou_Poste_vendeuse POSTE DE|VENDEUSE" "9 christian TCF_Tache2_P9_Christian_Centre_sportif CENTRE|SPORTIF" "9 leila TCF_Tache2_P9_Leila_Acheter_ordinateur ACHETER UN|ORDINATEUR" "9 serge TCF_Tache2_P9_Serge_Evenements_culturels ÉVÉNEMENTS|CULTURELS" "8 kenza TCF_Tache2_P8_Kenza_Jeux_societe JEUX DE|SOCIÉTÉ" "8 mamadou TCF_Tache2_P8_Mamadou_Fete_retraite FÊTE DE|RETRAITE" "8 anjali TCF_Tache2_P8_Anjali_Cours_jardinage COURS DE|JARDINAGE" "8 oumar TCF_Tache2_P8_Oumar_Bibliotheque EMPRUNTER À LA|BIBLIOTHÈQUE" "8 bintou TCF_Tache2_P8_Bintou_Cours_natation COURS DE|NATATION"; do
  P=${s%% *}; r=${s#* }; k=${r%% *}; r=${r#* }; o=${r%% *}; sub=${r#* }
  ./thumbs.sh $P $k $o "$sub" && echo "thumb $k ok"
done
echo ALLDONE98

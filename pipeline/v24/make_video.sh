#!/bin/bash
# Fabrique une vidéo complète (Tâche 2 ou 3) à partir des voix déjà téléchargées.
# usage : make_video.sh <cle> <tache 2|3> <partie> <n° sujet> <mois-slug ex. octobre-2026> <sortie sans .mp4> "<LIGNE1|LIGNE2 miniature>"
# Prérequis dans /home/claude/work/<cle>/ :
#   T3 : e.wav (7 répliques examinatrice), ca.wav (monologue), cb.wav (relances CB+CC)  — scénario SCEN=<module> (SIMS[cle])
#   T2 : e.wav (17 répliques), c.wav (16 répliques)                                       — scénario SCEN=<module> (SIMS[cle])
#   spec.wav : narration Corentin en 2 phrases : « On ouvre la partie … du mois de …, puis la tâche … » + « Le sujet du jour : … »
set -e
k=$1; TA=$2; PT=$3; SK=$4; MS=$5; OUT=$6; TH=$7
D=/home/claude/v24; W=/home/claude/work/$k; V6=/tmp/claude-0/-home-claude/7a22c9af-0a80-57d2-89a2-1a32e1824476/scratchpad/v6
NARR=/home/claude/pipe/narr; P=$D/p_$k; mkdir -p $P $D/$k /home/claude/out
MOIS=$(python3 -c "s='$MS'.split('-'); print(s[0].capitalize()+' '+s[1])")
CAP=$D/cap_${MS}_P${PT}_T${TA}/
cd $D
# 1. captures du site (une fois par partie / tâche)
if [ ! -f $CAP/s$SK/J.json ]; then
  mkdir -p $CAP; MSLUG=$MS PARTIE=$PT TACHE=$TA CAPDIR=$CAP node capAny.js
  MSLUG=$MS PARTIE=$PT TACHE=$TA CAPDIR=$CAP KS=$SK node capkAny.js
fi
# 2. piste voix + fichier de session
if [ $TA = 3 ]; then SCEN=$SCEN python3 t3build.py $k $W ${TEMPO:-0.97}
else cp $W/e.wav $W/c.wav $D/$k/ ; SCRIPT=$SCEN python3 buildX.py $k $D/$k/e.wav $D/$k/c.wav; fi
# 3. narration, intro animée, chronologie du site
python3 - <<EOF
import sys, json, wave, numpy as np, importlib
sys.path.insert(0, '/home/claude/t3'); sys.path.insert(0, '$D')
from segs import rd, segs, SR
S = importlib.import_module('$SCEN').SIMS['$k']
g = rd('$NARR/generic_T$TA.wav'); gs = segs(g, minsil=0.6); assert len(gs) == 5, len(gs)
s = rd('$W/spec.wav'); ss = segs(s, minsil=0.6); assert len(ss) == 2, ('spec.wav doit contenir 2 phrases', len(ss))
cut = lambda x, t: x[max(0, t[0] - int(0.03 * SR)):t[1] + int(0.2 * SR)]
parts = [cut(g, gs[0]), cut(g, gs[1]), cut(g, gs[2]), cut(s, ss[0]), cut(s, ss[1]), cut(g, gs[3]), cut(g, gs[4])]
sil = np.zeros(int(2.0 * SR)); o = np.concatenate([np.concatenate([p, sil]) for p in parts])
w = wave.open('$W/narr.wav', 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(o, -1, 1) * 32767).astype('<i2').tobytes()); w.close()
d0, d1, N4 = [(t[1] - t[0]) / SR for t in (gs[0], gs[1], ss[1])]
num = 'trois' if '$TA' == '3' else 'deux'
n0 = f"Bonjour et bienvenue dans cette nouvelle simulation de la tâche {num} d'expression orale du TCF Canada."
n1 = f"L'objectif de ces simulations : vous montrer le très bon déroulement de la tâche {num}, avec les " + ("arguments" if '$TA' == '3' else "thèmes") + ", les sujets et le vocabulaire."
def tm(txt, st, du, ws): return {k_: round(st + du * txt.find(w_) / len(txt) + 0.05, 2) for k_, w_ in ws}
T = tm(n0, 0.4, d0, [('bonjour', 'Bonjour'), ('bienvenue', 'bienvenue'), ('simulation', 'simulation'), ('tache', 'tâche'), ('deux', num), ('expression', "d'expression"), ('orale', 'orale'), ('tcf', 'TCF'), ('canada', 'Canada')])
T.update(tm(n1, 6.6, d1, [('objectif', "L'objectif"), ('montrer', 'montrer'), ('deroulement', 'déroulement'), ('tache2', 'tâche'), ('themes', 'arguments' if '$TA' == '3' else 'thèmes'), ('sujets', 'sujets'), ('vocabulaire', 'vocabulaire')]))
T['whip0'] = 6.15
json.dump({'dur': 15.4, 't': T, 'voc': S['voc'], 'digit': '$TA'}, open('$P/kin_$k.json', 'w'), ensure_ascii=False)
r_open = 9.9 + 2.95; r_t = r_open + 0.8; r_read = r_t + 2.6; theme_at = r_read + 0.2; r_click = theme_at + N4 + 0.6
Wp = {"real": [0, 2.4, 9.9, round(r_open, 2), round(r_t, 2), round(r_read, 2), round(r_click, 2), round(r_click + 2.3, 2), round(r_click + 3.3, 2)],
      "seq": [0, 1.45, 1.45, 4.4, 6.0, 8.7, 12.6, 13.2, 14.2], "outro": 10.0,
      "pop_in": {"in": 2.4, "url0": 2.9, "url1": 5.2, "enter": 5.5, "drop": 5.65, "badge": 5.85, "pack": 8.0, "out": 9.7},
      "pop_out": {"in": 2.3, "url0": 3.0, "url1": 4.9, "enter": 5.1, "drop": 5.25, "badge": 5.45, "pack": 7.3, "out": 9.6},
      "L4": round(r_click + 0.1, 2), "theme_at": round(theme_at, 2), "n3_at": 10.0, "n2_at": 0.3}
json.dump(Wp, open('$P/${k}_warp.json', 'w'), indent=1)
print('narration ok, sujet annoncé', round(N4, 2), 's')
EOF
python3 kinetic3.py $P/kin_$k.json $P/kin_$k.mp4
SUBJ=$SK PARTIE=$PT MOIS="$MOIS" TACHE=$TA CAPDIR=$CAP OUTK=$P/site_${k}_ WARP=$P/${k}_warp.json POPMOD=$D/omni.py python3 site3.py render
# 4. corps de la vidéo (examen + bilan + outro)
if [ $TA = 3 ]; then (cd $V6 && python3 exam_t3l.py sess_$k $D/$k/voice.wav $D/$k/body.mp4)
else (cd $V6 && python3 exam_light.py sess_$k $D/$k/voice.wav $D/$k/body.mp4); fi
# 5. montage final
python3 t3assemble.py $k p_$k $W/narr.wav /home/claude/out/$OUT.mp4
# 6. miniature (avec « EXPRESSION ORALE » et la photo d'Ayoub)
f=$P/site_${k}_site_intro.mp4; d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $f)
# miniature v2 (style validé par Ayoub le 31/10/2026 : fond bleu, TÂCHE N en jaune, nouvelle photo ayoub_new.png)
PILL=$(python3 -c "import sys; print('SUJET ' + sys.argv[1].upper())" "$MOIS"); L1=$(echo "$TH" | cut -d"|" -f1)
(cd $V6 && python3 thumb_v2.py EO $TA "$L1" /home/claude/out/${OUT}_miniature.jpg "Simulation réelle|Corrections|Bilan" "$PILL")
echo "$k DONE $(ffprobe -v error -show_entries format=duration -of csv=p=0 /home/claude/out/$OUT.mp4)"

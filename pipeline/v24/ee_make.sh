#!/bin/bash
# Fabrique une vidéo « exercice corrigé » d'expression écrite (Tâche 1 ou 2).
# usage : ee_make.sh <cle> <SORTIE sans .mp4>
# Prérequis dans /home/claude/work/<cle>/ :
#   spec.json  : task, mois, mslug, combi, mini, maxi, consigne, mots_cles, points, copie ([[faux|juste|raison]]), modele, vocab, bilan, thumb, ...
#   spec.wav   : Corentin, 2 phrases : « On ouvre la combinaison … du mois de …, puis la tâche … » + « Le sujet du jour : … »
#   body.wav   : Corentin, 6 + nb_erreurs segments : consigne, points, copie, erreur 1..n, modèle, vocabulaire, bilan
set -e
k=$1; OUT=$2
D=/home/claude/v24; W=/home/claude/work/$k; V6=/tmp/claude-0/-home-claude/7a22c9af-0a80-57d2-89a2-1a32e1824476/scratchpad/v6
NARR=/home/claude/pipe/narr; P=$D/p_$k; mkdir -p $P $D/$k /home/claude/out
eval $(python3 -c "import json;S=json.load(open('$W/spec.json'));print(f\"TA={S['task']} CB={S['combi']} MS={S['mslug']} TH='{S['thumb']}'\")")
MOIS=$(python3 -c "s='$MS'.split('-'); print(s[0].capitalize()+' '+s[1])")
CAP=$D/cap_${MS}_C${CB}_EE${TA}
cd $D
# 1. captures du site
if [ ! -f $CAP/s$TA/J.json ]; then mkdir -p $CAP; MSLUG=$MS COMBI=$CB TACHE=$TA CAPDIR=$CAP node capEE.js; fi
# 2. narration (intro + site) et narration du corps
python3 - <<EOF
import sys, json, wave, re, numpy as np
sys.path.insert(0, '/home/claude/t3')
from segs import rd, segs, robust, SR
S = json.load(open('$W/spec.json'))
def wr(p, o):
    w = wave.open(p, 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(o, -1, 1) * 32767).astype('<i2').tobytes()); w.close()
g = rd('$NARR/generic_EE_T$TA.wav'); gs = robust(g, 5); assert len(gs) == 5, len(gs)
s = rd('$W/spec.wav'); ss = robust(s, 2); assert len(ss) == 2, ('spec.wav doit contenir 2 phrases', len(ss))
cut = lambda x, t, a=0.03, b=0.2: x[max(0, t[0] - int(a * SR)):t[1] + int(b * SR)]
parts = [cut(g, gs[0]), cut(g, gs[1]), cut(g, gs[2]), cut(s, ss[0]), cut(s, ss[1]), cut(g, gs[3]), cut(g, gs[4])]
sil = np.zeros(int(2.0 * SR)); wr('$W/narr.wav', np.concatenate([np.concatenate([p, sil]) for p in parts]))
d0, d1, N4 = [(t[1] - t[0]) / SR for t in (gs[0], gs[1], ss[1])]
num = {'1': 'un', '2': 'deux', '3': 'trois'}['$TA']
n0 = f"Bonjour et bienvenue dans ce nouvel exercice corrigé de la tâche {num} d'expression écrite du TCF Canada."
n1 = f"L'objectif de ces exercices : vous montrer le très bon déroulement de la tâche {num}, avec la méthode, les sujets et le vocabulaire."
def tm(txt, st, du, ws): return {k_: round(st + du * txt.find(w_) / len(txt) + 0.05, 2) for k_, w_ in ws}
T = tm(n0, 0.4, d0, [('bonjour', 'Bonjour'), ('bienvenue', 'bienvenue'), ('simulation', 'exercice'), ('tache', 'tâche'), ('deux', num), ('expression', "d'expression"), ('orale', 'écrite'), ('tcf', 'TCF'), ('canada', 'Canada')])
T.update(tm(n1, 6.6, d1, [('objectif', "L'objectif"), ('montrer', 'montrer'), ('deroulement', 'déroulement'), ('tache2', 'tâche'), ('themes', 'méthode'), ('sujets', 'sujets'), ('vocabulaire', 'vocabulaire')]))
T['whip0'] = 6.15
json.dump({'dur': 15.4, 't': T, 'voc': S['vocab'][:4], 'digit': '$TA', 'mode': 'EE'}, open('$P/kin_$k.json', 'w'), ensure_ascii=False)
r_open = 9.9 + 2.95; r_t = r_open + 0.8; r_read = r_t + 2.6; theme_at = r_read + 0.2; r_click = theme_at + N4 + 0.6
Wp = {"real": [0, 2.4, 9.9, round(r_open, 2), round(r_t, 2), round(r_read, 2), round(r_click, 2), round(r_click + 2.3, 2), round(r_click + 3.3, 2)],
      "seq": [0, 1.45, 1.45, 4.4, 6.0, 8.7, 12.6, 13.2, 14.2], "outro": 10.0,
      "pop_in": {"in": 2.4, "url0": 2.9, "url1": 5.2, "enter": 5.5, "drop": 5.65, "badge": 5.85, "pack": 8.0, "out": 9.7},
      "pop_out": {"in": 2.3, "url0": 3.0, "url1": 4.9, "enter": 5.1, "drop": 5.25, "badge": 5.45, "pack": 7.3, "out": 9.6},
      "L4": round(r_click + 0.1, 2), "theme_at": round(theme_at, 2), "n3_at": 10.0, "n2_at": 0.3}
json.dump(Wp, open('$P/${k}_warp.json', 'w'), indent=1)
# corps : segments -> piste avec respirations, et chronologie des étapes
nerr = len(re.findall(r'\[\[', S['copie'])); kinds = ['consigne', 'points', 'copie'] + ['erreur'] * nerr + ['modele', 'vocab', 'bilan']
b = rd('$W/body.wav'); bs = robust(b, len(kinds)); assert len(bs) == len(kinds), ('body.wav', len(bs), len(kinds))
hold = {'copie': 6.0, 'modele': 4.0, 'bilan': 2.5, 'consigne': 1.5}
o = [np.zeros(int(0.8 * SR))]; t = 0.8; steps = []; e = 0
for kd, sg in zip(kinds, bs):
    c = cut(b, sg); st = {'kind': kd, 't0': round(t, 2)}
    if kd == 'erreur': st['k'] = e; e += 1
    gap = hold.get(kd, 1.3); o += [c, np.zeros(int(gap * SR))]; t += len(c) / SR + gap; st['t1'] = round(t, 2); steps.append(st)
wr('$D/$k/bodynarr.wav', np.concatenate(o))
S['steps'] = steps; tot = t
S['cta'] = [round(steps[3]['t0'] - 0.5, 1), round(steps[-2]['t0'], 1)]
json.dump(S, open('$P/spec_r.json', 'w'), ensure_ascii=False, indent=1)
print('narration ok, sujet annoncé', round(N4, 2), 's ; corps', round(tot, 1), 's ;', [(x['kind'], x['t0']) for x in steps])
EOF
python3 kinetic3.py $P/kin_$k.json $P/kin_$k.mp4
MODE=EE SUBJ=$TA PARTIE=$CB MOIS="$MOIS" TACHE=$TA CAPDIR=$CAP/ OUTK=$P/site_${k}_ WARP=$P/${k}_warp.json POPMOD=$D/omni.py python3 site3.py render
# 3. corps (consigne, copie, corrections, modèle, vocabulaire, bilan) + outro
(cd $V6 && python3 ee_body.py $P/spec_r.json $D/$k/bodynarr.wav $D/$k/body.mp4)
# 4. montage final
python3 ee_assemble.py $k p_$k $W/narr.wav /home/claude/out/$OUT.mp4
# 5. miniature « EXPRESSION ÉCRITE » avec la photo d'Ayoub
f=$P/site_${k}_site_intro.mp4; d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $f)
# miniature v2 (style validé par Ayoub le 31/10/2026 : fond bleu, TÂCHE N en jaune, nouvelle photo ayoub_new.png)
PILL=$(python3 -c "import sys; print('SUJET ' + sys.argv[1].upper())" "$MOIS"); L1=$(echo "$TH" | cut -d"|" -f1)
(cd $V6 && python3 thumb_v2.py EE $TA "$L1" /home/claude/out/${OUT}_miniature.jpg "Méthode|Erreurs corrigées|Modèle" "$PILL")
echo "$k DONE $(ffprobe -v error -show_entries format=duration -of csv=p=0 /home/claude/out/$OUT.mp4)"

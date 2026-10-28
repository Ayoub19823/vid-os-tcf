#!/bin/bash
# usage: t3pipe.sh <cle> <n° sujet> <index narration thème (0-3)> <nom sortie> "<LIGNE1|LIGNE2>"
set -e
k=$1; SK=$2; TI=$3; OUT=$4; TH=$5
D=/home/claude/v24; T=/home/claude/t3; V6=/tmp/claude-0/-home-claude/7a22c9af-0a80-57d2-89a2-1a32e1824476/scratchpad/v6
cd $D
python3 - <<EOF
import sys, json, numpy as np, wave
sys.path.insert(0, '$T'); sys.path.insert(0, '$D')
from segs import rd, segs, SR
import t3nov
S = t3nov.SIMS['$k']
# narration : segments génériques d'Hervé + annonce du sujet
base = rd('$T/herve/n1.wav'); bs = segs(base, minsil=0.6); assert len(bs) == 7
th = rd('$T/narr_themes.wav'); ts = segs(th, minsil=0.6); assert len(ts) == 4
cut = lambda x, s: x[max(0, s[0] - int(0.03 * SR)):s[1] + int(0.2 * SR)]
parts = [cut(base, bs[i]) for i in range(4)] + [cut(th, ts[$TI])] + [cut(base, bs[5]), cut(base, bs[6])]
sil = np.zeros(int(2.0 * SR)); o = np.concatenate([np.concatenate([p, sil]) for p in parts])
w = wave.open('$T/$k/narr.wav', 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(o, -1, 1) * 32767).astype('<i2').tobytes()); w.close()
N4 = (ts[$TI][1] - ts[$TI][0]) / SR
# intro animée : mêmes temps que la vidéo d'Hervé, vocabulaire du sujet
kin = json.load(open('$D/pN1/kin_herve.json')); kin['voc'] = S['voc']
json.dump(kin, open('$D/pN1/kin_$k.json', 'w'), ensure_ascii=False)
# chronologie de la navigation sur le site
r_open = 9.9 + 2.95; r_t3 = r_open + 0.8; r_read = r_t3 + 2.6; theme_at = r_read + 0.2; r_click = theme_at + N4 + 0.6
W = {"real": [0, 2.4, 9.9, round(r_open, 2), round(r_t3, 2), round(r_read, 2), round(r_click, 2), round(r_click + 2.3, 2), round(r_click + 3.3, 2)],
     "seq": [0, 1.45, 1.45, 4.4, 6.0, 8.7, 12.6, 13.2, 14.2], "outro": 10.0,
     "pop_in": {"in": 2.4, "url0": 2.9, "url1": 5.2, "enter": 5.5, "drop": 5.65, "badge": 5.85, "pack": 8.0, "out": 9.7},
     "pop_out": {"in": 2.3, "url0": 3.0, "url1": 4.9, "enter": 5.1, "drop": 5.25, "badge": 5.45, "pack": 7.3, "out": 9.6},
     "L4": round(r_click + 0.1, 2), "theme_at": round(theme_at, 2), "n3_at": 10.0, "n2_at": 0.3}
json.dump(W, open('$D/pN1/${k}_warp.json', 'w'), indent=1)
print('$k narration ok, N4', round(N4, 2))
EOF
python3 kinetic3.py pN1/kin_$k.json pN1/kin_$k.mp4
SUBJ=$SK PARTIE=1 MOIS="Novembre 2026" TACHE=3 CAPDIR=$D/capN1/ OUTK=$D/pN1/site_${k}_ WARP=pN1/${k}_warp.json POPMOD=$D/omni.py python3 site3.py render
(cd $V6 && python3 exam_t3l.py sess_$k $D/$k/voice.wav $D/$k/body.mp4)
python3 t3assemble.py $k pN1 $T/$k/narr.wav /home/claude/out/$OUT.mp4
f=$D/pN1/site_${k}_site_intro.mp4; d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $f)
mkdir -p $V6/th_$k && cd $V6/th_$k && cp $V6/thumb3b.py $V6/logoanim.py $V6/person.png $V6/logo.png . && cp -r $V6/lg . 2>/dev/null || true
cd $V6/th_$k && ffmpeg -v error -y -ss $(python3 -c "print($d*0.8)") -i $f -frames:v 1 ui.png && TASKN=3 python3 thumb3b.py light /home/claude/out/${OUT}_miniature.jpg 4:30 "$TH"
echo "$k DONE $(ffprobe -v error -show_entries format=duration -of csv=p=0 /home/claude/out/$OUT.mp4)"

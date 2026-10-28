#!/bin/bash
cd /tmp/claude-0/-home-claude/7a22c9af-0a80-57d2-89a2-1a32e1824476/scratchpad/v6
D=/home/claude/v24
for k in "$@"; do
  [ -f $D/$k/body.ok ] && continue
  s=$(date +%s); python3 exam_light.py sess_$k $D/$k/voice.wav $D/$k/body.mp4 > $D/$k/render.log 2>&1 && touch $D/$k/body.ok && echo "$k body $(( $(date +%s)-s ))s" || echo "$k BODY FAIL"
done

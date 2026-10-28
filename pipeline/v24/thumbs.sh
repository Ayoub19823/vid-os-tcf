#!/bin/bash
# usage: thumbs.sh P key outname "SUBJ|LINE"
P=$1; k=$2; o=$3; s=$4; D=/home/claude/v24; V=/tmp/claude-0/-home-claude/7a22c9af-0a80-57d2-89a2-1a32e1824476/scratchpad/v6
f=$D/p$P/site_${k}_site_intro.mp4; d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $f)
cd $V && ffmpeg -v error -y -ss $(python3 -c "print($d*0.8)") -i $f -frames:v 1 ui_tmp.png && cp ui.png ui_keep.png && cp ui_tmp.png ui.png && python3 thumb2b.py light /home/claude/out/${o}_miniature.jpg 3:30 "$s"; cp ui_keep.png ui.png

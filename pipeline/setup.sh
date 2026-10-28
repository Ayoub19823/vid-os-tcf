#!/bin/bash
# Réinstalle la chaîne de production vidéo dans un environnement neuf.
# usage : bash pipeline/setup.sh   (depuis la racine du dépôt vid-os-tcf)
set -e
R=$(cd "$(dirname "$0")" && pwd)
V6=/tmp/claude-0/-home-claude/7a22c9af-0a80-57d2-89a2-1a32e1824476/scratchpad/v6
mkdir -p /home/claude/v24 /home/claude/t3 /home/claude/pipe/narr /home/claude/work /home/claude/out $V6 /usr/share/fonts/opentype/inter
cp $R/v24/* /home/claude/v24/
cp -r $R/v6/* $V6/
cp $R/fonts/*.otf /usr/share/fonts/opentype/inter/
cp $R/t3/segs.py /home/claude/t3/
cp $R/narr/*.wav /home/claude/pipe/narr/
cp $R/pick.js /home/claude/pipe/
chmod +x /home/claude/v24/*.sh
python3 -c "import PIL, numpy, cv2" 2>/dev/null || pip install --break-system-packages -q pillow numpy opencv-python-headless
node -e "require('playwright')" && which ffmpeg >/dev/null && echo "setup OK"

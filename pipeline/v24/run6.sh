#!/bin/bash
# usage: run6.sh key subj outname
k=$1; s=$2; out=$3; D=/home/claude/v24
cd /tmp/claude-0/-home-claude/7a22c9af-0a80-57d2-89a2-1a32e1824476/scratchpad/v6
python3 exam_light.py sess_$k $D/$k/voice.wav $D/$k/body.mp4 > $D/$k/render.log 2>&1 || { echo "$k RENDER FAIL"; exit 1; }
cd $D/$k
AD=$(python3 -c "import wave;w=wave.open('voice.wav');print(w.getnframes()/w.getframerate())")
B=$(python3 -c "print(4+$AD+14)")
ffmpeg -v error -y -i body.mp4 -t 4 -c:v libx264 -crf 18 -pix_fmt yuv420p -r 25 s1.mp4
ffmpeg -v error -y -ss 4 -i body.mp4 -t $(python3 -c "print($B-4)") -c:v libx264 -crf 20 -tune stillimage -pix_fmt yuv420p -r 25 s3.mp4
ffmpeg -v error -y -ss $B -i body.mp4 -t 5.5 -c:v libx264 -crf 18 -pix_fmt yuv420p -r 25 s5.mp4
printf "file 's1.mp4'\nfile '../site$s/site_intro.mp4'\nfile 's3.mp4'\nfile '../site$s/site_outro.mp4'\nfile 's5.mp4'\n" > list.txt
ffmpeg -v error -y -f concat -safe 0 -i list.txt -c copy vid.mp4
cd $D && python3 assemble_audio.py $k x
ffmpeg -v error -y -i $k/vid.mp4 -i $k/mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 160k -shortest -movflags +faststart /home/claude/out/$out.mp4
echo "$k DONE $(ffprobe -v error -show_entries format=duration -of csv=p=0 /home/claude/out/$out.mp4) $(du -m /home/claude/out/$out.mp4 | cut -f1)MB"

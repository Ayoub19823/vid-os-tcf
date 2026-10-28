import re, subprocess, os
T=open('/root/.claude/projects/-home-claude/7a22c9af-0a80-57d2-89a2-1a32e1824476.jsonl').read()
for line in open('flows98.txt'):
    dst, flow, sess = line.split()
    if os.path.exists(dst+'.wav') and os.path.getsize(dst+'.wav')>100000: continue
    m=re.findall(r'https://storage\.googleapis\.com/xi-backend/database/workspace/[0-9a-f]+/content_generation/'+sess+r'/[A-Za-z0-9]+/content\.mp3\?[A-Za-z0-9%=&\-_.]+', T)
    if not m: print(dst,'no url'); continue
    os.makedirs(os.path.dirname(dst),exist_ok=True)
    r=subprocess.run(['curl','-sS','-o',dst+'.mp3',m[-1]])
    subprocess.run(['ffmpeg','-v','error','-y','-i',dst+'.mp3','-ar','44100','-ac','1',dst+'.wav'])
    print(dst, os.path.getsize(dst+'.wav') if os.path.exists(dst+'.wav') else 'FAIL')

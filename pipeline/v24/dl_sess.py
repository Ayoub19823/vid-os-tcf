"""Télécharge les audios ElevenLabs à partir des session_ids (les URL signées sont lues dans le journal de la conversation).
usage : python3 dl_sess.py '{"<session_id>": "/home/claude/work/<cle>/e", ...}'
Appeler creative_get_flow_run_status AVANT (c'est lui qui écrit les URL dans le journal)."""
import re, subprocess, sys, os, json, glob
T = ''.join(open(f, errors='ignore').read() for f in sorted(glob.glob('/root/.claude/projects/*/*.jsonl'), key=os.path.getmtime)[-3:])
T += ''.join(open(f, errors='ignore').read() for f in glob.glob('/root/.claude/projects/*/*/tool-results/*.txt') + glob.glob('/root/.claude/projects/*/tool-results/*.txt'))
for sess, dst in json.loads(sys.argv[1]).items():
    m = re.findall(r'https://storage\.googleapis\.com/xi-backend/database/workspace/[0-9a-f]+/content_generation/' + sess + r'/[A-Za-z0-9]+/content\.mp3\?[A-Za-z0-9%=&\-_.]+', T)
    if not m: print('PAS D’URL', sess, dst); continue
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    subprocess.run(['curl', '-sS', '-o', dst + '.mp3', m[-1]], check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', dst + '.mp3', '-ar', '44100', '-ac', '1', dst + '.wav'], check=True)
    print(dst + '.wav', os.path.getsize(dst + '.wav'))

"""Mixage audio + montage final d'une vidéo « exercice corrigé » d'expression écrite (dérivé de t3assemble).
usage: python3 t3assemble.py <cle> <dossier pX> <narration.wav> <sortie.mp4>"""
import numpy as np, wave, subprocess, sys, os, json
sys.path.insert(0, '/home/claude/t3')
from segs import segs
SR = 44100; S = '/tmp/claude-0/-home-claude/7a22c9af-0a80-57d2-89a2-1a32e1824476/scratchpad/v6/'
D = '/home/claude/v24/'; key, PD, NARR, OUT = sys.argv[1:5]
PRM = json.load(open(f'{D}{PD}/{key}_warp.json'))
def rd(p):
    w = wave.open(p); x = np.frombuffer(w.readframes(w.getnframes()), '<i2').astype(float) / 32768; x = x.reshape(-1, w.getnchannels()).mean(1); r = w.getframerate()
    if r != SR: x = np.interp(np.arange(int(len(x) * SR / r)) / SR, np.arange(len(x)) / r, x)
    return x
INTRO, OBJ, SITE, BILAN, SOUT, OUTRO = 4.0, 15.4, PRM["real"][-1], 0.0, PRM["outro"], 5.5
v = rd(D + key + '/bodynarr.wav'); AD = len(v) / SR
V0 = INTRO + OBJ + SITE; B0 = V0 + AD; O0 = B0 + BILAN
TOT = O0 + SOUT + OUTRO; N = int(TOT * SR)
o = np.zeros(N + 2 * SR)
o[int(V0 * SR):int(V0 * SR) + len(v)] += v * 1.1
im = rd(S + 'intro_music.wav'); im /= np.abs(im).max(); L = len(im); t = np.arange(L) / SR
g = 0.55 * np.clip((6.0 - t) / 2.0, 0, 1); o[:L] += im * g
b = rd(S + 'bed.wav'); b /= np.abs(b).max()
s0 = int(3.6 * SR); L1 = int(V0 * SR) - s0 + int(1.2 * SR); bb = np.resize(b, L1); tt = np.arange(L1) / SR
gb = 0.16 * np.clip(tt / 1.6, 0, 1) * np.clip((L1 / SR - tt) / 1.4, 0, 1); o[s0:s0 + L1] += bb * gb
def click(at):
    n = int(0.03 * SR); k = np.arange(n) / SR
    c = (np.random.default_rng(int(at * 100)).normal(0, 1, n) * np.exp(-k * 260) + np.sin(2 * np.pi * 1800 * k) * np.exp(-k * 180)) * 0.16
    i = int(at * SR); o[i:i + n] += c
SI = INTRO + OBJ
for sq in (1.95, 4.85, 6.6, 13.25): click(SI + float(np.interp(sq, PRM['seq'], PRM['real'])))
n = rd(NARR); sg = segs(n, minsil=0.6)
assert len(sg) == 7, len(sg)
def level(c, target=0.085):
    win = int(0.05 * SR); m = len(c) // win
    r = np.sqrt((c[:m * win].reshape(m, win) ** 2).mean(1)); act = r[r > 0.01]
    y = c * target / np.sqrt((act ** 2).mean()); pk = np.abs(y).max()
    return y / pk * 0.98 if pk > 0.98 else y
def put(i, at):
    a, e = sg[i]; c = level(n[max(0, a - int(0.03 * SR)):e + int(0.2 * SR)]); j = int(at * SR); o[j:j + len(c)] += c * 1.15
put(0, INTRO + 0.4); put(1, INTRO + 6.6)
put(2, SI + PRM['n2_at']); put(3, SI + PRM['n3_at']); put(4, SI + PRM['theme_at']); put(5, SI + PRM['L4'])
click(O0 + 1.9); put(6, O0 + 0.6)
sB = int(V0 * SR) + int(1.0 * SR); LB = int(B0 * SR) - sB; bb2 = np.resize(b, LB); tb = np.arange(LB) / SR
o[sB:sB + LB] += bb2 * 0.06 * np.clip(tb / 3, 0, 1) * np.clip((LB / SR - tb) / 2, 0, 1)
s0 = int(B0 * SR); L2 = N - s0; bb = np.resize(b, L2); tt = np.arange(L2) / SR
gb = 0.35 * np.clip(tt / 1.0, 0, 1) * np.clip((L2 / SR - tt) / 2.5, 0, 1)
duck = np.ones(L2); a0 = int((O0 - B0 + 0.3) * SR); a1 = int((O0 - B0 + 9.4) * SR); duck[a0:a1] = 0.45
o[s0:N] += bb * gb * duck
o = o[:N]; o /= max(1, np.abs(o).max() / 0.95)
mix = f'{D}{key}/mix.wav'
w = wave.open(mix, 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((np.stack([o, o], 1) * 32767).astype('<i2').tobytes()); w.close()
# vidéo
K = f'{D}{key}/'; P = f'{D}{PD}/'
run = lambda *a: subprocess.run(['ffmpeg', '-v', 'error', '-y', *a], check=True)
body = K + 'body.mp4'; BE = INTRO + AD + BILAN
run('-i', body, '-t', str(INTRO), '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', '25', K + 's1.mp4')
run('-ss', str(INTRO), '-i', body, '-t', str(BE - INTRO), '-c:v', 'libx264', '-crf', '20', '-tune', 'stillimage', '-pix_fmt', 'yuv420p', '-r', '25', K + 's3.mp4')
run('-ss', str(BE), '-i', body, '-t', str(OUTRO), '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', '25', K + 's5.mp4')
open(K + 'list.txt', 'w').write(f"file 's1.mp4'\nfile '{P}kin_{key}.mp4'\nfile '{P}site_{key}_site_intro.mp4'\nfile 's3.mp4'\nfile '{P}site_{key}_site_outro.mp4'\nfile 's5.mp4'\n")
run('-f', 'concat', '-safe', '0', '-i', K + 'list.txt', '-c', 'copy', K + 'vid.mp4')
run('-i', K + 'vid.mp4', '-i', mix, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', OUT)
print('TOT', round(TOT, 2), 'voice at', round(V0, 2), 'bilan', round(B0, 2), 'outro', round(O0, 2))

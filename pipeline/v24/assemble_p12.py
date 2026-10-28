import numpy as np, wave, subprocess, sys
SR = 44100; S = '/tmp/claude-0/-home-claude/7a22c9af-0a80-57d2-89a2-1a32e1824476/scratchpad/v6/'
D = '/home/claude/v24/'; key = sys.argv[1]; OUT = sys.argv[2]
import json; PRM = json.load(open(D + 'p12/' + key + '_warp.json'))
def rd(p):
    w = wave.open(p); x = np.frombuffer(w.readframes(w.getnframes()), '<i2').astype(float) / 32768; x = x.reshape(-1, w.getnchannels()).mean(1); r = w.getframerate()
    if r != SR: x = np.interp(np.arange(int(len(x) * SR / r)) / SR, np.arange(len(x)) / r, x)
    return x
INTRO, OBJ, SITE, BILAN, SOUT, OUTRO = 4.0, 15.4, PRM['real'][-1], 14.0, 10.0, 5.5
v = rd(D + key + '/voice.wav'); AD = len(v) / SR
V0 = INTRO + OBJ + SITE                      # voice start in final timeline
B0 = V0 + AD                           # bilan start
O0 = B0 + BILAN                        # site outro start
TOT = O0 + SOUT + OUTRO; N = int(TOT * SR)
o = np.zeros(N + SR)
o[int(V0 * SR):int(V0 * SR) + len(v)] += v * 0.95
# intro music: full level on logo, crossfade into bed under the site sequence
im = rd(S + 'intro_music.wav'); im /= np.abs(im).max(); L = len(im); t = np.arange(L) / SR
g = 0.55 * np.clip((6.0 - t) / 2.0, 0, 1); o[:L] += im * g
b = rd(S + 'bed.wav'); b /= np.abs(b).max()
s0 = int(3.6 * SR); L1 = int(V0 * SR) - s0 + int(1.2 * SR); bb = np.resize(b, L1); tt = np.arange(L1) / SR
gb = 0.16 * np.clip(tt / 1.6, 0, 1) * np.clip((L1 / SR - tt) / 1.4, 0, 1); o[s0:s0 + L1] += bb * gb
# soft UI clicks
def click(at):
    n = int(0.03 * SR); k = np.arange(n) / SR
    c = (np.random.default_rng(int(at * 100)).normal(0, 1, n) * np.exp(-k * 260) + np.sin(2 * np.pi * 1800 * k) * np.exp(-k * 180)) * 0.16
    i = int(at * SR); o[i:i + n] += c
SI = INTRO + OBJ
for c in (9.79, 12.43, PRM['L4'] + 2.25): click(SI + c)
n1 = rd(D + 'narr/n1.wav'); n2 = rd(D + 'narr/n2.wav'); n3 = rd(D + 'narr/n4.wav')
def level(c, target=0.085):
    win = int(0.05 * SR); n = len(c) // win
    r = np.sqrt((c[:n * win].reshape(n, win) ** 2).mean(1)); act = r[r > 0.01]
    y = c * target / np.sqrt((act ** 2).mean()); pk = np.abs(y).max()
    return y / pk * 0.98 if pk > 0.98 else y
def put(src, a, d, at):
    c = level(src[max(0, int(a * SR) - int(0.03 * SR)):int((a + d) * SR) + int(0.2 * SR)]); i = int(at * SR); o[i:i + len(c)] += c * 1.15
put(n2, 0.03, 5.51, INTRO + 0.4)
put(n2, 9.58, 7.75, INTRO + 6.6)
put(n1, 7.54, 8.34, SI + 0.5)
put(n3, 0.03, 3.5, SI + 9.5)
put(n3, *PRM['theme'], SI + 15.8)
put(n1, 27.61, 2.6, SI + PRM['L4'])
click(O0 + 1.9)
put(n1, 33.76, 8.46, O0 + 0.6)
# bed under bilan + site recall + outro
s0 = int(B0 * SR); L2 = N - s0; bb = np.resize(b, L2); tt = np.arange(L2) / SR
gb = 0.35 * np.clip(tt / 1.0, 0, 1) * np.clip((L2 / SR - tt) / 2.5, 0, 1)
duck = np.ones(L2); a0 = int((O0 - B0 + 0.3) * SR); a1 = int((O0 - B0 + 9.4) * SR); duck[a0:a1] = 0.45
o[s0:N] += bb * gb * duck
o = o[:N]; o /= max(1, np.abs(o).max() / 0.95)
w = wave.open(D + key + '/mix.wav', 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((np.stack([o, o], 1) * 32767).astype('<i2').tobytes()); w.close()
body = D + key + '/body.mp4'; BEND = INTRO + AD + BILAN
fc = (f"[0:v]trim=0:{INTRO},setpts=PTS-STARTPTS[a];[1:v]setpts=PTS-STARTPTS[b];"
      f"[0:v]trim={INTRO}:{BEND},setpts=PTS-STARTPTS[c];[2:v]setpts=PTS-STARTPTS[d];"
      f"[0:v]trim={BEND}:{BEND + OUTRO},setpts=PTS-STARTPTS[e];[a][b][c][d][e]concat=n=5:v=1:a=0,fps=25,format=yuv420p[v]")
subprocess.run(['true']) if 0 else None
if 0: subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', body, '-i', D + 'site_intro.mp4', '-i', D + 'site_outro.mp4', '-i', D + key + '/mix.wav',
                '-filter_complex', fc, '-map', '[v]', '-map', '3:a', '-c:v', 'libx264', '-crf', '23', '-tune', 'stillimage', '-c:a', 'aac', '-b:a', '160k',
                '-shortest', '-movflags', '+faststart', OUT], check=True)
print('TOT', round(TOT, 2), 'voice', round(V0, 2), round(B0, 2), 'outro', round(O0, 2))

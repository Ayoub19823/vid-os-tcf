import numpy as np, wave, subprocess, sys
SR = 44100; S = '/tmp/claude-0/-home-claude/7a22c9af-0a80-57d2-89a2-1a32e1824476/scratchpad/v6/'
D = '/home/claude/v24/'; key = sys.argv[1]; OUT = sys.argv[2]
def rd(p):
    w = wave.open(p); x = np.frombuffer(w.readframes(w.getnframes()), '<i2').astype(float) / 32768; x = x.reshape(-1, w.getnchannels()).mean(1); r = w.getframerate()
    if r != SR: x = np.interp(np.arange(int(len(x) * SR / r)) / SR, np.arange(len(x)) / r, x)
    return x
INTRO, SITE, BILAN, SOUT, OUTRO = 4.0, 14.2, 14.0, 6.5, 5.5
v = rd(D + key + '/voice.wav'); AD = len(v) / SR
V0 = INTRO + SITE                      # voice start in final timeline
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
gb = 0.40 * np.clip(tt / 1.6, 0, 1) * np.clip((L1 / SR - tt) / 1.4, 0, 1); o[s0:s0 + L1] += bb * gb
# soft UI clicks
def click(at):
    n = int(0.03 * SR); k = np.arange(n) / SR
    c = (np.random.default_rng(int(at * 100)).normal(0, 1, n) * np.exp(-k * 260) + np.sin(2 * np.pi * 1800 * k) * np.exp(-k * 180)) * 0.16
    i = int(at * SR); o[i:i + n] += c
for c in (1.95, 4.85, 13.25): click(INTRO + c)
click(O0 + 1.9)
# bed under bilan + site recall + outro
s0 = int(B0 * SR); L2 = N - s0; bb = np.resize(b, L2); tt = np.arange(L2) / SR
gb = 0.35 * np.clip(tt / 1.0, 0, 1) * np.clip((L2 / SR - tt) / 2.5, 0, 1); o[s0:N] += bb * gb
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

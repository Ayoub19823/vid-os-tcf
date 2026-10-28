import sys, re, json, wave, numpy as np
sys.path.insert(0, '/home/claude/v24')
from script6 import SIMS
key, ewav, cwav = sys.argv[1], sys.argv[2], sys.argv[3]
S = SIMS[key]; SR = 44100
clean = lambda t: re.sub(r'\s+', ' ', re.sub(r'\[[^\]]*\]', '', t)).strip()
def rd(p):
    w = wave.open(p); x = np.frombuffer(w.readframes(w.getnframes()), '<i2').astype(float) / 32768
    return x.reshape(-1, w.getnchannels()).mean(1)
def segs(x, thr=0.008, minsil=1.5):
    win = int(0.02 * SR); e = np.sqrt(np.convolve(x ** 2, np.ones(win) / win, 'same')); idx = np.nonzero(e > thr)[0]
    out = []; s = idx[0]; p = idx[0]
    for j in idx[1:]:
        if j - p > minsil * SR: out.append((s, p)); s = j
        p = j
    out.append((s, p)); return out
def clips(f, n):
    x = rd(f)
    for ms in (1.5, 1.3, 1.7, 1.1, 1.9, 2.1):
        sg = segs(x, minsil=ms)
        if len(sg) == n: break
    else: raise SystemExit(f'segment mismatch {f}: got {len(sg)} want {n}')
    return [x[max(0, a - int(0.05 * SR)):b + int(0.15 * SR)] for a, b in sg]
E = [clean(t) for t in S['E']]; C = [clean(t) for t in S['C']]
ec = clips(ewav, len(E)); cc = clips(cwav, len(C))
seq = [('E', ec[0], E[0])]
for i in range(len(C)):
    seq.append(('R', cc[i], C[i])); seq.append(('E', ec[i + 1], E[i + 1]))
rng = np.random.default_rng(11)
gaps = [rng.uniform(1.3, 2.3) if s == 'R' else rng.uniform(0.6, 1.1) for s, _, _ in seq[1:]]
dur = [len(c) / SR for _, c, _ in seq]
i14 = [k for k, (s, c, t) in enumerate(seq) if 'reste trente' in t][0]
target = 178.0
sc = (target - sum(dur[1:i14])) / sum(gaps[:i14 - 1])
sc = max(0.55, min(sc, 2.2))
gaps = [g * sc if k < i14 - 1 else g for k, g in enumerate(gaps)]
post = sum(dur[i14:]) + sum(gaps[i14 - 1:])
need = 213.0 - (sum(dur[1:i14]) + sum(gaps[:i14 - 1]))
if post < need:
    ex = (need - post) / len(gaps[i14 - 1:]); gaps = [g + ex if k >= i14 - 1 else g for k, g in enumerate(gaps)]
t = 0.3; L = []; parts = []; cstart = []; cend = []
for k, (s, c, txt) in enumerate(seq):
    if k: t += gaps[k - 1]
    parts.append((t, c)); d = len(c) / SR
    if k == 0:
        sp = txt.index("C'est parti")
        L.append(('E', round(t + 0.05, 2), round(t + d * 0.62, 2), txt[:sp].strip()))
        L.append(('E', round(t + d * 0.64, 2), round(t + d - 0.15, 2), txt[sp:].strip())); chrono0 = t + d
    else:
        L.append((s, round(t + 0.05, 2), round(t + d - 0.15, 2), txt))
        if s == 'R': cstart.append(t); cend.append(t + d)
    if 'reste trente' in txt: t14 = t + d * 0.5
    t += d
tot = t + 0.6; o = np.zeros(int(tot * SR) + SR)
for st, c in parts: i = int(st * SR); o[i:i + len(c)] += c
o = o[:int(tot * SR)]; o /= np.abs(o).max() / 0.89
w = wave.open(f'/home/claude/v24/{key}/voice.wav', 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((o * 32767).astype('<i2').tobytes()); w.close()
cs = max(chrono0 + 0.5, t14 - 180.0); stop = min(cs + 210.0, L[-1][2])
q = [round(cend[i] - 0.1, 1) for i in range(len(C)) if '?' in C[i]]
feed = [(round(cend[i] + 0.2, 1), k_, a, b) for i, k_, a, b in S['feed']]
themes = [(n, round(cstart[i], 2)) for n, i in S['themes']]
fts = [f[0] for f in feed]; cta = []
for i in range(len(C)):
    a0 = cend[i] + 0.3
    if a0 < 50 or any(a0 - 0.5 < ft < a0 + 7.5 for ft in fts): continue
    if not cta or a0 - cta[-1][0] > 60: cta.append((round(a0, 1), round(a0 + 6.5, 1)))
    if len(cta) == 2: break
role = 'Simulation PACK AYOUB'
sess = f'''E, R = 'C', 'H'
EXAM_NAME, CAND_NAME = {S['exam']!r}, {S['cand']!r}
CAND_ROLE = {role!r}
CAND_LABEL = {S['cand'] + (' · candidate' if S['gender'] == 'f' else ' · candidat')!r}
EXAM_LABEL = {S['exam'] + ' · examinatrice'!r}
FLAG = {S['flag']!r}
INTRO_TAG = "SIMULATION MODÈLE"
REG_LABEL = {S['reg']!r}
CONSIGNE = {S['consigne']!r}
LINES = [
''' + ''.join(f"    ({s}, {a}, {b}, {x!r}),\n" for s, a, b, x in L) + f''']
CHRONO_TOTAL = 210.0
CHRONO_START = {round(cs, 2)}
CHRONO_STOP = {round(stop, 2)}
QUESTIONS = {q}
THEMES = {themes!r}
REG_SWITCH = 999
FEED = {feed!r}
CTA_WINDOWS = {cta!r}
BILAN_STATS = [("{len(q)}", "questions"), ("{len(themes)}", "thèmes"), ("3:30", "d'échange")]
BILAN_BLOCKS = {S['bilan']!r}
TITLE_SUB = "Simulation d'examen — Interaction · TCF Canada"
'''
open(f'/tmp/claude-0/-home-claude/7a22c9af-0a80-57d2-89a2-1a32e1824476/scratchpad/v6/sess_{key}.py', 'w').write(sess)
print(key, 'tot', round(tot, 1), 'conv', round(L[-1][2] - chrono0, 1), 'E14 at chrono', round(210 - (t14 - cs), 1), 'scale', round(sc, 2), 'q', len(q), 'cta', cta)

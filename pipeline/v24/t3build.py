"""Assemble la piste voix d'une simulation Tâche 3 + écrit v6/sess_<cle>.py
usage: python3 t3build.py <cle> <dossier audio> [tempo]
Le dossier contient e.wav (E0..E4), ex.wav (E5, E6), ca.wav, cb.wav, cc.wav."""
import sys, re, os, wave, subprocess, numpy as np
sys.path.insert(0, '/home/claude/v24'); sys.path.insert(0, '/home/claude/t3')
import importlib; t3nov = importlib.import_module(os.environ.get("SCEN", "t3nov"))
from segs import rd, segs, robust
SR = 44100
V6 = '/tmp/claude-0/-home-claude/7a22c9af-0a80-57d2-89a2-1a32e1824476/scratchpad/v6/'
key, AD = sys.argv[1], sys.argv[2]; TEMPO = float(sys.argv[3]) if len(sys.argv) > 3 else 0.93
S = t3nov.SIMS[key]
clean = lambda t: re.sub(r'\s+', ' ', re.sub(r'\[[^\]]*\]', '', t)).strip()

def clips(f, n, tempo=1.0):
    if tempo != 1.0:
        g = f.replace('.wav', '_t.wav'); subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f, '-filter:a', f'atempo={tempo}', '-ar', '44100', '-ac', '1', g], check=True); f = g
    x = rd(f); sg = robust(x, n)
    if len(sg) != n: raise SystemExit(f'segment mismatch {f}')
    out = [x[max(0, a - int(0.05 * SR)):b + int(0.15 * SR)] for a, b in sg]
    return [squeeze(c) for c in out] if COMP else out
COMP = float(os.environ.get('COMP', '0'))
def squeeze(c):
    # raccourcit les silences internes plus longs que COMP secondes
    win = int(0.02 * SR); e = np.sqrt(np.convolve(c ** 2, np.ones(win) / win, 'same')); q = e < 0.006
    keep = np.ones(len(c), bool); i = 0; mx = int(COMP * SR)
    while i < len(c):
        if q[i]:
            j = i
            while j < len(c) and q[j]: j += 1
            if j - i > mx and i > 0 and j < len(c): keep[i + mx // 2: j - mx // 2] = False
            i = j
        else: i += 1
    return c[keep]
def level(c, target=0.085):
    win = int(0.05 * SR); n = len(c) // win
    r = np.sqrt((c[:n * win].reshape(n, win) ** 2).mean(1)); act = r[r > 0.01]
    y = c * target / (np.sqrt((act ** 2).mean()) if len(act) else 1); pk = np.abs(y).max()
    return y / pk * 0.98 if pk > 0.98 else y

E_txt = [clean(t) for t in S['E']]; C_txt = [clean(t) for t in S['CA'] + S['CB'] + S['CC']]
ec = clips(f'{AD}/e.wav', 5) + clips(f'{AD}/ex.wav', 2) if os.path.exists(f'{AD}/ex.wav') else clips(f'{AD}/e.wav', 7)
cc = clips(f'{AD}/ca.wav', len(S['CA']), TEMPO) + (clips(f'{AD}/cb.wav', len(S['CB']), TEMPO) + clips(f'{AD}/cc.wav', len(S['CC']), TEMPO)
      if os.path.exists(f'{AD}/cc.wav') else clips(f'{AD}/cb.wav', len(S['CB']) + len(S['CC']), TEMPO))
ec = [level(c) for c in ec]; cc = [level(c) for c in cc]
Q = t3nov.seq(S)
items = [(s, (ec if s == 'E' else cc)[i], (E_txt if s == 'E' else C_txt)[i], i) for s, i in Q]
rng = np.random.default_rng(7)
gaps = []
for k in range(1, len(items)):
    a, b = items[k - 1][0], items[k][0]
    gaps.append(rng.uniform(0.55, 1.0) if a == b == 'C' else rng.uniform(0.7, 1.0) if b == 'E' else rng.uniform(1.0, 1.5))
dur = [len(c) / SR for _, c, _, _ in items]
iE3 = [k for k, it in enumerate(items) if it[0] == 'E' and it[3] == 3][0]
# chrono démarre à la fin de E0 ; E3 (« Il nous reste trente secondes ») doit tomber à ~238 s
pre_speech = sum(dur[1:iE3]); pre_gaps = sum(gaps[:iE3])   # gaps[0] = E0->C0 ... gaps[iE3-1] = ->E3
sc = (238.0 - pre_speech) / pre_gaps
print('pre speech', round(pre_speech, 1), 'gaps', round(pre_gaps, 1), 'scale', round(sc, 2))
sc = max(0.7, min(sc, 1.9))
gaps = [g * sc if k < iE3 else g for k, g in enumerate(gaps)]
t = 0.3; L = []; parts = []; st = {}; en = {}
for k, (s, c, txt, i) in enumerate(items):
    if k: t += gaps[k - 1]
    parts.append((t, c)); d = len(c) / SR
    if k == 0:
        sp = txt.index('Vous avez')
        L.append(('E', round(t + 0.05, 2), round(t + d * 0.70, 2), txt[:sp].strip()))
        L.append(('E', round(t + d * 0.72, 2), round(t + d - 0.15, 2), txt[sp:].strip())); chrono0 = t + d + 0.2
    else:
        L.append(('R' if s == 'C' else 'E', round(t + 0.05, 2), round(t + d - 0.15, 2), txt))
    st[(s, i)] = t; en[(s, i)] = t + d
    t += d
tot = t + 0.8; o = np.zeros(int(tot * SR) + SR)
for a, c in parts: j = int(a * SR); o[j:j + len(c)] += c
o = o[:int(tot * SR)]; o /= np.abs(o).max() / 0.89
os.makedirs(f'/home/claude/v24/{key}', exist_ok=True)
w = wave.open(f'/home/claude/v24/{key}/voice.wav', 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((o * 32767).astype('<i2').tobytes()); w.close()
CT = 270.0; cs = chrono0; stop = min(cs + CT, st[('E', 4)])
def cpos(i, word):
    txt = C_txt[i]; p = txt.find(word); p = 0 if p < 0 else p
    return round(st[('C', i)] + (en[('C', i)] - st[('C', i)]) * p / max(1, len(txt)) + 0.2, 2)
conn = sorted([(cpos(i, w_), w_) for i, w_ in S['conn'] if ('C', i) in st])
args = sorted(round(st[('C', i)] + 0.3, 2) for i in S['args'] if ('C', i) in st)
themes = sorted([(n, round(st[('C', i)], 2)) for n, i in S['themes']], key=lambda x: x[1])
feed = sorted([(round(en[('C', i)] + 0.2, 1), k_, a, b) for i, k_, a, b in S['feed'] if ('C', i) in st])
fts = [f[0] for f in feed]; cta = []
for i in sorted(i for s_, i in st if s_ == 'C'):
    a0 = en[('C', i)] + 0.3
    if a0 < 50 or any(a0 - 0.5 < ft < a0 + 7.5 for ft in fts): continue
    if not cta or a0 - cta[-1][0] > 70: cta.append((round(a0, 1), round(a0 + 6.5, 1)))
    if len(cta) == 2: break
lab = S['cand'] + (' · candidate' if S['gender'] == 'f' else ' · candidat')
sess = f'''E, R = 'C', 'H'
EXAM_NAME, CAND_NAME = {S['exam']!r}, {S['cand']!r}
CAND_ROLE = 'Simulation PACK AYOUB'
CAND_LABEL = {lab!r}
EXAM_LABEL = {S['exam'] + ' · examinatrice'!r}
FLAG = {S['flag']!r}
INTRO_TAG = "SIMULATION MODÈLE"
TASK_TITLE = "Expression orale · Tâche 3"
TITLE_SUB = "Point de vue argumenté · TCF Canada"
STAT1_LABEL, STAT1_SUB = "ARGUMENTS", {('avancés par ' + S['cand'])!r}
STAT2_LABEL = "CONNECTEURS"
CONSIGNE_LABEL = "SUJET"
THEMES_LABEL = "PLAN DE L'EXPOSÉ"
CONSIGNE = {S['consigne']!r}
LINES = [
''' + ''.join(f"    ({s}, {a}, {b}, {x!r}),\n" for s, a, b, x in L) + f''']
CHRONO_TOTAL = {CT}
CHRONO_START = {round(cs, 2)}
CHRONO_STOP = {round(stop, 2)}
QUESTIONS = []
ARGS = {args!r}
CONNECTORS = {conn!r}
THEMES = {themes!r}
REG_SWITCH = 9999.0
FEED = {feed!r}
CTA_WINDOWS = {cta!r}
BILAN_STATS = [("{len(args)}", "arguments"), ("{len(conn)}", "connecteurs"), ("4:30", "d'épreuve")]
BILAN_BLOCKS = {S['bilan']!r}
'''
open(V6 + f'sess_{key}.py', 'w').write(sess)
print(key, 'tot', round(tot, 1), 'chrono0', round(cs, 1), 'E3 at elapsed', round(st[('E', 3)] - cs, 1), 'E4 at', round(st[('E', 4)] - cs, 1), 'scale', round(sc, 2), 'cta', cta)

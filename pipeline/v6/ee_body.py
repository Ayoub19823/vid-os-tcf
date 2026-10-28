"""Corps d'une vidéo « exercice corrigé » d'expression écrite.
usage : python3 ee_body.py <spec.json> <narration_corps.wav> <sortie.mp4> [instants pour aperçu]
spec.json : task, mois, combi, consigne, mots_cles[], points[], copie (erreurs notées [[faux|juste|raison]]),
            modele [[étiquette, paragraphe], ...], vocab[], bilan[[titre,[items]]x3], mini, maxi, steps (durées calculées par ee_make)"""
import sys, os, json, math, re, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
import logoanim
logoanim.THEME = 'light'
from logoanim import build as logo_build, static_logo
SP = json.load(open(sys.argv[1])); AUD = sys.argv[2]; OUTV = sys.argv[3]
ONLY = [float(v) for v in sys.argv[4].split(',')] if len(sys.argv) > 4 else None
W, H, FPS = 1920, 1080, 25
INTRO, OUTRO = 4.0, 5.5
ROYAL = (24, 56, 255); SKY = (38, 169, 255); INK = (20, 27, 77); SLATE = (92, 106, 146); FLAG = (229, 30, 32)
GREEN = (22, 163, 74); ORANGE = (234, 120, 10); GOLD = (214, 150, 0); WHITE = (255, 255, 255); LINEC = (220, 229, 248); YEL = (255, 214, 10)
FD = "/usr/share/fonts/opentype/inter/"
BL, XB, BD, SB, MD, IT = [FD + f for f in ("InterDisplay-Black.otf", "InterDisplay-ExtraBold.otf", "Inter-Bold.otf", "Inter-SemiBold.otf", "Inter-Medium.otf", "Inter-MediumItalic.otf")]
_fc = {}
def F(p, s):
    k = (p, int(s))
    if k not in _fc: _fc[k] = ImageFont.truetype(p, int(s))
    return _fc[k]
def clamp(v, a=0., b=1.): return max(a, min(b, v))
def ease(v): v = clamp(v); return v * v * (3 - 2 * v)
def ob(v, c=1.6): v = clamp(v); return 1 + (c + 1) * (v - 1) ** 3 + c * (v - 1) ** 2
def A(c, a): return tuple(c[:3]) + (int(255 * clamp(a)),)
wv = wave.open(AUD); sr = wv.getframerate(); ADUR = wv.getnframes() / sr
STEPS = SP['steps']            # [{kind, t0, t1, k?}] en secondes dans la piste narration
TOTAL = INTRO + ADUR + OUTRO
TASKN = SP['task']; TASKL = {1: "Message court", 2: "Narration", 3: "Argumentation"}[TASKN]

# ---------- copie : jetons (mot, n° d'erreur ou None)
ERR = []; TOK = []
for part in re.split(r'(\[\[.*?\]\])', SP['copie']):
    if part.startswith('[['):
        faux, juste, why = part[2:-2].split('|'); i = len(ERR); ERR.append((faux, juste, why))
        for w in faux.split(): TOK.append((w, i))
    else:
        for w in part.split(): TOK.append((w, None))
def nwords(toks): return sum(1 for w, _ in toks if re.search(r'\w', w))
NW_COPIE = nwords(TOK)
MODEL = SP['modele']; NW_MODEL = sum(len([w for w in p.split() if re.search(r'\w', w)]) for _, p in MODEL)

# ---------- fond
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
td = np.clip((xx / W) * .6 + (yy / H) * .4, 0, 1)[..., None]
bg = (np.array((250, 251, 255), np.float32) * (1 - td) + np.array((234, 241, 255), np.float32) * td)
dots = ((xx % 34 < 2.2) & (yy % 34 < 2.2))[..., None]; bg = np.where(dots, bg * .95, bg)
PLAIN = Image.fromarray(bg.astype(np.uint8)).convert('RGBA')
LG = static_logo(96)

def wrap(words, font, maxw):
    lines, cur, wc = [], [], 0; sp = font.getlength(' ')
    for wd in words:
        wl = font.getlength(wd if isinstance(wd, str) else wd[0])
        if cur and wc + sp + wl > maxw: lines.append(cur); cur, wc = [wd], wl
        else: cur.append(wd); wc += (sp if len(cur) > 1 else 0) + wl
    if cur: lines.append(cur)
    return lines
def nb(s): return s.replace(' ?', ' ?').replace(' !', ' !').replace(' :', ' :').replace(' »', ' »').replace('« ', '« ')
def card(d, b, col=None, a=1.0, r=28):
    x0, y0, x1, y1 = b
    d.rounded_rectangle([x0, y0 + 8, x1, y1 + 8], radius=r, fill=(20, 40, 120, int(16 * a)))
    d.rounded_rectangle(b, radius=r, fill=A(WHITE, a), outline=A(col or LINEC, a), width=3 if col else 2)

def header(fr, at):
    d = ImageDraw.Draw(fr, 'RGBA'); fr.alpha_composite(LG, (40, 22))
    d.text((40 + LG.width + 26, 46), f"Expression écrite · Tâche {TASKN}", font=F(BL, 44), fill=INK, anchor='lm')
    d.text((40 + LG.width + 28, 96), f"Exercice corrigé · {SP['mois']} · Combinaison {SP['combi']} · TCF Canada", font=F(MD, 22), fill=SLATE, anchor='lm')
    t = f"{TASKL.upper()} · {SP['mini']}–{SP['maxi']} MOTS"; f = F(BD, 24); tw = f.getlength(t)
    d.rounded_rectangle([W - 60 - tw - 48, 44, W - 60, 98], radius=27, fill=A(ROYAL, 1)); d.text((W - 60 - tw / 2 - 24, 71), t, font=f, fill=WHITE, anchor='mm')

def step_at(at):
    cur = None
    for s in STEPS:
        if at >= s['t0'] - 0.05: cur = s
    return cur

def left_panel(fr, at, s):
    d = ImageDraw.Draw(fr, 'RGBA')
    # sujet
    card(d, [40, 140, 690, 470]); d.text((70, 178), "SUJET", font=F(BD, 20), fill=FLAG, anchor='lm')
    words = nb(SP['consigne']).split(' '); f = F(MD, 21); lines = wrap(words, f, 590)
    while len(lines) > 9 and f.size > 15: f = F(MD, f.size - 1); lines = wrap(words, f, 590)
    for i, ln in enumerate(lines[:10]): d.text((70, 214 + i * (f.size + 7)), ' '.join(ln), font=f, fill=INK, anchor='lm')
    # attentes
    card(d, [40, 490, 690, 800]); d.text((70, 528), "CE QUE L'EXAMINATEUR ATTEND", font=F(BD, 20), fill=ROYAL, anchor='lm')
    kinds = [x['kind'] for x in STEPS]; i_pts = kinds.index('points')
    pts_on = at >= STEPS[i_pts]['t0']; done = s and s['kind'] in ('modele', 'vocab', 'bilan')
    for i, ptxt in enumerate(SP['points'][:5]):
        y = 572 + i * 46; a = 1.0 if pts_on else 0.35
        col = GREEN if done else (ROYAL if pts_on else (190, 200, 225))
        d.ellipse([70, y - 13, 96, y + 13], fill=A(col, a))
        if done: d.line([77, y, 82, y + 6, 90, y - 6], fill=WHITE, width=4)
        fp = F(SB, 21)
        while fp.getlength(ptxt) > 560 and fp.size > 14: fp = F(SB, fp.size - 1)
        d.text((110, y), ptxt, font=fp, fill=A(INK, a), anchor='lm')
    # compteur de mots
    card(d, [40, 820, 690, 1040]); d.text((70, 858), "NOMBRE DE MOTS", font=F(BD, 20), fill=SLATE, anchor='lm')
    if s is None or s['kind'] in ('consigne', 'points'): n, lab = 0, "—"
    elif s['kind'] == 'copie': n = int(nwords(TOK) * clamp((at - s['t0']) / max(1, s['t1'] - s['t0'] - 1.0))); lab = "copie du candidat"
    elif s['kind'] == 'erreur': n, lab = NW_COPIE, "copie du candidat"
    else: n, lab = NW_MODEL, "version corrigée"
    ok = SP['mini'] <= n <= SP['maxi']
    d.text((70, 930), str(n) if n else "—", font=F(BL, 66), fill=GREEN if ok else (ORANGE if n else (190, 200, 225)), anchor='lm')
    d.text((210, 942), lab, font=F(MD, 20), fill=SLATE, anchor='lm')
    x0, x1, yb = 70, 660, 1000; d.rounded_rectangle([x0, yb - 7, x1, yb + 7], radius=7, fill=(232, 238, 250))
    lo = x0 + (x1 - x0) * SP['mini'] / (SP['maxi'] * 1.25); hi = x0 + (x1 - x0) / 1.25
    d.rounded_rectangle([lo, yb - 7, hi, yb + 7], radius=7, fill=A(GREEN, 0.35))
    if n: px = x0 + (x1 - x0) * min(1, n / (SP['maxi'] * 1.25)); d.ellipse([px - 11, yb - 11, px + 11, yb + 11], fill=WHITE, outline=GREEN if ok else ORANGE, width=5)
    d.text((lo, yb + 22), str(SP['mini']), font=F(MD, 16), fill=SLATE, anchor='mt'); d.text((hi, yb + 22), str(SP['maxi']), font=F(MD, 16), fill=SLATE, anchor='mt')

def stage_title(d, txt, col=ROYAL):
    d.text((760, 178), txt, font=F(BD, 22), fill=col, anchor='lm')

def draw_text_tokens(d, toks, x0, y0, maxw, reveal=None, cur_err=None, show_err=False, size=31):
    f = F(SB, size); lines = wrap(toks, f, maxw)
    while (len(lines) * (size + 16) > 760) and size > 20: size -= 1; f = F(SB, size); lines = wrap(toks, f, maxw)
    idx = 0; spw = f.getlength(' '); boxes = {}
    for li, ln in enumerate(lines):
        x = x0; y = y0 + li * (size + 16)
        for w, e in ln:
            if reveal is not None and idx >= reveal: return boxes
            wl = f.getlength(w); col = INK
            if e is not None and show_err:
                col = FLAG if e == cur_err else (180, 60, 60)
                if e == cur_err: d.rounded_rectangle([x - 4, y - size * 0.62, x + wl + 4, y + size * 0.62], radius=6, fill=A(FLAG, 0.12))
                d.line([x, y + size * 0.52, x + wl, y + size * 0.52], fill=A(FLAG, 0.9 if e == cur_err else 0.45), width=3)
                b = boxes.get(e); boxes[e] = [min(b[0], x) if b else x, min(b[1], y) if b else y, max(b[2], x + wl) if b else x + wl, max(b[3], y) if b else y]
            d.text((x, y), w, font=f, fill=col, anchor='lm'); x += wl + spw; idx += 1
    return boxes

def main_stage(fr, at, s):
    d = ImageDraw.Draw(fr, 'RGBA'); card(d, [720, 140, 1880, 1040])
    if s is None: return
    k = s['kind']; u = at - s['t0']; dur = max(0.5, s['t1'] - s['t0'])
    if k == 'consigne':
        stage_title(d, "1. LIRE LA CONSIGNE", FLAG)
        words = nb(SP['consigne']).split(' '); f = F(SB, 38); lines = wrap(words, f, 1060)
        while len(lines) * 58 > 700 and f.size > 26: f = F(SB, f.size - 2); lines = wrap(words, f, 1060)
        kws = [kw.lower() for kw in SP['mots_cles']]; nk = len(kws)
        for li, ln in enumerate(lines):
            x = 770; y = 250 + li * (f.size + 20)
            for w in ln:
                wl = f.getlength(w); wc_ = re.sub(r'\W', '', re.sub(r"^[a-z]['’]", '', w.lower())); hit = [i for i, kw in enumerate(kws) if wc_ and wc_ in kw.split()]
                if hit:
                    kk = clamp((u - 1.0 - hit[0] * (dur - 2) / max(1, nk)) / 0.6)
                    if kk > 0: d.rounded_rectangle([x - 4, y - f.size * 0.6, x - 4 + (wl + 8) * ease(kk), y + f.size * 0.6], radius=6, fill=A(YEL, 0.55))
                d.text((x, y), w, font=f, fill=INK, anchor='lm'); x += wl + f.getlength(' ')
    elif k == 'points':
        stage_title(d, "2. CE QU'IL FAUT FAIRE", ROYAL)
        n = len(SP['points'])
        for i, ptxt in enumerate(SP['points']):
            a = ease((u - 0.4 - i * (dur - 1) / n) / 0.5); y = 280 + i * 140
            if a <= 0: continue
            dy = (1 - a) * 30
            d.rounded_rectangle([770, y - 50 + dy, 1830, y + 50 + dy], radius=24, fill=A((240, 245, 255), a), outline=A(ROYAL, 0.6 * a), width=2)
            d.ellipse([796, y - 26 + dy, 848, y + 26 + dy], fill=A(ROYAL, a)); d.text((822, y + dy), str(i + 1), font=F(BL, 30), fill=A(WHITE, a), anchor='mm')
            fp = F(SB, 32)
            while fp.getlength(ptxt) > 940 and fp.size > 20: fp = F(SB, fp.size - 1)
            d.text((874, y + dy), ptxt, font=fp, fill=A(INK, a), anchor='lm')
    elif k == 'copie':
        stage_title(d, "3. LA COPIE D'UN CANDIDAT", ORANGE)
        rev = int(len(TOK) * clamp(u / max(1, dur - 1.0)))
        draw_text_tokens(d, TOK, 770, 240, 1060, reveal=rev)
    elif k == 'erreur':
        e = s['k']; faux, juste, why = ERR[e]
        stage_title(d, f"4. CORRECTION · ERREUR {e + 1} / {len(ERR)}", FLAG)
        draw_text_tokens(d, TOK, 770, 240, 1060, cur_err=e, show_err=True, size=32)
        a = ease(u / 0.4); y0 = 846
        d.rounded_rectangle([760, y0, 1840, 1012], radius=22, fill=A((255, 247, 237), a), outline=A(ORANGE, a), width=3)
        d.text((790, y0 + 38), "Dit : " + faux, font=F(IT, 28), fill=A(SLATE, a), anchor='lm')
        f2 = F(XB, 34)
        while f2.getlength("Mieux : " + juste) > 1010 and f2.size > 22: f2 = F(XB, f2.size - 1)
        d.text((790, y0 + 84), "Mieux : " + juste, font=f2, fill=A(GREEN, a), anchor='lm')
        f3 = F(MD, 24)
        while f3.getlength(why) > 1010 and f3.size > 16: f3 = F(MD, f3.size - 1)
        d.text((790, y0 + 128), why, font=f3, fill=A(INK, a), anchor='lm')
    elif k == 'modele':
        stage_title(d, "5. LA VERSION CORRIGÉE", GREEN)
        size = 27; total = sum(len(p.split()) for _, p in MODEL)
        while True:
            f = F(SB, size); hgt = sum(len(wrap(p.split(), f, 860)) * (size + 12) + 22 for _, p in MODEL)
            if hgt < 800 or size <= 18: break
            size -= 1
        y = 230; cols = [ROYAL, SKY, GREEN, ORANGE, FLAG, GOLD]
        for pi, (lab, p) in enumerate(MODEL):
            lines = wrap(nb(p).split(' '), f, 860); a = ease((u - 0.3 - pi * (dur - 1.5) / len(MODEL)) / 0.5)
            col = cols[pi % len(cols)]; ph = len(lines) * (size + 12)
            fl = F(BD, 17); lw = fl.getlength(lab) + 28
            d.rounded_rectangle([770, y - 16, 770 + min(lw, 190), y + 16], radius=16, fill=A(col, max(a, 0.25)))
            fl2 = fl
            while fl2.getlength(lab) > 170 and fl2.size > 11: fl2 = F(BD, fl2.size - 1)
            d.text((770 + min(lw, 190) / 2, y), lab, font=fl2, fill=WHITE, anchor='mm')
            d.rectangle([968, y - 16, 972, y - 16 + ph], fill=A(col, 0.5 * max(a, 0.3)))
            for li, ln in enumerate(lines): d.text((990, y + li * (size + 12)), ' '.join(ln), font=f, fill=A(INK, 0.3 + 0.7 * a), anchor='lm')
            y += ph + 22
    elif k == 'vocab':
        stage_title(d, "6. VOCABULAIRE UTILE", SKY)
        for i, w in enumerate(SP['vocab']):
            a = ease((u - 0.3 - i * (dur - 1) / len(SP['vocab'])) / 0.5)
            if a <= 0: continue
            c, r = i % 2, i // 2; x = 780 + c * 540; y = 270 + r * 120 + (1 - a) * 20
            fw = F(SB, 30)
            while fw.getlength(w) > 440 and fw.size > 18: fw = F(SB, fw.size - 1)
            d.rounded_rectangle([x, y - 40, x + 500, y + 40], radius=40, fill=A((236, 246, 255), a), outline=A(SKY, a), width=3)
            d.ellipse([x + 24, y - 8, x + 40, y + 8], fill=A(ROYAL, a)); d.text((x + 56, y), w, font=fw, fill=A(INK, a), anchor='lm')
    elif k == 'bilan':
        stage_title(d, "7. BILAN", FLAG)
        cols3 = [GREEN, ORANGE, SKY]
        for bi, (title, items) in enumerate(SP['bilan']):
            a = ease((u - 0.3 - bi * (dur - 1) / 3) / 0.5)
            if a <= 0: continue
            y0 = 220 + bi * 270; col = cols3[bi]
            d.rounded_rectangle([770, y0, 1830, y0 + 240], radius=24, fill=A(WHITE, a), outline=A(col, a), width=3)
            d.rounded_rectangle([770, y0, 786, y0 + 240], radius=8, fill=A(col, a))
            d.text((810, y0 + 40), title, font=F(BD, 26), fill=A(col, a), anchor='lm')
            for j, it in enumerate(items[:3]):
                fi = F(SB, 27)
                while fi.getlength(it) > 960 and fi.size > 17: fi = F(SB, fi.size - 1)
                d.ellipse([812, y0 + 92 + j * 52 - 8, 828, y0 + 92 + j * 52 + 8], fill=A(col, a))
                d.text((846, y0 + 92 + j * 52), nb(it), font=fi, fill=A(INK, a), anchor='lm')

def cta(fr, at):
    for a0 in SP.get('cta', []):
        if a0 <= at < a0 + 6.5:
            p = min(ob((at - a0) / 0.5), 1 - ease((at - a0 - 6.1) / 0.4)); d = ImageDraw.Draw(fr, 'RGBA')
            txt = "Faites corriger vos textes"; url = "formation-tcfcanada.com"; f = F(BD, 24); fu = F(XB, 24)
            w = f.getlength(txt) + fu.getlength(url) + 110; x1 = 1880; x0 = x1 - w + (1 - p) * 60; y = 1046 - 0
            d.rounded_rectangle([x0, 1048 - 26, x0 + w, 1048 + 26], radius=26, fill=A(ROYAL, p))
            d.text((x0 + 26, 1048), txt + "  →", font=f, fill=A(WHITE, p), anchor='lm')
            d.text((x0 + 26 + f.getlength(txt + "  →") + 12, 1048), url, font=fu, fill=A((255, 214, 80), p), anchor='lm')

def main_frame(at):
    fr = PLAIN.copy(); header(fr, at); fr = fr.convert('RGB'); s = step_at(at)
    left_panel(fr, at, s); main_stage(fr, at, s); cta(fr, at)
    return fr.convert('RGBA')

def intro_frame(t):
    T_OUT = INTRO - 0.7; fr = PLAIN.copy()
    if t < T_OUT + 0.05: logo_build(t, 960, 400, 0.5, fr)
    d = ImageDraw.Draw(fr, 'RGBA'); a = ease((t - 2.3) / 0.5) * (1 - ease((t - T_OUT + 0.1) / 0.3))
    if a > 0:
        dy = (1 - ease((t - 2.3) / 0.5)) * 30; tag = "EXERCICE CORRIGÉ"; f = F(BD, 28); tw = f.getlength(tag) + 60
        d.rounded_rectangle([W / 2 - tw / 2, 700 + dy, W / 2 + tw / 2, 756 + dy], radius=28, fill=A(FLAG, a))
        d.text((W / 2, 728 + dy), tag, font=f, fill=A(WHITE, a), anchor='mm')
        d.text((W / 2, 830 + dy), f"Expression écrite · Tâche {TASKN}", font=F(BL, 76), fill=A(INK, a), anchor='mm')
        d.text((W / 2, 915 + dy), f"{TASKL} · {SP['mini']} à {SP['maxi']} mots · TCF Canada", font=F(MD, 34), fill=A(SLATE, a), anchor='mm')
    if t >= T_OUT:
        p = ease((t - T_OUT) / 0.7); m0 = main_frame(0).convert('RGB')
        return Image.blend(fr.convert('RGB'), m0, p)
    return fr.convert('RGB')

def outro_frame(u):
    base = PLAIN.copy(); logo_build(u * 1.15, 500, 470, 0.46, base); fr = base.convert('RGB'); d = ImageDraw.Draw(fr, 'RGBA')
    a2 = ease((u - 0.5) / 0.5)
    d.text((960, 400), "Entraînez-vous à l'écrit", font=F(BL, 64), fill=A(INK, a2), anchor='lm')
    d.text((960, 480), "avec correction détaillée", font=F(BL, 64), fill=A(ROYAL, a2), anchor='lm')
    d.text((960, 550), "Sujets d'actualité · Simulateur d'expression écrite", font=F(MD, 28), fill=A(SLATE, a2), anchor='lm')
    a3 = ease((u - 0.9) / 0.5); txt = "formation-tcfcanada.com"; f = F(BD, 46); tw = f.getlength(txt)
    d.rounded_rectangle([960, 620, 960 + tw + 100, 730], radius=55, fill=A(ROYAL, a3)); d.text((960 + (tw + 100) / 2, 675), txt, font=f, fill=A(WHITE, a3), anchor='mm')
    a4 = ease((u - 1.3) / 0.5); d.rounded_rectangle([960, 770, 1380, 830], radius=30, fill=A(FLAG, a4)); d.text((1170, 800), "EXCLUSIF PACK AYOUB", font=F(BD, 30), fill=A(WHITE, a4), anchor='mm')
    if u > OUTRO - 0.6: d.rectangle([0, 0, W, H], fill=(0, 0, 0, int(255 * (u - OUTRO + 0.6) / 0.6)))
    return fr

def frame(t):
    if t < INTRO: return intro_frame(t)
    if t < INTRO + ADUR:
        fr = main_frame(t - INTRO).convert('RGB')
        if t > INTRO + ADUR - 0.5: fr = Image.blend(fr, Image.new('RGB', (W, H), (255, 255, 255)), (t - INTRO - ADUR + 0.5) / 0.5)
        return fr
    return outro_frame(t - INTRO - ADUR)

if ONLY is not None:
    for v in ONLY: frame(v).save(f"{OUTV}_{v}.png")
    sys.exit()
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                        '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', OUTV], stdin=subprocess.PIPE)
for i in range(int(round(TOTAL * FPS))): enc.stdin.write(frame(i / FPS).tobytes())
enc.stdin.close(); enc.wait()
print('total', round(TOTAL, 2), 'adur', round(ADUR, 2))

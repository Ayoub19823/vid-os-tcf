import sys, os, math, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
from script import LINES, CHRONO_START, CHRONO_STOP

AUD = sys.argv[1]; OUTV = sys.argv[2]
ONLY = [float(v) for v in sys.argv[3].split(',')] if len(sys.argv) > 3 else None
W, H, FPS = 1080, 1920, 25
INTRO, BILAN, OUTRO = 3.0, 14.0, 5.0
wv = wave.open(AUD); sr = wv.getframerate(); x = np.frombuffer(wv.readframes(wv.getnframes()), '<i2').astype(np.float32) / 32768
ADUR = len(x) / sr
TOTAL = INTRO + ADUR + BILAN + OUTRO
hop = sr // FPS
env = np.array([np.sqrt(np.mean(x[i:i + hop] ** 2)) for i in range(0, len(x), hop)]); env /= (np.percentile(env, 98) + 1e-6)


def bars(at, n=13):
    i = int(at * sr); seg = x[max(0, i - 1200):i + 1200]
    if len(seg) < 256: return np.zeros(n)
    sp = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))[:len(seg) // 6]
    v = np.array([c.mean() for c in np.array_split(sp, n)]); v = np.sqrt(v / (sp.mean() * 3 + 1e-6))
    return np.clip(np.concatenate([v[::2][::-1], v[1::2]])[:n], 0, 1.2)


BG0 = (9, 16, 40); BG1 = (18, 30, 70)
WHITE = (255, 255, 255); MUTE = (160, 172, 210); YEL = (255, 200, 60); RED = (239, 68, 68); ORANGE = (255, 150, 40)
CC = (167, 112, 255); HC = (56, 160, 255); GREEN = (34, 197, 94); BRAND = (26, 92, 255)
BL = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
XB = "/usr/share/fonts/opentype/inter/InterDisplay-ExtraBold.otf"
SB = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
MD = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
BD = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
IT = "/usr/share/fonts/opentype/inter/Inter-MediumItalic.otf"
EF = ImageFont.truetype('/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf', 109)
_fc = {}
def F(p, s):
    k = (p, int(s))
    if k not in _fc: _fc[k] = ImageFont.truetype(p, int(s))
    return _fc[k]
def clamp(v, a=0.0, b=1.0): return max(a, min(b, v))
def ease(v): v = clamp(v); return v * v * (3 - 2 * v)
def ob(v):
    v = clamp(v); c = 1.6; return 1 + (c + 1) * (v - 1) ** 3 + c * (v - 1) ** 2
def A(c, a): return tuple(c[:3]) + (int(255 * clamp(a)),)
def emoji(e, s):
    im = Image.new('RGBA', (140, 140)); ImageDraw.Draw(im).text((70, 70), e, font=EF, embedded_color=True, anchor='mm')
    im = im.crop(im.getbbox()); k = s / max(im.size); return im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)

LOGO = Image.open(f'{D}/logo.png').convert('RGBA')
def logo(h):
    return LOGO.resize((int(LOGO.width * h / LOGO.height), h), Image.LANCZOS)

# ------------------------------------------------ pedagogy data (audio seconds)
QUESTIONS = [35.75, 49.25, 61.89, 77.70, 94.28, 112.71, 129.22, 143.27, 157.57]
THEMES = [("Activités", 35.75), ("Âge", 49.25), ("Lecture", 61.89), ("Type de cadeau", 77.70),
          ("Cuisine", 94.28), ("Besoins", 129.22), ("Jeux vidéo", 143.27), ("Travail", 157.57)]
FEED = [  # time, kind ok|fix|note, line1, line2
    (38.6, 'ok', "Bonne question", "Claire et naturelle pour lancer l'échange"),
    (50.6, 'ok', "Question simple et efficace", "« Quel âge a ta sœur ? »"),
    (61.3, 'ok', "Bonne reformulation", "Il reprend la réponse : « Elle va fêter ses trente ans, d'accord »"),
    (65.6, 'ok', "Question à choix", "« des romans ou des comédies ? » : bonne stratégie"),
    (85.9, 'fix', "« les cadeaux… ou les cadeaux utiles ? »", "Elle préfère les cadeaux utiles ou décoratifs ?"),
    (96.0, 'fix', "« est-ce qu'elle est une cuisinière ? »", "Est-ce qu'elle aime cuisiner ?"),
    (112.3, 'note', "Tutoiement → vouvoiement", "Gardez le même registre : « Qu'est-ce que tu me conseilles ? »"),
    (132.9, 'fix', "« des choses qu'elle a besoin »", "des choses dont elle a besoin"),
    (145.9, 'fix', "« jouer des jeux vidéo »", "jouer aux jeux vidéo"),
    (161.8, 'fix', "« Étudie-t-elle dans le collège, ou elle travaille »", "Est-ce qu'elle étudie ou est-ce qu'elle travaille ?"),
    (176.2, 'ok', "Bonne synthèse", "Il propose une idée de cadeau concrète"),
    (201.6, 'fix', "« lui donner un livre »", "lui offrir un livre"),
]
CTA_WINDOWS = [(100.0, 108.0), (184.0, 191.0)]
REG_SWITCH = 109.83

# ------------------------------------------------ static background
g = np.linspace(0, 1, H)[:, None, None]
arr = (np.array(BG0)[None, None] * (1 - g) + np.array(BG1)[None, None] * g).astype(np.uint8)
bgA = Image.fromarray(np.repeat(arr, W, axis=1)).convert('RGBA')
glow = Image.new('RGBA', (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
gd.ellipse([-300, 200, 600, 1000], fill=(90, 60, 220, 60)); gd.ellipse([600, 1000, 1500, 1900], fill=(30, 120, 255, 50))
bgA.alpha_composite(glow.filter(ImageFilter.GaussianBlur(160)))
bg = bgA.convert('RGB'); d = ImageDraw.Draw(bg, 'RGBA')
for yy in range(0, H, 60): d.line([0, yy, W, yy], fill=(255, 255, 255, 6))
for xx in range(0, W, 60): d.line([xx, 0, xx, H], fill=(255, 255, 255, 6))
# header with logo
d.rounded_rectangle([50, 46, 290, 146], radius=24, fill=(255, 255, 255))
lg = logo(84); bg.paste(lg, (int(170 - lg.width / 2), 54), lg)
d.text((320, 82), "Expression orale · Tâche 2", font=F(BL, 44), fill=WHITE, anchor='lm')
d.text((320, 124), "Simulation d'examen — Interaction", font=F(MD, 28), fill=MUTE, anchor='lm')
# stat cards frames
for x0 in (50, 760):
    d.rounded_rectangle([x0, 250, x0 + 270, 470], radius=28, fill=(255, 255, 255, 14), outline=(255, 255, 255, 30), width=2)
d.text((185, 290), "QUESTIONS", font=F(BD, 22), fill=MUTE, anchor='mm')
d.text((895, 290), "REGISTRE", font=F(BD, 22), fill=MUTE, anchor='mm')
# consigne + themes card
CY0, CY1 = 512, 852
d.rounded_rectangle([50, CY0, W - 50, CY1], radius=30, fill=(255, 255, 255, 14), outline=(255, 255, 255, 30), width=2)
d.text((90, CY0 + 44), "CONSIGNE", font=F(BD, 22), fill=YEL, anchor='lm')
cons = ["« Je vous invite à l'anniversaire de ma sœur. Posez-moi",
        "des questions sur elle pour savoir quel cadeau lui offrir. »"]
for i, l in enumerate(cons): d.text((90, CY0 + 90 + i * 42), l, font=F(SB, 30), fill=(225, 230, 245), anchor='lm')
d.text((90, CY0 + 186), "THÈMES ABORDÉS", font=F(BD, 22), fill=YEL, anchor='lm')
# footer
d.text((W / 2, 1880), "formation-tcfcanada.com  ·  Simulateur d'expression orale", font=F(MD, 26), fill=(130, 145, 190), anchor='mm')
BG = bg

# theme chip layout
CHIPS = []
cx, cy = 90, CY0 + 232
for name, ts in THEMES:
    w = F(SB, 25).getlength(name) + 40
    if cx + w > W - 90: cx = 90; cy += 52
    CHIPS.append((name, ts, cx, cy, w)); cx += w + 12

# tiles
TY0, TY1 = 876, 1214
TILES = {'C': (50, 'Catherine', 'Examinatrice certifiée', CC, 'C', '🎧'), 'H': (560, 'Harsh', 'Candidat', HC, 'H', '🎓')}
TW = 470
EMO = {k: emoji(v[5], 40) for k, v in TILES.items()}


def speaker_at(at):
    for s, a, b, txt in LINES:
        if a - 0.05 <= at <= b + 0.15: return s
    return None


def last_line(at):
    best = None
    for L in LINES:
        if L[1] - 0.05 <= at: best = L
    return best


def draw_tiles(fr, at):
    d = ImageDraw.Draw(fr, 'RGBA')
    sp = speaker_at(at); lvl = env[min(len(env) - 1, int(at * FPS))]
    for k, (tx, name, role, col, ini, _) in TILES.items():
        act = (k == sp)
        d.rounded_rectangle([tx, TY0, tx + TW, TY1], radius=32, fill=(255, 255, 255, 22 if act else 12), outline=A(col, 1 if act else 0.25), width=5 if act else 2)
        if act:
            gl = 10 + 8 * lvl
            d.rounded_rectangle([tx - gl / 2, TY0 - gl / 2, tx + TW + gl / 2, TY1 + gl / 2], radius=36, outline=A(col, 0.25), width=int(gl))
        ccx, ccy, r = tx + TW / 2, TY0 + 112, 78
        if act:
            rr = r + 12 + 22 * min(1.0, lvl); d.ellipse([ccx - rr, ccy - rr, ccx + rr, ccy + rr], fill=A(col, 0.18))
        d.ellipse([ccx - r, ccy - r, ccx + r, ccy + r], fill=col)
        d.ellipse([ccx - r + 7, ccy - r + 7, ccx + r - 7, ccy + r - 7], fill=tuple(int(c * 0.78) for c in col))
        d.text((ccx, ccy + 4), ini, font=F(BL, 82), fill=WHITE, anchor='mm')
        e = EMO[k]; fr.paste(e, (int(ccx + r * 0.62 - e.width / 2), int(ccy + r * 0.62 - e.height / 2)), e)
        d.text((ccx, TY0 + 222), name, font=F(XB, 40), fill=WHITE, anchor='mm')
        if k == 'C':
            f = F(BD, 22); tw = f.getlength("✓ EXAMINATRICE CERTIFIÉE") if False else f.getlength("EXAMINATRICE CERTIFIÉE")
            d.rounded_rectangle([ccx - tw / 2 - 40, TY0 + 248, ccx + tw / 2 + 18, TY0 + 284], radius=18, fill=YEL)
            d.ellipse([ccx - tw / 2 - 32, TY0 + 255, ccx - tw / 2 - 10, TY0 + 277], fill=(20, 30, 60))
            d.line([ccx - tw / 2 - 27, TY0 + 266, ccx - tw / 2 - 22, TY0 + 271, ccx - tw / 2 - 14, TY0 + 260], fill=YEL, width=3)
            d.text((ccx + 7, TY0 + 266), "EXAMINATRICE CERTIFIÉE", font=f, fill=(20, 30, 60), anchor='mm')
        else:
            d.text((ccx, TY0 + 266), role, font=F(MD, 26), fill=MUTE, anchor='mm')
        if act:
            b = bars(at); n = len(b); bw, gp = 9, 7; tot = n * bw + (n - 1) * gp; x0 = ccx - tot / 2
            for i, v in enumerate(b):
                hh = 6 + 28 * min(1.0, v * (0.4 + lvl))
                d.rounded_rectangle([x0 + i * (bw + gp), TY0 + 312 - hh / 2, x0 + i * (bw + gp) + bw, TY0 + 312 + hh / 2], radius=4, fill=col)


def draw_chrono(fr, at, t):
    d = ImageDraw.Draw(fr, 'RGBA')
    cx, cy, R = W / 2, 360, 130
    rem = 210.0 if at < CHRONO_START else max(0.0, 210 - (min(at, CHRONO_STOP) - CHRONO_START))
    done = at >= CHRONO_STOP
    col = GREEN if done else (RED if rem <= 20 else ORANGE if rem <= 60 else YEL)
    d.ellipse([cx - R - 26, cy - R - 26, cx + R + 26, cy + R + 26], fill=(255, 255, 255, 10))
    d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=(255, 255, 255, 30), width=16)
    if done:
        d.arc([cx - R, cy - R, cx + R, cy + R], 0, 360, fill=GREEN, width=16)
        d.text((cx, cy - 14), "TERMINÉ", font=F(BL, 50), fill=GREEN, anchor='mm')
        d.text((cx, cy + 40), "Épreuve finie", font=F(MD, 26), fill=MUTE, anchor='mm')
    else:
        frac = rem / 210
        d.arc([cx - R, cy - R, cx + R, cy + R], -90, -90 + 360 * frac, fill=col, width=16)
        ang = math.radians(-90 + 360 * frac)
        d.ellipse([cx + R * math.cos(ang) - 13, cy + R * math.sin(ang) - 13, cx + R * math.cos(ang) + 13, cy + R * math.sin(ang) + 13], fill=WHITE)
        sec = int(math.ceil(rem - 1e-9)); m, s = sec // 60, sec % 60
        pulse = 1.0 + (0.06 * (1 - (at % 1)) if rem <= 20 and at >= CHRONO_START else 0)
        d.text((cx, cy - 8), f"{m}:{s:02d}", font=F(BL, int(96 * pulse)), fill=WHITE if rem > 20 else RED, anchor='mm')
        d.text((cx, cy + 64), "TEMPS RESTANT" if at >= CHRONO_START else "PRÊT", font=F(BD, 20), fill=MUTE, anchor='mm')
    # REC
    blink = (int(t * 2) % 2 == 0)
    d.rounded_rectangle([W - 230, 1820 - 1820 + 180, W - 50, 230], radius=25, fill=(255, 255, 255, 18), outline=(255, 255, 255, 40), width=2)
    d.ellipse([W - 210, 194, W - 188, 216], fill=RED if blink else (120, 40, 40))
    d.text((W - 176, 205), "ENREG.", font=F(BD, 24), fill=WHITE, anchor='lm')


def draw_stats(fr, at):
    d = ImageDraw.Draw(fr, 'RGBA')
    nq = sum(1 for q in QUESTIONS if at >= q)
    last = max([q for q in QUESTIONS if at >= q], default=-9)
    s = 1 + 0.25 * (1 - ease((at - last) / 0.4))
    d.text((185, 372), str(nq), font=F(BL, int(96 * s)), fill=HC if nq else (100, 115, 160), anchor='mm')
    d.text((185, 440), "posées par Harsh", font=F(MD, 20), fill=MUTE, anchor='mm')
    if at < 20.7:
        d.text((895, 372), "—", font=F(BL, 70), fill=(100, 115, 160), anchor='mm')
    elif at < REG_SWITCH:
        d.text((895, 372), "« tu »", font=F(BL, 64), fill=GREEN, anchor='mm')
        d.text((895, 440), "tutoiement", font=F(MD, 20), fill=MUTE, anchor='mm')
    else:
        p = ease((at - REG_SWITCH) / 0.4)
        d.text((895, 366), "tu / vous", font=F(BL, 48), fill=A(ORANGE, 0.4 + 0.6 * p), anchor='mm')
        d.text((895, 432), "registre mélangé", font=F(MD, 20), fill=ORANGE, anchor='mm')


def draw_themes(fr, at):
    d = ImageDraw.Draw(fr, 'RGBA')
    for name, ts, x0, y0, w in CHIPS:
        on = at >= ts
        p = ease((at - ts) / 0.35) if on else 0
        fill = A(HC, 0.25 + 0.6 * p) if on else (255, 255, 255, 12)
        d.rounded_rectangle([x0, y0 - 22, x0 + w, y0 + 22], radius=22, fill=fill, outline=A(HC, 0.9) if on else (255, 255, 255, 40), width=2)
        d.text((x0 + w / 2, y0), name, font=F(SB, 25), fill=WHITE if on else (130, 145, 190), anchor='mm')
        if on and at - ts < 0.6:
            gr = 6 * (1 - (at - ts) / 0.6)
            d.rounded_rectangle([x0 - gr, y0 - 22 - gr, x0 + w + gr, y0 + 22 + gr], radius=26, outline=A(HC, 0.6), width=3)
    if at < 10.8:
        g2 = 0.5 + 0.5 * math.sin(at * 4)
        d.rounded_rectangle([50, CY0, W - 50, CY1], radius=30, outline=A(YEL, 0.5 + 0.4 * g2), width=4)


FY0, FY1 = 1238, 1402


def draw_feedback(fr, at):
    cur = None
    for i, (ts, kind, l1, l2) in enumerate(FEED):
        nxt = FEED[i + 1][0] if i + 1 < len(FEED) else 999
        end = min(ts + 7.0, nxt - 0.2)
        if ts <= at < end: cur = (ts, end, kind, l1, l2)
    if not cur: return
    ts, end, kind, l1, l2 = cur
    a = ease((at - ts) / 0.3) * (1 - ease((at - end + 0.35) / 0.35))
    dy = (1 - ob((at - ts) / 0.4)) * 30
    d = ImageDraw.Draw(fr, 'RGBA')
    col = {'ok': GREEN, 'fix': ORANGE, 'note': YEL}[kind]
    d.rounded_rectangle([50, FY0 + dy, W - 50, FY1 + dy], radius=28, fill=(10, 18, 44, int(235 * a)), outline=A(col, a), width=3)
    d.ellipse([78, FY0 + 34 + dy, 138, FY0 + 94 + dy], fill=A(col, a))
    if kind == 'ok':
        d.line([92, FY0 + 64 + dy, 104, FY0 + 77 + dy, 125, FY0 + 50 + dy], fill=A(WHITE, a), width=7, joint='curve')
    else:
        d.text((108, FY0 + 64 + dy), "!" if kind == "note" else "→", font=F(BL, 36), fill=A((20, 30, 60), a), anchor='mm')
    if kind == 'ok':
        d.text((162, FY0 + 50 + dy), l1, font=F(XB, 36), fill=A(GREEN, a), anchor='lm')
        d.text((162, FY0 + 104 + dy), l2, font=F(MD, 27), fill=A((215, 222, 240), a), anchor='lm')
    elif kind == 'fix':
        d.text((162, FY0 + 50 + dy), "Dit : " + l1, font=F(IT, 28), fill=A((190, 198, 225), a), anchor='lm')
        d.text((162, FY0 + 104 + dy), "Mieux : " + l2, font=F(XB, 32), fill=A(ORANGE, a), anchor='lm')
    else:
        d.text((162, FY0 + 50 + dy), l1, font=F(XB, 34), fill=A(YEL, a), anchor='lm')
        d.text((162, FY0 + 104 + dy), l2, font=F(MD, 27), fill=A((215, 222, 240), a), anchor='lm')


def wrap(d, words, font, maxw):
    lines, cur, wc = [], [], 0; sp = font.getlength(' ')
    for wd in words:
        wl = font.getlength(wd)
        if cur and wc + sp + wl > maxw: lines.append(cur); cur, wc = [wd], wl
        else: cur.append(wd); wc += (sp if len(cur) > 1 else 0) + wl
    if cur: lines.append(cur)
    return lines


def draw_subs(fr, at):
    L = last_line(at)
    if L is None: return
    s, a, b, txt = L
    if at > b + 1.6: return
    d = ImageDraw.Draw(fr, 'RGBA')
    col = CC if s == 'C' else HC
    name = "Catherine · examinatrice" if s == 'C' else "Harsh · candidat"
    fa = ease((at - a + 0.05) / 0.25) * (1 - ease((at - b - 1.2) / 0.4))
    Y0 = 1428
    d.rounded_rectangle([50, Y0, W - 50, 1830], radius=30, fill=(0, 0, 0, int(90 * fa)))
    f = F(SB, 44); words = txt.split(' ')
    lines = wrap(d, words, f, W - 180)
    if len(lines) > 4: f = F(SB, 38); lines = wrap(d, words, f, W - 180)
    nw = len(words); prog = clamp((at - a) / max(0.3, b - a)) * nw
    pw = F(BD, 26).getlength(name) + 44
    d.rounded_rectangle([90, Y0 + 30, 90 + pw, Y0 + 78], radius=24, fill=A(col, fa))
    d.text((90 + pw / 2, Y0 + 54), name, font=F(BD, 26), fill=A(WHITE, fa), anchor='mm')
    idx = 0
    for li, ln in enumerate(lines):
        x0 = 90; y = Y0 + 122 + li * (f.size + 14)
        for wd in ln:
            d.text((x0, y), wd, font=f, fill=A(WHITE, fa * (1 if idx < prog + 0.5 else 0.32)), anchor='lm')
            x0 += f.getlength(wd + ' '); idx += 1


def draw_cta(fr, at):
    for a0, a1 in CTA_WINDOWS:
        if a0 <= at < a1:
            p = min(ob((at - a0) / 0.5), 1 - ease((at - a1 + 0.4) / 0.4))
            d = ImageDraw.Draw(fr, 'RGBA')
            txt = "Passez votre propre simulation sur formation-tcfcanada.com"
            f = F(BD, 28); tw = f.getlength(txt); w = tw + 120
            x0 = W / 2 - w / 2; y = 1850 + (1 - p) * 80
            d.rounded_rectangle([x0, y - 4, x0 + w, y + 58], radius=31, fill=A(BRAND, p))
            d.polygon([(x0 + 34, y + 12), (x0 + 34, y + 42), (x0 + 58, y + 27)], fill=A(WHITE, p))
            d.text((x0 + 76, y + 27), txt, font=f, fill=A(WHITE, p), anchor='lm')
            return True
    return False


def intro_frame(t):
    fr = BG.copy(); d = ImageDraw.Draw(fr, 'RGBA')
    d.rectangle([0, 0, W, H], fill=(9, 16, 40, int(240 * (1 - ease((t - INTRO + 0.4) / 0.4)))))
    a = ease(t / 0.5) * (1 - ease((t - INTRO + 0.4) / 0.4))
    s = ob(t / 0.6)
    if s > 0.05:
        card = Image.new('RGBA', (520, 420), (0, 0, 0, 0)); cd = ImageDraw.Draw(card)
        cd.rounded_rectangle([0, 0, 519, 419], radius=44, fill=(255, 255, 255))
        lg = logo(330); card.paste(lg, (int(260 - lg.width / 2), 45), lg)
        card = card.resize((int(520 * s * 0.9), int(420 * s * 0.9)), Image.BICUBIC)
        card.putalpha(card.getchannel('A').point(lambda v: int(v * a)))
        fr.paste(card, (int(W / 2 - card.width / 2), int(560 - card.height / 2)), card)
    d.rounded_rectangle([W / 2 - 230, 840, W / 2 + 230, 900], radius=30, fill=A(RED, a))
    d.text((W / 2, 870), "SIMULATION RÉELLE", font=F(BD, 30), fill=A(WHITE, a), anchor='mm')
    d.text((W / 2, 990), "Expression orale · Tâche 2", font=F(BL, 64), fill=A(WHITE, a), anchor='mm')
    d.text((W / 2, 1070), "Catherine (examinatrice)  ×  Harsh (candidat)", font=F(MD, 36), fill=A(MUTE, a), anchor='mm')
    return fr


def bilan_frame(u):
    fr = BG.copy(); d = ImageDraw.Draw(fr, 'RGBA'); d.rectangle([0, 0, W, H], fill=(9, 16, 40, 250))
    a = ease(u / 0.5)
    lg = logo(70); d.rounded_rectangle([W / 2 - 115, 80, W / 2 + 115, 170], radius=22, fill=A(WHITE, a)); fr.paste(lg, (int(W / 2 - lg.width / 2), 90), lg)
    d.text((W / 2, 230), "BILAN DE LA SIMULATION", font=F(BD, 28), fill=A(YEL, a), anchor='mm')
    d.text((W / 2, 290), "Harsh · Tâche 2", font=F(BL, 60), fill=A(WHITE, a), anchor='mm')
    # stats row
    stats = [("9", "questions"), ("8", "thèmes"), ("3:20", "d'échange")]
    for i, (v, l) in enumerate(stats):
        ai = ease((u - 0.3 - i * 0.12) / 0.4); cx = 220 + i * 320
        d.rounded_rectangle([cx - 140, 350, cx + 140, 500], radius=26, fill=(255, 255, 255, int(16 * ai)), outline=(255, 255, 255, int(40 * ai)), width=2)
        d.text((cx, 410), v, font=F(BL, 64), fill=A(HC, ai), anchor='mm'); d.text((cx, 470), l, font=F(MD, 26), fill=A(MUTE, ai), anchor='mm')
    blocks = [
        (GREEN, "POINTS FORTS", ["Des questions variées sur 8 thèmes", "Il reformule les réponses de l'examinatrice", "Il conclut avec une idée de cadeau"], 1.0),
        (ORANGE, "À AMÉLIORER", ["Garder un seul registre : tu ou vous", "« dont elle a besoin », « jouer aux jeux vidéo »", "Des questions plus courtes et directes"], 3.0),
        (HC, "QUESTIONS MODÈLES", ["Qu'est-ce qu'elle fait pendant son temps libre ?", "Est-ce qu'elle a un style qu'elle préfère ?", "Quel est le plus beau cadeau qu'elle ait reçu ?"], 5.0),
    ]
    y = 560
    for col, title, items, t0 in blocks:
        ab = ease((u - t0) / 0.5)
        if ab > 0:
            d.rounded_rectangle([60, y, W - 60, y + 360], radius=30, fill=(255, 255, 255, int(12 * ab)), outline=A(col, 0.6 * ab), width=2)
            d.text((100, y + 50), title, font=F(BD, 28), fill=A(col, ab), anchor='lm')
            for j, it in enumerate(items):
                aj = ease((u - t0 - 0.3 - j * 0.25) / 0.4)
                yy = y + 130 + j * 82
                d.ellipse([100, yy - 14, 128, yy + 14], fill=A(col, aj))
                d.text((150, yy), it, font=F(SB, 32), fill=A(WHITE, aj), anchor='lm')
        y += 390
    if u > BILAN - 0.5: d.rectangle([0, 0, W, H], fill=(9, 16, 40, int(255 * (u - BILAN + 0.5) / 0.5)))
    d.text((W / 2, 1880), "Bilan pédagogique · formation-tcfcanada.com", font=F(MD, 24), fill=A((130, 145, 190), a), anchor='mm')
    return fr


def outro_frame(u):
    fr = BG.copy(); d = ImageDraw.Draw(fr, 'RGBA'); d.rectangle([0, 0, W, H], fill=(9, 16, 40, 245))
    s = ob(u / 0.6)
    if s > 0.05:
        card = Image.new('RGBA', (560, 450), (0, 0, 0, 0)); cd = ImageDraw.Draw(card)
        cd.rounded_rectangle([0, 0, 559, 449], radius=46, fill=(255, 255, 255))
        lg = logo(360); card.paste(lg, (int(280 - lg.width / 2), 45), lg)
        card = card.resize((int(560 * s * 0.85), int(450 * s * 0.85)), Image.BICUBIC)
        fr.paste(card, (int(W / 2 - card.width / 2), int(560 - card.height / 2)), card)
    a2 = ease((u - 0.5) / 0.5)
    d.text((W / 2, 850), "Entraînez-vous dans les conditions réelles", font=F(BL, 48), fill=A(WHITE, a2), anchor='mm')
    d.text((W / 2, 920), "Simulateur oral interactif · Examens blancs avec examinateur", font=F(MD, 30), fill=A(MUTE, a2), anchor='mm')
    a3 = ease((u - 0.9) / 0.5)
    txt = "formation-tcfcanada.com"; f = F(BD, 50); tw = f.getlength(txt)
    pul = 1 + 0.03 * math.sin(max(0, u - 1.4) * 7)
    d.rounded_rectangle([W / 2 - tw / 2 - 60, 1010, W / 2 + tw / 2 + 60, 1130], radius=60, fill=A(BRAND, a3))
    d.text((W / 2, 1070), txt, font=F(BD, int(50 * pul)), fill=A(WHITE, a3), anchor='mm')
    a4 = ease((u - 1.3) / 0.5)
    d.rounded_rectangle([W / 2 - 220, 1180, W / 2 + 220, 1240], radius=30, fill=A(YEL, a4))
    d.text((W / 2, 1210), "EXCLUSIF PACK AYOUB", font=F(BD, 30), fill=A((20, 30, 60), a4), anchor='mm')
    if u > OUTRO - 0.6: d.rectangle([0, 0, W, H], fill=(0, 0, 0, int(255 * (u - OUTRO + 0.6) / 0.6)))
    return fr


n = int(round(TOTAL * FPS))
frames = range(n) if ONLY is None else [int(round(v * FPS)) for v in ONLY]
enc = None
if ONLY is None:
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', OUTV], stdin=subprocess.PIPE)
for fi in frames:
    t = fi / FPS
    if t < INTRO: fr = intro_frame(t)
    elif t < INTRO + ADUR:
        at = t - INTRO
        fr = BG.copy()
        draw_chrono(fr, at, t); draw_stats(fr, at); draw_themes(fr, at)
        draw_tiles(fr, at); draw_feedback(fr, at); draw_subs(fr, at); draw_cta(fr, at)
    elif t < INTRO + ADUR + BILAN: fr = bilan_frame(t - INTRO - ADUR)
    else: fr = outro_frame(t - INTRO - ADUR - BILAN)
    if enc: enc.stdin.write(fr.tobytes())
    else: fr.save(f'{OUTV}_{t:.1f}.png')
if enc: enc.stdin.close(); enc.wait()
print('total', round(TOTAL, 2), 'intro', INTRO, 'adur', round(ADUR, 2))

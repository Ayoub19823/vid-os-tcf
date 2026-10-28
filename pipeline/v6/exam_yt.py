import sys, os, math, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
from script import LINES, CHRONO_START, CHRONO_STOP

AUD = sys.argv[1]; OUTV = sys.argv[2]
ONLY = [float(v) for v in sys.argv[3].split(',')] if len(sys.argv) > 3 else None
W, H, FPS = 1920, 1080, 25
INTRO, BILAN, OUTRO = 4.0, 14.0, 5.5
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


# ================= YouTube 16:9 layout, logo palette =================
ROYAL = (24, 56, 255); ROYAL2 = (76, 103, 254); MID = (43, 95, 186); NAVY = (30, 34, 110); SKY = (38, 169, 255); FLAG = (229, 30, 32)
CC = FLAG; HC = SKY; YEL = (255, 205, 70)
# background: diagonal navy -> royal -> sky glow
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
tdiag = np.clip((xx / W) * 0.65 + (yy / H) * 0.35, 0, 1)[..., None]
c0 = np.array((14, 18, 70), np.float32); c1 = np.array((22, 44, 170), np.float32); c2 = np.array((30, 110, 230), np.float32)
arr = np.where(tdiag < 0.6, c0 + (c1 - c0) * (tdiag / 0.6), c1 + (c2 - c1) * ((tdiag - 0.6) / 0.4)).astype(np.uint8)
bgA = Image.fromarray(arr).convert('RGBA')
glow = Image.new('RGBA', (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
gd.ellipse([1300, 500, 2300, 1400], fill=SKY + (90,)); gd.ellipse([-300, -300, 500, 400], fill=ROYAL2 + (70,))
bgA.alpha_composite(glow.filter(ImageFilter.GaussianBlur(180)))
bg = bgA.convert('RGB'); d = ImageDraw.Draw(bg, 'RGBA')
for k in range(-H, W, 46): d.line([k, 0, k + H, H], fill=(255, 255, 255, 5))
CARD = (255, 255, 255, 16); EDGE = (255, 255, 255, 40)
# header
from logoanim import build as logo_build, static_logo
BG_NOLOGO = bg.copy()
_hl = static_logo(104); bg.paste(_hl, (int(160 - _hl.width / 2), int(82 - _hl.height / 2)), _hl)
d.text((320, 64), "Expression orale · Tâche 2", font=F(BL, 46), fill=WHITE, anchor='lm')
d.text((320, 108), "Simulation d'examen — Interaction · TCF Canada", font=F(MD, 26), fill=(190, 205, 245), anchor='lm')
# left column cards
d.rounded_rectangle([40, 160, 690, 560], radius=34, fill=CARD, outline=EDGE, width=2)   # chrono card
d.rounded_rectangle([40, 580, 355, 740], radius=28, fill=CARD, outline=EDGE, width=2)   # questions
d.rounded_rectangle([375, 580, 690, 740], radius=28, fill=CARD, outline=EDGE, width=2)  # registre
d.text((197, 612), "QUESTIONS", font=F(BD, 20), fill=(190, 205, 245), anchor='mm')
d.text((532, 612), "REGISTRE", font=F(BD, 20), fill=(190, 205, 245), anchor='mm')
CY0, CY1 = 760, 1050
d.rounded_rectangle([40, CY0, 690, CY1], radius=30, fill=CARD, outline=EDGE, width=2)
d.text((72, CY0 + 38), "CONSIGNE", font=F(BD, 20), fill=YEL, anchor='lm')
cons = ["« Je vous invite à l'anniversaire de ma sœur.",
        "Posez-moi des questions sur elle pour savoir", "quel cadeau lui offrir (activités, personnalité…). »"]
for i, l in enumerate(cons): d.text((72, CY0 + 76 + i * 33), l, font=F(SB, 25), fill=(230, 236, 250), anchor='lm')
d.text((72, CY0 + 182), "THÈMES ABORDÉS", font=F(BD, 20), fill=YEL, anchor='lm')
BG = bg
CHIPS = []
cx, cy = 72, CY0 + 222
for name, ts in THEMES:
    w = F(SB, 22).getlength(name) + 34
    if cx + w > 660: cx = 72; cy += 42
    CHIPS.append((name, ts, cx, cy, w)); cx += w + 9

# right column geometry
TY0, TY1 = 160, 500
TILES = {'C': (720, 'Catherine', 'Examinatrice certifiée', CC, 'C', '🎧'), 'H': (1310, 'Harsh', 'Candidat', HC, 'H', '🎓')}
TW = 570
EMO = {k: emoji(v[5], 42) for k, v in TILES.items()}
FY0, FY1 = 520, 660
SY0, SY1 = 680, 1050


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
        d.rounded_rectangle([tx, TY0, tx + TW, TY1], radius=32, fill=(255, 255, 255, 26 if act else 14), outline=A(col, 1 if act else 0.3), width=5 if act else 2)
        if act:
            gl = 10 + 8 * lvl
            d.rounded_rectangle([tx - gl / 2, TY0 - gl / 2, tx + TW + gl / 2, TY1 + gl / 2], radius=36, outline=A(col, 0.3), width=int(gl))
        ccx, ccy, r = tx + TW / 2, TY0 + 118, 82
        if act:
            rr = r + 12 + 24 * min(1.0, lvl); d.ellipse([ccx - rr, ccy - rr, ccx + rr, ccy + rr], fill=A(col, 0.2))
        d.ellipse([ccx - r - 6, ccy - r - 6, ccx + r + 6, ccy + r + 6], fill=WHITE)
        d.ellipse([ccx - r, ccy - r, ccx + r, ccy + r], fill=col)
        d.text((ccx, ccy + 4), ini, font=F(BL, 86), fill=WHITE, anchor='mm')
        e = EMO[k]; fr.paste(e, (int(ccx + r * 0.66 - e.width / 2), int(ccy + r * 0.66 - e.height / 2)), e)
        d.text((ccx, TY0 + 236), name, font=F(XB, 42), fill=WHITE, anchor='mm')
        if k == 'C':
            f = F(BD, 22); tw = f.getlength("EXAMINATRICE CERTIFIÉE")
            d.rounded_rectangle([ccx - tw / 2 - 40, TY0 + 262, ccx + tw / 2 + 18, TY0 + 298], radius=18, fill=WHITE)
            d.ellipse([ccx - tw / 2 - 32, TY0 + 269, ccx - tw / 2 - 10, TY0 + 291], fill=FLAG)
            d.line([ccx - tw / 2 - 27, TY0 + 280, ccx - tw / 2 - 22, TY0 + 285, ccx - tw / 2 - 14, TY0 + 274], fill=WHITE, width=3)
            d.text((ccx + 7, TY0 + 280), "EXAMINATRICE CERTIFIÉE", font=f, fill=NAVY, anchor='mm')
        else:
            d.text((ccx, TY0 + 280), role, font=F(MD, 26), fill=(190, 205, 245), anchor='mm')
        if act:
            b = bars(at); n = len(b); bw, gp = 9, 7; tot = n * bw + (n - 1) * gp; x0 = ccx - tot / 2
            for i, v in enumerate(b):
                hh = 6 + 26 * min(1.0, v * (0.4 + lvl))
                d.rounded_rectangle([x0 + i * (bw + gp), TY0 + 320 - hh / 2, x0 + i * (bw + gp) + bw, TY0 + 320 + hh / 2], radius=4, fill=WHITE)


def draw_chrono(fr, at, t):
    d = ImageDraw.Draw(fr, 'RGBA')
    cx, cy, R = 365, 360, 150
    rem = 210.0 if at < CHRONO_START else max(0.0, 210 - (min(at, CHRONO_STOP) - CHRONO_START))
    done = at >= CHRONO_STOP
    col = GREEN if done else (FLAG if rem <= 20 else ORANGE if rem <= 60 else SKY)
    d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=(255, 255, 255, 40), width=18)
    if done:
        d.arc([cx - R, cy - R, cx + R, cy + R], 0, 360, fill=GREEN, width=18)
        d.text((cx, cy - 16), "TERMINÉ", font=F(BL, 58), fill=GREEN, anchor='mm')
        d.text((cx, cy + 46), "Épreuve finie", font=F(MD, 26), fill=(190, 205, 245), anchor='mm')
    else:
        frac = rem / 210
        d.arc([cx - R, cy - R, cx + R, cy + R], -90, -90 + 360 * frac, fill=col, width=18)
        ang = math.radians(-90 + 360 * frac)
        d.ellipse([cx + R * math.cos(ang) - 14, cy + R * math.sin(ang) - 14, cx + R * math.cos(ang) + 14, cy + R * math.sin(ang) + 14], fill=WHITE)
        sec = int(math.ceil(rem - 1e-9)); m, s = sec // 60, sec % 60
        pulse = 1.0 + (0.06 * (1 - (at % 1)) if rem <= 20 and at >= CHRONO_START else 0)
        d.text((cx, cy - 8), f"{m}:{s:02d}", font=F(BL, int(108 * pulse)), fill=WHITE if rem > 20 else (255, 120, 120), anchor='mm')
        d.text((cx, cy + 70), "TEMPS RESTANT" if at >= CHRONO_START else "PRÊT", font=F(BD, 22), fill=(190, 205, 245), anchor='mm')
    blink = (int(t * 2) % 2 == 0)
    d.rounded_rectangle([W - 230, 52, W - 40, 108], radius=28, fill=(255, 255, 255, 22), outline=(255, 255, 255, 60), width=2)
    d.ellipse([W - 210, 68, W - 186, 92], fill=FLAG if blink else (110, 30, 30))
    d.text((W - 172, 80), "ENREG.", font=F(BD, 26), fill=WHITE, anchor='lm')


def draw_stats(fr, at):
    d = ImageDraw.Draw(fr, 'RGBA')
    nq = sum(1 for q in QUESTIONS if at >= q)
    last = max([q for q in QUESTIONS if at >= q], default=-9)
    s = 1 + 0.25 * (1 - ease((at - last) / 0.4))
    d.text((197, 668), str(nq), font=F(BL, int(76 * s)), fill=WHITE if nq else (120, 135, 190), anchor='mm')
    d.text((197, 718), "posées par Harsh", font=F(MD, 19), fill=(190, 205, 245), anchor='mm')
    if at < 20.7:
        d.text((532, 668), "—", font=F(BL, 56), fill=(120, 135, 190), anchor='mm')
    elif at < REG_SWITCH:
        d.text((532, 666), "« tu »", font=F(BL, 54), fill=(110, 240, 160), anchor='mm')
        d.text((532, 718), "tutoiement", font=F(MD, 19), fill=(190, 205, 245), anchor='mm')
    else:
        d.text((532, 664), "tu / vous", font=F(BL, 44), fill=ORANGE, anchor='mm')
        d.text((532, 718), "registre mélangé", font=F(MD, 19), fill=ORANGE, anchor='mm')


def draw_themes(fr, at):
    d = ImageDraw.Draw(fr, 'RGBA')
    for name, ts, x0, y0, w in CHIPS:
        on = at >= ts; p = ease((at - ts) / 0.35) if on else 0
        d.rounded_rectangle([x0, y0 - 19, x0 + w, y0 + 19], radius=19, fill=A(WHITE, 0.15 + 0.85 * p) if on else (255, 255, 255, 12),
                            outline=(255, 255, 255, 200) if on else (255, 255, 255, 45), width=2)
        d.text((x0 + w / 2, y0), name, font=F(SB, 22), fill=ROYAL if on and p > 0.5 else ((235, 240, 255) if on else (150, 165, 215)), anchor='mm')
    if at < 10.8:
        g2 = 0.5 + 0.5 * math.sin(at * 4)
        d.rounded_rectangle([40, CY0, 690, CY1], radius=30, outline=A(YEL, 0.5 + 0.4 * g2), width=4)


def draw_feedback(fr, at):
    cur = None
    for i, (ts, kind, l1, l2) in enumerate(FEED):
        nxt = FEED[i + 1][0] if i + 1 < len(FEED) else 999
        end = min(ts + 7.0, nxt - 0.2)
        if ts <= at < end: cur = (ts, end, kind, l1, l2)
    if not cur: return
    ts, end, kind, l1, l2 = cur
    a = ease((at - ts) / 0.3) * (1 - ease((at - end + 0.35) / 0.35))
    dy = (1 - ob((at - ts) / 0.4)) * 24
    d = ImageDraw.Draw(fr, 'RGBA')
    col = {'ok': GREEN, 'fix': ORANGE, 'note': YEL}[kind]
    d.rounded_rectangle([720, FY0 + dy, 1880, FY1 + dy], radius=28, fill=(10, 16, 60, int(225 * a)), outline=A(col, a), width=3)
    d.ellipse([748, FY0 + 40 + dy, 808, FY0 + 100 + dy], fill=A(col, a))
    if kind == 'ok':
        d.line([762, FY0 + 70 + dy, 774, FY0 + 83 + dy, 795, FY0 + 56 + dy], fill=A(WHITE, a), width=7, joint='curve')
    else:
        d.text((778, FY0 + 70 + dy), "!" if kind == 'note' else "→", font=F(BL, 36), fill=A(NAVY, a), anchor='mm')
    if kind == 'fix':
        d.text((834, FY0 + 46 + dy), "Dit : " + l1, font=F(IT, 28), fill=A((200, 210, 240), a), anchor='lm')
        d.text((834, FY0 + 98 + dy), "Mieux : " + l2, font=F(XB, 34), fill=A(ORANGE, a), anchor='lm')
    else:
        d.text((834, FY0 + 46 + dy), l1, font=F(XB, 34), fill=A(col, a), anchor='lm')
        d.text((834, FY0 + 98 + dy), l2, font=F(MD, 28), fill=A((225, 232, 250), a), anchor='lm')


def wrap(d, words, font, maxw):
    lines, cur, wc = [], [], 0; sp = font.getlength(' ')
    for wd in words:
        wl = font.getlength(wd)
        if cur and wc + sp + wl > maxw: lines.append(cur); cur, wc = [wd], wl
        else: cur.append(wd); wc += (sp if len(cur) > 1 else 0) + wl
    if cur: lines.append(cur)
    return lines


def draw_subs(fr, at):
    d = ImageDraw.Draw(fr, 'RGBA')
    d.rounded_rectangle([720, SY0, 1880, SY1], radius=30, fill=(6, 10, 40, 120))
    L = last_line(at)
    if L is None: return
    s, a, b, txt = L
    if at > b + 1.6: return
    col = CC if s == 'C' else HC
    name = "Catherine · examinatrice" if s == 'C' else "Harsh · candidat"
    fa = ease((at - a + 0.05) / 0.25) * (1 - ease((at - b - 1.2) / 0.4))
    f = F(SB, 44); words = txt.split(' ')
    lines = wrap(d, words, f, 1880 - 720 - 90)
    if len(lines) > 4: f = F(SB, 38); lines = wrap(d, words, f, 1880 - 720 - 90)
    nw = len(words); prog = clamp((at - a) / max(0.3, b - a)) * nw
    pw = F(BD, 26).getlength(name) + 44
    d.rounded_rectangle([760, SY0 + 30, 760 + pw, SY0 + 78], radius=24, fill=A(col, fa))
    d.text((760 + pw / 2, SY0 + 54), name, font=F(BD, 26), fill=A(WHITE, fa), anchor='mm')
    idx = 0
    for li, ln in enumerate(lines):
        x0 = 760; y = SY0 + 128 + li * (f.size + 16)
        for wd in ln:
            d.text((x0, y), wd, font=f, fill=A(WHITE, fa * (1 if idx < prog + 0.5 else 0.32)), anchor='lm')
            x0 += f.getlength(wd + ' '); idx += 1


def draw_cta(fr, at):
    for a0, a1 in CTA_WINDOWS:
        if a0 <= at < a1:
            p = min(ob((at - a0) / 0.5), 1 - ease((at - a1 + 0.4) / 0.4))
            d = ImageDraw.Draw(fr, 'RGBA')
            txt = "Passez votre propre simulation sur formation-tcfcanada.com"
            f = F(BD, 26); tw = f.getlength(txt); w = tw + 110
            x0 = 1300 - w / 2 + 120; y = 52 - (1 - p) * 90
            d.rounded_rectangle([x0 - 130, y, x0 + w - 130, y + 56], radius=28, fill=A(WHITE, p))
            d.polygon([(x0 - 100, y + 14), (x0 - 100, y + 42), (x0 - 76, y + 28)], fill=A(FLAG, p))
            d.text((x0 - 60, y + 28), txt, font=f, fill=A(ROYAL, p), anchor='lm')


def logo_card(fr, cx, cy, s, a=1.0, h=300):
    card = Image.new('RGBA', (int(h * 1.6), int(h * 1.3)), (0, 0, 0, 0)); cd = ImageDraw.Draw(card)
    cd.rounded_rectangle([0, 0, card.width - 1, card.height - 1], radius=int(h * 0.14), fill=(255, 255, 255))
    lg = logo(int(h * 1.0)); card.paste(lg, (int(card.width / 2 - lg.width / 2), int(card.height / 2 - lg.height / 2)), lg)
    card = card.resize((max(1, int(card.width * s)), max(1, int(card.height * s))), Image.BICUBIC)
    if a < 1: card.putalpha(card.getchannel('A').point(lambda v: int(v * a)))
    fr.paste(card, (int(cx - card.width / 2), int(cy - card.height / 2)), card)


_BGPLAIN = None
def intro_frame(t, main0):
    global _BGPLAIN
    if _BGPLAIN is None:
        _BGPLAIN = Image.fromarray(arr).convert('RGBA'); _BGPLAIN.alpha_composite(glow.filter(ImageFilter.GaussianBlur(180)))
        dd = ImageDraw.Draw(_BGPLAIN); dd.rectangle([0, 0, W, H], fill=(10, 14, 60, 150))
    T_OUT = INTRO - 0.7
    fr = _BGPLAIN.copy()
    if t < T_OUT + 0.05:
        logo_build(t, 960, 400, 0.5, fr)
    d = ImageDraw.Draw(fr, 'RGBA')
    a = ease((t - 2.3) / 0.5) * (1 - ease((t - T_OUT + 0.1) / 0.3))
    if a > 0:
        dy = (1 - ease((t - 2.3) / 0.5)) * 30
        f = F(BD, 28); tw = f.getlength("SIMULATION RÉELLE") + 60
        d.rounded_rectangle([W / 2 - tw / 2, 700 + dy, W / 2 + tw / 2, 756 + dy], radius=28, fill=A(FLAG, a))
        d.text((W / 2, 728 + dy), "SIMULATION RÉELLE", font=f, fill=A(WHITE, a), anchor='mm')
        d.text((W / 2, 830 + dy), "Expression orale · Tâche 2", font=F(BL, 76), fill=A(WHITE, a), anchor='mm')
        d.text((W / 2, 915 + dy), "Catherine (examinatrice)  ×  Harsh (candidat)", font=F(MD, 34), fill=A((200, 212, 245), a), anchor='mm')
    if t >= T_OUT:
        p = ease((t - T_OUT) / 0.7)
        out = Image.blend(fr.convert('RGB'), main0, p).convert('RGBA')
        # flying logo: from centre (960,400,h=548) to header (160,82,h=104)
        h = 548 + (104 - 548) * p
        cx = 960 + (160 - 960) * p; cy = 400 + (82 - 400) * p
        lg2 = static_logo(int(h), glow=True)
        out.alpha_composite(lg2, (int(cx - lg2.width / 2), int(cy - lg2.height / 2)))
        return out.convert('RGB')
    return fr.convert('RGB')


def bilan_frame(u):
    fr = BG.copy(); d = ImageDraw.Draw(fr, 'RGBA'); d.rectangle([0, 0, W, H], fill=(12, 16, 64, 250))
    a = ease(u / 0.5)
    _bl = static_logo(110); _bl.putalpha(_bl.getchannel('A').point(lambda v: int(v * a))); fr.paste(_bl, (int(150 - _bl.width / 2), int(90 - _bl.height / 2)), _bl)
    d.text((W / 2, 70), "BILAN DE LA SIMULATION", font=F(BD, 28), fill=A(SKY, a), anchor='mm')
    d.text((W / 2, 130), "Harsh · Expression orale · Tâche 2", font=F(BL, 54), fill=A(WHITE, a), anchor='mm')
    stats = [("9", "questions"), ("8", "thèmes"), ("3:20", "d'échange")]
    for i, (v, l) in enumerate(stats):
        ai = ease((u - 0.3 - i * 0.12) / 0.4); cx = 660 + i * 300
        d.rounded_rectangle([cx - 130, 190, cx + 130, 320], radius=26, fill=(255, 255, 255, int(20 * ai)), outline=(255, 255, 255, int(50 * ai)), width=2)
        d.text((cx, 242), v, font=F(BL, 60), fill=A(WHITE, ai), anchor='mm'); d.text((cx, 295), l, font=F(MD, 26), fill=A((200, 212, 245), ai), anchor='mm')
    blocks = [
        (GREEN, "POINTS FORTS", ["Questions variées sur 8 thèmes", "Il reformule les réponses", "Il conclut avec une idée de cadeau"], 1.0),
        (ORANGE, "À AMÉLIORER", ["Un seul registre : tu ou vous", "« dont elle a besoin »", "« jouer aux jeux vidéo »", "Questions plus courtes"], 3.0),
        (SKY, "QUESTIONS MODÈLES", ["Qu'est-ce qu'elle fait pendant son temps libre ?", "Est-ce qu'elle a un style qu'elle préfère ?", "Quel est le plus beau cadeau qu'elle ait reçu ?"], 5.0),
    ]
    for bi, (col, title, items, t0) in enumerate(blocks):
        ab = ease((u - t0) / 0.5)
        if ab <= 0: continue
        x0 = 60 + bi * 610
        d.rounded_rectangle([x0, 360, x0 + 580, 1000], radius=30, fill=(255, 255, 255, int(16 * ab)), outline=A(col, 0.7 * ab), width=3)
        d.text((x0 + 40, 420), title, font=F(BD, 30), fill=A(col, ab), anchor='lm')
        for j, it in enumerate(items):
            aj = ease((u - t0 - 0.3 - j * 0.25) / 0.4)
            lines = wrap(d, it.split(' '), F(SB, 32), 470)
            yy = 520 + j * 120
            d.ellipse([x0 + 40, yy - 13, x0 + 66, yy + 13], fill=A(col, aj))
            for k2, ln in enumerate(lines[:2]):
                d.text((x0 + 86, yy + k2 * 42), ' '.join(ln), font=F(SB, 32), fill=A(WHITE, aj), anchor='lm')
    d.text((W / 2, 1045), "Bilan pédagogique · formation-tcfcanada.com", font=F(MD, 24), fill=A((170, 185, 230), a), anchor='mm')
    if u > BILAN - 0.5: d.rectangle([0, 0, W, H], fill=(12, 16, 64, int(255 * (u - BILAN + 0.5) / 0.5)))
    return fr


def outro_frame(u):
    global _BGPLAIN
    if _BGPLAIN is None: intro_frame(0, None) if False else None
    base = Image.fromarray(arr).convert('RGBA'); base.alpha_composite(glow.filter(ImageFilter.GaussianBlur(180)))
    ImageDraw.Draw(base).rectangle([0, 0, W, H], fill=(10, 14, 60, 150))
    logo_build(u * 1.15, 500, 470, 0.46, base)
    fr = base.convert('RGB'); d = ImageDraw.Draw(fr, 'RGBA')
    a2 = ease((u - 0.5) / 0.5)
    d.text((960, 400), "Entraînez-vous dans", font=F(BL, 64), fill=A(WHITE, a2), anchor='lm')
    d.text((960, 480), "les conditions réelles", font=F(BL, 64), fill=A(WHITE, a2), anchor='lm')
    d.text((960, 550), "Simulateur oral interactif · Examens blancs avec examinateur", font=F(MD, 28), fill=A((200, 212, 245), a2), anchor='lm')
    a3 = ease((u - 0.9) / 0.5)
    txt = "formation-tcfcanada.com"; f = F(BD, 46); tw = f.getlength(txt)
    pul = 1 + 0.03 * math.sin(max(0, u - 1.4) * 7)
    d.rounded_rectangle([960, 620, 960 + tw + 100, 730], radius=55, fill=A(WHITE, a3))
    d.text((960 + (tw + 100) / 2, 675), txt, font=F(BD, int(46 * pul)), fill=A(ROYAL, a3), anchor='mm')
    a4 = ease((u - 1.3) / 0.5)
    d.rounded_rectangle([960, 770, 1380, 830], radius=30, fill=A(FLAG, a4))
    d.text((1170, 800), "EXCLUSIF PACK AYOUB", font=F(BD, 30), fill=A(WHITE, a4), anchor='mm')
    if u > OUTRO - 0.6: d.rectangle([0, 0, W, H], fill=(0, 0, 0, int(255 * (u - OUTRO + 0.6) / 0.6)))
    return fr


n = int(round(TOTAL * FPS))
frames = range(n) if ONLY is None else [int(round(v * FPS)) for v in ONLY]
enc = None
if ONLY is None:
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', OUTV], stdin=subprocess.PIPE)
MAIN0 = None
for fi in frames:
    t = fi / FPS
    if t < INTRO:
        if MAIN0 is None:
            MAIN0 = BG.copy(); MAIN0.paste(BG_NOLOGO.crop((0, 0, 310, 170)), (0, 0)); draw_chrono(MAIN0, 0, INTRO); draw_stats(MAIN0, 0); draw_themes(MAIN0, 0); draw_tiles(MAIN0, 0); draw_subs(MAIN0, 0)
        fr = intro_frame(t, MAIN0)
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
print('total', round(TOTAL, 2))

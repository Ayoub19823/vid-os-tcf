import sys, os, math, subprocess, wave, importlib
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
SESS = importlib.import_module(sys.argv[1])
AUD = sys.argv[2]; OUTV = sys.argv[3]
ONLY = [float(v) for v in sys.argv[4].split(',')] if len(sys.argv) > 4 else None
import logoanim
logoanim.THEME = 'light'
from logoanim import build as logo_build, static_logo
LINES = SESS.LINES; QUESTIONS = SESS.QUESTIONS; THEMES = SESS.THEMES; FEED = SESS.FEED
CT, CS, CE = SESS.CHRONO_TOTAL, SESS.CHRONO_START, SESS.CHRONO_STOP

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


# palette (logo)
ROYAL = (24, 56, 255); SKY = (38, 169, 255); NAVY = (20, 27, 77); FLAG = (229, 30, 32)
INK = (20, 27, 77); SLATE = (92, 106, 146); LINEC = (220, 229, 248); WHITE = (255, 255, 255)
GREEN = (22, 163, 74); ORANGE = (234, 120, 10); GOLD = (214, 150, 0)
CC = FLAG; HC = ROYAL
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

# ------------------------------------------------ background (light, logo colours)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
tdiag = np.clip((xx / W) * 0.6 + (yy / H) * 0.4, 0, 1)[..., None]
c0 = np.array((255, 255, 255), np.float32); c1 = np.array((236, 243, 255), np.float32)
arr = (c0 + (c1 - c0) * tdiag).astype(np.uint8)
PLAIN = Image.fromarray(arr).convert('RGBA')
blob = Image.new('RGBA', (W, H), (0, 0, 0, 0)); bd_ = ImageDraw.Draw(blob)
bd_.ellipse([1350, 600, 2300, 1400], fill=SKY + (70,)); bd_.ellipse([-350, -300, 450, 380], fill=ROYAL + (40,)); bd_.ellipse([700, -500, 1300, 100], fill=FLAG + (14,))
PLAIN.alpha_composite(blob.filter(ImageFilter.GaussianBlur(170)))
pd = ImageDraw.Draw(PLAIN)
for yy_ in range(40, H, 44):
    for xx_ in range(40, W, 44): pd.ellipse([xx_ - 1.4, yy_ - 1.4, xx_ + 1.4, yy_ + 1.4], fill=ROYAL + (22,))
PLAIN_RGB = PLAIN.convert('RGB')


def card(base, box, r=30, shadow=True, fill=WHITE, outline=LINEC):
    x0, y0, x1, y1 = box
    if shadow:
        sh = Image.new('RGBA', (int(x1 - x0) + 80, int(y1 - y0) + 80), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle([40, 48, sh.width - 40, sh.height - 32], radius=r, fill=(20, 40, 120, 38))
        base.paste(Image.new('RGB', sh.size, (0, 0, 0)), (int(x0 - 40), int(y0 - 40)), sh.filter(ImageFilter.GaussianBlur(16)).getchannel('A').point(lambda v: v // 3)) if False else None
        sh = sh.filter(ImageFilter.GaussianBlur(16))
        tmp = base.convert('RGBA'); tmp.alpha_composite(sh, (int(x0 - 40), int(y0 - 40)))
        base.paste(tmp.convert('RGB'))
    ImageDraw.Draw(base, 'RGBA').rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=2)


bg = PLAIN_RGB.copy()
BG_NOLOGO = None
d = ImageDraw.Draw(bg, 'RGBA')
d.text((300, 64), "Expression orale · Tâche 2", font=F(BL, 46), fill=INK, anchor='lm')
d.text((300, 108), SESS.TITLE_SUB, font=F(MD, 26), fill=SLATE, anchor='lm')
card(bg, (40, 160, 690, 470))
card(bg, (40, 490, 355, 620)); card(bg, (375, 490, 690, 620))
d = ImageDraw.Draw(bg, 'RGBA')
d.text((197, 518), "QUESTIONS", font=F(BD, 18), fill=SLATE, anchor='mm')
d.text((532, 518), "REGISTRE", font=F(BD, 18), fill=SLATE, anchor='mm')
CY0, CY1 = 640, 850
card(bg, (40, CY0, 690, CY1)); d = ImageDraw.Draw(bg, 'RGBA')
d.rounded_rectangle([72, CY0 + 28, 78, CY0 + 50], radius=3, fill=FLAG)
d.text((90, CY0 + 39), "CONSIGNE", font=F(BD, 19), fill=FLAG, anchor='lm')
_n5 = len(SESS.CONSIGNE) >= 5
for i, l in enumerate(SESS.CONSIGNE):
    f = F(SB, 21 if _n5 else 23)
    while f.getlength(l) > 590: f = F(SB, f.size - 1)
    d.text((72, CY0 + (74 + i * 27 if _n5 else 80 + i * 31)), l, font=f, fill=INK, anchor='lm')
KY0, KY1 = 870, 1050
card(bg, (40, KY0, 690, KY1)); d = ImageDraw.Draw(bg, 'RGBA')
d.rounded_rectangle([72, KY0 + 28, 78, KY0 + 50], radius=3, fill=ROYAL)
d.text((90, KY0 + 39), "THÈMES ABORDÉS", font=F(BD, 19), fill=ROYAL, anchor='lm')
TY0, TY1 = 160, 500
TW = 570
card(bg, (720, TY0, 720 + TW, TY1)); card(bg, (1310, TY0, 1310 + TW, TY1))
SY0, SY1 = 680, 1050
card(bg, (720, SY0, 1880, SY1))
d = ImageDraw.Draw(bg, 'RGBA')
d.rounded_rectangle([W - 230, 52, W - 40, 108], radius=28, fill=WHITE, outline=LINEC, width=2)
BG_NOLOGO = bg.copy()
_hl = static_logo(110); bg.paste(_hl, (int(160 - _hl.width / 2), int(84 - _hl.height / 2)), _hl)
BG = bg

CHIPS = []
_n = len(THEMES); _per = 4; _gap = 10; _cw = (650 - 64 - (_per - 1) * _gap) / _per
for i, (name, ts) in enumerate(THEMES):
    r, c = divmod(i, _per)
    CHIPS.append((name, ts, 72 + c * (_cw + _gap), KY0 + 92 + r * 50, _cw))

TILES = {'C': (720, SESS.EXAM_NAME, 'Examinatrice certifiée', CC, SESS.EXAM_NAME[0], '🎧'),
         'H': (1310, SESS.CAND_NAME, SESS.CAND_ROLE, HC, SESS.CAND_NAME[0], '🎓')}
EMO = {k: emoji(v[5], 42) for k, v in TILES.items()}
def dz_flag(fw=60, fh=42, S=8):
    fl = Image.new('RGBA', (fw * S, fh * S)); fd = ImageDraw.Draw(fl)
    fd.rectangle([0, 0, fw * S // 2, fh * S], fill=(0, 98, 51)); fd.rectangle([fw * S // 2, 0, fw * S, fh * S], fill=(255, 255, 255))
    cr = Image.new('L', fl.size, 0); cd = ImageDraw.Draw(cr); fx, fy = fw * S / 2, fh * S / 2; r = fh * S * 0.32
    cd.ellipse([fx - r, fy - r, fx + r, fy + r], fill=255); r2 = r * 0.8; ox = r * 0.28; cd.ellipse([fx - r2 + ox, fy - r2, fx + r2 + ox, fy + r2], fill=0)
    sx, sy, so, si = fx + r * 0.42, fy, r * 0.42, r * 0.17
    cd.polygon([(sx + (so if i % 2 == 0 else si) * math.cos(math.pi * i / 5 - math.pi), sy + (so if i % 2 == 0 else si) * math.sin(math.pi * i / 5 - math.pi)) for i in range(10)], fill=255)
    fl.paste(Image.new('RGBA', fl.size, (210, 16, 52, 255)), (0, 0), cr)
    m = Image.new('L', fl.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, fl.width - 1, fl.height - 1], radius=6 * S, fill=255); fl.putalpha(m)
    return fl.resize((fw, fh), Image.LANCZOS)
def cm_flag(fw=72, fh=50, S=8):
    fl = Image.new('RGBA', (fw * S, fh * S)); fd = ImageDraw.Draw(fl); t = fw * S / 3
    fd.rectangle([0, 0, t, fh * S], fill=(0, 122, 94)); fd.rectangle([t, 0, 2 * t, fh * S], fill=(206, 17, 38)); fd.rectangle([2 * t, 0, fw * S, fh * S], fill=(252, 209, 22))
    cx, cy, ro = fw * S / 2, fh * S / 2, fh * S * 0.2; ri = ro * 0.38
    fd.polygon([(cx + (ro if i % 2 == 0 else ri) * math.cos(-math.pi / 2 + math.pi * i / 5), cy + (ro if i % 2 == 0 else ri) * math.sin(-math.pi / 2 + math.pi * i / 5)) for i in range(10)], fill=(252, 209, 22))
    m = Image.new('L', fl.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, fl.width - 1, fl.height - 1], radius=6 * S, fill=255); fl.putalpha(m)
    return fl.resize((fw, fh), Image.LANCZOS)
def ci_flag(fw=72, fh=50, S=8):
    fl = Image.new('RGBA', (fw * S, fh * S)); fd = ImageDraw.Draw(fl); t = fw * S / 3
    fd.rectangle([0, 0, t, fh * S], fill=(247, 127, 0)); fd.rectangle([t, 0, 2 * t, fh * S], fill=(255, 255, 255)); fd.rectangle([2 * t, 0, fw * S, fh * S], fill=(0, 158, 96))
    fd.rounded_rectangle([0, 0, fl.width - 1, fl.height - 1], radius=6 * S, outline=(205, 212, 228), width=2 * S)
    m = Image.new('L', fl.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, fl.width - 1, fl.height - 1], radius=6 * S, fill=255); fl.putalpha(m)
    return fl.resize((fw, fh), Image.LANCZOS)
def ma_flag(fw=72, fh=50, S=8):
    fl = Image.new('RGBA', (fw * S, fh * S), (193, 39, 45, 255)); fd = ImageDraw.Draw(fl)
    cx, cy, r = fw * S / 2, fh * S / 2, fh * S * 0.3
    pts = [(cx + r * math.cos(-math.pi / 2 + i * 4 * math.pi / 5), cy + r * math.sin(-math.pi / 2 + i * 4 * math.pi / 5)) for i in range(5)]
    fd.line(pts + [pts[0]], fill=(0, 98, 51), width=int(fh * S * 0.06), joint='curve')
    m = Image.new('L', fl.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, fl.width - 1, fl.height - 1], radius=6 * S, fill=255); fl.putalpha(m)
    return fl.resize((fw, fh), Image.LANCZOS)
def in_flag(fw=72, fh=50, S=8):
    fl = Image.new('RGBA', (fw * S, fh * S)); fd = ImageDraw.Draw(fl); t = fh * S / 3
    fd.rectangle([0, 0, fw * S, t], fill=(255, 153, 51)); fd.rectangle([0, t, fw * S, 2 * t], fill=(255, 255, 255)); fd.rectangle([0, 2 * t, fw * S, fh * S], fill=(19, 136, 8))
    cx, cy, r = fw * S / 2, fh * S / 2, t * 0.42
    fd.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(0, 0, 128), width=int(S * 1.2))
    for i in range(24):
        a = math.pi * 2 * i / 24; fd.line([cx, cy, cx + r * math.cos(a), cy + r * math.sin(a)], fill=(0, 0, 128), width=max(1, S // 3))
    fd.rounded_rectangle([0, 0, fl.width - 1, fl.height - 1], radius=6 * S, outline=(205, 212, 228), width=2 * S)
    m = Image.new('L', fl.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, fl.width - 1, fl.height - 1], radius=6 * S, fill=255); fl.putalpha(m)
    return fl.resize((fw, fh), Image.LANCZOS)
def sn_flag(fw=72, fh=50, S=8):
    fl = Image.new('RGBA', (fw * S, fh * S)); fd = ImageDraw.Draw(fl); t = fw * S / 3
    fd.rectangle([0, 0, t, fh * S], fill=(0, 133, 63)); fd.rectangle([t, 0, 2 * t, fh * S], fill=(253, 239, 66)); fd.rectangle([2 * t, 0, fw * S, fh * S], fill=(227, 27, 35))
    cx, cy, ro = fw * S / 2, fh * S / 2, fh * S * 0.2; ri = ro * 0.38
    fd.polygon([(cx + (ro if i % 2 == 0 else ri) * math.cos(-math.pi / 2 + math.pi * i / 5), cy + (ro if i % 2 == 0 else ri) * math.sin(-math.pi / 2 + math.pi * i / 5)) for i in range(10)], fill=(0, 133, 63))
    m = Image.new('L', fl.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, fl.width - 1, fl.height - 1], radius=6 * S, fill=255); fl.putalpha(m)
    return fl.resize((fw, fh), Image.LANCZOS)
FLAG_DZ = None if getattr(SESS, 'FLAG', 'dz') == 'none' else {'sn': lambda: sn_flag(72, 50), 'in': lambda: in_flag(72, 50), 'ma': lambda: ma_flag(72, 50), 'dz': lambda: dz_flag(72, 50), 'cm': lambda: cm_flag(72, 50), 'ci': lambda: ci_flag(72, 50)}[getattr(SESS, 'FLAG', 'dz')]()

FY0, FY1 = 520, 660


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
        if act:
            gl = 8 + 8 * lvl
            d.rounded_rectangle([tx - gl / 2, TY0 - gl / 2, tx + TW + gl / 2, TY1 + gl / 2], radius=36, outline=A(col, 0.22), width=int(gl))
            d.rounded_rectangle([tx, TY0, tx + TW, TY1], radius=30, outline=col, width=4)
        ccx, ccy, r = tx + TW / 2, TY0 + 118, 82
        if act:
            rr = r + 12 + 24 * min(1.0, lvl); d.ellipse([ccx - rr, ccy - rr, ccx + rr, ccy + rr], fill=A(col, 0.14))
        d.ellipse([ccx - r - 6, ccy - r - 6, ccx + r + 6, ccy + r + 6], fill=WHITE, outline=LINEC, width=2)
        d.ellipse([ccx - r, ccy - r, ccx + r, ccy + r], fill=col)
        d.text((ccx, ccy + 4), ini, font=F(BL, 86), fill=WHITE, anchor='mm')
        if k == 'C':
            e = EMO[k]; fr.paste(e, (int(ccx + r * 0.66 - e.width / 2), int(ccy + r * 0.66 - e.height / 2)), e)
        elif FLAG_DZ is not None:
            fx, fy = int(ccx + r * 0.55 - 10), int(ccy + r * 0.55 - 14)
            d.rounded_rectangle([fx - 5, fy - 5, fx + 77, fy + 55], radius=12, fill=WHITE, outline=(200, 208, 228), width=2)
            fr.paste(FLAG_DZ, (fx, fy), FLAG_DZ)
        d.text((ccx, TY0 + 236), name, font=F(XB, 42), fill=INK, anchor='mm')
        if k == 'C':
            f = F(BD, 22); tw = f.getlength("EXAMINATRICE CERTIFIÉE")
            d.rounded_rectangle([ccx - tw / 2 - 40, TY0 + 262, ccx + tw / 2 + 18, TY0 + 298], radius=18, fill=A(FLAG, 0.1), outline=A(FLAG, 0.5), width=2)
            d.ellipse([ccx - tw / 2 - 32, TY0 + 269, ccx - tw / 2 - 10, TY0 + 291], fill=FLAG)
            d.line([ccx - tw / 2 - 27, TY0 + 280, ccx - tw / 2 - 22, TY0 + 285, ccx - tw / 2 - 14, TY0 + 274], fill=WHITE, width=3)
            d.text((ccx + 7, TY0 + 280), "EXAMINATRICE CERTIFIÉE", font=f, fill=FLAG, anchor='mm')
        else:
            f = F(BD, 22); tw = f.getlength(SESS.CAND_ROLE.upper())
            d.rounded_rectangle([ccx - tw / 2 - 22, TY0 + 262, ccx + tw / 2 + 22, TY0 + 298], radius=18, fill=A(ROYAL, 0.1), outline=A(ROYAL, 0.5), width=2)
            d.text((ccx, TY0 + 280), SESS.CAND_ROLE.upper(), font=f, fill=ROYAL, anchor='mm')
        if act:
            b = bars(at); n = len(b); bw, gp = 9, 7; tot = n * bw + (n - 1) * gp; x0 = ccx - tot / 2
            for i, v in enumerate(b):
                hh = 6 + 26 * min(1.0, v * (0.4 + lvl))
                d.rounded_rectangle([x0 + i * (bw + gp), TY0 + 320 - hh / 2, x0 + i * (bw + gp) + bw, TY0 + 320 + hh / 2], radius=4, fill=col)


def draw_chrono(fr, at, t):
    d = ImageDraw.Draw(fr, 'RGBA')
    cx, cy, R = 365, 315, 120
    rem = CT if at < CS else max(0.0, CT - (min(at, CE) - CS))
    done = at >= CE
    col = GREEN if done else (FLAG if rem <= 20 else ORANGE if rem <= 60 else ROYAL)
    d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=(226, 234, 250), width=16)
    if done:
        d.arc([cx - R, cy - R, cx + R, cy + R], 0, 360, fill=GREEN, width=16)
        d.text((cx, cy - 12), "TERMINÉ", font=F(BL, 46), fill=GREEN, anchor='mm')
        d.text((cx, cy + 36), "Épreuve finie", font=F(MD, 22), fill=SLATE, anchor='mm')
    else:
        frac = rem / CT
        d.arc([cx - R, cy - R, cx + R, cy + R], -90, -90 + 360 * frac, fill=col, width=16)
        ang = math.radians(-90 + 360 * frac)
        px, py = cx + R * math.cos(ang), cy + R * math.sin(ang)
        d.ellipse([px - 15, py - 15, px + 15, py + 15], fill=WHITE, outline=col, width=5)
        sec = int(math.ceil(rem - 1e-9)); m, s = sec // 60, sec % 60
        pulse = 1.0 + (0.06 * (1 - (at % 1)) if rem <= 20 and at >= CS else 0)
        d.text((cx, cy - 8), f"{m}:{s:02d}", font=F(BL, int(86 * pulse)), fill=INK if rem > 20 else FLAG, anchor='mm')
        d.text((cx, cy + 56), "TEMPS RESTANT" if at >= CS else "PRÊT", font=F(BD, 18), fill=SLATE, anchor='mm')
    blink = (int(t * 2) % 2 == 0)
    d.ellipse([W - 210, 68, W - 186, 92], fill=FLAG if blink else (245, 190, 190))
    d.text((W - 172, 80), "ENREG.", font=F(BD, 26), fill=INK, anchor='lm')


def draw_stats(fr, at):
    d = ImageDraw.Draw(fr, 'RGBA')
    nq = sum(1 for q in QUESTIONS if at >= q)
    last = max([q for q in QUESTIONS if at >= q], default=-9)
    s = 1 + 0.25 * (1 - ease((at - last) / 0.4))
    d.text((197, 562), str(nq), font=F(BL, int(58 * s)), fill=ROYAL if nq else (190, 200, 225), anchor='mm')
    d.text((197, 598), f"posées par {SESS.CAND_NAME}", font=F(MD, 17), fill=SLATE, anchor='mm')
    first = QUESTIONS[0] - 0.3
    if at < first:
        d.text((532, 562), "—", font=F(BL, 46), fill=(190, 200, 225), anchor='mm')
    elif at < SESS.REG_SWITCH:
        _rl = getattr(SESS, 'REG_LABEL', ("« tu »", "tutoiement constant"))
        d.text((532, 560), _rl[0], font=F(BL, 44), fill=GREEN, anchor='mm')
        d.text((532, 598), _rl[1], font=F(MD, 17), fill=SLATE, anchor='mm')
    else:
        d.text((532, 560), "tu / vous", font=F(BL, 38), fill=ORANGE, anchor='mm')
        d.text((532, 598), "registre mélangé", font=F(MD, 19), fill=ORANGE, anchor='mm')


def draw_themes(fr, at):
    d = ImageDraw.Draw(fr, 'RGBA')
    for name, ts, x0, y0, w in CHIPS:
        fsz = 21
        while fsz > 14 and F(SB, fsz).getlength(name) > w - 14: fsz -= 1
        on = at >= ts; p = ease((at - ts) / 0.35) if on else 0
        if on:
            d.rounded_rectangle([x0, y0 - 19, x0 + w, y0 + 19], radius=12, fill=A(ROYAL, 0.15 + 0.85 * p), outline=ROYAL, width=2)
            d.text((x0 + w / 2, y0), name, font=F(SB, fsz), fill=WHITE if p > 0.5 else ROYAL, anchor='mm')
        else:
            d.rounded_rectangle([x0, y0 - 19, x0 + w, y0 + 19], radius=12, fill=(246, 248, 253), outline=LINEC, width=2)
            d.text((x0 + w / 2, y0), name, font=F(SB, fsz), fill=(160, 170, 198), anchor='mm')
    if at < 11.0:
        g2 = 0.5 + 0.5 * math.sin(at * 4)
        d.rounded_rectangle([40, CY0, 690, CY1], radius=30, outline=A(FLAG, 0.4 + 0.4 * g2), width=4)


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
    col = {'ok': GREEN, 'fix': ORANGE, 'note': GOLD}[kind]
    d.rounded_rectangle([720, FY0 + dy + 8, 1880, FY1 + dy + 8], radius=28, fill=(20, 40, 120, int(22 * a)))
    d.rounded_rectangle([720, FY0 + dy, 1880, FY1 + dy], radius=28, fill=A(WHITE, a), outline=A(col, a), width=3)
    d.rounded_rectangle([720, FY0 + dy, 736, FY1 + dy], radius=8, fill=A(col, a))
    d.ellipse([756, FY0 + 40 + dy, 816, FY0 + 100 + dy], fill=A(col, a))
    if kind == 'ok':
        d.line([770, FY0 + 70 + dy, 782, FY0 + 83 + dy, 803, FY0 + 56 + dy], fill=A(WHITE, a), width=7, joint='curve')
    else:
        d.text((786, FY0 + 70 + dy), "!" if kind == 'note' else "→", font=F(BL, 36), fill=A(WHITE, a), anchor='mm')
    if kind == 'fix':
        d.text((842, FY0 + 46 + dy), "Dit : " + l1, font=F(IT, 28), fill=A(SLATE, a), anchor='lm')
        d.text((842, FY0 + 98 + dy), "Mieux : " + l2, font=F(XB, 34), fill=A(ORANGE, a), anchor='lm')
    else:
        d.text((842, FY0 + 46 + dy), l1, font=F(XB, 34), fill=A(col, a), anchor='lm')
        f2 = F(MD, 28)
        while f2.getlength(l2) > 1010: f2 = F(MD, f2.size - 1)
        d.text((842, FY0 + 98 + dy), l2, font=f2, fill=A(INK, a), anchor='lm')


def wrap(words, font, maxw):
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
    name = SESS.EXAM_LABEL if s == 'C' else SESS.CAND_LABEL
    fa = ease((at - a + 0.05) / 0.25) * (1 - ease((at - b - 1.2) / 0.4))
    f = F(SB, 44); words = txt.replace(' ?', '\u00a0?').replace(' !', '\u00a0!').replace(' :', '\u00a0:').split(' ')
    lines = wrap(words, f, 1880 - 720 - 90)
    if len(lines) > 4: f = F(SB, 38); lines = wrap(words, f, 1880 - 720 - 90)
    nw = len(words); prog = clamp((at - a) / max(0.3, b - a)) * nw
    pw = F(BD, 26).getlength(name) + 44
    d.rounded_rectangle([760, SY0 + 30, 760 + pw, SY0 + 78], radius=24, fill=A(col, fa))
    d.text((760 + pw / 2, SY0 + 54), name, font=F(BD, 26), fill=A(WHITE, fa), anchor='mm')
    idx = 0
    for li, ln in enumerate(lines):
        x0 = 760; y = SY0 + 128 + li * (f.size + 16)
        for wd in ln:
            on = idx < prog + 0.5
            d.text((x0, y), wd, font=f, fill=A(INK if on else (178, 188, 212), fa), anchor='lm')
            x0 += f.getlength(wd + ' '); idx += 1


def draw_cta(fr, at):
    for a0, a1 in SESS.CTA_WINDOWS:
        if a0 <= at < a1:
            p = min(ob((at - a0) / 0.5), 1 - ease((at - a1 + 0.4) / 0.4))
            d = ImageDraw.Draw(fr, 'RGBA')
            txt = "Passez votre simulation"; url = "formation-tcfcanada.com"
            f = F(BD, 24); fu = F(XB, 24)
            w = f.getlength(txt) + fu.getlength(url) + 150
            x1 = W - 250; x0 = x1 - w + (1 - p) * 60; y = 56
            d.rounded_rectangle([x0, y, x0 + w, y + 56], radius=28, fill=A(ROYAL, p))
            d.ellipse([x0 + 10, y + 10, x0 + 46, y + 46], fill=A(WHITE, p))
            d.polygon([(x0 + 23, y + 18), (x0 + 23, y + 38), (x0 + 38, y + 28)], fill=A(ROYAL, p))
            d.text((x0 + 60, y + 28), txt, font=f, fill=A(WHITE, p), anchor='lm')
            xa = x0 + 60 + f.getlength(txt) + 14
            d.text((xa, y + 28), "→", font=f, fill=A(WHITE, p), anchor='lm')
            d.text((xa + 34, y + 28), url, font=fu, fill=A((255, 214, 80), p), anchor='lm')


def intro_frame(t, main0):
    T_OUT = INTRO - 0.7
    fr = PLAIN.copy()
    if t < T_OUT + 0.05: logo_build(t, 960, 400, 0.5, fr)
    d = ImageDraw.Draw(fr, 'RGBA')
    a = ease((t - 2.3) / 0.5) * (1 - ease((t - T_OUT + 0.1) / 0.3))
    if a > 0:
        dy = (1 - ease((t - 2.3) / 0.5)) * 30
        _tag = getattr(SESS, "INTRO_TAG", "SIMULATION RÉELLE"); f = F(BD, 28); tw = f.getlength(_tag) + 60
        d.rounded_rectangle([W / 2 - tw / 2, 700 + dy, W / 2 + tw / 2, 756 + dy], radius=28, fill=A(FLAG, a))
        d.text((W / 2, 728 + dy), _tag, font=f, fill=A(WHITE, a), anchor='mm')
        d.text((W / 2, 830 + dy), "Expression orale · Tâche 2", font=F(BL, 76), fill=A(INK, a), anchor='mm')
        d.text((W / 2, 915 + dy), f"{SESS.EXAM_NAME} (examinatrice)  ×  {SESS.CAND_NAME} ({SESS.CAND_ROLE[0].lower() + SESS.CAND_ROLE[1:]})", font=F(MD, 34), fill=A(SLATE, a), anchor='mm')
    if t >= T_OUT:
        p = ease((t - T_OUT) / 0.7)
        out = Image.blend(fr.convert('RGB'), main0, p).convert('RGBA')
        h = 548 + (110 - 548) * p
        cx = 960 + (160 - 960) * p; cy = 400 + (84 - 400) * p
        lg2 = static_logo(int(h), glow=True)
        out.alpha_composite(lg2, (int(cx - lg2.width / 2), int(cy - lg2.height / 2)))
        return out.convert('RGB')
    return fr.convert('RGB')


def bilan_frame(u):
    fr = PLAIN_RGB.copy(); d = ImageDraw.Draw(fr, 'RGBA')
    a = ease(u / 0.5)
    bl = static_logo(110); bl.putalpha(bl.getchannel('A').point(lambda v: int(v * a))); fr.paste(bl, (int(160 - bl.width / 2), int(84 - bl.height / 2)), bl)
    d.text((W / 2, 70), "BILAN DE LA SIMULATION", font=F(BD, 28), fill=A(FLAG, a), anchor='mm')
    d.text((W / 2, 130), f"{SESS.CAND_NAME} · Expression orale · Tâche 2", font=F(BL, 54), fill=A(INK, a), anchor='mm')
    for i, (v, l) in enumerate(SESS.BILAN_STATS):
        ai = ease((u - 0.3 - i * 0.12) / 0.4); cx = 660 + i * 300
        if ai > 0:
            d.rounded_rectangle([cx - 130, 190, cx + 130, 320], radius=26, fill=A(WHITE, ai), outline=A(LINEC, ai), width=2)
            d.text((cx, 242), v, font=F(BL, 60), fill=A(ROYAL, ai), anchor='mm'); d.text((cx, 295), l, font=F(MD, 26), fill=A(SLATE, ai), anchor='mm')
    cols = [GREEN, ORANGE, SKY]
    for bi, (title, items) in enumerate(SESS.BILAN_BLOCKS):
        t0 = 1.0 + bi * 2.0; col = cols[bi]
        ab = ease((u - t0) / 0.5)
        if ab <= 0: continue
        x0 = 60 + bi * 610
        d.rounded_rectangle([x0, 368, x0 + 580, 1008], radius=30, fill=(20, 40, 120, int(18 * ab)))
        d.rounded_rectangle([x0, 360, x0 + 580, 1000], radius=30, fill=A(WHITE, ab), outline=A(col, 0.8 * ab), width=3)
        d.rounded_rectangle([x0, 360, x0 + 580, 376], radius=8, fill=A(col, ab))
        d.text((x0 + 40, 430), title, font=F(BD, 30), fill=A(col, ab), anchor='lm')
        for j, it in enumerate(items):
            aj = ease((u - t0 - 0.3 - j * 0.25) / 0.4)
            lines = wrap(it.replace(' ?', '\u00a0?').replace(' »', '\u00a0»').replace('« ', '«\u00a0').replace(' :', '\u00a0:').split(' '), F(SB, 32), 460)
            yy_ = 530 + j * 140
            d.ellipse([x0 + 40, yy_ - 13, x0 + 66, yy_ + 13], fill=A(col, aj))
            for k2, ln in enumerate(lines[:2]):
                d.text((x0 + 86, yy_ + k2 * 42), ' '.join(ln), font=F(SB, 32), fill=A(INK, aj), anchor='lm')
    d.text((W / 2, 1045), "Bilan pédagogique · formation-tcfcanada.com", font=F(MD, 24), fill=A(SLATE, a), anchor='mm')
    if u > BILAN - 0.5: d.rectangle([0, 0, W, H], fill=(255, 255, 255, int(255 * (u - BILAN + 0.5) / 0.5)))
    return fr


def outro_frame(u):
    base = PLAIN.copy()
    logo_build(u * 1.15, 500, 470, 0.46, base)
    fr = base.convert('RGB'); d = ImageDraw.Draw(fr, 'RGBA')
    a2 = ease((u - 0.5) / 0.5)
    d.text((960, 400), "Entraînez-vous dans", font=F(BL, 64), fill=A(INK, a2), anchor='lm')
    d.text((960, 480), "les conditions réelles", font=F(BL, 64), fill=A(ROYAL, a2), anchor='lm')
    d.text((960, 550), "Simulateur oral interactif · Examens blancs avec examinateur", font=F(MD, 28), fill=A(SLATE, a2), anchor='lm')
    a3 = ease((u - 0.9) / 0.5)
    txt = "formation-tcfcanada.com"; f = F(BD, 46); tw = f.getlength(txt)
    pul = 1 + 0.03 * math.sin(max(0, u - 1.4) * 7)
    d.rounded_rectangle([960, 620, 960 + tw + 100, 730], radius=55, fill=A(ROYAL, a3))
    d.text((960 + (tw + 100) / 2, 675), txt, font=F(BD, int(46 * pul)), fill=A(WHITE, a3), anchor='mm')
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
            MAIN0 = BG_NOLOGO.copy(); draw_chrono(MAIN0, 0, INTRO); draw_stats(MAIN0, 0); draw_themes(MAIN0, 0); draw_tiles(MAIN0, 0)
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
print('total', round(TOTAL, 2), 'adur', round(ADUR, 2))

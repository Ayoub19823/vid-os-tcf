import sys, os, math, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
from script import LINES, CHRONO_START, CHRONO_STOP

AUD = sys.argv[1]; OUTV = sys.argv[2]
ONLY = [float(x) for x in sys.argv[3].split(',')] if len(sys.argv) > 3 else None
W, H, FPS = 1080, 1920, 25
INTRO, OUTRO = 2.5, 5.0
w = wave.open(AUD); sr = w.getframerate(); x = np.frombuffer(w.readframes(w.getnframes()), '<i2').astype(np.float32) / 32768
ADUR = len(x) / sr
TOTAL = INTRO + ADUR + OUTRO
hop = sr // FPS
env = np.array([np.sqrt(np.mean(x[i:i + hop] ** 2)) for i in range(0, len(x), hop)])
env = env / (np.percentile(env, 98) + 1e-6)
# spectral-ish bands for bars: use 12 short sub-windows energy
def bars(at, n=13):
    i = int(at * sr); seg = x[max(0, i - 1200):i + 1200]
    if len(seg) < 256: return np.zeros(n)
    sp = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))[:len(seg) // 6]
    chunks = np.array_split(sp, n)
    v = np.array([c.mean() for c in chunks]); v = np.sqrt(v / (sp.mean() * 3 + 1e-6))
    order = np.argsort(-np.arange(n) % n)
    sym = np.concatenate([v[::2][::-1], v[1::2]])[:n]
    return np.clip(sym, 0, 1.2)

BG0 = (9, 16, 40); BG1 = (18, 30, 70); CARD = (255, 255, 255, 14); LINE = (255, 255, 255, 30)
WHITE = (255, 255, 255); MUTE = (160, 172, 210); YEL = (255, 200, 60); RED = (239, 68, 68); ORANGE = (255, 150, 40)
CC = (167, 112, 255); HC = (56, 160, 255); GREEN = (34, 197, 94)
BL = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
XB = "/usr/share/fonts/opentype/inter/InterDisplay-ExtraBold.otf"
SB = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
MD = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
BD = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
EF = ImageFont.truetype('/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf', 109)
_fc = {}
def F(p, s):
    k = (p, int(s))
    if k not in _fc: _fc[k] = ImageFont.truetype(p, int(s))
    return _fc[k]
def clamp(v, a=0.0, b=1.0): return max(a, min(b, v))
def ease(v): v = clamp(v); return v * v * (3 - 2 * v)
def A(c, a): return tuple(c[:3]) + (int(255 * clamp(a)),)
def emoji(e, s):
    im = Image.new('RGBA', (140, 140)); ImageDraw.Draw(im).text((70, 70), e, font=EF, embedded_color=True, anchor='mm')
    im = im.crop(im.getbbox()); k = s / max(im.size); return im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)

# ------------------------------------------------ static background
bg = Image.new('RGB', (W, H), BG0)
g = np.linspace(0, 1, H)[:, None, None]
arr = (np.array(BG0)[None, None] * (1 - g) + np.array(BG1)[None, None] * g).astype(np.uint8)
bg = Image.fromarray(np.repeat(arr, W, axis=1)).convert('RGBA')
glow = Image.new('RGBA', (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
gd.ellipse([-300, 200, 600, 1000], fill=(90, 60, 220, 60)); gd.ellipse([600, 1000, 1500, 1900], fill=(30, 120, 255, 50))
bg.alpha_composite(glow.filter(ImageFilter.GaussianBlur(160)))
bg = bg.convert('RGB'); d = ImageDraw.Draw(bg, 'RGBA')
for yy in range(0, H, 60): d.line([0, yy, W, yy], fill=(255, 255, 255, 6))
for xx in range(0, W, 60): d.line([xx, 0, xx, H], fill=(255, 255, 255, 6))
# header
d.rounded_rectangle([50, 60, 330, 120], radius=16, fill=(255, 255, 255, 235))
d.text((86, 90), "TCF", font=F(BL, 34), fill=(14, 40, 120), anchor='lm')
d.rectangle([160, 74, 166, 106], fill=RED)
d.text((182, 90), "CANADA", font=F(BL, 30), fill=(14, 40, 120), anchor='lm')
d.text((50, 180), "Expression orale · Tâche 2", font=F(BL, 56), fill=WHITE, anchor='lm')
d.text((50, 236), "Simulation d'examen — Interaction", font=F(MD, 32), fill=MUTE, anchor='lm')
# consigne card
CY0, CY1 = 690, 960
d.rounded_rectangle([50, CY0, W - 50, CY1], radius=30, fill=CARD, outline=LINE, width=2)
d.text((90, CY0 + 50), "CONSIGNE", font=F(BD, 24), fill=YEL, anchor='lm')
cons = ["« Je suis votre amie. Je vous invite à l'anniversaire de",
        "ma sœur. Posez-moi des questions sur elle pour savoir",
        "quel cadeau lui offrir (activités, personnalité, etc.). »"]
for i, l in enumerate(cons): d.text((90, CY0 + 108 + i * 50), l, font=F(SB, 34), fill=(225, 230, 245), anchor='lm')
# footer
d.text((W / 2, 1878), "formation-tcfcanada.com  ·  Simulateur d'expression orale", font=F(MD, 26), fill=(130, 145, 190), anchor='mm')
BG = bg

# ------------------------------------------------ tiles
TY0, TY1 = 1000, 1400
TILES = {'C': (50, 'Catherine', 'Examinatrice certifiée', CC, 'C', '🎧'), 'H': (560, 'Harsh', 'Candidat', HC, 'H', '🎓')}
TW = 470
EMO = {k: emoji(v[5], 44) for k, v in TILES.items()}


def speaker_at(at):
    for s, a, b, txt in LINES:
        if a - 0.05 <= at <= b + 0.15: return s, a, b, txt
    return None, 0, 0, ''


def last_line(at):
    best = None
    for L in LINES:
        if L[1] - 0.05 <= at: best = L
    return best


def draw_tiles(fr, at, live):
    d = ImageDraw.Draw(fr, 'RGBA')
    sp = speaker_at(at)[0] if live else None
    lvl = env[min(len(env) - 1, int(at * FPS))] if live else 0
    for k, (tx, name, role, col, ini, _) in TILES.items():
        act = (k == sp)
        d.rounded_rectangle([tx, TY0, tx + TW, TY1], radius=34, fill=(255, 255, 255, 22 if act else 12),
                            outline=A(col, 1 if act else 0.25), width=5 if act else 2)
        if act:
            gl = 10 + 8 * lvl
            d.rounded_rectangle([tx - gl / 2, TY0 - gl / 2, tx + TW + gl / 2, TY1 + gl / 2], radius=38, outline=A(col, 0.25), width=int(gl))
        cx, cy, r = tx + TW / 2, TY0 + 150, 92
        if act:
            rr = r + 14 + 26 * min(1.0, lvl)
            d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=A(col, 0.18))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
        d.ellipse([cx - r + 8, cy - r + 8, cx + r - 8, cy + r - 8], fill=tuple(int(c * 0.78) for c in col))
        d.text((cx, cy + 4), ini, font=F(BL, 96), fill=WHITE, anchor='mm')
        e = EMO[k]; fr.paste(e, (int(cx + r * 0.62 - e.width / 2), int(cy + r * 0.62 - e.height / 2)), e)
        d.text((cx, TY0 + 268), name, font=F(XB, 44), fill=WHITE, anchor='mm')
        d.text((cx, TY0 + 312), role, font=F(MD, 26), fill=MUTE, anchor='mm')
        # mic indicator / bars
        if act and live:
            b = bars(at)
            n = len(b); bw = 10; gap = 8; tot = n * bw + (n - 1) * gap; x0 = cx - tot / 2
            for i, v in enumerate(b):
                hh = 6 + 34 * min(1.0, v * (0.4 + lvl))
                d.rounded_rectangle([x0 + i * (bw + gap), TY0 + 362 - hh / 2, x0 + i * (bw + gap) + bw, TY0 + 362 + hh / 2], radius=5, fill=col)
        else:
            d.text((cx, TY0 + 360), "micro actif" if live else "", font=F(MD, 22), fill=(110, 125, 170), anchor='mm')


def draw_chrono(fr, at, t):
    d = ImageDraw.Draw(fr, 'RGBA')
    cx, cy, R = W / 2, 470, 175
    if at < CHRONO_START: rem = 210.0
    elif at < CHRONO_STOP: rem = max(0.0, 210 - (at - CHRONO_START))
    else: rem = max(0.0, 210 - (CHRONO_STOP - CHRONO_START))
    done = at >= CHRONO_STOP
    col = GREEN if done else (RED if rem <= 20 else ORANGE if rem <= 60 else YEL)
    d.ellipse([cx - R - 30, cy - R - 30, cx + R + 30, cy + R + 30], fill=(255, 255, 255, 10))
    d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=(255, 255, 255, 30), width=18)
    frac = rem / 210
    if frac > 0 and not done:
        d.arc([cx - R, cy - R, cx + R, cy + R], -90, -90 + 360 * frac, fill=col, width=18)
        ang = math.radians(-90 + 360 * frac)
        d.ellipse([cx + R * math.cos(ang) - 15, cy + R * math.sin(ang) - 15, cx + R * math.cos(ang) + 15, cy + R * math.sin(ang) + 15], fill=WHITE)
    if done:
        d.arc([cx - R, cy - R, cx + R, cy + R], 0, 360, fill=GREEN, width=18)
        d.text((cx, cy - 20), "TERMINÉ", font=F(BL, 64), fill=GREEN, anchor='mm')
        d.text((cx, cy + 48), "Épreuve finie", font=F(MD, 30), fill=MUTE, anchor='mm')
    else:
        m, s = int(rem // 60), int(math.ceil(rem - 1e-6)) % 60 if rem % 60 else 0
        sec = int(math.ceil(rem - 1e-9)); m, s = sec // 60, sec % 60
        pulse = 1.0 + (0.06 * (1 - (at % 1)) if rem <= 20 and at >= CHRONO_START else 0)
        d.text((cx, cy - 10), f"{m}:{s:02d}", font=F(BL, int(120 * pulse)), fill=WHITE if rem > 20 else RED, anchor='mm')
        lab = "TEMPS RESTANT" if at >= CHRONO_START else "PRÊT"
        d.text((cx, cy + 82), lab, font=F(BD, 24), fill=MUTE, anchor='mm')
    # REC badge
    blink = (int(t * 2) % 2 == 0)
    d.rounded_rectangle([W - 250, 62, W - 50, 118], radius=28, fill=(255, 255, 255, 18), outline=(255, 255, 255, 40), width=2)
    d.ellipse([W - 228, 78, W - 204, 102], fill=RED if blink else (120, 40, 40))
    d.text((W - 190, 90), "ENREG.", font=F(BD, 26), fill=WHITE, anchor='lm')


def wrap(d, words, font, maxw):
    lines, cur, wcur = [], [], 0
    sp = d.textlength(' ', font=font)
    for wd in words:
        wl = d.textlength(wd, font=font)
        if cur and wcur + sp + wl > maxw: lines.append(cur); cur, wcur = [wd], wl
        else: cur.append(wd); wcur += (sp if len(cur) > 1 else 0) + wl
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
    Y0 = 1440
    d.rounded_rectangle([50, Y0, W - 50, 1820], radius=30, fill=(0, 0, 0, int(90 * fa)))
    f = F(SB, 46)
    words = txt.split(' ')
    lines = wrap(d, words, f, W - 180)
    if len(lines) > 4:
        f = F(SB, 40); lines = wrap(d, words, f, W - 180)
    nw = len(words); prog = clamp((at - a) / max(0.3, b - a)) * nw
    pw = d.textlength(name, font=F(BD, 26)) + 44
    d.rounded_rectangle([90, Y0 + 34, 90 + pw, Y0 + 82], radius=24, fill=A(col, fa))
    d.text((90 + pw / 2, Y0 + 58), name, font=F(BD, 26), fill=A(WHITE, fa), anchor='mm')
    idx = 0
    for li, ln in enumerate(lines):
        x0 = 90; y = Y0 + 130 + li * (f.size + 16)
        for wd in ln:
            on = idx < prog + 0.5
            d.text((x0, y), wd, font=f, fill=A(WHITE, fa * (1 if on else 0.32)), anchor='lm')
            x0 += d.textlength(wd + ' ', font=f); idx += 1


def intro_frame(t):
    fr = BG.copy(); d = ImageDraw.Draw(fr, 'RGBA')
    a = ease(t / 0.5) * (1 - ease((t - INTRO + 0.4) / 0.4))
    d.rectangle([0, 0, W, H], fill=(9, 16, 40, int(235 * (1 - ease((t - INTRO + 0.4) / 0.4)))))
    d.rounded_rectangle([W / 2 - 230, 640, W / 2 + 230, 700], radius=30, fill=A(RED, a))
    d.text((W / 2, 670), "SIMULATION RÉELLE", font=F(BD, 30), fill=A(WHITE, a), anchor='mm')
    d.text((W / 2, 800), "TCF Canada", font=F(BL, 96), fill=A(WHITE, a), anchor='mm')
    d.text((W / 2, 900), "Expression orale · Tâche 2", font=F(XB, 54), fill=A(YEL, a), anchor='mm')
    d.text((W / 2, 1010), "Catherine (examinatrice)  ×  Harsh (candidat)", font=F(MD, 36), fill=A(MUTE, a), anchor='mm')
    return fr


def outro_frame(u):
    fr = BG.copy(); d = ImageDraw.Draw(fr, 'RGBA'); d.rectangle([0, 0, W, H], fill=(9, 16, 40, 240))
    a = ease(u / 0.5)
    r = 90 * ease(u / 0.4)
    d.ellipse([W / 2 - r, 560 - r, W / 2 + r, 560 + r], fill=GREEN)
    if u > 0.3: d.line([W / 2 - 40, 562, W / 2 - 10, 594, W / 2 + 45, 530], fill=WHITE, width=16, joint='curve')
    d.text((W / 2, 740), "Épreuve terminée", font=F(BL, 84), fill=A(WHITE, a), anchor='mm')
    a2 = ease((u - 0.5) / 0.5)
    d.text((W / 2, 850), "Entraînez-vous dans les conditions réelles", font=F(SB, 42), fill=A(MUTE, a2), anchor='mm')
    a3 = ease((u - 0.9) / 0.5)
    txt = "formation-tcfcanada.com"; f = F(BD, 50); tw = d.textlength(txt, font=f)
    pul = 1 + 0.03 * math.sin(max(0, u - 1.4) * 7)
    d.rounded_rectangle([W / 2 - tw / 2 - 60, 960, W / 2 + tw / 2 + 60, 1080], radius=60, fill=A((26, 92, 255), a3))
    d.text((W / 2, 1020), txt, font=F(BD, int(50 * pul)), fill=A(WHITE, a3), anchor='mm')
    a4 = ease((u - 1.3) / 0.5)
    d.text((W / 2, 1170), "Simulateur d'expression orale · Examens blancs avec examinateur", font=F(MD, 30), fill=A(MUTE, a4), anchor='mm')
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
    if t < INTRO:
        fr = intro_frame(t)
    elif t >= INTRO + ADUR:
        fr = outro_frame(t - INTRO - ADUR)
    else:
        at = t - INTRO
        fr = BG.copy()
        # consigne highlight while examiner reads it
        if at < 10.8:
            dd = ImageDraw.Draw(fr, 'RGBA'); g2 = 0.5 + 0.5 * math.sin(at * 4)
            dd.rounded_rectangle([50, CY0, W - 50, CY1], radius=30, outline=A(YEL, 0.5 + 0.4 * g2), width=4)
        draw_chrono(fr, at, t)
        draw_tiles(fr, at, True)
        draw_subs(fr, at)
    rgb = fr.convert('RGB')
    if enc: enc.stdin.write(rgb.tobytes())
    else: rgb.save(f'{OUTV}_{t:.1f}.png')
if enc: enc.stdin.close(); enc.wait()
print('total', TOTAL)

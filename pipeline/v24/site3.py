import sys, json, math, subprocess, glob
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

import os
PT = os.environ.get('PARTIE', '14')
CAP = os.environ.get('CAPDIR', '/home/claude/v24/cap/')
import os
SK = int(os.environ.get('SUBJ', '1'))
J = json.load(open(CAP + 'J.json'))
SD = CAP + f's{SK}/' if os.path.isdir(CAP + f's{SK}/') else CAP
if SD != CAP: J.update(json.load(open(SD + 'J.json')))
OUTK = os.environ.get('OUTK', '/home/claude/v24/')
W, H, FPS = 1920, 1080, 25
LOGO = '/tmp/claude-0/-home-claude/7a22c9af-0a80-57d2-89a2-1a32e1824476/scratchpad/v6/logo.png'
ROYAL = (24, 56, 255); SKY = (38, 169, 255); INK = (20, 27, 77); SLATE = (92, 106, 146); FLAG = (229, 30, 32)
GREEN = (22, 163, 74); WHITE = (255, 255, 255)
XB = "/usr/share/fonts/opentype/inter/InterDisplay-ExtraBold.otf"
BD = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
SB = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
MD = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
_fc = {}
def F(p, s):
    k = (p, int(s))
    if k not in _fc: _fc[k] = ImageFont.truetype(p, int(s))
    return _fc[k]
def clamp(v, a=0., b=1.): return max(a, min(b, v))
def ease(v): v = clamp(v); return v * v * (3 - 2 * v)
def eio(v): v = clamp(v); return 4 * v ** 3 if v < .5 else 1 - (-2 * v + 2) ** 3 / 2
def lerp(a, b, k): return a + (b - a) * k
def A(c, a): return tuple(c[:3]) + (int(255 * clamp(a)),)

# ---------- background
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
td = np.clip((xx / W) * .6 + (yy / H) * .4, 0, 1)[..., None]
bg = (np.array((255, 255, 255), np.float32) * (1 - td) + np.array((236, 243, 255), np.float32) * td)
dots = ((xx % 34 < 2.2) & (yy % 34 < 2.2))[..., None]
bg = np.where(dots, bg * .93, bg)
BG = Image.fromarray(bg.astype(np.uint8)).convert('RGBA')
lg = Image.open(LOGO).convert('RGBA'); k = 74 / lg.height; lg = lg.resize((int(lg.width * k), 74), Image.LANCZOS)
BG.alpha_composite(lg, (60, 38))

# ---------- window geometry
CW, CH = 1472, 828
WX, WY = (W - CW) // 2, 196            # content top-left
BAR = 46
MOIS = os.environ.get("MOIS", "Octobre 2026"); MSLUG = MOIS.lower().replace(" ", "-").replace("é", "e").replace("û", "u")
EE = os.environ.get("MODE") == "EE"
EPR = "expression-ecrite" if EE else "expression-orale"; EPL = "Expression écrite" if EE else "Expression orale"; UNIT = "Combinaison" if EE else "Partie"
URL = "formation-tcfcanada.com/epreuve/" + EPR + "/sujets-actualites/" + MSLUG
TACHE = os.environ.get("TACHE", "2"); TLAB = ({"1": "Tâche 1 · Message court", "2": "Tâche 2 · Narration", "3": "Tâche 3 · Argumentation"} if os.environ.get("MODE") == "EE" else {"2": "Tâche 2 · Interaction orale", "3": "Tâche 3 · Argumentation"})[TACHE]
def window_layer():
    L = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(L)
    sh = Image.new('RGBA', (W, H)); ImageDraw.Draw(sh).rounded_rectangle([WX - 2, WY - BAR + 14, WX + CW + 2, WY + CH + 18], 18, fill=(20, 27, 77, 70))
    sh = sh.filter(ImageFilter.GaussianBlur(22)); L.alpha_composite(sh)
    d.rounded_rectangle([WX - 1, WY - BAR, WX + CW + 1, WY + CH + 1], 16, fill=(255, 255, 255, 255), outline=(214, 223, 242, 255), width=2)
    d.rectangle([WX, WY - 2, WX + CW, WY], fill=(226, 232, 245, 255))
    for i, c in enumerate([(255, 95, 87), (254, 188, 46), (40, 200, 64)]):
        d.ellipse([WX + 20 + i * 24, WY - BAR / 2 - 7, WX + 34 + i * 24, WY - BAR / 2 + 7], fill=c + (255,))
    ux0, ux1 = WX + 120, WX + CW - 120
    d.rounded_rectangle([ux0, WY - BAR + 9, ux1, WY - 9], 14, fill=(241, 245, 252, 255))
    f = F(MD, 18); d.text(((ux0 + ux1) / 2 + 10, WY - BAR / 2), URL, font=f, fill=SLATE, anchor='mm')
    tw = f.getlength(URL); lx = (ux0 + ux1) / 2 + 10 - tw / 2 - 22
    d.rounded_rectangle([lx - 6, WY - BAR / 2 - 3, lx + 6, WY - BAR / 2 + 7], 2, fill=(130, 140, 170, 255))
    d.arc([lx - 4, WY - BAR / 2 - 10, lx + 4, WY - BAR / 2 + 2], 180, 360, fill=(130, 140, 170, 255), width=2)
    return L
WIN = window_layer()
MASK = Image.new('L', (CW, CH), 0); ImageDraw.Draw(MASK).rounded_rectangle([0, -20, CW - 1, CH - 1], 15, fill=255)

# ---------- cursor sprite
def cursor_sprite(s=1.0, S=4):
    pts = [(0, 0), (0, 34), (8, 26), (14, 40), (20, 37), (14, 24), (25, 24)]
    im = Image.new('RGBA', (40 * S, 50 * S)); d = ImageDraw.Draw(im)
    P = [((x + 3) * S, (y + 3) * S) for x, y in pts]
    d.polygon(P, fill=(255, 255, 255, 255)); d.line(P + [P[0]], fill=(20, 20, 30, 255), width=int(2.2 * S), joint='curve')
    d.polygon([((x + 3) * S, (y + 3) * S) for x, y in [(2.2, 5), (2.2, 29), (8.6, 22.6), (14.8, 36.6), (17.6, 35.3), (11.4, 21.4), (19.6, 21.4)]], fill=(20, 20, 30, 255))
    im = im.resize((int(40 * s), int(50 * s)), Image.LANCZOS)
    shd = Image.new('RGBA', im.size); shd.putalpha(im.split()[3].point(lambda a: a * .35)); shd = shd.filter(ImageFilter.GaussianBlur(3))
    out = Image.new('RGBA', (im.width + 8, im.height + 8)); out.alpha_composite(shd, (4, 5)); out.alpha_composite(im, (0, 0))
    return out
CUR = cursor_sprite(1.05)

_img = {}
def cap(n):
    if n not in _img: _img[n] = Image.open((SD if n[0] in 'DE' else CAP) + n + '.png').convert('RGB')
    return _img[n]

# view: (cx, cy, z) in css viewport coords (1600x900); z=1 full
def view_rect(v):
    cx, cy, z = v; w, h = 1600 / z, 900 / z
    x0 = clamp(cx - w / 2, 0, 1600 - w); y0 = clamp(cy - h / 2, 0, 900 - h)
    return x0, y0, w, h
def to_scr(p, v):
    x0, y0, w, h = view_rect(v)
    return WX + (p[0] - x0) / w * CW, WY + (p[1] - y0) / h * CH
def box_scr(b, v, pad=0):
    a = to_scr((b[0] - pad, b[1] - pad), v); c = to_scr((b[2] + pad, b[3] + pad), v); return [a[0], a[1], c[0], c[1]]

def content(src, v):
    x0, y0, w, h = view_rect(v)
    im = cap(src).crop((int(x0 * 2), int(y0 * 2), int((x0 + w) * 2), int((y0 + h) * 2))).resize((CW, CH), Image.LANCZOS)
    return im

def hl_box(d, b, a, col=FLAG, r=14, wdt=5):
    if a <= 0: return
    d.rounded_rectangle(b, r, outline=A(col, a), width=wdt)
def ripple(L, p, k):
    if not (0 <= k <= 1): return
    d = ImageDraw.Draw(L); r = 10 + 46 * ease(k)
    d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], outline=A(ROYAL, (1 - k) * .9), width=5)
    d.ellipse([p[0] - r * .45, p[1] - r * .45, p[0] + r * .45, p[1] + r * .45], fill=A(ROYAL, (1 - k) * .25))
def tag(d, xy, txt, a, col=FLAG, anchor='lb', size=26):
    if a <= 0: return
    f = F(BD, size); tw = f.getlength(txt); x, y = xy; hgt = size + 22
    if anchor == 'lb': r = [x, y - hgt, x + tw + 36, y]
    elif anchor == 'lt': r = [x, y, x + tw + 36, y + hgt]
    elif anchor == 'rb': r = [x - tw - 36, y - hgt, x, y]
    else: r = [x - tw - 36, y, x, y + hgt]
    d.rounded_rectangle(r, hgt / 2, fill=A(col, a)); d.text(((r[0] + r[2]) / 2, (r[1] + r[3]) / 2), txt, font=f, fill=A(WHITE, a), anchor='mm')

def header(d, title, sub, a=1.0, step=None):
    d.text((60 + lg.width + 34, 58), title, font=F(XB, 44), fill=A(INK, a), anchor='lt')
    d.text((60 + lg.width + 36, 114), sub, font=F(SB, 24), fill=A(SLATE, a), anchor='lt')
    if step:
        n, txt = step; f = F(BD, 24); tw = f.getlength(txt)
        x1 = W - 60; x0 = x1 - tw - 96
        d.rounded_rectangle([x0, 66, x1, 118], 26, fill=A(WHITE, a), outline=A((214, 223, 242), a), width=2)
        d.ellipse([x0 + 8, 72, x0 + 48, 112], fill=A(ROYAL, a)); d.text((x0 + 28, 92), str(n), font=F(XB, 24), fill=A(WHITE, a), anchor='mm')
        d.text((x0 + 62, 92), txt, font=f, fill=A(INK, a), anchor='lm')

def compose(src, v, t_in=1.0, cursor=None, boxes=(), rip=None, tags=(), title=None, step=None, marker=None, white=0.0):
    fr = BG.copy()
    a = ease(t_in); dy = (1 - a) * 40
    L = Image.new('RGBA', (W, H)); L.alpha_composite(WIN)
    c = content(src, v).convert('RGBA'); c.putalpha(MASK); L.alpha_composite(c, (WX, WY))
    d = ImageDraw.Draw(L)
    if marker:  # subject text sweep (light yellow behind multiply)
        b, k = marker
        if k > 0:
            ov = Image.new('RGBA', (W, H)); od = ImageDraw.Draw(ov)
            x0, y0, x1, y1 = box_scr(b, v, 4); lines = max(1, round((b[3] - b[1]) / 26)); lh = (y1 - y0) / lines
            for i in range(lines):
                kk = clamp(k * lines - i)
                if kk > 0: od.rounded_rectangle([x0, y0 + i * lh + 2, x0 + (x1 - x0) * eio(kk), y0 + (i + 1) * lh - 2], 6, fill=(255, 214, 10, 90))
            L.alpha_composite(ov)
    for b, al, col in boxes: hl_box(d, b, al, col)
    for xy, txt, al, an in tags: tag(d, xy, txt, al, anchor=an)
    if rip: ripple(L, *rip)
    if cursor: L.alpha_composite(CUR, (int(cursor[0]) - 3, int(cursor[1]) - 3))
    if a < 1:
        L = L.resize((W, H)); al = L.split()[3].point(lambda p: int(p * a)); L.putalpha(al)
    fr.alpha_composite(L, (0, int(dy)))
    if title:
        hd = Image.new('RGBA', (W, H)); header(ImageDraw.Draw(hd), *title, a=1.0, step=step); fr.alpha_composite(hd)
    if white > 0:
        fr = Image.blend(fr, Image.new('RGBA', (W, H), (255, 255, 255, 255)), clamp(white))
    return fr.convert('RGB')

def mid(b): return ((b[0] + b[2]) / 2, (b[1] + b[3]) / 2)
FULL = (800, 450, 1.0)
chip, hdr, t2 = J['chip'], J['hdr'], J['t2']
btn, cor, card, txt = J['btn'], J['cor'], J['card'], J['text']['r']
ZC = ((card[0] + card[2]) / 2, (card[1] + card[3]) / 2 - 10, 1.22)
NB, ND = len(glob.glob(CAP + 'B*.png')), len(glob.glob(SD + 'D*.png'))
TITLE = ("Le sujet, directement sur la plateforme", "formation-tcfcanada.com  ·  " + EPL + "  ·  " + MOIS)
PARK = (1460, 840)
PARK2 = (1150, 760)

def cpath(t, pts):
    """pts: list of (t, (x,y)) css positions; eased interpolation"""
    if t <= pts[0][0]: return pts[0][1]
    for (t0, p0), (t1, p1) in zip(pts, pts[1:]):
        if t <= t1:
            k = eio((t - t0) / (t1 - t0)) if t1 > t0 else 1
            return (lerp(p0[0], p1[0], k), lerp(p0[1], p1[1], k))
    return pts[-1][1]

def intro_frame(t):
    T_IN = (t) / 0.6
    # source + view
    if t < 1.45: src = 'A0'
    elif t < 2.0: src = 'A1'
    elif t < 4.0: src = 'B%03d' % min(NB - 1, int((t - 2.0) / 2.0 * (NB - 1)))
    elif t < 4.75: src = 'B%03d' % (NB - 1)
    elif t < 5.0: src = 'C0'
    elif t < 6.0: src = 'C1'
    elif t < 7.2: src = 'C2'
    elif t < 8.7: src = 'D%03d' % min(ND - 1, int((t - 7.2) / 1.5 * (ND - 1)))
    elif t < 12.9: src = 'E0'
    else: src = 'E1'
    zk = eio((t - 8.9) / 1.1) * (1 - 0)
    v = (lerp(800, ZC[0], zk), lerp(450, ZC[1], zk), lerp(1.0, ZC[2], zk)) if t >= 8.9 else FULL
    if t > 13.5:  # push in on button for transition
        kk = eio((t - 13.5) / 0.75); bc = mid(btn)
        v = (lerp(v[0], bc[0], kk), lerp(v[1], bc[1], kk), lerp(v[2], 1.55, kk))
    cp = cpath(t, [(0.0, PARK), (0.5, PARK), (1.45, mid(chip)), (4.0, mid(chip)), (4.7, mid(hdr)), (5.3, mid(hdr)), (6.0, mid(t2)), (7.2, mid(t2)), (8.0, PARK), (8.9, PARK), (9.6, PARK2), (12.0, PARK2), (12.9, mid(btn))])
    cur = to_scr(cp, v)
    boxes = []; tags = []; rip = None; marker = None
    if 1.2 <= t < 3.2:
        al = clamp((t - 1.2) / .25) * clamp((3.2 - t) / .3)
        if t < 2.0: boxes.append((box_scr(chip, v, 5), al, FLAG)); tags.append(((box_scr(chip, v, 5)[0], box_scr(chip, v, 5)[1] - 10), f"{UNIT} {PT}", al, 'lb'))
    if 1.95 <= t < 2.6: rip = (cur, (t - 1.95) / .6)
    if 4.4 <= t < 6.0:
        al = clamp((t - 4.4) / .25) * clamp((6.0 - t) / .3); hb = box_scr(hdr, v, 5)
        boxes.append((hb, al, FLAG))
    if 4.85 <= t < 5.5: rip = (cur, (t - 4.85) / .6)
    if 5.8 <= t < 7.3:
        al = clamp((t - 5.8) / .25) * clamp((7.3 - t) / .3); tb = box_scr(t2, v, 4)
        boxes.append((tb, al, FLAG)); tags.append(((tb[2], tb[1] - 10), TLAB, al, 'rb'))
    if t >= 8.9:
        al = clamp((t - 9.6) / .3) * clamp((13.3 - t) / .3); cb = box_scr(card, v, 3)
        boxes.append((cb, al, FLAG)); tags.append(((cb[0], cb[1] - 10), (f"Tâche {SK} · Combinaison {PT}" if EE else f"Sujet n° {SK} · Partie {PT}"), al, 'lb'))
        marker = (txt, clamp((t - 10.2) / 1.6) * clamp((13.6 - t) / .3))
    if 12.6 <= t:
        al = clamp((t - 12.6) / .25); bb = box_scr(btn, v, 4)
        boxes.append((bb, al, GREEN))
    if 13.25 <= t < 13.9: rip = (cur, (t - 13.25) / .6)
    step = (1, "Choisir la combinaison" if EE else "Choisir la partie") if t < 4.4 else (2, "Ouvrir la tâche " + TACHE) if t < 8.7 else (3, "Lire le sujet") if t < 12.6 else (4, "Voir la correction" if EE else "Commencer la simulation")
    white = clamp((t - 13.75) / .45)
    return compose(src, v, T_IN, cur, boxes, rip, tags, TITLE, step, marker, white)

def outro_frame(t, D=6.5):
    v = ZC
    cp = cpath(t, [(0, PARK2), (0.7, PARK2), (1.6, mid(cor))])
    src = 'E2' if t > 1.5 else 'E0'
    cur = to_scr(cp, v)
    cb = box_scr(cor, v, 4); al = clamp((t - 1.4) / .3)
    boxes = [(cb, al, FLAG)]; tags = [((cb[2], cb[3] + 12), "Correction détaillée", al, 'rt')]
    rip = (cur, (t - 1.9) / .6) if 1.9 <= t < 2.5 else None
    fade = clamp(t / 0.6)
    tt = ("Retrouvez ce sujet et sa correction", f"formation-tcfcanada.com  ·  {EPL}  ·  {MOIS}  ·  {UNIT} {PT}")
    fr = compose(src, v, fade, cur, boxes, rip, tags, tt, (5, "Voir la correction"), (txt, 1.0), white=clamp((t - (D - 0.5)) / 0.5) * 0)
    return fr

def render(fn, dur, out):
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for i in range(int(round(dur * FPS))):
        p.stdin.write(fn(i / FPS).tobytes())
    p.stdin.close(); p.wait()

if __name__ == '__main__':
    if sys.argv[1] == 'still':
        for t in sys.argv[3:]:
            f = intro_frame if sys.argv[2] == 'i' else outro_frame
            f(float(t)).save(f'/home/claude/v24/prev_{sys.argv[2]}_{t}.png')
    else:
        W8 = os.environ.get('WARP')
        if W8:
            W8 = json.load(open(W8)); R, Sq = W8['real'], W8['seq']
            exec(open(os.environ.get('POPMOD', '/home/claude/v24/omni.py')).read())
            PI, PO = W8['pop_in'], W8['pop_out']
            fi = lambda t: overlay(intro_frame(float(np.interp(t, R, Sq))), t, PI, 470)
            fo = lambda t: overlay(outro_frame(t), t, PO, 470)
            if os.environ.get('STILL'):
                for tt in map(float, os.environ['STILL'].split(',')):
                    fi(tt).save(OUTK + f'pi_{tt}.png'); fo(tt).save(OUTK + f'po_{tt}.png')
                sys.exit()
            render(fi, R[-1], OUTK + 'site_intro.mp4')
            render(fo, W8['outro'], OUTK + 'site_outro.mp4')
        else:
            render(intro_frame, 14.2, OUTK + 'site_intro.mp4')
            render(outro_frame, 6.5, OUTK + 'site_outro.mp4')

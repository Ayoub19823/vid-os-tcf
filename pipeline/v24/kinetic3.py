import sys, json, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
W, H, FPS = 1920, 1080, 25
LOGO = '/tmp/claude-0/-home-claude/7a22c9af-0a80-57d2-89a2-1a32e1824476/scratchpad/v6/logo.png'
ROYAL = (24, 56, 255); SKY = (38, 169, 255); INK = (16, 22, 66); SLATE = (92, 106, 146); FLAG = (229, 30, 32)
GREEN = (22, 163, 74); WHITE = (255, 255, 255); GOLD = (255, 196, 0)
BL = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
XB = "/usr/share/fonts/opentype/inter/InterDisplay-ExtraBold.otf"
BD = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
SB = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
MD = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
_fc = {}
def F(p, s):
    k = (p, int(s))
    if k not in _fc: _fc[k] = ImageFont.truetype(p, max(1, int(s)))
    return _fc[k]
def clamp(v, a=0., b=1.): return max(a, min(b, v))
def eo(v): v = clamp(v); return 1 - (1 - v) ** 3
def eio(v): v = clamp(v); return 4 * v ** 3 if v < .5 else 1 - (-2 * v + 2) ** 3 / 2
def ob(v, c=1.6):
    v = clamp(v); return 1 + (c + 1) * (v - 1) ** 3 + c * (v - 1) ** 2
def A(c, a): return tuple(c[:3]) + (int(255 * clamp(a)),)

P = json.load(open(sys.argv[1])); T = P['t']; DUR = P['dur']; VOC = P['voc']; DIGIT = P.get('digit', '2'); EEM = P.get('mode') == 'EE'

# ---------- animated mesh-gradient background (computed at low res)
lw, lh = 192, 108
gy, gx = np.mgrid[0:lh, 0:lw].astype(np.float32)
base = np.array((247, 249, 255), np.float32)
BLOBS = [(ROYAL, 0.20, 46, (0.25, 0.30), (0.10, 0.07), 0.23), (SKY, 0.26, 52, (0.78, 0.35), (0.08, 0.10), 0.17),
         (FLAG, 0.07, 34, (0.62, 0.85), (0.12, 0.05), 0.29), (GOLD, 0.06, 30, (0.12, 0.85), (0.06, 0.08), 0.21)]
_noise = (np.random.default_rng(3).normal(0, 1, (H, W)) * 2.2).astype(np.float32)
def background(t):
    img = np.tile(base, (lh, lw, 1))
    for col, a, r, (cx, cy), (ax, ay), sp in BLOBS:
        x = (cx + ax * math.sin(t * sp * 2 * math.pi * 0.35 + cx * 7)) * lw; y = (cy + ay * math.cos(t * sp * 2 * math.pi * 0.3 + cy * 5)) * lh
        m = np.exp(-(((gx - x) ** 2 + (gy - y) ** 2) / (2 * r * r)))[..., None] * a
        img = img * (1 - m) + np.array(col, np.float32) * m
    big = np.array(Image.fromarray(img.clip(0, 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)).astype(np.float32)
    big += _noise[..., None]
    im = Image.fromarray(big.clip(0, 255).astype(np.uint8)).convert('RGBA')
    # fine grid with slow drift
    g = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(g); off = (t * 12) % 80
    for x in np.arange(-80 + off, W, 80): d.line([(x, 0), (x, H)], fill=(24, 56, 255, 10))
    for y in np.arange(-80 + off, H, 80): d.line([(0, y), (W, y)], fill=(24, 56, 255, 10))
    im.alpha_composite(g)
    return im

LG = Image.open(LOGO).convert('RGBA')
def logo(h):
    k = h / LG.height; return LG.resize((max(1, int(LG.width * k)), max(1, int(h))), Image.LANCZOS)

# ---------- kinetic text helpers
def text_rise(layer, xy, txt, font, col, t0, t, stagger=0.035, dur=0.55, anchor='ls', track=0, alpha=1.0):
    """per-letter rise from a mask below the baseline"""
    x, y = xy; d = ImageDraw.Draw(layer)
    widths = [font.getlength(ch) + track for ch in txt]; total = sum(widths) - track
    if anchor[0] == 'm': x -= total / 2
    elif anchor[0] == 'r': x -= total
    asc, desc = font.getmetrics()
    for i, ch in enumerate(txt):
        k = eo((t - t0 - i * stagger) / dur)
        if k <= 0: x += widths[i]; continue
        dy = (1 - k) * asc * 1.05
        tmp = Image.new('RGBA', (int(widths[i] + 40), asc + desc + 20)); td = ImageDraw.Draw(tmp)
        td.text((10, 10 + asc + dy), ch, font=font, fill=A(col, alpha * min(1, k * 1.4)), anchor='ls')
        layer.alpha_composite(tmp, (int(x - 10), int(y - asc - 10)))
        x += widths[i]
    return total

def slam(layer, center, txt, font, col, t0, t, from_scale=2.4, dur=0.45):
    """word slams in from depth with motion trail"""
    k = clamp((t - t0) / dur)
    if k <= 0: return
    tw = font.getlength(txt); asc, desc = font.getmetrics()
    base = Image.new('RGBA', (int(tw + 60), asc + desc + 40)); ImageDraw.Draw(base).text((30, 20), txt, font=font, fill=A(col, 1))
    for g, ga in ([(0.0, 1.0)] if k >= 1 else [(0.16, 0.18), (0.08, 0.35), (0.0, 1.0)]):
        kk = clamp(k - g); sc = 1 + (from_scale - 1) * (1 - eo(kk))
        im = base.resize((max(1, int(base.width * sc)), max(1, int(base.height * sc))), Image.BILINEAR)
        a = ga * clamp(kk * 2.5)
        if a < 1: im.putalpha(im.split()[3].point(lambda v: int(v * a)))
        layer.alpha_composite(im, (int(center[0] - im.width / 2), int(center[1] - im.height / 2)))

def stroke_line(d, p0, p1, k, col, w):
    if k <= 0: return
    x = p0[0] + (p1[0] - p0[0]) * eio(k); y = p0[1] + (p1[1] - p0[1]) * eio(k)
    d.line([p0, (x, y)], fill=col, width=w); d.ellipse([x - w / 2, y - w / 2, x + w / 2, y + w / 2], fill=col)

def ring(d, c, r, k, col, w, start=-90):
    if k <= 0: return
    d.arc([c[0] - r, c[1] - r, c[0] + r, c[1] + r], start, start + 360 * eio(k), fill=col, width=w)

def chip(layer, cx, cy, txt, a, sc=1.0):
    f = F(SB, 34 * sc); tw = f.getlength(txt); w_, h_ = tw + 56 * sc, 70 * sc
    g = Image.new('RGBA', (int(w_ + 60), int(h_ + 60))); gd = ImageDraw.Draw(g)
    gd.rounded_rectangle([30, 38, 30 + w_, 38 + h_], h_ / 2, fill=(20, 27, 77, int(40 * a)))
    g = g.filter(ImageFilter.GaussianBlur(12)); gd = ImageDraw.Draw(g)
    gd.rounded_rectangle([30, 30, 30 + w_, 30 + h_], h_ / 2, fill=(255, 255, 255, int(225 * a)), outline=A(SKY, a * 0.9), width=3)
    gd.ellipse([30 + 22 * sc, 30 + h_ / 2 - 7 * sc, 30 + 36 * sc, 30 + h_ / 2 + 7 * sc], fill=A(ROYAL, a))
    gd.text((30 + 46 * sc, 30 + h_ / 2), txt, font=f, fill=A(INK, a), anchor='lm')
    layer.alpha_composite(g, (int(cx - g.width / 2), int(cy - g.height / 2)))

# ---------- scenes
def scene_a(t):
    L = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(L)
    push = 1 + 0.03 * clamp(t / 6)
    # left block: greeting
    up = eio((t - T['simulation']) / 0.7)
    yb = 470 - 150 * up; sc = 1 - 0.32 * up
    text_rise(L, (150, yb), "Bonjour", F(BL, 170 * sc), INK, T['bonjour'], t, stagger=0.04)
    text_rise(L, (156, yb + 150 * sc), "et bienvenue", F(XB, 104 * sc), ROYAL, T['bienvenue'], t, stagger=0.03)
    # kicker
    kk = eo((t - T['simulation']) / 0.5)
    if kk > 0:
        f = F(BD, 28); txt = "EXERCICE CORRIGÉ" if EEM else "NOUVELLE SIMULATION"; tw = f.getlength(txt)
        x0 = 150; y0 = 470 + 40
        d.rounded_rectangle([x0, y0, x0 + (tw + 48) * kk, y0 + 54], 27, fill=A(FLAG, 1))
        if kk > 0.7: d.text((x0 + 24, y0 + 27), txt, font=f, fill=A(WHITE, (kk - 0.7) / 0.3), anchor='lm')
    # big "TÂCHE 2" with ring
    cx, cy = 1420, 470
    kr = clamp((t - T['tache']) / 0.8)
    if kr > 0:
        ring(d, (cx, cy + 10), 200, kr, A(ROYAL, 1), 16)
        for i in range(36):
            a = math.radians(i * 10 + t * 40)
            if (i * 10) / 360 <= eio(kr):
                r0, r1 = 236, 250 if i % 3 == 0 else 244
                d.line([(cx + r0 * math.cos(a), cy + r0 * math.sin(a)), (cx + r1 * math.cos(a), cy + r1 * math.sin(a))], fill=A(SKY, 0.8), width=3)
        text_rise(L, (cx, cy - 272), "TÂCHE", F(BD, 44), SLATE, T['tache'] + 0.1, t, anchor='ms', track=10)
    k2 = clamp((t - T['deux']) / 0.5)
    if k2 > 0:
        f = F(BL, 300); s2 = ob(k2, 2.0)
        im = Image.new('RGBA', (400, 400)); ImageDraw.Draw(im).text((200, 200), DIGIT, font=f, fill=A(ROYAL, 1), anchor='mm')
        im = im.resize((max(1, int(400 * s2)), max(1, int(400 * s2))), Image.BICUBIC)
        L.alpha_composite(im, (int(cx - im.width / 2), int(cy + 20 - im.height / 2)))
    # EXPRESSION ORALE with tracking collapse
    ke = eo((t - T['expression']) / 0.9)
    if ke > 0:
        f = F(BL, 74); trk = 40 * (1 - ke)
        text_rise(L, (150, 760), "EXPRESSION ÉCRITE" if EEM else "EXPRESSION ORALE", f, INK, T['expression'], t, stagger=0.025, track=trk)
        stroke_line(d, (152, 790), (152 + F(BL, 74).getlength("EXPRESSION ÉCRITE" if EEM else "EXPRESSION ORALE") - 4, 790), clamp((t - T['orale']) / 0.6), A(SKY, 1), 10)
    # TCF CANADA with red wipe
    kw = eio((t - T['tcf']) / 0.5)
    if kw > 0:
        f = F(BL, 74); txt = "TCF CANADA"; tw = f.getlength(txt) + 60
        d.rectangle([150, 830, 150 + tw * kw, 930], fill=A(FLAG, 1))
        if kw > 0.4:
            m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).rectangle([150, 830, 150 + tw * kw, 930], fill=255)
            tx = Image.new('RGBA', (W, H)); ImageDraw.Draw(tx).text((180, 880), txt, font=f, fill=A(WHITE, 1), anchor='lm')
            L.paste(tx, (0, 0), ImageChops.multiply(m, tx.split()[3]))
        kl = clamp((t - T['canada']) / 0.5)
        if kl > 0:
            lgi = logo(150 * ob(kl, 2.2)); L.alpha_composite(lgi, (int(150 + tw + 40), int(880 - lgi.height / 2)))
    if push != 1:
        L = L.resize((int(W * push), int(H * push)), Image.BILINEAR).crop((int((W * push - W) / 2), int((H * push - H) / 2), int((W * push - W) / 2) + W, int((H * push - H) / 2) + H))
    return L

def scene_b(t):
    L = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(L)
    # kicker "L'OBJECTIF"
    k = eo((t - T['objectif']) / 0.5)
    if k > 0:
        stroke_line(d, (150, 150), (230, 150), k, A(FLAG, 1), 8)
        text_rise(L, (250, 166), "L'OBJECTIF DE CES SIMULATIONS", F(BD, 38), FLAG, T['objectif'], t, stagger=0.015, track=3)
    move = eio((t - (T['themes'] - 0.6)) / 0.7)
    # headline: "vous montrer le très bon" / DÉROULEMENT / "de la tâche"
    hy = 330 - 75 * move; hs = 1 - 0.42 * move
    text_rise(L, (150, hy), "Vous montrer le très bon", F(XB, 66 * hs), SLATE, T['montrer'], t, stagger=0.02)
    text_rise(L, (146, hy + 190 * hs), "DÉROULEMENT", F(BL, 168 * hs), ROYAL, T['deroulement'], t, stagger=0.03)
    text_rise(L, (150, hy + 280 * hs), "de la tâche", F(XB, 66 * hs), INK, T['tache2'], t, stagger=0.02)
    # timeline drawing under headline (fades when move)
    if move < 1:
        a = 1 - move; y = 720; x0, x1 = 150, 1300
        kt = clamp((t - T['deroulement'] - 0.2) / 1.6)
        stroke_line(d, (x0, y), (x1, y), kt, A(SKY, a), 6)
        for i, lab in enumerate((["Lire la consigne", "Rédiger", "Corriger", "Améliorer"] if EEM else ["Donner son avis", "Argumenter", "Nuancer", "Conclure"] if DIGIT == "3" else ["Saluer", "Poser les questions", "Réagir", "Conclure"])):
            q = i / 3; kx = clamp((kt - q * 0.95) / 0.12)
            if kx > 0:
                x = x0 + (x1 - x0) * q; r = 18 * ob(kx, 2)
                d.ellipse([x - r, y - r, x + r, y + r], fill=A(WHITE, a), outline=A(ROYAL, a), width=6)
                d.text((x, y + 52), lab, font=F(SB, 30), fill=A(INK, a * kx), anchor='mm')
    # three words slam in
    if t > T['themes'] - 0.1:
        f = F(BL, 120); xs = 150
        for i, (key, word, col) in enumerate([('themes', "MÉTHODE" if EEM else "ARGUMENTS" if DIGIT == "3" else "THÈMES", ROYAL), ('sujets', "SUJETS", SKY), ('vocabulaire', "VOCABULAIRE", FLAG)]):
            cy = 540 + i * 150
            tw = f.getlength(word)
            slam(L, (xs + tw / 2, cy), word, f, col if i != 1 else INK, T[key], t)
            stroke_line(d, (xs, cy + 72), (xs + tw, cy + 72), clamp((t - T[key] - 0.25) / 0.45), A(col, 1), 10)
            if clamp((t - T[key]) / 0.3) > 0.5:
                d.text((xs - 30, cy + 8), "+", font=F(BL, 70), fill=A(col, clamp((t - T[key] - 0.15) / 0.3)), anchor='rm')
    # vocabulary chips floating on the right
    for i, w in enumerate(VOC):
        t0 = T['vocabulaire'] + 0.12 * i; kc = clamp((t - t0) / 0.5)
        if kc <= 0: continue
        cx = 1440 + 150 * math.sin(i * 2.1) + 18 * math.sin(t * 1.3 + i); cy = 400 + i * 115 + 10 * math.cos(t * 1.1 + i * 1.7)
        cy += (1 - eo(kc)) * 80
        chip(L, cx, cy, w, eo(kc), 0.9 + 0.15 * ob(kc))
    return L

def whip(a, b, k):
    """horizontal whip transition from layer a to layer b"""
    out = Image.new('RGBA', (W, H)); e = eio(k)
    for lay, off in ((a, -e * W * 1.1), (b, (1 - e) * W * 1.1)):
        blur = int(60 * math.sin(math.pi * k)) + 1
        l2 = lay.resize((max(1, W // blur), H), Image.BILINEAR).resize((W, H), Image.BILINEAR) if blur > 2 else lay
        out.alpha_composite(l2, (int(off), 0))
    return out

def frame(t):
    fr = background(t)
    tw0, tw1 = T['whip0'], T['whip0'] + 0.55
    if t < tw0: fr.alpha_composite(scene_a(t))
    elif t < tw1: fr.alpha_composite(whip(scene_a(t), scene_b(t), (t - tw0) / 0.55))
    else: fr.alpha_composite(scene_b(t))
    # corner logo + progress line
    lg = logo(70); fr.alpha_composite(lg, (60, 34))
    d = ImageDraw.Draw(fr); d.rectangle([0, H - 8, W * clamp(t / DUR), H], fill=A(ROYAL, 0.9))
    # exit: zoom blur to white
    ke = clamp((t - (DUR - 0.6)) / 0.6)
    out = fr.convert('RGB')
    if ke > 0:
        s = 1 + 0.25 * eio(ke); z = out.resize((int(W * s), int(H * s)), Image.BILINEAR)
        out = z.crop((int((z.width - W) / 2), int((z.height - H) / 2), int((z.width - W) / 2) + W, int((z.height - H) / 2) + H))
        out = Image.blend(out, Image.new('RGB', (W, H), (255, 255, 255)), eio(ke))
    return out

if __name__ == '__main__':
    if len(sys.argv) > 3:
        for tt in sys.argv[3].split(','): frame(float(tt)).save(sys.argv[2] + f'_{tt}.png')
    else:
        p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                              '-c:v', 'libx264', '-crf', '17', '-pix_fmt', 'yuv420p', sys.argv[2]], stdin=subprocess.PIPE)
        for i in range(int(round(DUR * FPS))): p.stdin.write(frame(i / FPS).tobytes())
        p.stdin.close(); p.wait()

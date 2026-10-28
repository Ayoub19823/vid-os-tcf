import os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
D = os.path.dirname(os.path.abspath(__file__))
_fcx, _fcy, _fr, LW, LH = map(float, open(f'{D}/lg/geom.txt').read().split())
LW, LH = int(LW), int(LH)
CCX, CCY = 905, 498          # circle centre in layer coords
FCX, FCY = _fcx, _fcy
SKY = (38, 169, 255)
_layers = {n: Image.open(f'{D}/lg/{n}.png').convert('RGBA') for n in ['circle', 'flag', 'tcf', 'canada', 'full']}
_cd = _layers['canada'].copy(); _cdA = _cd.getchannel('A'); _cd = Image.new('RGBA', _cd.size, (12, 12, 20, 255)); _cd.putalpha(_cdA); _layers['canada_dark'] = _cd
_fl = Image.new('RGBA', (LW, LH), (0, 0, 0, 0))
for _n in ['circle', 'flag', 'tcf', 'canada_dark']: _fl.alpha_composite(_layers[_n])
_layers['full_light'] = _fl
THEME = 'dark'
def nm(n):
    if THEME == 'light' and n in ('canada', 'full'): return {'canada': 'canada_dark', 'full': 'full_light'}[n]
    return n
_sq = Image.new('RGBA', (1010, 1010), (0, 0, 0, 0)); _sq.alpha_composite(_layers['circle'], (505 - CCX, 505 - CCY)); _layers['circsq'] = _sq
_cache = {}


def clamp(v, a=0.0, b=1.0): return max(a, min(b, v))
def ease(v): v = clamp(v); return v * v * (3 - 2 * v)
def oc(v): v = clamp(v); return 1 - (1 - v) ** 3
def ob(v):
    v = clamp(v); c = 1.8; return 1 + (c + 1) * (v - 1) ** 3 + c * (v - 1) ** 2


def layer(name, k):
    key = (name, round(k, 3))
    if key not in _cache:
        im = _layers[name]
        _cache[key] = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.LANCZOS)
        if len(_cache) > 60: _cache.pop(next(iter(_cache)))
    return _cache[key]


def with_alpha(im, a):
    if a >= 0.999: return im
    im = im.copy(); im.putalpha(im.getchannel('A').point(lambda v: int(v * clamp(a)))); return im


def static_logo(height, glow=True):
    k = height / LH
    im = layer(nm('full'), k).copy()
    if not glow: return im
    pad = int(height * 0.25)
    out = Image.new('RGBA', (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
    g = Image.new('RGBA', out.size, SKY + (0,)); al = Image.new('L', out.size, 0); al.paste(im.getchannel('A'), (pad, pad))
    g.putalpha(al.filter(ImageFilter.GaussianBlur(pad / 2.5)).point(lambda v: int(v * 0.55)))
    out.alpha_composite(g); out.alpha_composite(im, (pad, pad))
    return out


def paste_center(dst, im, cx, cy, rot=0.0):
    if rot: im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    dst.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))


rng = np.random.default_rng(11)
PART = [(rng.uniform(0, 2 * math.pi), rng.uniform(0.6, 1.6), rng.uniform(0, 0.5), rng.choice([0, 1])) for _ in range(70)]


def build(t, cx, cy, scale, canvas, speed=1.0, shine=True):
    """Animated assembly of the logo onto canvas (RGBA). t in seconds from start; scale = logo width factor."""
    t = t * speed
    W, H = canvas.size
    d = ImageDraw.Draw(canvas, 'RGBA')
    k = scale
    ox, oy = cx - LW * k / 2, cy - LH * k / 2          # top-left of logo box
    ccx, ccy = ox + CCX * k, oy + CCY * k
    fcx, fcy = ox + FCX * k, oy + FCY * k
    R = 500 * k
    # converging particles (0 - 0.9)
    for ang, sp, dl, c in PART:
        p = clamp((t - dl) / 0.7)
        if 0 < p < 1:
            r0 = R * (3.2 - 2.4 * oc(p)) * sp
            r1 = r0 + 60 * k * 3 * (1 - p)
            col = ((255, 255, 255) if THEME == 'dark' else (24, 56, 255)) if c else SKY
            a = int(255 * math.sin(p * math.pi))
            d.line([ccx + r0 * math.cos(ang), ccy + r0 * math.sin(ang), ccx + r1 * math.cos(ang), ccy + r1 * math.sin(ang)], fill=col + (a,), width=max(2, int(6 * k * 2)))
    # light rays behind circle (0.3 - 2.2)
    ra = clamp((t - 0.3) / 0.4) * (1 - clamp((t - 1.6) / 0.8))
    if ra > 0:
        rays = Image.new('RGBA', canvas.size, (0, 0, 0, 0)); rd = ImageDraw.Draw(rays)
        for i in range(16):
            a0 = i * 22.5 + t * 25
            a1 = a0 + 7
            rd.pieslice([ccx - R * 2.4, ccy - R * 2.4, ccx + R * 2.4, ccy + R * 2.4], a0, a1, fill=SKY + (int((70 if THEME == 'dark' else 45) * ra),))
        rays = rays.filter(ImageFilter.GaussianBlur(18 * k * 2 + 4))
        canvas.alpha_composite(rays)
    # glow halo
    ga = clamp((t - 0.5) / 0.6)
    if ga > 0:
        pulse = 1 + 0.06 * math.sin(t * 3)
        gr = R * 1.25 * pulse
        halo = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
        ImageDraw.Draw(halo).ellipse([ccx - gr, ccy - gr, ccx + gr, ccy + gr], fill=SKY + (int(110 * ga),))
        canvas.alpha_composite(halo.filter(ImageFilter.GaussianBlur(R * 0.35 + 4)))
    # circle: spin + scale in (0.15 - 0.95)
    pc = (t - 0.15) / 0.8
    if pc > 0:
        s = 0.15 + 0.85 * ob(pc)
        rot = -140 * (1 - oc(pc))
        im = with_alpha(layer('circsq', k * s), oc(pc * 1.6))
        if abs(rot) > 0.05: im = im.rotate(rot, resample=Image.BICUBIC)
        canvas.alpha_composite(im, (int(ccx - im.width / 2), int(ccy - im.height / 2)))
    # flash ring when circle lands
    fa = (t - 0.8) / 0.45
    if 0 < fa < 1:
        rr = R * (1.0 + 0.7 * oc(fa))
        d.ellipse([ccx - rr, ccy - rr, ccx + rr, ccy + rr], outline=((255, 255, 255) if THEME == 'dark' else (38, 169, 255)) + (int(220 * (1 - fa)),), width=max(2, int(14 * k * 2 * (1 - fa)) + 1))
    # flag pop (0.75 - 1.2)
    pf = (t - 0.75) / 0.45
    if pf > 0:
        s = ob(pf)
        im = with_alpha(layer('flag', k * s), oc(pf * 2))
        canvas.alpha_composite(im, (int(fcx - FCX * k * s), int(fcy - FCY * k * s)))
        if pf < 1:
            fl = Image.new('RGBA', canvas.size, (0, 0, 0, 0)); fr_ = _fr * k * (1 + 1.2 * oc(pf))
            ImageDraw.Draw(fl).ellipse([fcx - fr_, fcy - fr_, fcx + fr_, fcy + fr_], fill=(255, 255, 255, int(170 * (1 - pf))))
            canvas.alpha_composite(fl.filter(ImageFilter.GaussianBlur(20 * k + 3)))
    # tcf slide with motion trail (1.0 - 1.5)
    pt = (t - 1.0) / 0.5
    if pt > 0:
        base = layer('tcf', k)
        dx = -LW * k * 0.55 * (1 - oc(pt))
        if pt < 1:
            for gi in range(1, 5):
                gx = dx - gi * 40 * k * 2 * (1 - pt)
                canvas.alpha_composite(with_alpha(base, 0.18 * (1 - pt) * (5 - gi) / 4), (int(ox + gx), int(oy)))
        canvas.alpha_composite(with_alpha(base, oc(pt * 1.5)), (int(ox + dx), int(oy)))
    # CANADA wipe reveal (1.35 - 1.95)
    pw = (t - 1.35) / 0.6
    if pw > 0:
        base = layer(nm('canada'), k)
        x_rev = oc(pw) * base.width
        m = Image.new('L', base.size, 0); ImageDraw.Draw(m).rectangle([0, 0, x_rev, base.height], fill=255)
        im = base.copy(); im.putalpha(ImageChops.multiply(base.getchannel('A'), m))
        canvas.alpha_composite(im, (int(ox), int(oy)))
        if pw < 1:
            bx = ox + x_rev
            bar = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
            ImageDraw.Draw(bar).rectangle([bx - 6 * k * 2, oy + LH * k * 0.84, bx + 6 * k * 2, oy + LH * k * 1.0], fill=((255, 255, 255) if THEME == 'dark' else (38, 169, 255)) + (230,))
            canvas.alpha_composite(bar.filter(ImageFilter.GaussianBlur(8 * k + 2)))
    # shine sweep across the assembled logo (1.9 - 2.6)
    ps = (t - 1.9) / 0.7
    if shine and 0 < ps < 1:
        full = layer(nm('full'), k)
        band = Image.new('L', full.size, 0); bd = ImageDraw.Draw(band)
        x0 = -full.width * 0.4 + ps * full.width * 1.8
        bd.polygon([(x0, 0), (x0 + full.width * 0.18, 0), (x0 - full.height * 0.4 + full.width * 0.18, full.height), (x0 - full.height * 0.4, full.height)], fill=200)
        band = band.filter(ImageFilter.GaussianBlur(12 * k + 2))
        sh = Image.new('RGBA', full.size, (255, 255, 255, 0)); sh.putalpha(ImageChops.multiply(band, full.getchannel('A')))
        canvas.alpha_composite(sh, (int(ox), int(oy)))
    # sparkles burst (1.95 - 2.8)
    pb = (t - 1.95) / 0.85
    if 0 < pb < 1:
        for i, (ang, sp, dl, c) in enumerate(PART[:36]):
            r = R * (1.1 + 1.1 * oc(pb) * sp)
            x, y = ccx + r * math.cos(ang), ccy + r * math.sin(ang) * 0.9
            sz = max(2, 7 * k * 2 * (1 - pb))
            d.ellipse([x - sz, y - sz, x + sz, y + sz], fill=(((255, 255, 255) if THEME == 'dark' else (24, 56, 255)) if c else SKY) + (int(255 * (1 - pb)),))

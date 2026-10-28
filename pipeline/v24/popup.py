import math, numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
BL = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
GOLD = (255, 196, 0)
def ob(v):
    v = clamp(v); c = 1.7; return 1 + (c + 1) * (v - 1) ** 3 + c * (v - 1) ** 2
CWd, CHt = 1200, 270
URL = "formation-tcfcanada.com"
_lg = Image.open(LOGO).convert('RGBA'); _k = 128 / max(_lg.size); _lg = _lg.resize((int(_lg.width * _k), int(_lg.height * _k)), Image.LANCZOS)
def pcard(t, p):
    """t: time since pop-in; p: dict of relative times"""
    S = 2; c = Image.new('RGBA', (CWd * S, CHt * S)); d = ImageDraw.Draw(c)
    # gradient border
    g = Image.new('RGBA', c.size); gd = ImageDraw.Draw(g)
    for i in range(c.width):
        k = i / c.width; col = tuple(int(ROYAL[j] * (1 - k) + SKY[j] * k) for j in range(3))
        gd.line([(i, 0), (i, c.height)], fill=col + (255,))
    m = Image.new('L', c.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, c.width - 1, c.height - 1], 34 * S, fill=255)
    c.paste(g, (0, 0), m)
    d.rounded_rectangle([5 * S, 5 * S, c.width - 5 * S, c.height - 5 * S], 30 * S, fill=WHITE + (255,))
    # logo disc with pulse rings
    cx, cy = 140 * S, CHt * S // 2
    for r_i in range(2):
        ph = ((t * 0.9 + r_i * 0.5) % 1.0)
        rr = (78 + 46 * ph) * S
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=A(SKY, (1 - ph) * 0.55), width=4 * S)
    d.ellipse([cx - 82 * S, cy - 82 * S, cx + 82 * S, cy + 82 * S], fill=(236, 243, 255, 255), outline=A(ROYAL, 0.25), width=3 * S)
    lg = _lg.resize((_lg.width * S, _lg.height * S), Image.LANCZOS); c.alpha_composite(lg, (cx - lg.width // 2, cy - lg.height // 2))
    x0 = 268 * S
    # badge
    kb = clamp((t - p['badge']) / 0.35)
    if kb > 0:
        txt = "★  SEULE PLATEFORME OFFICIELLE"; f = F(BD, 25 * S); tw = f.getlength(txt); sc = ob(kb)
        bw, bh = (tw + 44 * S) * sc, 50 * S * sc; by = 40 * S
        d.rounded_rectangle([x0, by + (50 * S - bh) / 2, x0 + bw, by + (50 * S + bh) / 2], bh / 2, fill=A(FLAG, min(1, kb * 2)))
        if kb > 0.6: d.text((x0 + 22 * S, by + 25 * S), txt, font=f, fill=A(WHITE, (kb - 0.6) / 0.4), anchor='lm')
    # URL typewriter
    ku = clamp((t - p['url0']) / (p['url1'] - p['url0']))
    n = int(round(len(URL) * ku)); f = F(BL, 60 * S); uy = 128 * S
    shown = URL[:n]
    if n > 0:
        # two-tone: formation- / tcfcanada / .com
        parts = [("formation-", INK), ("tcfcanada", ROYAL), (".com", INK)]; x = x0; left = n
        for s, col in parts:
            seg = s[:max(0, left)]; left -= len(s)
            if seg: d.text((x, uy), seg, font=f, fill=col + (255,), anchor='lm'); x += f.getlength(seg)
        if ku < 1 or (t * 2) % 1 < 0.5:
            d.rectangle([x + 4 * S, uy - 34 * S, x + 10 * S, uy + 34 * S], fill=A(ROYAL, 0.9))
        # underline sweep
        ks = clamp((t - p['url1']) / 0.5)
        if ks > 0:
            full = f.getlength(URL); d.rounded_rectangle([x0, uy + 42 * S, x0 + full * eio(ks), uy + 50 * S], 4 * S, fill=A(SKY, 1))
    # operated by
    ko = clamp((t - p['pack']) / 0.4)
    if ko > 0:
        f2 = F(SB, 28 * S); y2 = 214 * S; dx = (1 - eio(ko)) * 30 * S
        t1 = "Opérée par"; d.text((x0 + dx, y2), t1, font=f2, fill=A(SLATE, ko), anchor='lm')
        px = x0 + dx + f2.getlength(t1) + 14 * S; f3 = F(XB, 28 * S); t2 = "PACK AYOUB"; pw = f3.getlength(t2) + 36 * S
        d.rounded_rectangle([px, y2 - 24 * S, px + pw, y2 + 24 * S], 24 * S, fill=A(GOLD, ko))
        d.text((px + pw / 2, y2), t2, font=f3, fill=A(INK, ko), anchor='mm')
    # shine sweep after URL typed
    kh = (t - p['url1'] - 0.3) / 0.9
    if 0 < kh < 1:
        sh = Image.new('L', c.size, 0); sd = ImageDraw.Draw(sh); sx = -200 * S + kh * (c.width + 400 * S)
        sd.polygon([(sx, 0), (sx + 90 * S, 0), (sx - 60 * S, c.height), (sx - 150 * S, c.height)], fill=110)
        sh = sh.filter(ImageFilter.GaussianBlur(8 * S)); sh = Image.composite(sh, Image.new('L', c.size, 0), m)
        wl = Image.new('RGBA', c.size, (255, 255, 255, 0)); wl.putalpha(sh); c.alpha_composite(wl)
    return c.resize((CWd, CHt), Image.LANCZOS)

def overlay(frame_rgb, t, p, cy):
    """p: abs times in: 'in','out','badge','url0','url1','pack'"""
    if t < p['in'] or t > p['out'] + 0.4: return frame_rgb
    ti = t - p['in']; rel = {k: v - p['in'] for k, v in p.items()}
    c = pcard(ti, rel)
    kin = clamp(ti / 0.45); kout = clamp((t - p['out']) / 0.4)
    sc = (0.55 + 0.45 * ob(kin)) * (1 - 0.25 * eio(kout)); al = clamp(kin * 3) * (1 - kout)
    cw, ch = int(CWd * sc), int(CHt * sc)
    c = c.resize((max(1, cw), max(1, ch)), Image.LANCZOS)
    fr = frame_rgb.convert('RGBA')
    shd = Image.new('RGBA', (W, H)); ImageDraw.Draw(shd).rounded_rectangle([W / 2 - cw / 2 + 6, cy - ch / 2 + 18, W / 2 + cw / 2 - 6, cy + ch / 2 + 22], 30, fill=(20, 27, 77, int(90 * al)))
    shd = shd.filter(ImageFilter.GaussianBlur(20)); fr.alpha_composite(shd)
    if al < 1: c.putalpha(c.split()[3].point(lambda v: int(v * al)))
    # sparkles at pop
    fr.alpha_composite(c, (int(W / 2 - cw / 2), int(cy - ch / 2 + (1 - eio(kin)) * 60)))
    if 0 < ti < 0.9:
        d = ImageDraw.Draw(fr)
        for i in range(14):
            a = i / 14 * 2 * math.pi + 0.3; rr = (CWd * 0.42) * eio(ti / 0.9) + 40
            px, py = W / 2 + math.cos(a) * rr, cy + math.sin(a) * rr * 0.42; s = 9 * (1 - ti / 0.9)
            col = [SKY, FLAG, GOLD, ROYAL][i % 4]
            d.polygon([(px, py - s), (px + s * 0.35, py), (px, py + s), (px - s * 0.35, py)], fill=A(col, 1 - ti / 0.9))
    return fr.convert('RGB')

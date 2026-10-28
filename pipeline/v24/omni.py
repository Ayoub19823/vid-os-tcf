import math
from PIL import Image, ImageDraw, ImageFilter
BL = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
GOLD = (255, 196, 0)
def ob(v):
    v = clamp(v); c = 1.7; return 1 + (c + 1) * (v - 1) ** 3 + c * (v - 1) ** 2
TYPED = "www.formation-tcfcanada.com"
OW, OH = 1240, 112          # omnibox
DW, DH = 1240, 198          # dropdown
_lgo = Image.open(LOGO).convert('RGBA'); _k = 92 / max(_lgo.size); _lgo = _lgo.resize((int(_lgo.width * _k), int(_lgo.height * _k)), Image.LANCZOS)
def magnifier(d, x, y, r, col, w):
    d.ellipse([x - r, y - r, x + r, y + r], outline=col, width=w); d.line([x + r * 0.7, y + r * 0.7, x + r * 1.6, y + r * 1.6], fill=col, width=w + 1)
def omni_layer(t, p):
    """returns RGBA (OW+40, OH+DH+60) graphic at local time t"""
    S = 2; L = Image.new('RGBA', ((OW + 40) * S, (OH + DH + 70) * S)); d = ImageDraw.Draw(L)
    ox, oy = 20 * S, 10 * S
    # omnibox pill
    d.rounded_rectangle([ox, oy, ox + OW * S, oy + OH * S], OH * S // 2, fill=WHITE + (255,), outline=ROYAL + (255,), width=5 * S)
    magnifier(d, ox + 62 * S, oy + OH * S / 2 - 6 * S, 17 * S, SLATE + (255,), 5 * S)
    ku = clamp((t - p['url0']) / (p['url1'] - p['url0'])); n = int(round(len(TYPED) * ku))
    f = F(BL, 52 * S); x = ox + 112 * S; y = oy + OH * S / 2
    parts = [("www.", SLATE), ("formation-", INK), ("tcfcanada", ROYAL), (".com", INK)]; left = n
    for s, col in parts:
        seg = s[:max(0, left)]; left -= len(s)
        if seg: d.text((x, y), seg, font=f, fill=col + (255,), anchor='lm'); x += f.getlength(seg)
    if n == 0:
        d.text((x, y), "Rechercher ou saisir une adresse", font=F(MD, 36 * S), fill=A(SLATE, 0.55), anchor='lm')
    if t < p['enter'] and ((t * 2.2) % 1 < 0.6 or ku < 1):
        d.rectangle([x + 5 * S, y - 32 * S, x + 10 * S, y + 32 * S], fill=ROYAL + (255,))
    # Enter key cap
    ke = clamp((t - p['enter'] + 0.05) / 0.25); press = 6 * S if 0 < ke < 1 else 0
    kx1 = ox + OW * S - 30 * S; kx0 = kx1 - 150 * S; ky0 = oy + 24 * S + press; ky1 = oy + OH * S - 24 * S + press
    kc = GREEN if ke > 0 else (226, 232, 245)
    d.rounded_rectangle([kx0, ky0 + 6 * S - press, kx1, ky1 + 6 * S - press], 14 * S, fill=A((150, 160, 190) if ke <= 0 else (12, 120, 52), 1))
    d.rounded_rectangle([kx0, ky0, kx1, ky1], 14 * S, fill=kc + (255,))
    d.text(((kx0 + kx1) / 2, (ky0 + ky1) / 2), "Entrée ↵", font=F(BD, 28 * S), fill=(WHITE if ke > 0 else INK) + (255,), anchor='mm')
    # dropdown
    kd = clamp((t - p['drop']) / 0.35)
    if kd > 0:
        dy0 = oy + OH * S + 14 * S; hh = DH * S * eio(kd)
        m = Image.new('L', L.size, 0); ImageDraw.Draw(m).rectangle([0, dy0, L.width, dy0 + hh], fill=255)
        D = Image.new('RGBA', L.size); dd = ImageDraw.Draw(D)
        dd.rounded_rectangle([ox, dy0, ox + OW * S, dy0 + DH * S], 28 * S, fill=WHITE + (255,), outline=(214, 223, 242, 255), width=3 * S)
        rx0, ry0 = ox + 16 * S, dy0 + 16 * S
        dd.rounded_rectangle([rx0, ry0, ox + OW * S - 16 * S, ry0 + 96 * S], 20 * S, fill=(236, 243, 255, 255))
        lg = _lgo.resize((_lgo.width * S * 76 // 92, _lgo.height * S * 76 // 92), Image.LANCZOS); D.alpha_composite(lg, (int(rx0 + 20 * S), int(ry0 + 48 * S - lg.height / 2)))
        dd.text((rx0 + 120 * S, ry0 + 30 * S), "formation-tcfcanada.com", font=F(XB, 36 * S), fill=INK + (255,), anchor='lm')
        dd.text((rx0 + 120 * S, ry0 + 70 * S), "Préparation au TCF Canada · Simulations · Corrections", font=F(MD, 26 * S), fill=SLATE + (255,), anchor='lm')
        by = ry0 + 140 * S; bx = rx0 + 20 * S
        kb = clamp((t - p['badge']) / 0.35)
        if kb > 0:
            txt = "★  SEULE PLATEFORME OFFICIELLE"; fb = F(BD, 28 * S); tw = fb.getlength(txt); sc = ob(kb)
            w_, h_ = (tw + 48 * S) * sc, 56 * S * sc
            dd.rounded_rectangle([bx, by - h_ / 2, bx + w_, by + h_ / 2], h_ / 2, fill=A(FLAG, min(1, kb * 2)))
            if kb > 0.6: dd.text((bx + 24 * S, by), txt, font=fb, fill=A(WHITE, (kb - 0.6) / 0.4), anchor='lm')
            bx += (tw + 48 * S) + 22 * S
        ko = clamp((t - p['pack']) / 0.35)
        if ko > 0:
            fo = F(SB, 30 * S); t1 = "Opérée par"; dxo = (1 - eio(ko)) * 30 * S
            dd.text((bx + dxo, by), t1, font=fo, fill=A(SLATE, ko), anchor='lm')
            px = bx + dxo + fo.getlength(t1) + 14 * S; f3 = F(XB, 30 * S); t2 = "PACK AYOUB"; pw = f3.getlength(t2) + 40 * S
            dd.rounded_rectangle([px, by - 28 * S, px + pw, by + 28 * S], 28 * S, fill=A(GOLD, ko)); dd.text((px + pw / 2, by), t2, font=f3, fill=A(INK, ko), anchor='mm')
        L.paste(D, (0, 0), Image.composite(D.split()[3], Image.new('L', L.size, 0), m))
    # shine on the pill after typing
    kh = (t - p['url1'] - 0.2) / 0.8
    if 0 < kh < 1:
        sh = Image.new('L', L.size, 0); sd = ImageDraw.Draw(sh); sx = ox - 200 * S + kh * (OW * S + 400 * S)
        sd.polygon([(sx, oy), (sx + 80 * S, oy), (sx - 40 * S, oy + OH * S), (sx - 120 * S, oy + OH * S)], fill=120)
        pm = Image.new('L', L.size, 0); ImageDraw.Draw(pm).rounded_rectangle([ox, oy, ox + OW * S, oy + OH * S], OH * S // 2, fill=255)
        sh = Image.composite(sh.filter(ImageFilter.GaussianBlur(8 * S)), Image.new('L', L.size, 0), pm)
        wl = Image.new('RGBA', L.size, (255, 255, 255, 0)); wl.putalpha(sh); L.alpha_composite(wl)
    return L.resize((OW + 40, OH + DH + 70), Image.LANCZOS)

def overlay(frame_rgb, t, p, cy):
    if t < p['in'] or t > p['out'] + 0.45: return frame_rgb
    ti = t - p['in']; rel = {k: v - p['in'] for k, v in p.items()}
    G = omni_layer(ti, rel)
    fr = frame_rgb.convert('RGBA')
    # dim background slightly
    kin = clamp(ti / 0.5); kout = clamp((t - p['out']) / 0.45)
    dim = 0.28 * eio(kin) * (1 - kout)
    fr = Image.blend(fr, Image.new('RGBA', fr.size, (20, 27, 77, 255)), dim)
    # grow out of the browser address bar
    ax, ay = WX + CW / 2, WY - BAR / 2
    tx, ty = W / 2, cy
    k = eio(kin) * (1 - eio(kout))
    sc = 0.22 + 0.78 * (ob(kin) if kout == 0 else 1) * (1 - kout * 0.78 / 0.78 * eio(kout))
    sc = max(0.05, sc)
    cxp, cyp = ax + (tx - ax) * k, ay + (ty - ay) * k
    gw, gh = int(G.width * sc), int(G.height * sc)
    G2 = G.resize((max(1, gw), max(1, gh)), Image.LANCZOS)
    al = clamp(kin * 3) * (1 - kout)
    if al < 1: G2.putalpha(G2.split()[3].point(lambda v: int(v * al)))
    top = cyp - (OH / 2 + 10) * sc
    shd = Image.new('RGBA', fr.size); ImageDraw.Draw(shd).rounded_rectangle([cxp - gw / 2 + 20, top + 20, cxp + gw / 2 - 20, top + gh - 10], 40, fill=(20, 27, 77, int(70 * al)))
    fr.alpha_composite(shd.filter(ImageFilter.GaussianBlur(24)))
    fr.alpha_composite(G2, (int(cxp - gw / 2), int(top)))
    # ripple on the real address bar at start
    if ti < 0.6:
        d = ImageDraw.Draw(fr); r = 10 + 60 * eio(ti / 0.6)
        d.ellipse([ax - r * 3, ay - r * 0.6, ax + r * 3, ay + r * 0.6], outline=A(ROYAL, 1 - ti / 0.6), width=4)
    return fr.convert('RGB')

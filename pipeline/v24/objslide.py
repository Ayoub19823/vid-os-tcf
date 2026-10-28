import sys, json, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W, H, FPS = 1920, 1080, 25
LOGO = '/tmp/claude-0/-home-claude/7a22c9af-0a80-57d2-89a2-1a32e1824476/scratchpad/v6/logo.png'
ROYAL = (24, 56, 255); SKY = (38, 169, 255); INK = (20, 27, 77); SLATE = (92, 106, 146); FLAG = (229, 30, 32)
GREEN = (22, 163, 74); WHITE = (255, 255, 255); GOLD = (255, 196, 0); ORANGE = (234, 120, 10)
BL = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
XB = "/usr/share/fonts/opentype/inter/InterDisplay-ExtraBold.otf"
BD = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
SB = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
MD = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
EF = ImageFont.truetype('/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf', 109)
_fc = {}
def F(p, s):
    k = (p, int(s))
    if k not in _fc: _fc[k] = ImageFont.truetype(p, int(s))
    return _fc[k]
def clamp(v, a=0., b=1.): return max(a, min(b, v))
def eio(v): v = clamp(v); return 4 * v ** 3 if v < .5 else 1 - (-2 * v + 2) ** 3 / 2
def ob(v):
    v = clamp(v); c = 1.7; return 1 + (c + 1) * (v - 1) ** 3 + c * (v - 1) ** 2
def A(c, a): return tuple(c[:3]) + (int(255 * clamp(a)),)
def emoji(e, s):
    im = Image.new('RGBA', (140, 140)); ImageDraw.Draw(im).text((70, 70), e, font=EF, embedded_color=True, anchor='mm')
    im = im.crop(im.getbbox()); k = s / max(im.size); return im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)

yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
td = np.clip((xx / W) * .6 + (yy / H) * .4, 0, 1)[..., None]
bg = (np.array((255, 255, 255), np.float32) * (1 - td) + np.array((236, 243, 255), np.float32) * td)
bg = np.where(((xx % 34 < 2.2) & (yy % 34 < 2.2))[..., None], bg * .93, bg)
BG = Image.fromarray(bg.astype(np.uint8)).convert('RGBA')
lg = Image.open(LOGO).convert('RGBA'); k = 74 / lg.height; lgs = lg.resize((int(lg.width * k), 74), Image.LANCZOS)
BG.alpha_composite(lgs, (60, 38))
LG_BIG = lg.resize((int(lg.width * 230 / lg.height), 230), Image.LANCZOS)

P = json.load(open(sys.argv[1]))        # timings
SUB = P.get('sub', "Sujet réel · Octobre 2026 · Partie 14")
CARDS = [("🎯", "Le bon déroulement", "de la tâche 2", P['c1']), ("🗂️", "Les thèmes", "et les sujets réels", P['c2']), ("📚", "Le vocabulaire", "à utiliser", P['c3'])]
DUR = P['dur']

def frame(t):
    fr = BG.copy(); d = ImageDraw.Draw(fr)
    # ---- phase A: title (until P['b0'])
    kA_out = eio((t - P['b0']) / 0.6)
    if kA_out < 1:
        a = 1 - kA_out
        k1 = eio(t / 0.6); sc = 0.7 + 0.3 * ob(clamp(t / 0.7))
        L = LG_BIG.resize((max(1, int(LG_BIG.width * sc)), max(1, int(LG_BIG.height * sc))), Image.LANCZOS)
        if a < 1 or k1 < 1: L.putalpha(L.split()[3].point(lambda v: int(v * a * k1)))
        fr.alpha_composite(L, (int(W / 2 - L.width / 2), int(300 - L.height / 2 - kA_out * 80)))
        y0 = 500 - kA_out * 80
        k2 = eio((t - 0.35) / 0.5)
        f = F(BD, 26); txt = "SIMULATION MODÈLE"; tw = f.getlength(txt)
        d.rounded_rectangle([W / 2 - tw / 2 - 24, y0 - 22 + (1 - k2) * 30, W / 2 + tw / 2 + 24, y0 + 26 + (1 - k2) * 30], 24, fill=A(FLAG, k2 * a))
        d.text((W / 2, y0 + 2 + (1 - k2) * 30), txt, font=f, fill=A(WHITE, k2 * a), anchor='mm')
        k3 = eio((t - 0.6) / 0.6)
        d.text((W / 2, y0 + 110 + (1 - k3) * 40), "Expression orale · Tâche 2", font=F(BL, 92), fill=A(INK, k3 * a), anchor='mm')
        k4 = eio((t - 0.9) / 0.6)
        d.text((W / 2, y0 + 210 + (1 - k4) * 40), "TCF CANADA", font=F(BL, 64), fill=A(ROYAL, k4 * a), anchor='mm')
        k5 = eio((t - 1.3) / 0.6)
        d.text((W / 2, y0 + 290 + (1 - k5) * 30), SUB, font=F(SB, 32), fill=A(SLATE, k5 * a), anchor='mm')
    # ---- phase B: objective
    if t >= P['b0']:
        tb = t - P['b0']; kt = eio(tb / 0.6)
        d.text((W / 2, 175 + (1 - kt) * 40), "Pourquoi ces simulations ?", font=F(BL, 76), fill=A(INK, kt), anchor='mm')
        # underline sweep
        uw = 520 * eio((tb - 0.3) / 0.6)
        if uw > 0: d.rounded_rectangle([W / 2 - uw / 2, 228, W / 2 + uw / 2, 238], 5, fill=A(SKY, 1))
        cw, ch, gap = 500, 330, 50; x0 = W / 2 - (3 * cw + 2 * gap) / 2; cy = 470
        for i, (em, l1, l2, tc) in enumerate(CARDS):
            kc = clamp((t - tc) / 0.5)
            if kc <= 0: continue
            sc = 0.6 + 0.4 * ob(kc); cx = x0 + i * (cw + gap) + cw / 2
            w_, h_ = cw * sc, ch * sc
            sh = Image.new('RGBA', (W, H)); ImageDraw.Draw(sh).rounded_rectangle([cx - w_ / 2 + 10, cy - h_ / 2 + 22, cx + w_ / 2 - 10, cy + h_ / 2 + 22], 30, fill=(20, 27, 77, int(60 * kc)))
            fr.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18))); d = ImageDraw.Draw(fr)
            col = [ROYAL, SKY, GREEN][i]
            d.rounded_rectangle([cx - w_ / 2, cy - h_ / 2, cx + w_ / 2, cy + h_ / 2], 30, fill=A(WHITE, min(1, kc * 2)), outline=A(col, min(1, kc * 2)), width=4)
            d.rounded_rectangle([cx - w_ / 2, cy - h_ / 2, cx + w_ / 2, cy - h_ / 2 + 12 * sc], 6, fill=A(col, min(1, kc * 2)))
            if kc > 0.35:
                aa = clamp((kc - 0.35) / 0.65)
                e = emoji(em, 110 * sc); e.putalpha(e.split()[3].point(lambda v: int(v * aa)))
                fr.alpha_composite(e, (int(cx - e.width / 2), int(cy - 70 * sc - e.height / 2))); d = ImageDraw.Draw(fr)
                d.text((cx, cy + 60 * sc), l1, font=F(XB, 42 * sc), fill=A(INK, aa), anchor='mm')
                d.text((cx, cy + 112 * sc), l2, font=F(SB, 32 * sc), fill=A(SLATE, aa), anchor='mm')
            # check badge
            kk = clamp((t - tc - 0.5) / 0.3)
            if kk > 0:
                r = 26 * ob(kk); bx, by = cx + w_ / 2 - 30, cy - h_ / 2 + 30
                d.ellipse([bx - r, by - r, bx + r, by + r], fill=A(GREEN, 1))
                d.line([(bx - r * 0.45, by), (bx - r * 0.1, by + r * 0.35), (bx + r * 0.5, by - r * 0.35)], fill=WHITE + (255,), width=max(2, int(6 * kk)), joint='curve')
        # niveau soutenu gauge
        ks = clamp((t - P['sout']) / 0.6)
        if ks > 0:
            gy = 800; gw = 1200; gx0 = W / 2 - gw / 2; dy = (1 - eio(ks)) * 40
            d.rounded_rectangle([gx0 - 30, gy - 60 + dy, gx0 + gw + 30, gy + 150 + dy], 34, fill=A(WHITE, ks), outline=A((214, 223, 242), ks), width=3)
            d.text((gx0 + 10, gy - 18 + dy), "Niveau de langue utilisé", font=F(BD, 34), fill=A(INK, ks), anchor='lm')
            # bar
            by0 = gy + 40 + dy; d.rounded_rectangle([gx0 + 10, by0, gx0 + gw - 10, by0 + 26], 13, fill=A((228, 234, 246), ks))
            kf = eio((t - P['sout'] - 0.3) / 1.2); fw = (gw - 20) * 0.9 * kf
            if fw > 26:
                for i in range(int(fw)):
                    q = i / (gw - 20); col = tuple(int(SKY[j] * (1 - q) + ROYAL[j] * q) for j in range(3))
                    d.line([(gx0 + 10 + i, by0 + 3), (gx0 + 10 + i, by0 + 23)], fill=col + (int(255 * ks),))
            labs = [("Familier", 0.12), ("Courant", 0.5), ("Soutenu", 0.88)]
            for name, q in labs:
                lx = gx0 + 10 + (gw - 20) * q; on = name == "Soutenu" and kf > 0.95
                d.text((lx, by0 + 66), name, font=F(XB if on else SB, 32 if on else 28), fill=A(ROYAL if on else SLATE, ks), anchor='mm')
            kp = clamp((t - P['sout'] - 1.4) / 0.4)
            if kp > 0:
                lx = gx0 + 10 + (gw - 20) * 0.9; sc = ob(kp)
                d.ellipse([lx - 22 * sc, by0 + 13 - 22 * sc, lx + 22 * sc, by0 + 13 + 22 * sc], fill=A(WHITE, 1), outline=A(ROYAL, 1), width=6)
                txt = "SOUTENU"; f = F(BL, 30); tw = f.getlength(txt)
                d.rounded_rectangle([gx0 + gw - tw - 70, gy - 42 + dy, gx0 + gw + 6, gy + 6 + dy], 24, fill=A(ROYAL, kp))
                d.text((gx0 + gw - tw / 2 - 32, gy - 18 + dy), txt, font=f, fill=A(WHITE, kp), anchor='mm')
    # fade to white at end
    kw = clamp((t - (DUR - 0.45)) / 0.45)
    out = fr.convert('RGB')
    if kw > 0: out = Image.blend(out, Image.new('RGB', (W, H), (255, 255, 255)), kw)
    return out

if __name__ == '__main__':
    if len(sys.argv) > 3:
        for tt in sys.argv[3].split(','): frame(float(tt)).save(sys.argv[2] + f'_{tt}.png')
    else:
        p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                              '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', sys.argv[2]], stdin=subprocess.PIPE)
        for i in range(int(round(DUR * FPS))): p.stdin.write(frame(i / FPS).tobytes())
        p.stdin.close(); p.wait()

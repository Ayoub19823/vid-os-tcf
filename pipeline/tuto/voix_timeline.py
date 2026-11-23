"""Tutoriel v2 « Examen blanc d'expression orale avec Ahlem et Emmanuel » (accroche + grille stricte).
usage : python3 tuto2.py <voix.wav (11 segments)> <sortie.mp4> [instants d'aperçu, séparés par des virgules]"""
import sys, os, json, subprocess, wave, math, re
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
V6 = '/tmp/claude-0/-home-claude/7a22c9af-0a80-57d2-89a2-1a32e1824476/scratchpad/v6'
EX = '/tmp/claude-0/-home-claude/01538168-a956-5f77-b6bb-db6feebb7757/scratchpad/exo/'
WK = '/home/claude/work/exo/'
sys.path.insert(0, V6); sys.path.insert(0, '/home/claude/t3')
import logoanim
from logoanim import static_logo
from segs import rd, robust, SR
AUD, OUTV = sys.argv[1], sys.argv[2]
ONLY = [float(v) for v in sys.argv[3].split(',')] if len(sys.argv) > 3 else None
W, H, FPS = 1920, 1080, 25
ROYAL = (24, 56, 255); SKY = (38, 169, 255); INK = (20, 27, 77); SLATE = (92, 106, 146); FLAG = (229, 30, 32)
GREEN = (22, 163, 74); ORANGE = (234, 120, 10); WHITE = (255, 255, 255); LINEC = (214, 224, 246); YEL = (255, 214, 64)
AMB = (180, 83, 9); AMBBG = (255, 250, 232); AMBL = (250, 215, 120); TINT = (232, 240, 255)
FD = "/usr/share/fonts/opentype/inter/"
BL, XB, BD, SB, MD = [FD + f for f in ("InterDisplay-Black.otf", "InterDisplay-ExtraBold.otf", "Inter-Bold.otf", "Inter-SemiBold.otf", "Inter-Medium.otf")]
_fc = {}
def F(p, s):
    k = (p, int(s))
    if k not in _fc: _fc[k] = ImageFont.truetype(p, int(s))
    return _fc[k]
def clamp(v, a=0., b=1.): return max(a, min(b, v))
def ease(v): v = clamp(v); return v * v * (3 - 2 * v)
def A(c, a): return tuple(c[:3]) + (int(255 * clamp(a)),)
def lerp(a, b, k): return a + (b - a) * k
def fit(p, s, txt, mw, mn=16):
    f = F(p, s)
    while f.getlength(txt) > mw and f.size > mn: f = F(p, f.size - 1)
    return f

TXT = ["TCF Canada et TCF Québec : douze minutes, seul, face à un examinateur. Et si vous viviez cet examen avant le jour J ? Restez jusqu'à la fin : vous allez voir comment réserver, comment se passe la séance, et ce que vous recevez après.",
       "L'examen blanc d'expression orale, c'est une séance individuelle d'environ quarante minutes, en visio sur Zoom, avec un examinateur habilité : Ahlem ou Emmanuel. Vous passez deux simulations complètes des trois tâches, avec un retour personnalisé après chacune. Attention : ce n'est pas un cours, c'est une simulation. L'examinateur se comporte exactement comme le jour de l'examen.",
       "Cette séance est idéale si vous passez le TCF Canada ou le TCF Québec dans les prochaines semaines, si vous n'avez jamais parlé face à un examinateur, ou si vous voulez savoir précisément ce qui vous coûte des points à l'oral.",
       "Première étape : choisir l'offre. Sur le site, ouvrez la page Tarifs. Dans la rubrique « Nos nouveautés », vous trouvez l'examen blanc d'expression orale. Le prix est de vingt dollars américains pour la séance complète, avec les deux examens blancs. Cliquez sur le bouton « Réserver mon examen oral ».",
       "Deuxième étape : choisir votre créneau. Les heures s'affichent automatiquement dans votre fuseau horaire, celui de votre téléphone ou de votre ordinateur. Dans le calendrier, chaque jour indique le nombre de créneaux disponibles. Cliquez sur un jour : les heures libres apparaissent, avec le nom de l'examinateur. Choisissez l'heure et l'examinateur qui vous conviennent, vérifiez le récapitulatif, puis cliquez sur « Continuer ».",
       "Troisième étape : le paiement. Connectez-vous à votre compte, puis réglez en ligne. Votre créneau est retenu pendant le paiement, et il vous est réservé dès que le paiement est validé. Le jour de la séance, il vous suffit de rejoindre la visioconférence Zoom à l'heure prévue.",
       "Voici comment se passe la séance. D'abord, un premier examen blanc d'environ douze minutes : l'examinateur pose les questions, tient son rôle et chronomètre, sans vous aider. Ensuite, un feedback personnalisé. Puis un deuxième examen blanc, avec de nouveaux sujets, pour appliquer les conseils reçus. Et enfin, un feedback final sur vos progrès.",
       "Chaque examen blanc reprend exactement le format officiel. Tâche un : l'entretien dirigé, environ deux minutes, sans préparation. Tâche deux : l'interaction, environ trois minutes trente, avec deux minutes de préparation. Tâche trois : l'expression d'un point de vue, environ quatre minutes trente, sans préparation.",
       "Après chaque simulation, l'examinateur revient sur votre performance : vos points forts, vos erreurs principales, et les conseils à appliquer immédiatement. Vous savez exactement quoi corriger avant le jour J.",
       "Avant votre séance, quatre réflexes : une bonne connexion Internet, un casque ou des écouteurs, une pièce calme, et connectez-vous cinq minutes en avance.",
       "Réservez votre examen blanc d'expression orale dès maintenant, sur formation-tcfcanada.com. Et le jour J, vous aurez déjà vécu l'examen."]
NS = len(TXT)
# ---------- voix : segments -> piste avec respirations + chronologie
x = rd(AUD); sg = robust(x, NS); assert len(sg) == NS, len(sg)
CL = [x[max(0, a - int(0.03 * SR)):b + int(0.2 * SR)] for a, b in sg]
y = rd(os.environ['PATCH']); s2 = robust(y, 2); assert len(s2) == 2, len(s2)
y = y * (np.abs(x).max() / np.abs(y).max())
for k, (a, b) in zip((0, 3), s2): CL[k] = y[max(0, a - int(0.03 * SR)):b + int(0.2 * SR)]
HOLD = [0.5, 0.8, 0.7, 0.9, 1.1, 0.9, 1.0, 1.0, 1.2, 1.0, 2.8]
parts = [np.zeros(int(0.25 * SR))]; t = 0.25; T0 = []; VD = []
for c, h in zip(CL, HOLD):
    T0.append(t); VD.append(len(c) / SR); parts += [c, np.zeros(int(h * SR))]; t += len(c) / SR + h
T0.append(t); TOTAL = t; VO = np.concatenate(parts)
SEG = []
def _sent(i):
    """débuts de phrases (s) dans le segment i, d'après les plus longs silences internes"""
    c = CL[i]
    st = [m.end() for m in re.finditer(r'[.?!] ', TXT[i])]; n = len(st)
    w = int(0.02 * SR); env = np.array([np.abs(c[k:k + w]).max() for k in range(0, len(c) - w, w)]); sil = env < 0.02 * np.abs(c).max()
    runs = []; k = 0
    while k < len(sil):
        if sil[k]:
            j = k
            while j < len(sil) and sil[j]: j += 1
            if k > 5 and j < len(sil) - 12: runs.append((j - k, k, j))
            k = j
        else: k += 1
    runs = sorted(sorted(runs, reverse=True)[:n], key=lambda r: r[1])
    if len(runs) < n: return None
    return [0] + st, [0.] + [r[2] * 0.02 for r in runs] + [len(c) / SR]
for i in range(NS): SEG.append(_sent(i))
print('phrases', [None if q is None else [round(v, 1) for v in q[1]] for q in SEG])
def cue(i, w, lead=0.12):
    p = TXT[i].find(w); assert p >= 0, w
    if SEG[i] is None: return max(0., VD[i] * p / len(TXT[i]) - lead)
    cs, ts = SEG[i]; k = max(j for j in range(len(cs)) if cs[j] <= p); c1 = cs[k + 1] if k + 1 < len(cs) else len(TXT[i])
    return max(0., ts[k] + (ts[k + 1] - ts[k] - 0.25) * (p - cs[k]) / max(1, c1 - cs[k]) - lead)
# ---------- ressources
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
td = np.clip((xx / W) * .6 + (yy / H) * .4, 0, 1)[..., None]
bg = (np.array((250, 251, 255), np.float32) * (1 - td) + np.array((232, 240, 255), np.float32) * td)
PLAIN = Image.fromarray(bg.astype(np.uint8)).convert('RGB')
tn = np.clip(xx / W * 0.55 + yy / H * 0.45, 0, 1)[..., None]
nb = np.array((34, 66, 222), np.float32) * (1 - tn) + np.array((10, 20, 96), np.float32) * tn
gl = np.clip(1 - np.sqrt((xx - W / 2) ** 2 + (yy - 430) ** 2) / 900, 0, 1)[..., None] ** 1.8; nb = nb + gl * np.array((30, 44, 60), np.float32)
NAVY = Image.fromarray(np.clip(nb, 0, 255).astype(np.uint8)).convert('RGB')
_o = Image.new('RGBA', (W, H)); _d = ImageDraw.Draw(_o)
for i in range(-10, 40): _d.line([(i * 90, 0), (i * 90 - 600, H)], fill=(255, 255, 255, 9), width=2)
NAVY.paste(_o, (0, 0), _o)
logoanim.THEME = 'light'; LG = static_logo(80); LGB = static_logo(120)
try:
    logoanim.THEME = 'dark'; LGD = static_logo(130, glow=True)
except Exception as e:
    print('logo dark', e); LGD = static_logo(130)
logoanim.THEME = 'light'
def circle(im, d):
    im = im.resize((d * 2, d * 2), Image.LANCZOS); m = Image.new('L', (d * 2, d * 2), 0); ImageDraw.Draw(m).ellipse([0, 0, d * 2 - 1, d * 2 - 1], fill=255)
    im = im.convert('RGBA'); im.putalpha(m); return im.resize((d, d), Image.LANCZOS)
_as = Image.open(EX + 'ahlem_still.png').convert('RGB'); _es = Image.open(EX + 'emmanuel_still.png').convert('RGB')
FA = _as.crop((190, 90, 530, 430)); FE = _es.crop((230, 80, 570, 420))
CAP = {k: Image.open(EX + k + '.png').convert('RGB') for k in ('c_tarifs', 'c_res0', 'c_res1', 'c_res2')}
J = json.load(open(EX + 'J.json'))
for k in ('c_res1', 'c_res2'):      # vraies photos des examinateurs à la place des initiales
    for s in J['slots']:
        if s['r'][1] > 700: continue
        a = [v * 1.5 for v in s['a']]; dd = int(a[2] - a[0]); c = circle(FA if 'AHLEM' in s['t'] else FE, dd); CAP[k].paste(c, (int(a[0]), int(a[1])), c)
for cx_, fc_ in ((336, FE), (662, FA)): c = circle(fc_, 84); CAP['c_tarifs'].paste(c, (int(cx_ * 1.5), int(451 * 1.5)), c)
c = circle(FE, 72); CAP['c_res2'].paste(c, (int(441 * 1.5), int(809 * 1.5)), c)
def frames(path):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-vf', 'fps=25,scale=1280:720', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
    n = len(r) // (1280 * 720 * 3); return [Image.frombuffer('RGB', (1280, 720), r[i * 1280 * 720 * 3:(i + 1) * 1280 * 720 * 3]) for i in range(n)]
CLA = frames(WK + 'ahlem.mp4'); CLE = frames(WK + 'emmanuel.mp4')

# ---------- grille : marges 96, 4 colonnes de 414 (gouttière 24)
ML, MR = 96, 1824; GUT = 24; CW4 = 414
def col4(i, span=1): x0 = ML + i * (CW4 + GUT); return x0, x0 + span * CW4 + (span - 1) * GUT
def card(d, b, col=None, a=1.0, r=26, fill=WHITE, w=3):
    x0, y0, x1, y1 = [int(round(v)) for v in b]
    d.rounded_rectangle([x0, y0 + 8, x1, y1 + 8], radius=r, fill=(20, 40, 120, int(16 * a)))
    d.rounded_rectangle([x0, y0, x1, y1], radius=r, fill=A(fill, a), outline=A(col or LINEC, a), width=w)
def num(d, cx, cy, n, col, a, r=34):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=A(col, a)); d.text((cx, cy), str(n), font=F(BL, int(r * 1.1)), fill=A(WHITE, a), anchor='mm')
def check(d, cx, cy, col, a, r=34):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=A(col, a)); k = r / 34
    d.line([cx - 15 * k, cy + 1 * k, cx - 4 * k, cy + 12 * k, cx + 16 * k, cy - 11 * k], fill=A(WHITE, a), width=max(4, int(7 * k)), joint='curve')
def header(fr, step, title):
    d = ImageDraw.Draw(fr, 'RGBA'); fr.paste(LG, (ML - 56, 12), LG)
    d.text((ML + 106, 48), "Examen blanc d'expression orale", font=F(BL, 42), fill=INK, anchor='lm')
    d.text((ML + 108, 96), "Avec un examinateur habilité · formation-tcfcanada.com", font=F(MD, 22), fill=SLATE, anchor='lm')
    if title:
        f = F(BD, 28); tw = int(f.getlength(title)) + (108 if step else 56); x1 = MR
        d.rounded_rectangle([x1 - tw, 40, x1, 104], radius=32, fill=A(ROYAL, 1))
        if step: d.ellipse([x1 - tw + 10, 50, x1 - tw + 54, 94], fill=WHITE); d.text((x1 - tw + 32, 72), str(step), font=F(BL, 26), fill=ROYAL, anchor='mm')
        d.text((x1 - 28, 72), title, font=f, fill=WHITE, anchor='rm')
def caption(fr, txt, a=1.0):
    if a <= 0: return
    d = ImageDraw.Draw(fr, 'RGBA'); f = fit(BD, 34, txt, 1560); tw = int(f.getlength(txt)) + 72
    d.rounded_rectangle([W // 2 - tw // 2, 986, W // 2 + tw // 2, 1054], radius=34, fill=A(INK, 0.94 * a)); d.text((W // 2, 1020), txt, font=f, fill=A(WHITE, a), anchor='mm')
BX0, BY0, BW, BH = ML, 160, MR - ML, 800
def kf(u, keys):
    """keys : [(t, zoom, cx, cy)] ; interpolation douce sur 0,9 s avant chaque clé"""
    z, cx, cy = keys[0][1:]
    for (tk, z1, x1, y1) in keys[1:]:
        k = ease((u - tk + 0.2) / 0.9); z, cx, cy = lerp(z, z1, k), lerp(cx, x1, k), lerp(cy, y1, k)
    return z, cx, cy
def browser(fr, shot, zoom=1.0, cx=0.5, cy=0.5, box=None, hl=0.0, url="formation-tcfcanada.com"):
    d = ImageDraw.Draw(fr, 'RGBA')
    d.rounded_rectangle([BX0, BY0 + 10, BX0 + BW, BY0 + BH + 10], radius=22, fill=(20, 40, 120, 28))
    d.rounded_rectangle([BX0, BY0, BX0 + BW, BY0 + BH], radius=20, fill=WHITE, outline=LINEC, width=2)
    d.rounded_rectangle([BX0, BY0, BX0 + BW, BY0 + 46], radius=20, fill=(238, 243, 252)); d.rectangle([BX0 + 2, BY0 + 26, BX0 + BW - 2, BY0 + 46], fill=(238, 243, 252))
    for i, c in enumerate(((255, 95, 86), (255, 189, 46), (39, 201, 63))): d.ellipse([BX0 + 22 + i * 24, BY0 + 16, BX0 + 36 + i * 24, BY0 + 30], fill=c)
    d.rounded_rectangle([BX0 + 140, BY0 + 9, BX0 + BW - 140, BY0 + 37], radius=14, fill=WHITE); d.text((BX0 + BW // 2, BY0 + 23), url, font=F(MD, 17), fill=SLATE, anchor='mm')
    vw, vh = BW - 4, BH - 48; sw, sh = shot.size; cw = sw / zoom; ch = cw * vh / vw
    x0 = clamp(cx * sw - cw / 2, 0, sw - cw); y0 = clamp(cy * sh - ch / 2, 0, sh - ch)
    v = shot.resize((vw, vh), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))
    m = Image.new('L', (vw, vh), 0); ImageDraw.Draw(m).rounded_rectangle([0, -30, vw - 1, vh - 1], radius=18, fill=255); fr.paste(v, (BX0 + 2, BY0 + 46), m)
    if box and hl > 0:
        k = vw / cw; ox, oy = BX0 + 2, BY0 + 46
        b = [ox + (box[0] * 1.5 - x0) * k, oy + (box[1] * 1.5 - y0) * k, ox + (box[2] * 1.5 - x0) * k, oy + (box[3] * 1.5 - y0) * k]
        g = 10 + 5 * math.sin(hl * 8); d = ImageDraw.Draw(fr, 'RGBA'); al = min(1, hl * 3)
        bb = [max(ox + 4, b[0] - g), max(oy + 4, b[1] - g), min(ox + vw - 4, b[2] + g), min(oy + vh - 4, b[3] + g)]
        d.rounded_rectangle(bb, radius=16, outline=A(FLAG, al), width=6)

# ---------- accroche (fond sombre)
_dk = {}
def dark_clip(cl, idx, key):
    idx = min(len(cl) - 1, max(0, idx)); k = (key, idx)
    if k not in _dk:
        if len(_dk) > 6: _dk.clear()
        im = cl[idx].resize((W, H), Image.BILINEAR); _dk[k] = Image.blend(im, Image.new('RGB', (W, H), (8, 16, 70)), 0.60)
    return _dk[k].copy()
def big(d, y, txt, font, col, a, dy=22):
    if a <= 0: return
    yy_ = int(y + (1 - a) * dy); d.text((W // 2 + 4, yy_ + 5), txt, font=font, fill=(4, 8, 40, int(150 * a)), anchor='mm'); d.text((W // 2, yy_), txt, font=font, fill=A(col, a), anchor='mm')
def s0(fr, u, D):
    cC, cD = cue(0, "Et si"), cue(0, "Restez"); CLIP = 2.8
    if u < CLIP + 0.4: base = Image.blend(CLA[min(len(CLA) - 1, int(u * 25))].resize((W, H), Image.BILINEAR), Image.new('RGB', (W, H), (8, 16, 70)), 0.45)
    else: base = NAVY.copy()
    if CLIP <= u < CLIP + 0.4: base = Image.blend(base, NAVY, ease((u - CLIP) / 0.4))
    fr.paste(base); d = ImageDraw.Draw(fr, 'RGBA')
    if u < cC:
        a = ease(u / 0.2); big(d, 330, "TCF CANADA & TCF QUÉBEC", F(BL, 124), YEL, a)
        a2 = ease((u - cue(0, "douze")) / 0.3); s = max(0, 720 - max(0, u - cue(0, "douze"))); tx = f"{int(s) // 60}:{int(s) % 60:02d}"
        if a2 > 0:
            f = F(BL, 60); tw = int(f.getlength("12:00")) + 120; d.rounded_rectangle([W // 2 - tw // 2, 470, W // 2 + tw // 2, 570], radius=50, fill=A(FLAG, a2))
            d.ellipse([W // 2 - tw // 2 + 30, 508, W // 2 - tw // 2 + 54, 532], fill=A(WHITE, a2 * (0.55 + 0.45 * math.sin(u * 7)))); d.text((W // 2 + 24, 520), tx, font=f, fill=A(WHITE, a2), anchor='mm')
        big(d, 690, "12 minutes, seul,", F(BL, 100), WHITE, a2); big(d, 810, "face à un examinateur.", F(BL, 100), WHITE, ease((u - cue(0, "face à")) / 0.3))
    elif u < cD:
        v = u - cC; big(d, 400, "Et si vous viviez cet examen", F(BL, 92), WHITE, ease(v / 0.35))
        big(d, 570, "AVANT le jour J ?", F(BL, 150), YEL, ease((v - 0.9) / 0.35))
    else:
        v = u - cD; a = ease(v / 0.35); t1 = "EXAMEN BLANC D'EXPRESSION ORALE"; f = F(BD, 34); tw = int(f.getlength(t1)) + 80
        d.rounded_rectangle([W // 2 - tw // 2, 196, W // 2 + tw // 2, 264], radius=34, fill=A(FLAG, a)); d.text((W // 2, 230), t1, font=f, fill=A(WHITE, a), anchor='mm')
        big(d, 370, "Dans cette vidéo", F(BL, 96), WHITE, a)
        its = [("Comment réserver", "L'offre, le créneau, le paiement", "comment réserver"), ("Comment se passe la séance", "2 examens blancs, étape par étape", "comment se passe"), ("Ce que vous recevez", "Un feedback personnalisé", "ce que vous")]
        cw = 560;
        for i, (t1, t2, w) in enumerate(its):
            ai = a * (0.38 + 0.62 * ease((u - cue(0, w)) / 0.4))
            x0 = ML + i * (cw + GUT); y0 = 500
            d.rounded_rectangle([x0, y0, x0 + cw, y0 + 300], radius=28, fill=(255, 255, 255, int(28 * ai)), outline=A(WHITE, 0.85 * ai), width=3)
            num(d, x0 + 280, y0 + 76, i + 1, YEL, ai, r=40); d.text((x0 + 280, y0 + 76), str(i + 1), font=F(BL, 44), fill=A(INK, ai), anchor='mm')
            d.text((x0 + 280, y0 + 176), t1, font=fit(BL, 40, t1, cw - 50), fill=A(WHITE, ai), anchor='mm'); d.text((x0 + 280, y0 + 236), t2, font=fit(MD, 26, t2, cw - 50), fill=A((205, 218, 255), ai), anchor='mm')
        big(d, 900, "Restez jusqu'à la fin", F(XB, 44), YEL, ease((v - 0.5) / 0.4), dy=0)

def s1(fr, u, D):     # c'est quoi
    header(fr, None, "C'est quoi ?"); d = ImageDraw.Draw(fr, 'RGBA')
    tiles = [("2", "examens blancs", "complets", "deux simulations"), ("3", "tâches", "par examen", "trois tâches"), ("≈ 40", "minutes", "séance individuelle", "séance individuelle"), ("Zoom", "en visio", "depuis chez vous", "en visio")]
    for i, (bigt, t1, t2, w) in enumerate(tiles):
        a = ease((u - cue(1, w)) / 0.4)
        if a <= 0: continue
        x0, x1 = col4(i); y0 = 180 + int((1 - a) * 18); card(d, [x0, y0, x1, y0 + 230], ROYAL, a)
        d.text((x0 + 36, y0 + 82), bigt, font=fit(BL, 96, bigt, 340), fill=A(ROYAL, a), anchor='lm')
        d.text((x0 + 36, y0 + 158), t1, font=F(BL, 34), fill=A(INK, a), anchor='lm'); d.text((x0 + 36, y0 + 198), t2, font=F(MD, 24), fill=A(SLATE, a), anchor='lm')
    a = ease((u - cue(1, "avec un examinateur")) / 0.4)
    if a > 0:
        x0, x1 = col4(0, 2); y0 = 440; card(d, [x0, y0, x1, 950], LINEC, a, w=2)
        d.text((x0 + 40, y0 + 52), "VOS EXAMINATEURS", font=F(BD, 24), fill=A(ROYAL, a), anchor='lm')
        for i, (nm, role, face, w) in enumerate((("AHLEM", "Examinatrice habilitée", FA, "Ahlem"), ("EMMANUEL", "Examinateur habilité", FE, "Emmanuel"))):
            ai = ease((u - cue(1, w)) / 0.4)
            if ai <= 0: continue
            cx_ = x0 + 213 + i * 426; c = circle(face, 210); c.putalpha(c.getchannel('A').point(lambda v: int(v * ai))); fr.paste(c, (cx_ - 105, y0 + 96), c)
            d.ellipse([cx_ - 108, y0 + 93, cx_ + 108, y0 + 309], outline=A(ROYAL, ai), width=4)
            d.text((cx_, y0 + 350), nm, font=F(BL, 40), fill=A(INK, ai), anchor='mm'); d.text((cx_, y0 + 394), role, font=F(MD, 24), fill=A(SLATE, ai), anchor='mm')
        d.rounded_rectangle([x0 + 40, y0 + 432, x1 - 40, y0 + 484], radius=26, fill=A(TINT, a)); d.text(((x0 + x1) // 2, y0 + 458), "Vous choisissez votre examinateur au moment de réserver", font=fit(SB, 24, "Vous choisissez votre examinateur au moment de réserver", x1 - x0 - 130), fill=A(ROYAL, a), anchor='mm')
    x0, x1 = col4(2, 2)
    a = ease((u - cue(1, "avec un retour")) / 0.4)
    if a > 0:
        card(d, [x0, 440, x1, 610], GREEN, a); check(d, x0 + 78, 525, GREEN, a, r=38)
        d.text((x0 + 140, 500), "Un retour personnalisé", font=F(BL, 38), fill=A(INK, a), anchor='lm'); d.text((x0 + 140, 552), "Après chacune des deux simulations", font=F(MD, 26), fill=A(SLATE, a), anchor='lm')
    a = ease((u - cue(1, "Attention")) / 0.4)
    if a > 0:
        card(d, [x0, 634, x1, 950], AMBL, a, fill=AMBBG)
        d.text((x0 + 40, 700), "Ce n'est pas un cours.", font=F(BL, 44), fill=A(AMB, a), anchor='lm'); d.text((x0 + 40, 758), "C'est une simulation.", font=F(BL, 44), fill=A(AMB, a), anchor='lm')
        a2 = ease((u - cue(1, "L'examinateur se")) / 0.4)
        d.text((x0 + 40, 846), "L'examinateur se comporte exactement", font=F(SB, 28), fill=A(INK, a2), anchor='lm'); d.text((x0 + 40, 888), "comme le jour de l'examen.", font=F(SB, 28), fill=A(INK, a2), anchor='lm')

def rows(d, u, items, y0, h, gap, col_fn):
    for i, (t1, t2, at) in enumerate(items):
        a = ease((u - at) / 0.4)
        if a <= 0: continue
        y = y0 + i * (h + gap) + int((1 - a) * 18); col = col_fn(i); card(d, [ML, y, MR, y + h], col, a)
        check(d, ML + 90, y + h // 2, col, a, r=40)
        d.text((ML + 170, y + h // 2 - 28), t1, font=fit(BL, 44, t1, 1500), fill=A(INK, a), anchor='lm'); d.text((ML + 170, y + h // 2 + 30), t2, font=fit(MD, 28, t2, 1500), fill=A(SLATE, a), anchor='lm')
def s2(fr, u, D):     # pour qui
    header(fr, None, "Pour qui ?"); d = ImageDraw.Draw(fr, 'RGBA')
    d.text((ML, 222), "Cette séance est idéale si…", font=F(BL, 60), fill=INK, anchor='lm')
    rows(d, u, [("Vous passez le TCF Canada ou le TCF Québec bientôt", "Dans les prochaines semaines : c'est le moment de vous tester.", cue(2, "si vous passez")),
                ("Vous n'avez jamais parlé face à un examinateur", "Vous vivez le stress du jour J avant, sans l'enjeu.", cue(2, "si vous n'avez")),
                ("Vous voulez savoir ce qui vous coûte des points à l'oral", "Un avis humain, précis, sur votre performance.", cue(2, "ou si vous"))], 290, 202, 27, lambda i: GREEN)

def s3(fr, u, D):     # étape 1 : l'offre
    header(fr, 1, "Choisir l'offre"); c1, c2, c3, c4 = cue(3, "Dans la rubrique"), cue(3, "vous trouvez"), cue(3, "Le prix"), cue(3, "Cliquez sur le bouton")
    z, cx, cy = kf(u, [(0, 1.0, 0.5, 0.42), (c2, 1.25, 0.5, 0.48), (c3, 1.25, 0.5, 0.56), (c4, 1.25, 0.5, 0.56)])
    if u < c1: box, hl, cap = None, 0, "Sur formation-tcfcanada.com, ouvrez la page « Tarifs »"
    elif u < c2: box, hl, cap = [560, 100, 1040, 172], u - c1, "Rubrique « Nos nouveautés »"
    elif u < c3: box, hl, cap = [288, 188, 1312, 697], u - c2 - 0.4, "Examen blanc d'expression orale · avec Emmanuel ou Ahlem · en visio sur Zoom"
    elif u < c4: box, hl, cap = [312, 566, 775, 662], u - c3 - 0.5, "$20.00 USD la séance : 2 examens blancs, 3 tâches par examen, ≈ 40 minutes"
    else: box, hl, cap = [932, 620, 1280, 666], u - c4 - 0.4, "Cliquez sur « Réserver mon examen oral — $20.00 USD »"
    browser(fr, CAP['c_tarifs'], z, cx, cy, box, hl, url="formation-tcfcanada.com/tarification"); caption(fr, cap)

def s4(fr, u, D):     # étape 2 : le créneau
    header(fr, 2, "Choisir votre créneau")
    c1, c2, c3, c4, c5, c6, c7 = [cue(4, w) for w in ("Les heures s'affichent", "Dans le calendrier", "Cliquez sur un jour", "les heures libres", "Choisissez l'heure", "vérifiez", "puis cliquez")]
    z, cx, cy = kf(u, [(0, 1.0, 0.5, 0.58), (c1, 1.3, 0.5, 0.46), (c2, 1.4, 0.42, 0.58), (c4, 1.4, 0.58, 0.60), (c6, 1.3, 0.5, 0.70)])
    shot = CAP['c_res0']
    if u < c1: box, hl, cap = None, 0, "Page « Réserver mon créneau »"
    elif u < c2: box, hl, cap = [441, 197, 1159, 303], u - c1 - 0.5, "Les heures s'affichent dans votre fuseau horaire (téléphone ou ordinateur)"
    elif u < c3: box, hl, cap = [441, 512, 832, 740], u - c2 - 0.5, "Chaque jour indique le nombre de créneaux disponibles"
    elif u < c4: box, hl, cap = J['day'], u - c3, "Cliquez sur le jour qui vous convient"; shot = CAP['c_res0' if u < c3 + 0.9 else 'c_res1']
    elif u < c5: shot, box, hl, cap = CAP['c_res1'], [874, 372, 1161, 722], u - c4 - 0.3, "Les heures libres apparaissent avec le nom de l'examinateur · 40 min par séance"
    elif u < c6: shot, box, hl, cap = CAP['c_res2'], J['slots'][2]['r'], u - c5, "Choisissez l'heure et l'examinateur qui vous conviennent"
    elif u < c7: shot, box, hl, cap = CAP['c_res2'], [441, 792, 900, 872], u - c6 - 0.5, "Vérifiez le récapitulatif : date, heure, examinateur, prix"
    else: shot, box, hl, cap = CAP['c_res2'], [930, 813, 1159, 853], u - c7, "Cliquez sur « Continuer — $20.00 USD »"
    browser(fr, shot, z, cx, cy, box, hl, url="formation-tcfcanada.com/examen-oral/reserver"); caption(fr, cap)

def grid2(d, u, items, col_fn, mark):
    xs = [(ML, ML + 852), (ML + 876, MR)]; ys = [(180, 553), (577, 950)]
    for i, (t1, t2, t3, at) in enumerate(items):
        a = ease((u - at) / 0.4)
        if a <= 0: continue
        (x0, x1), (y0, y1) = xs[i % 2], ys[i // 2]; o = int((1 - a) * 18); col = col_fn(i); card(d, [x0, y0 + o, x1, y1 + o], col, a)
        if mark == 'num': num(d, x0 + 96, y0 + 104 + o, i + 1, col, a, r=48)
        else: check(d, x0 + 96, y0 + 104 + o, col, a, r=48)
        d.text((x0 + 48, y0 + 216 + o), t1, font=fit(BL, 46, t1, 756), fill=A(INK, a), anchor='lm')
        d.text((x0 + 48, y0 + 276 + o), t2, font=fit(MD, 28, t2, 756), fill=A(SLATE, a), anchor='lm')
        if t3: d.text((x0 + 48, y0 + 318 + o), t3, font=fit(MD, 28, t3, 756), fill=A(SLATE, a), anchor='lm')
def s5(fr, u, D):     # étape 3 : paiement
    header(fr, 3, "Payer et rejoindre la séance"); d = ImageDraw.Draw(fr, 'RGBA')
    grid2(d, u, [("Connectez-vous à votre compte", "Il faut être connecté pour finaliser", "votre réservation.", cue(5, "Connectez-vous")),
                 ("Réglez en ligne : $20.00 USD", "Paiement sécurisé, directement sur le site.", "", cue(5, "puis réglez")),
                 ("Votre créneau vous est réservé", "Retenu pendant le paiement,", "réservé dès que le paiement est validé.", cue(5, "Votre créneau")),
                 ("Le jour J : rejoignez Zoom", "Connectez-vous à la visioconférence", "à l'heure prévue.", cue(5, "Le jour de la séance"))], lambda i: (ROYAL, ROYAL, GREEN, FLAG)[i], 'num')

def inset(fr, cl, idx, b, lab, a=1.0, who=""):
    x0, y0, x1, y1 = b; w = x1 - x0; h = int(w * 9 / 16); d = ImageDraw.Draw(fr, 'RGBA'); card(d, [x0, y0, x1, y1], LINEC, 1, w=2)
    f = cl[min(len(cl) - 1, max(0, idx))].resize((w - 6, h), Image.BILINEAR)
    m = Image.new('L', (w - 6, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 7, h + 40], radius=23, fill=255); fr.paste(f, (x0 + 3, y0 + 3), m); d = ImageDraw.Draw(fr, 'RGBA')
    fl = F(BD, 24); tw = int(fl.getlength(lab)) + 44
    d.rounded_rectangle([x0 + 24, y0 + 24, x0 + 24 + tw, y0 + 72], radius=24, fill=A(FLAG, a)); d.text((x0 + 24 + tw // 2, y0 + 48), lab, font=fl, fill=A(WHITE, a), anchor='mm')
    yb = (y0 + h + y1) // 2
    d.text((x0 + 40, yb - 16), who, font=F(BL, 30), fill=INK, anchor='lm'); d.text((x0 + 40, yb + 24), "Illustration générée par IA · déroulement d'une séance", font=F(MD, 21), fill=SLATE, anchor='lm')
def s6(fr, u, D):     # déroulement
    header(fr, None, "Le déroulement · ≈ 40 minutes"); d = ImageDraw.Draw(fr, 'RGBA')
    cs = [cue(6, "D'abord"), cue(6, "Ensuite"), cue(6, "Puis un deuxième"), cue(6, "Et enfin")]
    cur = max([k for k in range(4) if u >= cs[k]] or [-1])
    steps = [("Examen blanc n° 1", "≈ 12 minutes", ROYAL), ("Feedback", "personnalisé", GREEN), ("Examen blanc n° 2", "≈ 12 minutes", ROYAL), ("Feedback final", "progrès et axes de travail", GREEN)]
    for i, (t1, t2, col) in enumerate(steps):
        a = ease((u - 0.3 - i * 0.2) / 0.4)
        if a <= 0: continue
        x0, x1 = col4(i); on = (i == cur); card(d, [x0, 180, x1, 320], col, a, fill=col if on else WHITE)
        d.ellipse([x0 + 24, 216, x0 + 92, 284], fill=A(WHITE if on else col, a)); d.text((x0 + 58, 250), str(i + 1), font=F(BL, 36), fill=A(col if on else WHITE, a), anchor='mm')
        d.text((x0 + 112, 232), t1, font=fit(BL, 31, t1, 280), fill=A(WHITE if on else INK, a), anchor='lm'); d.text((x0 + 112, 272), t2, font=fit(MD, 22, t2, 280), fill=A((225, 233, 255) if on else SLATE, a), anchor='lm')
        if i < 3: d.polygon([(x1 + 6, 240), (x1 + 18, 250), (x1 + 6, 260)], fill=A(SLATE, a))
    x0, x1 = col4(0, 2); bx = [x0, 356, x1, 950]
    if cur < 0: inset(fr, CLA, 0, bx, "LA SÉANCE", 1.0, "Séance individuelle en visio (Zoom)")
    else:
        v = u - cs[cur]; cl, base, lab = [(CLA, 0, "EXAMEN BLANC N° 1"), (CLE, 0, "FEEDBACK"), (CLA, 130, "EXAMEN BLANC N° 2"), (CLE, 120, "FEEDBACK FINAL")][cur]
        inset(fr, cl, base + int(v * 25 * 0.7), bx, lab, ease(v / 0.3), "Avec Ahlem, examinatrice habilitée" if cl is CLA else "Avec Emmanuel, examinateur habilité")
    det = [("Premier examen blanc", ROYAL, ["Simulation complète des 3 tâches", "L'examinateur pose les questions et tient son rôle", "Il chronomètre, sans vous aider"]),
           ("Feedback personnalisé", GREEN, ["Vos points forts", "Vos erreurs principales", "Des conseils à appliquer immédiatement"]),
           ("Deuxième examen blanc", ROYAL, ["Une nouvelle simulation complète", "Avec de nouveaux sujets", "Vous appliquez les conseils reçus"]),
           ("Feedback final", GREEN, ["Retour sur cette deuxième performance", "Vos principaux progrès", "Vos axes de travail"])]
    x0, x1 = col4(2, 2); d = ImageDraw.Draw(fr, 'RGBA'); card(d, [x0, 356, x1, 950], LINEC, 1, w=2)
    if cur < 0:
        d.text((x0 + 44, 430), "Votre séance en 4 temps", font=F(BL, 46), fill=INK, anchor='lm'); d.text((x0 + 44, 496), "Vous testez, vous écoutez, vous recommencez.", font=fit(MD, 30, "Vous testez, vous écoutez, vous recommencez.", x1 - x0 - 90), fill=SLATE, anchor='lm')
    else:
        v = u - cs[cur]; t1, col, bl = det[cur]; a = ease(v / 0.35); num(d, x0 + 84, 440, cur + 1, col, a, r=40)
        d.text((x0 + 148, 440), t1, font=fit(BL, 46, t1, x1 - x0 - 190), fill=A(INK, a), anchor='lm')
        for j, tx in enumerate(bl):
            aj = ease((v - 0.5 - j * 0.7) / 0.4)
            if aj <= 0: continue
            y = 560 + j * 118; check(d, x0 + 78, y, col, aj, r=26); d.text((x0 + 128, y), tx, font=fit(SB, 33, tx, x1 - x0 - 170), fill=A(INK, aj), anchor='lm')

def s7(fr, u, D):     # les 3 tâches
    header(fr, None, "Les 3 tâches · format officiel"); d = ImageDraw.Draw(fr, 'RGBA'); cw = 560
    tasks = [("TÂCHE 1", "Entretien dirigé", "≈ 2 min", "Sans préparation", "Se présenter et parler de soi", "de manière naturelle.", "Tâche un"),
             ("TÂCHE 2", "Interaction", "≈ 3 min 30", "≈ 2 min de préparation", "Poser des questions pour obtenir", "des informations.", "Tâche deux"),
             ("TÂCHE 3", "Point de vue", "≈ 4 min 30", "Sans préparation", "Exprimer et défendre une opinion", "de manière structurée.", "Tâche trois")]
    for i, (tg, nm, du, pr, d1, d2, w) in enumerate(tasks):
        a = ease((u - cue(7, w)) / 0.4); x = ML + i * (cw + GUT); y = 180 + int((1 - a) * 20)
        if a <= 0: continue
        card(d, [x, y, x + cw, y + 770], SKY, a); d.rounded_rectangle([x + 44, y + 48, x + 234, y + 106], radius=29, fill=A(FLAG, a)); d.text((x + 139, y + 77), tg, font=F(BD, 28), fill=A(WHITE, a), anchor='mm')
        d.text((x + 44, y + 200), nm, font=F(BL, 60), fill=A(INK, a), anchor='lm'); d.line([x + 44, y + 262, x + cw - 44, y + 262], fill=A(LINEC, a), width=3)
        d.text((x + 44, y + 370), du, font=F(BL, 96), fill=A(ROYAL, a), anchor='lm')
        pw = int(F(SB, 28).getlength(pr)) + 52; d.rounded_rectangle([x + 44, y + 458, x + 44 + pw, y + 518], radius=30, fill=A(TINT, a)); d.text((x + 70, y + 488), pr, font=F(SB, 28), fill=A(ROYAL, a), anchor='lm')
        d.text((x + 44, y + 620), d1, font=fit(MD, 30, d1, cw - 88), fill=A(SLATE, a), anchor='lm'); d.text((x + 44, y + 664), d2, font=fit(MD, 30, d2, cw - 88), fill=A(SLATE, a), anchor='lm')

FW, FH = 852, 770
def fiche():
    im = Image.new('RGB', (FW, FH), WHITE); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, FW, 120], fill=ROYAL); d.text((44, 44), "Fiche de retour", font=F(BL, 42), fill=WHITE, anchor='lm'); d.text((44, 90), "Examen blanc d'expression orale", font=F(MD, 24), fill=(220, 230, 255), anchor='lm')
    rng = np.random.RandomState(4); secs = (("POINTS FORTS", GREEN, 3, 160), ("ERREURS PRINCIPALES", FLAG, 3, 350), ("CONSEILS À APPLIQUER", ROYAL, 3, 540))
    for tt, col, n, y in secs:
        for i in range(n): yy_ = y + 44 + i * 42; d.ellipse([48, yy_, 64, yy_ + 16], fill=col); d.rounded_rectangle([84, yy_ - 2, 84 + rng.randint(420, 700), yy_ + 18], radius=10, fill=(60, 70, 110))
    b = im.crop((70, 180, FW, 700)).filter(ImageFilter.GaussianBlur(7)); im.paste(b, (70, 180)); d = ImageDraw.Draw(im)
    for tt, col, n, y in secs: d.text((44, y + 8), tt, font=F(BD, 26), fill=col, anchor='lm')
    d.rounded_rectangle([44, 700, 344, 748], radius=24, fill=(238, 243, 252)); d.text((194, 724), "Exemple · contenu flouté", font=F(SB, 20), fill=SLATE, anchor='mm')
    return im
FICHE = fiche()
def s8(fr, u, D):     # feedback
    header(fr, None, "Ce que vous recevez"); d = ImageDraw.Draw(fr, 'RGBA'); x0, x1 = col4(0, 2)
    its = [("Vos points forts", "Ce que vous faites déjà bien", GREEN, "vos points forts"), ("Vos erreurs principales", "Ce qui vous coûte des points", FLAG, "vos erreurs"), ("Des conseils concrets", "À appliquer immédiatement", ROYAL, "et les conseils")]
    for i, (t1, t2, col, w) in enumerate(its):
        a = ease((u - cue(8, w)) / 0.4)
        if a <= 0: continue
        y = 180 + i * 196 + int((1 - a) * 18); card(d, [x0, y, x1, y + 172], col, a); check(d, x0 + 86, y + 86, col, a, r=40)
        d.text((x0 + 158, y + 62), t1, font=F(BL, 42), fill=A(INK, a), anchor='lm'); d.text((x0 + 158, y + 114), t2, font=F(MD, 27), fill=A(SLATE, a), anchor='lm')
    a = ease((u - cue(8, "Vous savez")) / 0.4)
    if a > 0:
        d.rounded_rectangle([x0, 768, x1, 950], radius=26, fill=A(INK, a)); d.text((x0 + 44, 832), "Vous savez exactement quoi corriger", font=fit(BL, 40, "Vous savez exactement quoi corriger", x1 - x0 - 88), fill=A(WHITE, a), anchor='lm'); d.text((x0 + 44, 890), "avant le jour J.", font=F(BL, 40), fill=A(YEL, a), anchor='lm')
    a = ease((u - 0.4) / 0.5); x0, x1 = col4(2, 2); o = int((1 - a) * 30)
    if a > 0:
        d.rounded_rectangle([x0 + o, 190, x1 + o, 960], radius=26, fill=(20, 40, 120, int(30 * a)))
        mm = Image.new('L', (FW, FH), 0); ImageDraw.Draw(mm).rounded_rectangle([0, 0, FW - 1, FH - 1], radius=26, fill=int(255 * a)); fr.paste(FICHE, (x0 + o, 180), mm)
        ImageDraw.Draw(fr, 'RGBA').rounded_rectangle([x0 + o, 180, x1 + o, 950], radius=26, outline=A(LINEC, a), width=3)

def s9(fr, u, D):     # checklist
    header(fr, None, "Avant votre séance : 4 réflexes"); d = ImageDraw.Draw(fr, 'RGBA')
    grid2(d, u, [("Une bonne connexion Internet", "Testez votre réseau avant la séance.", "", cue(9, "une bonne connexion")),
                 ("Un casque ou des écouteurs", "Pour bien entendre et être bien entendu.", "", cue(9, "un casque")),
                 ("Une pièce calme", "Sans bruit ni interruption.", "", cue(9, "une pièce")),
                 ("5 minutes d'avance", "Connectez-vous avant l'heure prévue.", "", cue(9, "et connectez-vous"))], lambda i: GREEN, 'check')

def s10(fr, u, D):    # appel à l'action
    fr.paste(NAVY); d = ImageDraw.Draw(fr, 'RGBA'); lw = LGB.width + 70; d.rounded_rectangle([W // 2 - lw // 2, 40, W // 2 + lw // 2, 40 + LGB.height + 24], radius=40, fill=WHITE); fr.paste(LGB, (W // 2 - LGB.width // 2, 52), LGB); d = ImageDraw.Draw(fr, 'RGBA'); a = ease(u / 0.5)
    big(d, 330, "Réservez votre examen blanc", F(BL, 88), WHITE, a); big(d, 436, "d'expression orale", F(BL, 88), YEL, a)
    a2 = ease((u - cue(10, "sur formation")) / 0.4); f = F(BD, 56); tx = "formation-tcfcanada.com"; tw = int(f.getlength(tx)) + 120
    d.rounded_rectangle([W // 2 - tw // 2, 540, W // 2 + tw // 2, 664], radius=62, fill=A(WHITE, a2)); d.text((W // 2, 602), tx, font=f, fill=A(ROYAL, a2), anchor='mm')
    a3 = ease((u - cue(10, "sur formation") - 0.6) / 0.4); d.text((W // 2, 730), "$20.00 USD · 2 examens blancs · feedback personnalisé · ≈ 40 min en visio", font=F(SB, 32), fill=A((215, 226, 255), a3), anchor='mm')
    t2 = "WhatsApp officiel : +1 506 253 60 67"; f2 = F(BD, 32); tw = int(f2.getlength(t2)) + 72
    d.rounded_rectangle([W // 2 - tw // 2, 786, W // 2 + tw // 2, 854], radius=34, fill=A(GREEN, a3)); d.text((W // 2, 820), t2, font=f2, fill=A(WHITE, a3), anchor='mm')
    big(d, 932, "Le jour J, vous aurez déjà vécu l'examen.", F(XB, 44), YEL, ease((u - cue(10, "Et le jour")) / 0.4), dy=0)
    d.text((W // 2, 1028), "Simulation d'entraînement proposée par la plateforme : ce n'est pas une épreuve officielle.", font=F(MD, 21), fill=A((190, 204, 245), a3), anchor='mm')

SC = [s0, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10]
def scene(i, t):
    fr = PLAIN.copy(); SC[i](fr, t - T0[i], T0[i + 1] - T0[i]); return fr
def frame(t):
    i = max(k for k in range(NS) if t >= T0[k] or k == 0); fr = scene(i, t); u = t - T0[i]
    if i > 0 and u < 0.3: fr = Image.blend(scene(i - 1, t), fr, ease(u / 0.3))
    if t > TOTAL - 0.5: fr = Image.blend(fr, Image.new('RGB', (W, H), (10, 20, 96)), (t - TOTAL + 0.5) / 0.5)
    d = ImageDraw.Draw(fr); d.rectangle([0, H - 6, int(W * t / TOTAL), H], fill=YEL if i in (0, NS - 1) else ROYAL)
    return fr
if ONLY is not None:
    for v in ONLY: frame(v).save(f"{OUTV}_{v}.jpg", quality=88)
    print('T0', [round(v, 1) for v in T0]); sys.exit()
# ---------- audio : voix + impacts de l'accroche
def wr(p, o):
    w = wave.open(p, 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(o, -1, 1) * 32767).astype('<i2').tobytes()); w.close()
N = int(TOTAL * SR); o = np.zeros(N); o[:len(VO)] += VO[:N] * 1.05
def hit(t0, g=0.32):
    n = int(0.9 * SR); tt = np.arange(n) / SR; f = 46 + 60 * np.exp(-tt * 9); s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 5.5)
    nz = np.random.RandomState(1).randn(n) * np.exp(-tt * 40) * 0.25; i0 = int(t0 * SR); o[i0:i0 + n] += (s + nz)[:max(0, N - i0)] * g
for tc in (0.02, T0[0] + cue(0, "Et si"), T0[0] + cue(0, "Restez"), T0[NS - 1]): hit(tc)
wr(WK + 'mix3.wav', o)
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-i', WK + 'mix3.wav',
                        '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-shortest', OUTV], stdin=subprocess.PIPE)
for i in range(int(round(TOTAL * FPS))): enc.stdin.write(frame(i / FPS).tobytes())
enc.stdin.close(); enc.wait(); print('total', round(TOTAL, 1))

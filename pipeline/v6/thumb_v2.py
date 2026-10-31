"""Miniature YouTube v2 (style validé par Ayoub le 31/10/2026 : fond bleu, « TÂCHE N » jaune, nouvelle photo).
usage : python3 thumb_v2.py <EO|EE> <tache> "<ligne sujet>" <sortie.jpg> ["coche1|coche2|coche3"] ["TCF CANADA 2026"]
La photo utilisée est ayoub_new.png (détourée, avec contour blanc), dans le même dossier que ce script."""
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
D = os.path.dirname(os.path.abspath(__file__))
EP, TA, SUBJ, OUT = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
CHECKS = (sys.argv[5] if len(sys.argv) > 5 and sys.argv[5] else
          ("Simulation réelle|Corrections|Bilan" if EP == "EO" else "Méthode|Erreurs corrigées|Modèle")).split('|')
PILL = sys.argv[6] if len(sys.argv) > 6 else "TCF CANADA 2026"
W, H = 1280, 720
FD = "/usr/share/fonts/opentype/inter/"
BL, XB, BD = FD + "InterDisplay-Black.otf", FD + "InterDisplay-ExtraBold.otf", FD + "Inter-Bold.otf"
F = lambda p, s: ImageFont.truetype(p, int(s))
YEL = (255, 214, 64); RED = (229, 57, 53); NAVY = (21, 32, 110); WHITE = (255, 255, 255)

# fond : dégradé bleu roi -> marine, halo clair derrière la photo
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
t = np.clip(xx / W * 0.55 + yy / H * 0.45, 0, 1)[..., None]
c0 = np.array((36, 70, 230), np.float32); c1 = np.array((14, 28, 120), np.float32)
bg = c0 * (1 - t) + c1 * t
r = np.sqrt((xx - 960) ** 2 + (yy - 330) ** 2); glow = np.clip(1 - r / 520, 0, 1)[..., None] ** 1.6
bg = bg + glow * np.array((70, 95, 140), np.float32)
vig = np.clip(1 - (np.sqrt((xx - W / 2) ** 2 + (yy - H / 2) ** 2) / 900) ** 2.2 * 0.35, 0, 1)[..., None]
img = Image.fromarray(np.clip(bg * vig, 0, 255).astype(np.uint8)).convert('RGBA')
# fines lignes diagonales décoratives
ov = Image.new('RGBA', (W, H)); od = ImageDraw.Draw(ov)
for i in range(-10, 30): od.line([(i * 70, 0), (i * 70 - 400, H)], fill=(255, 255, 255, 10), width=2)
img.alpha_composite(ov)

# photo
P = Image.open(os.path.join(D, 'ayoub_new.png')).convert('RGBA')
k = 660 / P.height; P = P.resize((int(P.width * k), 660), Image.LANCZOS)
px, py = W - P.width + 60, H - P.height + 76
sh = Image.new('RGBA', (W, H)); m = P.split()[3].point(lambda v: int(v * 0.55))
sh.paste((5, 10, 50, 255), (px - 18, py + 14), m); sh = sh.filter(ImageFilter.GaussianBlur(18)); img.alpha_composite(sh)
img.alpha_composite(P, (px, py))
d = ImageDraw.Draw(img)

def shadow_text(xy, txt, font, fill, off=5, blur=6, alpha=150):
    L = Image.new('RGBA', (W, H)); ImageDraw.Draw(L).text((xy[0] + off, xy[1] + off), txt, font=font, fill=(5, 10, 50, alpha), anchor='ls')
    img.alpha_composite(L.filter(ImageFilter.GaussianBlur(blur))); ImageDraw.Draw(img).text(xy, txt, font=font, fill=fill, anchor='ls')

X = 46; MAXW = 660
# pastille rouge
fp = F(BD, 30); tw = fp.getlength(PILL)
d.rounded_rectangle([X, 40, X + tw + 44, 92], radius=14, fill=RED); d.text((X + 22, 66), PILL, font=fp, fill=WHITE, anchor='lm')
# TÂCHE N
ft = F(BL, 168)
while ft.getlength(f"TÂCHE {TA}") > MAXW and ft.size > 100: ft = F(BL, ft.size - 4)
shadow_text((X - 4, 262), f"TÂCHE {TA}", ft, YEL)
# EXPRESSION / ÉCRITE|ORALE
fe = F(BL, 76)
shadow_text((X, 352), "EXPRESSION", fe, WHITE, off=4, blur=5)
shadow_text((X, 432), "ÉCRITE" if EP == "EE" else "ORALE", fe, WHITE, off=4, blur=5)
# encadré blanc : sujet
fs = F(XB, 44)
while fs.getlength(SUBJ) > MAXW - 60 and fs.size > 26: fs = F(XB, fs.size - 2)
bw = fs.getlength(SUBJ) + 56; y0 = 470
L = Image.new('RGBA', (W, H)); ImageDraw.Draw(L).rounded_rectangle([X + 4, y0 + 10, X + bw + 4, y0 + 92], radius=16, fill=(5, 10, 50, 120))
img.alpha_composite(L.filter(ImageFilter.GaussianBlur(8))); d = ImageDraw.Draw(img)
d.rounded_rectangle([X, y0, X + bw, y0 + 82], radius=16, fill=WHITE)
d.rounded_rectangle([X, y0 + 74, X + bw, y0 + 82], radius=4, fill=(38, 169, 255))
d.text((X + 28, y0 + 39), SUBJ, font=fs, fill=NAVY, anchor='lm')
# coches
fc = F(BD, 27); y = 616
while sum(32 + fc.getlength(c) + 26 for c in CHECKS) > 700 and fc.size > 18: fc = F(BD, fc.size - 1)
x = X
for c in CHECKS:
    d.line([(x + 2, y), (x + 9, y + 8), (x + 22, y - 9)], fill=WHITE, width=4, joint='curve')
    d.text((x + 32, y), c, font=fc, fill=WHITE, anchor='lm'); x += 32 + fc.getlength(c) + 26
# logo
if os.environ.get('LOGO'):
  try:
    sys.path.insert(0, D); import logoanim; logoanim.THEME = 'dark'
    lg = logoanim.static_logo(70, glow=True); img.alpha_composite(lg, (W - lg.width - 18, 10))
  except Exception as e: print('logo', e)
img.convert('RGB').save(OUT, quality=92)
print('ok', OUT)

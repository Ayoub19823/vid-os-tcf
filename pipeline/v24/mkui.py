import sys, json
from PIL import Image, ImageDraw, ImageFont
P, k, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
J = json.load(open(f'cap{P}/s{k}/J.json')); c = J['card']
E = Image.open(f'cap{P}/s{k}/E0.png').convert('RGB'); s = 1.36
E = E.resize((int(E.width * s / 2), int(E.height * s / 2)), Image.LANCZOS)
x0 = 771 - c[0] * s; y0 = 471 - c[1] * s
img = Image.new('RGB', (1920, 1080), (255, 255, 255)); img.paste(E, (int(x0), int(y0)))
d = ImageDraw.Draw(img); RED = (229, 30, 32)
r = [x0 + c[0] * s - 8, y0 + c[1] * s - 8, x0 + c[2] * s + 8, y0 + c[3] * s + 8]
d.rounded_rectangle(r, 26, outline=RED, width=10)
f = ImageFont.truetype('/usr/share/fonts/opentype/inter/InterDisplay-Black.otf', 40)
t = f"Sujet n° {k} · Partie {P}"; tw = f.getlength(t)
d.rounded_rectangle([r[0] - 6, r[1] - 62, r[0] + tw + 44, r[1] - 2], 30, fill=RED)
d.text((r[0] + 19, r[1] - 32), t, font=f, fill='white', anchor='lm')
img.save(out)

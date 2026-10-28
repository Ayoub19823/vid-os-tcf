import sys, os, math, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
from script import LINES, CHRONO_START, CHRONO_STOP

AUD = sys.argv[1]; OUTV = sys.argv[2]
ONLY = [float(v) for v in sys.argv[3].split(',')] if len(sys.argv) > 3 else None
W, H, FPS = 1920, 1080, 25
INTRO, BILAN, OUTRO = 3.0, 14.0, 5.0
wv = wave.open(AUD); sr = wv.getframerate(); x = np.frombuffer(wv.readframes(wv.getnframes()), '<i2').astype(np.float32) / 32768
ADUR = len(x) / sr
TOTAL = INTRO + ADUR + BILAN + OUTRO
hop = sr // FPS
env = np.array([np.sqrt(np.mean(x[i:i + hop] ** 2)) for i in range(0, len(x), hop)]); env /= (np.percentile(env, 98) + 1e-6)


def bars(at, n=13):
    i = int(at * sr); seg = x[max(0, i - 1200):i + 1200]
    if len(seg) < 256: return np.zeros(n)
    sp = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))[:len(seg) // 6]
    v = np.array([c.mean() for c in np.array_split(sp, n)]); v = np.sqrt(v / (sp.mean() * 3 + 1e-6))
    return np.clip(np.concatenate([v[::2][::-1], v[1::2]])[:n], 0, 1.2)


BG0 = (9, 16, 40); BG1 = (18, 30, 70)
WHITE = (255, 255, 255); MUTE = (160, 172, 210); YEL = (255, 200, 60); RED = (239, 68, 68); ORANGE = (255, 150, 40)
CC = (167, 112, 255); HC = (56, 160, 255); GREEN = (34, 197, 94); BRAND = (26, 92, 255)
BL = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
XB = "/usr/share/fonts/opentype/inter/InterDisplay-ExtraBold.otf"
SB = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
MD = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
BD = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
IT = "/usr/share/fonts/opentype/inter/Inter-MediumItalic.otf"
EF = ImageFont.truetype('/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf', 109)
_fc = {}
def F(p, s):
    k = (p, int(s))
    if k not in _fc: _fc[k] = ImageFont.truetype(p, int(s))
    return _fc[k]
def clamp(v, a=0.0, b=1.0): return max(a, min(b, v))
def ease(v): v = clamp(v); return v * v * (3 - 2 * v)
def ob(v):
    v = clamp(v); c = 1.6; return 1 + (c + 1) * (v - 1) ** 3 + c * (v - 1) ** 2
def A(c, a): return tuple(c[:3]) + (int(255 * clamp(a)),)
def emoji(e, s):
    im = Image.new('RGBA', (140, 140)); ImageDraw.Draw(im).text((70, 70), e, font=EF, embedded_color=True, anchor='mm')
    im = im.crop(im.getbbox()); k = s / max(im.size); return im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)

LOGO = Image.open(f'{D}/logo.png').convert('RGBA')
def logo(h):
    return LOGO.resize((int(LOGO.width * h / LOGO.height), h), Image.LANCZOS)

# ------------------------------------------------ pedagogy data (audio seconds)
QUESTIONS = [35.75, 49.25, 61.89, 77.70, 94.28, 112.71, 129.22, 143.27, 157.57]
THEMES = [("Activités", 35.75), ("Âge", 49.25), ("Lecture", 61.89), ("Type de cadeau", 77.70),
          ("Cuisine", 94.28), ("Besoins", 129.22), ("Jeux vidéo", 143.27), ("Travail", 157.57)]
FEED = [  # time, kind ok|fix|note, line1, line2
    (38.6, 'ok', "Bonne question", "Claire et naturelle pour lancer l'échange"),
    (50.6, 'ok', "Question simple et efficace", "« Quel âge a ta sœur ? »"),
    (61.3, 'ok', "Bonne reformulation", "Il reprend la réponse : « Elle va fêter ses trente ans, d'accord »"),
    (65.6, 'ok', "Question à choix", "« des romans ou des comédies ? » : bonne stratégie"),
    (85.9, 'fix', "« les cadeaux… ou les cadeaux utiles ? »", "Elle préfère les cadeaux utiles ou décoratifs ?"),
    (96.0, 'fix', "« est-ce qu'elle est une cuisinière ? »", "Est-ce qu'elle aime cuisiner ?"),
    (112.3, 'note', "Tutoiement → vouvoiement", "Gardez le même registre : « Qu'est-ce que tu me conseilles ? »"),
    (132.9, 'fix', "« des choses qu'elle a besoin »", "des choses dont elle a besoin"),
    (145.9, 'fix', "« jouer des jeux vidéo »", "jouer aux jeux vidéo"),
    (161.8, 'fix', "« Étudie-t-elle dans le collège, ou elle travaille »", "Est-ce qu'elle étudie ou est-ce qu'elle travaille ?"),
    (176.2, 'ok', "Bonne synthèse", "Il propose une idée de cadeau concrète"),
    (201.6, 'fix', "« lui donner un livre »", "lui offrir un livre"),
]
CTA_WINDOWS = [(100.0, 108.0), (184.0, 191.0)]
REG_SWITCH = 109.83


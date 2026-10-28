import numpy as np, sys, math, cv2
sys.path.insert(0,'.')
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import logoanim
W,H=1280,720
ROYAL=(24,56,255); SKY=(38,169,255); FLAG=(229,30,32); INK=(15,20,60); YEL=(255,212,0)
BL="/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"; BD="/usr/share/fonts/opentype/inter/Inter-Bold.otf"; XB="/usr/share/fonts/opentype/inter/InterDisplay-ExtraBold.otf"
F=lambda p,s: ImageFont.truetype(p,s)
VAR=sys.argv[1]

def outline(P,px,col=(255,255,255)):
    a=np.array(P.getchannel('A'))
    k=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*px+1,2*px+1))
    d=cv2.dilate(a,k); o=Image.new('RGBA',P.size,col+(0,)); o.putalpha(Image.fromarray(d).filter(ImageFilter.GaussianBlur(1.2)))
    o.alpha_composite(P); return o

def tilt_card(src, w, h, ang=-8, border=10):
    c=Image.open(src).convert('RGB').crop((690,150,1900,1060)).resize((w,int(w*910/1210)),Image.LANCZOS)
    card=Image.new('RGBA',(c.width+2*border,c.height+2*border),(255,255,255,255)); card.paste(c,(border,border))
    m=Image.new('L',card.size,0); ImageDraw.Draw(m).rounded_rectangle([0,0,card.width-1,card.height-1],radius=26,fill=255); card.putalpha(m)
    # perspective
    cw,ch=card.size; arr=np.array(card)
    src_pts=np.float32([[0,0],[cw,0],[cw,ch],[0,ch]]); dst=np.float32([[0,ch*0.06],[cw,0],[cw,ch],[0,ch*0.94]])
    M=cv2.getPerspectiveTransform(src_pts,dst); warped=cv2.warpPerspective(arr,M,(cw,ch),flags=cv2.INTER_LINEAR,borderValue=(0,0,0,0))
    card=Image.fromarray(warped).rotate(ang,resample=Image.BICUBIC,expand=True)
    return card

def shadow(img,layer,pos,blur=22,off=(16,22),alpha=0.45,col=(5,10,50)):
    a=Image.new('L',img.size,0); a.paste(layer.getchannel('A'),pos)
    s=Image.new('RGBA',img.size,col+(0,)); s.putalpha(a.filter(ImageFilter.GaussianBlur(blur)).point(lambda v:int(v*alpha)))
    img.alpha_composite(s,off)

def stroke_text(d,xy,txt,font,fill,sw,sf,anchor='lm'):
    d.text(xy,txt,font=font,fill=fill,stroke_width=sw,stroke_fill=sf,anchor=anchor)

if VAR=='dark':
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
    r=np.sqrt(((xx-900)/W)**2+((yy-330)/H)**2)[...,None]
    c0=np.array((38,120,255)); c1=np.array((14,30,140)); c2=np.array((6,10,50))
    arr=np.where(r<0.45,c0+(c1-c0)*(r/0.45),c1+(c2-c1)*np.clip((r-0.45)/0.5,0,1))
    img=Image.fromarray(arr.astype(np.uint8)).convert('RGBA')
    ray=Image.new('RGBA',(W,H),(0,0,0,0)); rd=ImageDraw.Draw(ray)
    for i in range(18):
        a0=i*20; rd.pieslice([900-1400,330-1400,900+1400,330+1400],a0,a0+7,fill=(120,190,255,38))
    img.alpha_composite(ray.filter(ImageFilter.GaussianBlur(3)))
    TXT=(255,255,255); ST=INK
else:
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32); t=np.clip(xx/W*0.6+yy/H*0.4,0,1)[...,None]
    img=Image.fromarray((np.array((255,255,255))+(np.array((220,233,255))-255)*t).astype(np.uint8)).convert('RGBA')
    gl=Image.new('RGBA',(W,H),(0,0,0,0)); ImageDraw.Draw(gl).ellipse([700,-150,1450,650],fill=SKY+(150,)); ImageDraw.Draw(gl).ellipse([-200,450,500,1000],fill=ROYAL+(50,))
    img.alpha_composite(gl.filter(ImageFilter.GaussianBlur(90)))
    TXT=INK; ST=(255,255,255)

# UI card tilted, center behind person
card=tilt_card('ui.png',520,0,ang=7)
cpos=(560,190)
shadow(img,card,cpos,blur=26,off=(18,26),alpha=0.5)
img.alpha_composite(card,cpos)
P=Image.open('person.png'); ph=800; P=P.resize((int(P.width*ph/P.height),ph),Image.LANCZOS)
P=outline(P,9)
px=W-P.width+70; py=H-ph+110
shadow(img,P,(px,py),blur=20,off=(-14,14),alpha=0.5)
img.alpha_composite(P,(px,py))
d=ImageDraw.Draw(img,'RGBA')
logoanim.THEME='dark' if VAR=='dark' else 'light'
lg=logoanim.static_logo(110 if VAR=='light' else 96,glow=(VAR=='dark')); img.alpha_composite(lg,(18 if VAR=='dark' else 30, 4 if VAR=='dark' else 22))
SUBJ = sys.argv[4].split('|') if len(sys.argv) > 4 else None
if SUBJ:
    stroke_text(d,(34,212),"TÂCHE 2",F(BL,108),TXT,9,ST)
    f2=F(BL,62); ws=[f2.getlength(t) for t in SUBJ]; bw=max(ws)+40
    by0=278; lh=72
    d.rounded_rectangle([34,by0,34+bw+40,by0+lh*len(SUBJ)+24],radius=22,fill=YEL)
    for i,t in enumerate(SUBJ): d.text((62,by0+12+lh*i+lh/2),t,font=f2,fill=INK,anchor='lm')
    EF=ImageFont.truetype('/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf',109)
    em=Image.new('RGBA',(140,140)); ImageDraw.Draw(em).text((70,70),"📺",font=EF,embedded_color=True,anchor='mm'); em=em.crop(em.getbbox()).resize((96,96),Image.LANCZOS).rotate(-10,expand=True,resample=Image.BICUBIC)
    if len(sys.argv) > 5 and sys.argv[5] == 'tv': img.alpha_composite(em,(int(34+bw-20),by0-62)); d=ImageDraw.Draw(img,'RGBA')
else:
    stroke_text(d,(34,270),"TÂCHE 2",F(BL,148),TXT,10,ST)
    f2=F(BL,72); txt="EXAMEN RÉEL"; tw=f2.getlength(txt)
    d.rounded_rectangle([34,352,34+tw+44,452],radius=18,fill=YEL)
    d.text((56,402),txt,font=f2,fill=INK,anchor='lm')
bx,by,br=118,570,74
d.ellipse([bx-br-8,by-br-8,bx+br+8,by+br+8],fill=(255,255,255))
d.ellipse([bx-br,by-br,bx+br,by+br],outline=(225,232,250),width=14); d.arc([bx-br,by-br,bx+br,by+br],-90,200,fill=FLAG,width=14)
d.text((bx,by),(sys.argv[3] if len(sys.argv) > 3 else "3:50"),font=F(BL,50),fill=INK,anchor='mm')
tg="+ CORRECTIONS"; ft=F(BD,32); tw=ft.getlength(tg)
d.rounded_rectangle([222,540,222+tw+44,600],radius=30,fill=FLAG); d.text((244,570),tg,font=ft,fill='white',anchor='lm')
# arrow from tag to correction line on card
ax0,ay0=222+tw+50,560; ax1,ay1=618,450
pts=[(ax0+(ax1-ax0)*t_, ay0+(ay1-ay0)*t_-40*math.sin(math.pi*t_)) for t_ in [i/29 for i in range(30)]]
d.line(pts,fill=(255,255,255),width=20,joint='curve'); d.line(pts,fill=FLAG,width=10,joint='curve')
ang=math.atan2(pts[-1][1]-pts[-4][1],pts[-1][0]-pts[-4][0])
hx,hy=ax1,ay1
head=[(hx+30*math.cos(ang),hy+30*math.sin(ang)),(hx+24*math.cos(ang+2.3),hy+24*math.sin(ang+2.3)),(hx+24*math.cos(ang-2.3),hy+24*math.sin(ang-2.3))]
d.polygon(head,fill=FLAG,outline=(255,255,255),width=4)
out=sys.argv[2]
img.convert('RGB').save(out,quality=95); img.convert('RGB').save(f'th_{VAR}.png')

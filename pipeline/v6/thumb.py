import numpy as np, sys, math
sys.path.insert(0,'.')
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import logoanim; logoanim.THEME='light'
from logoanim import static_logo
W,H=1280,720
ROYAL=(24,56,255); SKY=(38,169,255); FLAG=(229,30,32); INK=(20,27,77); SLATE=(92,106,146)
BL="/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"; BD="/usr/share/fonts/opentype/inter/Inter-Bold.otf"; XB="/usr/share/fonts/opentype/inter/InterDisplay-ExtraBold.otf"
F=lambda p,s: ImageFont.truetype(p,s)
yy,xx=np.mgrid[0:H,0:W].astype(np.float32); t=np.clip(xx/W*0.6+yy/H*0.4,0,1)[...,None]
img=Image.fromarray((np.array((255,255,255))+(np.array((232,240,255))-255)*t).astype(np.uint8)).convert('RGBA')
d=ImageDraw.Draw(img)
for y in range(20,H,34):
    for x in range(20,W,34): d.ellipse([x-1.2,y-1.2,x+1.2,y+1.2],fill=ROYAL+(26,))
cx,cy,R=1000,380,320
Y,X=np.mgrid[0:2*R,0:2*R]; inside=(X-R)**2+(Y-R)**2<=R*R
u=np.clip((X+Y*0.6)/(2*R*1.6),0,1)[...,None]
c0=np.array((120,200,255)); c1=np.array((38,169,255)); c2=np.array((24,56,200))
col=np.where(u<0.45,c0+(c1-c0)*(u/0.45),c1+(c2-c1)*((u-0.45)/0.55))
g=np.zeros((2*R,2*R,4),np.uint8); g[...,:3]=col.astype(np.uint8); g[...,3]=inside*255
glow=Image.new('RGBA',(W,H),(0,0,0,0)); ImageDraw.Draw(glow).ellipse([cx-R-40,cy-R-40,cx+R+40,cy+R+40],fill=SKY+(110,))
img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(50))); img.alpha_composite(Image.fromarray(g),(cx-R,cy-R))
d=ImageDraw.Draw(img); d.ellipse([cx-R-22,cy-R-22,cx+R+22,cy+R+22],outline=ROYAL+(90,),width=4)
P=Image.open('person.png'); ph=700; P=P.resize((int(P.width*ph/P.height),ph),Image.LANCZOS)
px=cx-P.width//2+10; py=H-ph+30
a=Image.new('L',(W,H),0); a.paste(P.getchannel('A'),(px,py))
s=Image.new('RGBA',(W,H),(10,20,90,0)); s.putalpha(a.filter(ImageFilter.GaussianBlur(18)).point(lambda v:int(v*0.35)))
img.alpha_composite(s,(14,10)); img.alpha_composite(P,(px,py))
d=ImageDraw.Draw(img,'RGBA')
img.alpha_composite(static_logo(150,glow=False),(40,26))
d.rounded_rectangle([46,205,402,259],radius=27,fill=FLAG); d.text((224,232),"SIMULATION RÉELLE",font=F(BD,30),fill='white',anchor='mm')
d.text((40,340),"TÂCHE 2",font=F(BL,136),fill=INK,anchor='lm')
d.text((46,450),"Expression orale",font=F(BL,62),fill=ROYAL,anchor='lm')
d.rounded_rectangle([46,505,560,575],radius=35,fill='white',outline=(210,222,248),width=3)
S=8; fw,fh=60,42
fl=Image.new('RGBA',(fw*S,fh*S)); fd=ImageDraw.Draw(fl)
fd.rectangle([0,0,fw*S//2,fh*S],fill=(0,98,51)); fd.rectangle([fw*S//2,0,fw*S,fh*S],fill=(255,255,255))
cr=Image.new('L',fl.size,0); cd=ImageDraw.Draw(cr); fx,fy=fw*S/2,fh*S/2; r=fh*S*0.32
cd.ellipse([fx-r,fy-r,fx+r,fy+r],fill=255); r2=r*0.8; ox=r*0.28; cd.ellipse([fx-r2+ox,fy-r2,fx+r2+ox,fy+r2],fill=0)
sx,sy,so,si=fx+r*0.42,fy,r*0.42,r*0.17
cd.polygon([(sx+(so if i%2==0 else si)*math.cos(math.pi*i/5-math.pi),sy+(so if i%2==0 else si)*math.sin(math.pi*i/5-math.pi)) for i in range(10)],fill=255)
fl.paste(Image.new('RGBA',fl.size,(210,16,52,255)),(0,0),cr); fl=fl.resize((fw,fh),Image.LANCZOS)
d.rounded_rectangle([64,517,128,563],radius=7,fill='white',outline=(205,210,225),width=2); img.alpha_composite(fl,(66,519))
d=ImageDraw.Draw(img,'RGBA')
d.text((146,540),"Candidate : Rahma",font=F(XB,34),fill=INK,anchor='lm')
f=F(BD,30); x0=46
for t_,c in [("15 questions",ROYAL),("Corrections + bilan",(234,120,10))]:
    tw=f.getlength(t_); d.rounded_rectangle([x0,600,x0+tw+56,656],radius=28,fill=c); d.text((x0+28,628),t_,font=f,fill='white',anchor='lm'); x0+=tw+56+18
bx,by,br=1170,600,72
d.ellipse([bx-br-6,by-br-6,bx+br+6,by+br+6],fill='white')
d.ellipse([bx-br,by-br,bx+br,by+br],outline=(226,234,250),width=12); d.arc([bx-br,by-br,bx+br,by+br],-90,180,fill=FLAG,width=12)
d.text((bx,by-4),"3:50",font=F(BL,46),fill=INK,anchor='mm'); d.text((bx,by+34),"CHRONO",font=F(BD,14),fill=SLATE,anchor='mm')
img.convert('RGB').save('/home/claude/out/TCF_Tache2_Rahma_miniature.jpg',quality=94); img.convert('RGB').save('thumb_rahma_prev.png')

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math,random
W=3000; random.seed(4)
# gradient bg
bg=Image.new("RGB",(W,W)); px=bg.load()
for y in range(W):
    for x in range(0,W,1): pass
g=Image.linear_gradient("L").resize((2*W,2*W)).rotate(35).crop((W//2,W//2,W//2+W,W//2+W))
bg=Image.composite(Image.new("RGB",(W,W),"#0b1026"),Image.new("RGB",(W,W),"#2a0f4f"),g)
lay=Image.new("RGBA",(W,W),(0,0,0,0)); d=ImageDraw.Draw(lay)
# nodes network on a ring, upper area
cx,cy,R=1500,1050,620; nodes=[(cx+R*math.cos(a),cy+R*math.sin(a)) for a in [i*2*math.pi/7-math.pi/2 for i in range(7)]]
for i,a in enumerate(nodes):
    for j,b in enumerate(nodes):
        if i<j and (j-i) in (1,2,3): d.line([a,b],fill=(120,200,255,70 if j-i>1 else 140),width=8)
# sync pulses along edges (dashes)
for i in range(7):
    a,b=nodes[i],nodes[(i+1)%7]
    for t in (0.3,0.55):
        x,y=a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t; d.ellipse([x-16,y-16,x+16,y+16],fill=(255,180,80,230))
cols=[(0,229,255),(0,229,255),(0,229,255),(0,229,255),(255,170,60),(0,229,255),(255,170,60)]
glow=Image.new("RGBA",(W,W),(0,0,0,0)); gd=ImageDraw.Draw(glow)
for (x,y),c in zip(nodes,cols): gd.ellipse([x-110,y-110,x+110,y+110],fill=c+(160,))
glow=glow.filter(ImageFilter.GaussianBlur(60))
for (x,y),c in zip(nodes,cols):
    d.ellipse([x-70,y-70,x+70,y+70],fill=(11,16,38,255),outline=c+(255,),width=18); d.ellipse([x-30,y-30,x+30,y+30],fill=c+(255,))
im=Image.alpha_composite(Image.alpha_composite(bg.convert("RGBA"),glow),lay); d=ImageDraw.Draw(im)
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; L="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
def ctext(t,f,s,y,c):
    ft=ImageFont.truetype(f,s); w=d.textlength(t,font=ft); d.text(((W-w)/2,y),t,font=ft,fill=c)
ctext("EVENTUALLY",B,330,1910,"#ffffff"); ctext("CONSISTENT",B,330,2270,"#00e5ff")
d.rectangle([1200,2680,1800,2692],fill="#ffaa3c")
ctext("one systems concept a day",L,115,2760,"#c9d1ff")
im.convert("RGB").save("site/cover.jpg",quality=92)

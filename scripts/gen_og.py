from PIL import Image, ImageDraw, ImageFont
import os
BASE = r"C:\Users\Windows 11\Documents\Default Project\curso-claude"
img = Image.new("RGB",(1200,630))
d = ImageDraw.Draw(img)
for y in range(630):
    t=y/629
    r=int(11+(255-11)*t*0.4); g=int(11+(107-11)*t); b=int(20+(157-20)*t)
    d.line([(0,y),(1200,y)],fill=(r,g,b))
f1=ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf",72)
f2=ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf",34)
d.text((80,180),"Curso Gratuito de Claude",font=f1,fill=(255,255,255))
d.text((80,290),"Do zero ao seu primeiro projeto com IA",font=f2,fill=(230,230,255))
d.text((80,360),"4 aulas · materiais · certificado",font=f2,fill=(200,200,240))
os.makedirs(os.path.join(BASE,"assets","images"),exist_ok=True)
img.save(os.path.join(BASE,"assets","images","og.jpg"),"JPEG",quality=90)
print("OK")

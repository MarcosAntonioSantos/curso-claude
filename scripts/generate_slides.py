import os, sys, math
sys.path.insert(0, os.path.dirname(__file__))
from roteiros import AULAS
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE = r"C:\Users\Windows 11\Documents\Default Project\curso-claude"
W, H = 1920, 1080

def load_font(size, bold=False):
    candidates = [
        r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\calibri.ttf",
    ]
    if bold:
        candidates = [r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\calibrib.ttf"] + candidates
    for c in candidates:
        if os.path.exists(c):
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                pass
    return ImageFont.load_default()

def gradient_bg(draw, w, h, c1, c2):
    for y in range(h):
        t = y / (h-1)
        r = int(c1[0] + (c2[0]-c1[0])*t)
        g = int(c1[1] + (c2[1]-c1[1])*t)
        b = int(c1[2] + (c2[2]-c1[2])*t)
        draw.line([(0,y),(w,y)], fill=(r,g,b))

def wrap_text(text, font, max_width, draw):
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        test = (cur + " " + w).strip()
        bbox = draw.textbbox((0,0), test, font=font)
        if bbox[2]-bbox[0] <= max_width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def make_slide(aula, slide, idx):
    img = Image.new("RGB", (W,H))
    draw = ImageDraw.Draw(img)
    # gradient background per aula
    palettes = {
        1: ((253,242,248),(237,233,254)),
        2: ((239,246,255),(224,242,254)),
        3: ((240,253,244),(209,250,229)),
        4: ((255,251,235),(254,243,199)),
    }
    c1,c2 = palettes.get(aula["id"], ((253,242,248),(237,233,254)))
    gradient_bg(draw, W, H, c1, c2)
    # decorative circles
    for (cx,cy,r,col) in [(1700,120,180,(255,255,255,60)),(200,900,220,(255,255,255,50)),(1600,900,120,(255,200,220,70))]:
        overlay = Image.new("RGBA",(W,H),(0,0,0,0))
        od = ImageDraw.Draw(overlay)
        od.ellipse([cx-r,cy-r,cx+r,cy+r], fill=col)
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(img)
    # top bar
    draw.rectangle([0,0,W,8], fill=(124,58,237))
    # aula badge
    badge_font = load_font(28, bold=True)
    badge_text = f"AULA {aula['id']}  •  {aula['data']}"
    draw.rounded_rectangle([60,40,60+draw.textbbox((0,0),badge_text,font=badge_font)[2]+40, 40+46], radius=23, fill=(124,58,237))
    draw.text((80,46), badge_text, font=badge_font, fill=(255,255,255))
    # title
    title_font = load_font(64, bold=True)
    title_lines = wrap_text(slide["titulo"], title_font, W-120, draw)
    y = 130
    for line in title_lines:
        draw.text((60, y), line, font=title_font, fill=(30,20,60))
        y += 78
    # divider
    draw.rectangle([60, y+10, 260, y+16], fill=(124,58,237))
    y += 40
    # bullets
    bullet_font = load_font(40)
    for b in slide["bullets"]:
        # bullet marker
        draw.ellipse([60, y+14, 84, y+38], fill=(124,58,237))
        lines = wrap_text(b, bullet_font, W-140, draw)
        for li, line in enumerate(lines):
            draw.text((100, y), line, font=bullet_font, fill=(50,40,80))
            y += 52
        y += 12
    # footer
    foot_font = load_font(24)
    draw.text((60, H-60), "Curso Gratuito de Claude  •  claude.ai", font=foot_font, fill=(120,100,160))
    # slide counter
    counter = f"{idx+1}/{len(aula['slides'])}"
    cb = draw.textbbox((0,0), counter, font=foot_font)
    draw.text((W-60-cb[2], H-60), counter, font=foot_font, fill=(120,100,160))
    return img

def main():
    for aula in AULAS:
        outdir = os.path.join(BASE, "assets", "images", f"aula-{aula['id']}")
        os.makedirs(outdir, exist_ok=True)
        for i, slide in enumerate(aula["slides"]):
            img = make_slide(aula, slide, i)
            img.save(os.path.join(outdir, f"slide-{i:02d}.png"), "PNG", optimize=True)
            print(f"Aula {aula['id']} slide {i} OK")
    print("DONE")

main()

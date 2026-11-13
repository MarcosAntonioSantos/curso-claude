import os, sys, math
sys.path.insert(0, os.path.dirname(__file__))
from roteiros import AULAS
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE = r"C:\Users\Windows 11\Documents\Default Project\curso-claude"
W, H = 1920, 1080

def load_font(size, bold=False, mono=False):
    if mono:
        cands = [r"C:\Windows\Fonts\consola.ttf", r"C:\Windows\Fonts\cour.ttf"]
    elif bold:
        cands = [r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\calibrib.ttf"]
    else:
        cands = [r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\arial.ttf", r"C:\Windows\Fonts\calibri.ttf"]
    for c in cands:
        if os.path.exists(c):
            try: return ImageFont.truetype(c, size)
            except: pass
    return ImageFont.load_default()

def gradient_bg(draw, w, h, c1, c2):
    for y in range(h):
        t = y/(h-1)
        r=int(c1[0]+(c2[0]-c1[0])*t); g=int(c1[1]+(c2[1]-c1[1])*t); b=int(c1[2]+(c2[2]-c1[2])*t)
        draw.line([(0,y),(w,y)], fill=(r,g,b))

def wrap_text(text, font, max_width, draw):
    words = text.split(); lines=[]; cur=""
    for w in words:
        test=(cur+" "+w).strip()
        bbox=draw.textbbox((0,0),test,font=font)
        if bbox[2]-bbox[0] <= max_width: cur=test
        else:
            if cur: lines.append(cur)
            cur=w
    if cur: lines.append(cur)
    return lines

def draw_mockup(img, draw, kind, x, y, w, h):
    # mockup container
    draw.rounded_rectangle([x,y,x+w,y+h], radius=16, fill=(255,255,255), outline=(200,190,220), width=2)
    # title bar
    draw.rounded_rectangle([x,y,x+w,y+36], radius=16, fill=(230,225,245))
    draw.rectangle([x,y+20,x+w,y+36], fill=(230,225,245))
    # dots
    for i,c in enumerate([(255,95,87),(255,189,46),(39,201,63)]):
        draw.ellipse([x+12+i*22, y+10, x+26+i*22, y+24], fill=c)
    inner_y = y+46
    if kind == "chat":
        # messages
        msgs = [("user","Olá, quero aumentar vendas da minha padaria.", (220,230,255)),
                ("claude","Claro! Aqui estão 3 ideias: 1) Clube de fidelidade...", (245,240,255))]
        yy = inner_y
        for who,txt,bg in msgs:
            bw = w-40
            lines = wrap_text(txt, load_font(20), bw-20, draw)
            bh = 16 + len(lines)*26
            if who=="user":
                draw.rounded_rectangle([x+20, yy, x+w-20, yy+bh], radius=12, fill=bg)
                for li,line in enumerate(lines): draw.text((x+30,yy+8+li*26), line, font=load_font(20), fill=(30,30,60))
            else:
                draw.rounded_rectangle([x+20, yy, x+w-20, yy+bh], radius=12, fill=bg)
                draw.text((x+30,yy+8), "Claude:", font=load_font(20,bold=True), fill=(90,60,160))
                for li,line in enumerate(lines): draw.text((x+30,yy+34+li*26), line, font=load_font(20), fill=(40,30,70))
            yy += bh + 12
    elif kind == "login":
        draw.text((x+20, inner_y), "Entrar", font=load_font(26,bold=True), fill=(40,30,70))
        draw.rounded_rectangle([x+20, inner_y+44, x+w-20, inner_y+80], radius=8, fill=(245,245,250), outline=(200,190,220))
        draw.text((x+30, inner_y+52), "email@exemplo.com", font=load_font(20), fill=(150,140,170))
        draw.rounded_rectangle([x+20, inner_y+92, x+w-20, inner_y+128], radius=8, fill=(245,245,250), outline=(200,190,220))
        draw.text((x+30, inner_y+100), "••••••••", font=load_font(20), fill=(150,140,170))
        draw.rounded_rectangle([x+20, inner_y+144, x+w-20, inner_y+180], radius=8, fill=(124,58,237))
        draw.text((x+w//2-30, inner_y+152), "Entrar", font=load_font(20,bold=True), fill=(255,255,255))
    elif kind == "interface":
        # sidebar
        draw.rectangle([x, inner_y, x+180, y+h], fill=(240,235,250))
        draw.text((x+16, inner_y+12), "Conversas", font=load_font(18,bold=True), fill=(90,60,160))
        for i in range(4):
            draw.rounded_rectangle([x+12, inner_y+44+i*44, x+168, inner_y+80+i*44], radius=8, fill=(255,255,255))
        # top bar
        draw.rectangle([x+180, inner_y, x+w, inner_y+40], fill=(250,248,255))
        draw.text((x+200, inner_y+10), "Seletor de modelo ▾", font=load_font(18), fill=(90,60,160))
        # chat area
        draw.text((x+200, inner_y+60), "Campo de mensagem...", font=load_font(18), fill=(160,150,180))
        draw.rounded_rectangle([x+200, y+h-60, x+w-20, y+h-20], radius=20, fill=(245,245,250), outline=(200,190,220))
    elif kind == "terminal":
        draw.rectangle([x+2, inner_y, x+w-2, y+h-2], fill=(15,15,25))
        lines = ["$ npm install -g @anthropic-ai/claude-code", "added 1 package", "$ claude", "Welcome to Claude Code!", "> /help"]
        yy = inner_y+10
        for ln in lines:
            col = (80,220,120) if ln.startswith("$") else (220,220,240)
            draw.text((x+14, yy), ln, font=load_font(18,mono=True), fill=col)
            yy += 26
    elif kind == "prompt":
        # colored blocks
        blocks = [("Contexto", (59,130,246)), ("Papel", (34,197,94)), ("Formato", (249,115,22))]
        yy = inner_y
        for label,col in blocks:
            draw.rounded_rectangle([x+16, yy, x+w-16, yy+52], radius=8, fill=col)
            draw.text((x+28, yy+14), label, font=load_font(20,bold=True), fill=(255,255,255))
            yy += 62
    elif kind == "artefato-todo":
        draw.text((x+20, inner_y), "Minhas Tarefas", font=load_font(24,bold=True), fill=(40,30,70))
        for i,txt in enumerate(["Estudar Claude","Fazer exercício","Tomar café"]):
            draw.rounded_rectangle([x+20, inner_y+40+i*46, x+w-20, inner_y+78+i*46], radius=8, fill=(245,245,250), outline=(200,190,220))
            draw.text((x+32, inner_y+50+i*46), txt, font=load_font(20), fill=(40,30,70))
            draw.text((x+w-40, inner_y+50+i*46), "✕", font=load_font(20,bold=True), fill=(220,80,80))
        draw.rounded_rectangle([x+20, inner_y+40+3*46, x+w-20, inner_y+78+3*46], radius=8, fill=(124,58,237))
        draw.text((x+32, inner_y+50+3*46), "+ Adicionar tarefa", font=load_font(20,bold=True), fill=(255,255,255))
    elif kind == "artefato":
        draw.text((x+20, inner_y), "Artefato", font=load_font(24,bold=True), fill=(40,30,70))
        draw.rounded_rectangle([x+20, inner_y+40, x+w-20, y+h-20], radius=8, fill=(245,245,250), outline=(200,190,220))
        draw.text((x+32, inner_y+52), "<!-- código gerado -->", font=load_font(16,mono=True), fill=(120,100,160))
    elif kind == "conectores":
        apps = ["Drive","Gmail","Slack","GitHub","Notion","Calendar"]
        yy = inner_y
        for a in apps:
            draw.rounded_rectangle([x+16, yy, x+w-16, yy+36], radius=8, fill=(245,245,250), outline=(200,190,220))
            draw.text((x+28, yy+8), a, font=load_font(18), fill=(40,30,70))
            draw.ellipse([x+w-40, yy+10, x+w-24, yy+26], fill=(34,197,94))
            yy += 46
    elif kind == "conector-exemplo":
        draw.text((x+16, inner_y), "Você: resuma meus e-mails não lidos", font=load_font(18), fill=(40,30,70))
        draw.rounded_rectangle([x+16, inner_y+30, x+w-16, inner_y+120], radius=8, fill=(245,240,255))
        draw.text((x+28, inner_y+40), "Claude: você tem 5 e-mails não lidos:", font=load_font(18,bold=True), fill=(90,60,160))
        for i,t in enumerate(["1. Reunião amanhã às 10h","2. Fatura do cartão","3. Convite para evento"]):
            draw.text((x+28, inner_y+66+i*22), t, font=load_font(16), fill=(60,50,90))
    elif kind == "cowork":
        draw.text((x+20, inner_y), "Projeto: Campanha Q4", font=load_font(22,bold=True), fill=(40,30,70))
        for i,av in enumerate(["Ana","Bruno","Carla"]):
            draw.ellipse([x+20+i*70, inner_y+40, x+60+i*70, inner_y+80], fill=(124,58,237))
            draw.text((x+28+i*70, inner_y+52), av[0], font=load_font(20,bold=True), fill=(255,255,255))
        draw.rounded_rectangle([x+20, inner_y+100, x+w-20, inner_y+160], radius=8, fill=(245,245,250), outline=(200,190,220))
        draw.text((x+32, inner_y+112), "Briefing, persona, tom de voz", font=load_font(18), fill=(90,60,160))
    elif kind == "terminal-install":
        draw.rectangle([x+2, inner_y, x+w-2, y+h-2], fill=(15,15,25))
        lines = ["$ npm install -g @anthropic-ai/claude-code", "added 1 package in 3s", "$ claude", "✓ Autenticado com sucesso"]
        yy = inner_y+10
        for ln in lines:
            col = (80,220,120) if ln.startswith("$") else (220,220,240)
            if "✓" in ln: col=(80,220,120)
            draw.text((x+14, yy), ln, font=load_font(18,mono=True), fill=col)
            yy += 26
    elif kind == "terminal-commands":
        draw.rectangle([x+2, inner_y, x+w-2, y+h-2], fill=(15,15,25))
        lines = ["> /help", "Comandos disponíveis...", "> /init", "Criando CLAUDE.md...", "> adicione validação", "Implementando..."]
        yy = inner_y+10
        for ln in lines:
            col = (80,220,120) if ln.startswith(">") else (220,220,240)
            draw.text((x+14, yy), ln, font=load_font(18,mono=True), fill=col)
            yy += 26
    elif kind == "terminal-task":
        draw.rectangle([x+2, inner_y, x+w-2, y+h-2], fill=(15,15,25))
        lines = ["> crie uma página HTML", "Criando index.html...", "✓ Arquivo criado", "Abra no navegador"]
        yy = inner_y+10
        for ln in lines:
            col = (80,220,120) if ">" in ln or "✓" in ln else (220,220,240)
            draw.text((x+14, yy), ln, font=load_font(18,mono=True), fill=col)
            yy += 26
    elif kind == "terminal":
        draw.rectangle([x+2, inner_y, x+w-2, y+h-2], fill=(15,15,25))
        lines = ["$ claude", "Welcome to Claude Code", "> /help", "> /init"]
        yy = inner_y+10
        for ln in lines:
            col = (80,220,120) if ln.startswith("$") or ln.startswith(">") else (220,220,240)
            draw.text((x+14, yy), ln, font=load_font(18,mono=True), fill=col)
            yy += 26
    elif kind == "projeto":
        draw.text((x+20, inner_y), "Projeto: Marketing", font=load_font(22,bold=True), fill=(40,30,70))
        draw.rounded_rectangle([x+20, inner_y+40, x+w-20, inner_y+80], radius=8, fill=(245,245,250), outline=(200,190,220))
        draw.text((x+32, inner_y+50), "Voz da marca, públicos, docs", font=load_font(18), fill=(90,60,160))
        for i in range(3):
            draw.rounded_rectangle([x+20, inner_y+96+i*44, x+w-20, inner_y+132+i*44], radius=8, fill=(255,255,255), outline=(200,190,220))
            draw.text((x+32, inner_y+106+i*44), f"Conversa {i+1}", font=load_font(18), fill=(40,30,70))
    elif kind == "chat-resposta":
        draw.text((x+16, inner_y), "Você: ideias para padaria", font=load_font(18), fill=(40,30,70))
        draw.rounded_rectangle([x+16, inner_y+30, x+w-16, inner_y+130], radius=8, fill=(245,240,255))
        draw.text((x+28, inner_y+40), "Claude:", font=load_font(18,bold=True), fill=(90,60,160))
        for i,t in enumerate(["1. Clube de fidelidade","2. Parceria com cafeterias","3. Vídeos dos bastidores"]):
            draw.text((x+28, inner_y+66+i*22), t, font=load_font(16), fill=(60,50,90))
    elif kind == "claude-md":
        draw.text((x+20, inner_y), "CLAUDE.md", font=load_font(22,bold=True), fill=(40,30,70))
        lines = ["# Stack","- HTML, CSS, JS","","# Regras","- Usuário logado","","# Comandos","- npm run dev"]
        yy = inner_y+36
        for ln in lines:
            draw.text((x+20, yy), ln, font=load_font(16,mono=True), fill=(60,50,90))
            yy += 22
    elif kind == "claude-md-exemplo":
        draw.rectangle([x+2, inner_y, x+w-2, y+h-2], fill=(245,245,250))
        lines = ["# CLAUDE.md","","## Stack","- HTML, CSS, JS","- localStorage","","## Padrões","- Funções pequenas","","## Regras","- Usuário logado","","## Comandos","- Abrir index.html"]
        yy = inner_y+10
        for ln in lines:
            draw.text((x+14, yy), ln, font=load_font(16,mono=True), fill=(60,50,90))
            yy += 22
    elif kind == "fluxo":
        steps = ["Prompt","Código","Diff","Commit"]
        yy = inner_y
        for i,s in enumerate(steps):
            draw.rounded_rectangle([x+20, yy, x+w-20, yy+44], radius=8, fill=(124,58,237) if i==0 else (245,245,250), outline=(124,58,237))
            col = (255,255,255) if i==0 else (90,60,160)
            draw.text((x+32, yy+12), f"{i+1}. {s}", font=load_font(20,bold=True), fill=col)
            yy += 56
    elif kind == "git":
        draw.rectangle([x+2, inner_y, x+w-2, y+h-2], fill=(15,15,25))
        lines = ["$ git checkout -b feature/login","$ git add .","$ git commit -m \"login\"","$ git push origin feature/login"]
        yy = inner_y+10
        for ln in lines:
            draw.text((x+14, yy), ln, font=load_font(16,mono=True), fill=(80,220,120))
            yy += 26

def make_slide(aula, slide, idx):
    img = Image.new("RGB", (W,H))
    draw = ImageDraw.Draw(img)
    palettes = {1:((253,242,248),(237,233,254)),2:((239,246,255),(224,242,254)),
                3:((240,253,244),(209,250,229)),4:((255,251,235),(254,243,199))}
    c1,c2 = palettes.get(aula["id"], ((253,242,248),(237,233,254)))
    gradient_bg(draw, W, H, c1, c2)
    # decorative circles
    for (cx,cy,r,col) in [(1720,140,200,(255,255,255,50)),(180,920,240,(255,255,255,40)),(1620,920,130,(255,200,220,60))]:
        overlay = Image.new("RGBA",(W,H),(0,0,0,0))
        od = ImageDraw.Draw(overlay)
        od.ellipse([cx-r,cy-r,cx+r,cy+r], fill=col)
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(img)
    draw.rectangle([0,0,W,8], fill=(124,58,237))
    badge_font = load_font(26, bold=True)
    badge_text = f"AULA {aula['id']}  •  {aula['data']}"
    bb = draw.textbbox((0,0),badge_text,font=badge_font)
    draw.rounded_rectangle([60,40,60+bb[2]+36,84], radius=22, fill=(124,58,237))
    draw.text((78,46), badge_text, font=badge_font, fill=(255,255,255))
    title_font = load_font(56, bold=True)
    title_lines = wrap_text(slide["titulo"], title_font, W-120, draw)
    y = 120
    for line in title_lines:
        draw.text((60,y), line, font=title_font, fill=(30,20,60)); y += 68
    draw.rectangle([60, y+6, 260, y+12], fill=(124,58,237)); y += 34
    # layout: left content (bullets) + right mockup/code
    content_w = 760
    bullet_font = load_font(34)
    for b in slide["bullets"]:
        draw.ellipse([60, y+12, 82, y+34], fill=(124,58,237))
        lines = wrap_text(b, bullet_font, content_w-40, draw)
        for li,line in enumerate(lines):
            draw.text((96, y), line, font=bullet_font, fill=(50,40,80)); y += 44
        y += 10
    # right panel
    rx, ry, rw, rh = 860, 130, 1000, 760
    mockup = slide.get("mockup")
    codigo = slide.get("codigo")
    if mockup:
        draw_mockup(img, draw, mockup, rx, ry, rw, rh)
    elif codigo:
        # code block
        draw.rounded_rectangle([rx,ry,rx+rw,ry+rh], radius=16, fill=(20,20,35))
        draw.rectangle([rx,ry,rx+rw,ry+36], fill=(40,40,60))
        draw.text((rx+16, ry+8), "exemplo", font=load_font(16,mono=True), fill=(180,180,200))
        cy = ry+46
        for ln in codigo.split("\n"):
            draw.text((rx+16, cy), ln, font=load_font(20,mono=True), fill=(180,220,180))
            cy += 28
    else:
        # decorative card
        draw.rounded_rectangle([rx,ry,rx+rw,ry+rh], radius=16, fill=(255,255,255,180) if False else (250,248,255))
        draw.text((rx+40, ry+rh//2-20), "💡", font=load_font(80), fill=(124,58,237))
    # footer
    foot_font = load_font(22)
    draw.text((60, H-50), "Curso Gratuito de Claude  •  claude.ai", font=foot_font, fill=(120,100,160))
    counter = f"{idx+1}/{len(aula['slides'])}"
    cb = draw.textbbox((0,0), counter, font=foot_font)
    draw.text((W-60-cb[2], H-50), counter, font=foot_font, fill=(120,100,160))
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

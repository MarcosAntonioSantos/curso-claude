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
        cands = [r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\arialbd.ttf"]
    else:
        cands = [r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\arial.ttf"]
    for c in cands:
        if os.path.exists(c):
            try: return ImageFont.truetype(c, size)
            except: pass
    return ImageFont.load_default()

def gradient_bg(draw, img, w, h, c1, c2, c3=None):
    for y in range(h):
        t = y/(h-1)
        if c3:
            if t < 0.5:
                tt = t*2
                r=int(c1[0]+(c2[0]-c1[0])*tt); g=int(c1[1]+(c2[1]-c1[1])*tt); b=int(c1[2]+(c2[2]-c1[2])*tt)
            else:
                tt = (t-0.5)*2
                r=int(c2[0]+(c3[0]-c2[0])*tt); g=int(c2[1]+(c3[1]-c2[1])*tt); b=int(c2[2]+(c3[2]-c2[2])*tt)
        else:
            r=int(c1[0]+(c2[0]-c1[0])*t); g=int(c1[1]+(c2[1]-c1[1])*t); b=int(c1[2]+(c2[2]-c1[2])*t)
        draw.line([(0,y),(w,y)], fill=(r,g,b))

def add_dots(img, spacing=40, color=(255,255,255,25)):
    overlay = Image.new("RGBA",(W,H),(0,0,0,0))
    od = ImageDraw.Draw(overlay)
    for x in range(0,W,spacing):
        for y in range(0,H,spacing):
            od.ellipse([x-1,y-1,x+1,y+1], fill=color)
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

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

def shadow_text(draw, x, y, text, font, fill, shadow=(0,0,0,80), off=3):
    draw.text((x+off,y+off), text, font=font, fill=shadow)
    draw.text((x,y), text, font=font, fill=fill)

def draw_mockup(img, draw, kind, x, y, w, h):
    # shadow
    sh = Image.new("RGBA",(W,H),(0,0,0,0))
    sd = ImageDraw.Draw(sh)
    sd.rounded_rectangle([x+8,y+8,x+w+8,y+h+8], radius=20, fill=(0,0,0,60))
    sh = sh.filter(ImageFilter.GaussianBlur(12))
    img2 = Image.alpha_composite(img.convert("RGBA"), sh).convert("RGB")
    # copy back
    img.paste(img2)
    draw = ImageDraw.Draw(img)
    # container
    draw.rounded_rectangle([x,y,x+w,y+h], radius=18, fill=(255,255,255), outline=(220,210,240), width=2)
    draw.rounded_rectangle([x,y,x+w,y+40], radius=18, fill=(235,230,250))
    draw.rectangle([x,y+24,x+w,y+40], fill=(235,230,250))
    for i,c in enumerate([(255,95,87),(255,189,46),(39,201,63)]):
        draw.ellipse([x+14+i*24, y+12, x+28+i*24, y+26], fill=c)
    inner = y+50
    # dispatch
    if kind in ("chat","chat-resposta"):
        msgs = [("user","Olá, quero aumentar vendas da minha padaria.",(219,234,254)),
                ("claude","Claro! 1) Clube de fidelidade 2) Parceria com cafeterias 3) Vídeos dos bastidores",(243,232,255))]
        yy = inner
        for who,txt,bg in msgs:
            bh = 16 + len(wrap_text(txt, load_font(20), w-30, draw))*26
            draw.rounded_rectangle([x+16,yy,x+w-16,yy+bh], radius=12, fill=bg)
            if who=="user":
                for li,line in enumerate(wrap_text(txt, load_font(20), w-30, draw)):
                    draw.text((x+26,yy+8+li*26), line, font=load_font(20), fill=(30,41,59))
            else:
                draw.text((x+26,yy+8), "Claude", font=load_font(20,bold=True), fill=(109,40,217))
                for li,line in enumerate(wrap_text(txt, load_font(20), w-30, draw)):
                    draw.text((x+26,yy+34+li*26), line, font=load_font(20), fill=(55,48,107))
            yy += bh + 14
    elif kind == "login":
        draw.text((x+20,inner), "Entrar", font=load_font(28,bold=True), fill=(30,20,60))
        for i,ph in enumerate(["email@exemplo.com","••••••••"]):
            yy = inner+44+i*48
            draw.rounded_rectangle([x+20,yy,x+w-20,yy+36], radius=10, fill=(248,248,252), outline=(200,190,220))
            draw.text((x+30,yy+8), ph, font=load_font(20), fill=(160,150,180))
        draw.rounded_rectangle([x+20,inner+144,x+w-20,inner+180], radius=10, fill=(124,58,237))
        draw.text((x+w//2-32,inner+152), "Entrar", font=load_font(20,bold=True), fill=(255,255,255))
    elif kind == "interface":
        draw.rectangle([x,inner,x+200,y+h], fill=(237,233,254))
        draw.text((x+16,inner+12), "Conversas", font=load_font(18,bold=True), fill=(90,60,160))
        for i in range(5):
            draw.rounded_rectangle([x+12,inner+44+i*40,x+188,inner+76+i*40], radius=8, fill=(255,255,255))
        draw.rectangle([x+200,inner,x+w,inner+44], fill=(250,248,255))
        draw.text((x+220,inner+12), "Seletor de modelo ▾", font=load_font(18), fill=(90,60,160))
        draw.rounded_rectangle([x+220,y+h-56,x+w-20,y+h-16], radius=20, fill=(245,245,250), outline=(200,190,220))
        draw.text((x+240,y+h-44), "Digite sua mensagem...", font=load_font(18), fill=(160,150,180))
    elif kind and kind.startswith("terminal"):
        draw.rectangle([x+2,inner,x+w-2,y+h-2], fill=(18,18,30))
        tlines = {
            "terminal":["$ claude","Welcome to Claude Code","> /help","> /init"],
            "terminal-install":["$ npm install -g @anthropic-ai/claude-code","added 1 package in 3s","$ claude","✓ Autenticado com sucesso"],
            "terminal-commands":["> /help","Comandos disponíveis...","/init","Criando CLAUDE.md...","adicione validação","Implementando..."],
            "terminal-task":["> crie uma página HTML","Criando index.html...","✓ Arquivo criado","Abra no navegador"],
        }.get(kind, ["$ claude"])
        yy = inner+12
        for ln in tlines:
            col = (110,230,140) if (ln.startswith("$") or ln.startswith(">") or "✓" in ln) else (200,210,240)
            draw.text((x+16,yy), ln, font=load_font(18,mono=True), fill=col)
            yy += 28
    elif kind == "prompt":
        yy = inner
        for label,col in [("Contexto",(59,130,246)),("Papel",(34,197,94)),("Formato",(249,115,22))]:
            draw.rounded_rectangle([x+16,yy,x+w-16,yy+56], radius=10, fill=col)
            draw.text((x+28,yy+16), label, font=load_font(22,bold=True), fill=(255,255,255))
            yy += 68
    elif kind == "artefato-todo":
        draw.text((x+20,inner), "Minhas Tarefas", font=load_font(26,bold=True), fill=(30,20,60))
        for i,txt in enumerate(["Estudar Claude","Fazer exercício","Tomar café"]):
            yy = inner+44+i*50
            draw.rounded_rectangle([x+20,yy,x+w-20,yy+40], radius=10, fill=(248,248,252), outline=(200,190,220))
            draw.text((x+32,yy+10), txt, font=load_font(20), fill=(30,20,60))
            draw.text((x+w-40,yy+10), "×", font=load_font(20,bold=True), fill=(220,80,80))
        yy = inner+44+3*50
        draw.rounded_rectangle([x+20,yy,x+w-20,yy+40], radius=10, fill=(124,58,237))
        draw.text((x+32,yy+10), "+ Adicionar tarefa", font=load_font(20,bold=True), fill=(255,255,255))
    elif kind == "artefato":
        draw.text((x+20,inner), "Artefato", font=load_font(26,bold=True), fill=(30,20,60))
        draw.rounded_rectangle([x+20,inner+44,x+w-20,y+h-20], radius=10, fill=(248,248,252), outline=(200,190,220))
        draw.text((x+32,inner+56), "<!-- código gerado -->", font=load_font(16,mono=True), fill=(120,100,160))
    elif kind == "conectores":
        yy = inner
        for a in ["Drive","Gmail","Slack","GitHub","Notion","Calendar"]:
            draw.rounded_rectangle([x+16,yy,x+w-16,yy+40], radius=10, fill=(248,248,252), outline=(200,190,220))
            draw.text((x+28,yy+10), a, font=load_font(20), fill=(30,20,60))
            draw.ellipse([x+w-42,yy+12,x+w-26,yy+28], fill=(34,197,94))
            yy += 48
    elif kind == "conector-exemplo":
        draw.text((x+16,inner), "Você: resuma meus e-mails não lidos", font=load_font(18), fill=(30,20,60))
        draw.rounded_rectangle([x+16,inner+30,x+w-16,inner+120], radius=10, fill=(243,232,255))
        draw.text((x+28,inner+40), "Claude: você tem 5 e-mails não lidos:", font=load_font(18,bold=True), fill=(109,40,217))
        for i,t in enumerate(["1. Reunião amanhã às 10h","2. Fatura do cartão","3. Convite para evento"]):
            draw.text((x+28,inner+66+i*24), t, font=load_font(16), fill=(55,48,107))
    elif kind == "cowork":
        draw.text((x+20,inner), "Projeto: Campanha Q4", font=load_font(24,bold=True), fill=(30,20,60))
        for i,av in enumerate(["Ana","Bruno","Carla"]):
            draw.ellipse([x+20+i*74,inner+44,x+64+i*74,inner+88], fill=(124,58,237))
            draw.text((x+34+i*74,inner+56), av[0], font=load_font(22,bold=True), fill=(255,255,255))
        draw.rounded_rectangle([x+20,inner+104,x+w-20,inner+164], radius=10, fill=(248,248,252), outline=(200,190,220))
        draw.text((x+32,inner+116), "Briefing, persona, tom de voz", font=load_font(18), fill=(109,40,217))
    elif kind == "projeto":
        draw.text((x+20,inner), "Projeto: Marketing", font=load_font(24,bold=True), fill=(30,20,60))
        draw.rounded_rectangle([x+20,inner+44,x+w-20,inner+84], radius=10, fill=(248,248,252), outline=(200,190,220))
        draw.text((x+32,inner+56), "Voz da marca, públicos, docs", font=load_font(18), fill=(109,40,217))
        for i in range(3):
            draw.rounded_rectangle([x+20,inner+100+i*48,x+w-20,inner+136+i*48], radius=10, fill=(255,255,255), outline=(200,190,220))
            draw.text((x+32,inner+110+i*48), f"Conversa {i+1}", font=load_font(18), fill=(30,20,60))
    elif kind == "chat-resposta":
        draw.text((x+16,inner), "Você: ideias para padaria", font=load_font(18), fill=(30,20,60))
        draw.rounded_rectangle([x+16,inner+30,x+w-16,inner+130], radius=10, fill=(243,232,255))
        draw.text((x+28,inner+40), "Claude:", font=load_font(18,bold=True), fill=(109,40,217))
        for i,t in enumerate(["1. Clube de fidelidade","2. Parceria com cafeterias","3. Vídeos dos bastidores"]):
            draw.text((x+28,inner+66+i*24), t, font=load_font(16), fill=(55,48,107))
    elif kind in ("claude-md","claude-md-exemplo"):
        draw.text((x+20,inner), "CLAUDE.md", font=load_font(24,bold=True), fill=(30,20,60))
        lines = ["# Stack","- HTML, CSS, JS","- localStorage","","# Regras","- Usuário logado","","# Comandos","- Abrir index.html"]
        yy = inner+36
        draw.rectangle([x+2,inner+34,x+w-2,y+h-2], fill=(248,248,252))
        for ln in lines:
            draw.text((x+16,yy), ln, font=load_font(16,mono=True), fill=(60,50,90))
            yy += 24
    elif kind == "fluxo":
        steps = ["1. Prompt","2. Código","3. Diff","4. Commit"]
        yy = inner
        for i,s in enumerate(steps):
            draw.rounded_rectangle([x+20,yy,x+w-20,yy+48], radius=10, fill=(124,58,237) if i==0 else (248,248,252), outline=(124,58,237))
            col = (255,255,255) if i==0 else (90,60,160)
            draw.text((x+32,yy+12), s, font=load_font(20,bold=True), fill=col)
            yy += 60
    elif kind == "git":
        draw.rectangle([x+2,inner,x+w-2,y+h-2], fill=(18,18,30))
        lines = ["$ git checkout -b feature/login","$ git add .","$ git commit -m \"login\"","$ git push origin feature/login"]
        yy = inner+12
        for ln in lines:
            draw.text((x+16,yy), ln, font=load_font(16,mono=True), fill=(110,230,140))
            yy += 28

def make_slide(aula, slide, idx):
    img = Image.new("RGB", (W,H))
    draw = ImageDraw.Draw(img)
    palettes = {1:((255,240,245),(230,225,250),(200,210,255)),
                2:((235,245,255),(220,235,255),(200,225,255)),
                3:((235,252,240),(215,245,225),(195,240,215)),
                4:((255,248,230),(255,235,200),(255,220,170))}
    c1,c2,c3 = palettes.get(aula["id"], palettes[1])
    gradient_bg(draw, img, W, H, c1, c2, c3)
    img = add_dots(img, 50, (255,255,255,30))
    draw = ImageDraw.Draw(img)
    # top bar gradient
    for x in range(W):
        t = x/W
        r=int(124+(192-124)*t); g=int(58+(132-58)*t); b=int(237+(252-237)*t)
        draw.line([(x,0),(x,10)], fill=(r,g,b))
    # badge with glow
    badge_font = load_font(26, bold=True)
    badge_text = f"AULA {aula['id']}  •  {aula['data']}"
    bb = draw.textbbox((0,0),badge_text,font=badge_font)
    bw = bb[2]+36
    # glow
    glow = Image.new("RGBA",(W,H),(0,0,0,0))
    gd = ImageDraw.Draw(glow)
    gd.rounded_rectangle([56,36,56+bw+8,88], radius=26, fill=(124,58,237,60))
    glow = glow.filter(ImageFilter.GaussianBlur(8))
    img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([60,40,60+bw,84], radius=22, fill=(124,58,237))
    draw.text((78,46), badge_text, font=badge_font, fill=(255,255,255))
    # title
    title_font = load_font(58, bold=True)
    title_lines = wrap_text(slide["titulo"], title_font, 760, draw)
    y = 120
    for line in title_lines:
        shadow_text(draw, 60, y, line, title_font, (30,20,60))
        y += 70
    # accent line
    draw.rounded_rectangle([60, y+4, 280, y+12], radius=4, fill=(124,58,237))
    y += 36
    # bullets
    bullet_font = load_font(34)
    for b in slide["bullets"]:
        # bullet icon
        draw.ellipse([60, y+10, 84, y+34], fill=(124,58,237))
        draw.text((66, y+8), "✓", font=load_font(20,bold=True), fill=(255,255,255))
        lines = wrap_text(b, bullet_font, 700, draw)
        for li,line in enumerate(lines):
            draw.text((96, y+li*42), line, font=bullet_font, fill=(40,30,70))
        y += 44*max(1,len(lines)) + 12
    # right panel with shadow
    rx, ry, rw, rh = 880, 120, 980, 780
    sh = Image.new("RGBA",(W,H),(0,0,0,0))
    sd = ImageDraw.Draw(sh)
    sd.rounded_rectangle([rx+10,ry+10,rx+rw+10,ry+rh+10], radius=22, fill=(0,0,0,70))
    sh = sh.filter(ImageFilter.GaussianBlur(14))
    img = Image.alpha_composite(img.convert("RGBA"), sh).convert("RGB")
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([rx,ry,rx+rw,ry+rh], radius=20, fill=(255,255,255), outline=(220,210,240), width=2)
    mockup = slide.get("mockup")
    codigo = slide.get("codigo")
    if mockup:
        draw_mockup(img, draw, mockup, rx+16, ry+16, rw-32, rh-32)
    elif codigo:
        draw.rectangle([rx+16, ry+16, rx+rw-16, ry+rh-16], fill=(20,24,40))
        draw.text((rx+28, ry+24), "exemplo", font=load_font(16,mono=True), fill=(140,150,180))
        cy = ry+56
        for ln in codigo.split("\n"):
            draw.text((rx+28, cy), ln, font=load_font(20,mono=True), fill=(130,220,170))
            cy += 28
    else:
        # decorative
        draw.text((rx+rw//2-40, ry+rh//2-50), "💡", font=load_font(100), fill=(124,58,237))
    # footer bar
    draw.rectangle([0,H-46,W,H], fill=(255,255,255,180) if False else (248,245,255))
    draw.line([(0,H-46),(W,H-46)], fill=(200,190,220), width=1)
    foot_font = load_font(20)
    draw.text((60,H-32), "Curso Gratuito de Claude  •  claude.ai", font=foot_font, fill=(120,100,160))
    counter = f"{idx+1} / {len(aula['slides'])}"
    cb = draw.textbbox((0,0), counter, font=foot_font)
    draw.text((W-60-cb[2], H-32), counter, font=foot_font, fill=(120,100,160))
    # progress bar
    prog = (idx+1)/len(aula['slides'])
    draw.rectangle([0,H-48,int(W*prog),H-46], fill=(124,58,237))
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

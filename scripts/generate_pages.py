import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from roteiros import AULAS
BASE = r"C:\Users\Windows 11\Documents\Default Project\curso-claude"

def transcript_html(aula):
    out = []
    for slide in aula["slides"]:
        out.append(f"<div class='t-slide'><strong>{slide['titulo']}</strong><p>{slide['narracao']}</p></div>")
    return "\n".join(out)

template = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Aula {id} — {titulo} | Curso Gratuito de Claude</title>
<meta name="description" content="{titulo}. Aula {id} do Curso Gratuito de Claude.">
<meta name="robots" content="index,follow">
<link rel="canonical" href="https://marcosantoniosantos.github.io/curso-claude/aulas/aula-{id}.html">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../assets/css/style.css">
</head>
<body>
<nav>
  <div class="inner">
    <a class="logo" href="../index.html">Claude · Curso Gratuito</a>
    <div class="nav-links">
      <a href="../index.html#aulas">Aulas</a>
      <a href="../index.html">Início</a>
    </div>
    <a class="nav-cta" href="../index.html#inscricao">Inscrever-se</a>
  </div>
</nav>

<section class="aula-hero">
  <div class="container">
    <div class="badge"><span class="dot"></span>AULA {id} · {data}</div>
    <h1>{titulo}</h1>
    <p class="sub">Curso Gratuito de Claude · {dur} min · Vídeo, transcrição e materiais</p>
  </div>
</section>

<div class="container">
  <div class="player-wrap">
    <video controls preload="metadata" poster="../assets/images/aula-{id}/slide-00.png">
      <source src="../videos/aula-{id}.mp4" type="video/mp4">
      <track kind="subtitles" src="../legendas/aula-{id}.vtt" srclang="pt" label="Português" default>
      Seu navegador não suporta vídeo HTML5.
    </video>
  </div>

  <div class="aula-body">
    <div>
      <div class="transcript">
        <h3>Transcrição da aula</h3>
        <p>Leia ou acompanhe o conteúdo narrado no vídeo.</p>
        {transcript}
      </div>
    </div>
    <aside class="sidebar">
      <div class="card">
        <h4>Materiais da aula</h4>
        <a class="link" href="../audio/aula-{id}.mp3" download>🎧 Áudio (MP3)</a>
        <a class="link" href="../legendas/aula-{id}.vtt" download>💬 Legendas (VTT)</a>
        <a class="link" href="../videos/aula-{id}.mp4" download>📹 Vídeo (MP4)</a>
      </div>
      <div class="card">
        <h4>Materiais complementares</h4>
        <a class="link" href="../materiais/prompts-essenciais.md">📝 Prompts essenciais</a>
        <a class="link" href="../materiais/CLAUDE.md.template">📄 Template CLAUDE.md</a>
      </div>
      <div class="card">
        <h4>Exercício prático</h4>
        <p style="color:var(--muted);font-size:.9rem">Complete o exercício ao final do vídeo antes de avançar para a próxima aula.</p>
      </div>
    </aside>
  </div>

  <div class="nav-aulas">
    {prev}
    {next}
  </div>
</div>

<footer>
  <div class="container inner">
    <div>© 2026 Curso Gratuito de Claude</div>
    <div><a href="../index.html" style="color:var(--accent)">Voltar ao início</a></div>
  </div>
</footer>
</body>
</html>
"""

for i, aula in enumerate(AULAS):
    aid = aula["id"]
    # prev/next
    if i > 0:
        prev = f'<a href="aula-{AULAS[i-1]["id"]}.html"><div class="label">← Anterior</div><div class="title">{AULAS[i-1]["titulo"]}</div></a>'
    else:
        prev = '<div></div>'
    if i < len(AULAS)-1:
        nxt = f'<a href="aula-{AULAS[i+1]["id"]}.html" style="text-align:right"><div class="label">Próxima →</div><div class="title">{AULAS[i+1]["titulo"]}</div></a>'
    else:
        nxt = '<a href="../index.html" style="text-align:right"><div class="label">Concluir</div><div class="title">Voltar ao início</div></a>'
    html = template.format(
        id=aid,
        titulo=aula["titulo"],
        data=aula["data"],
        dur=aula["duracao_estimada_min"],
        transcript=transcript_html(aula),
        prev=prev,
        next=nxt,
    )
    out = os.path.join(BASE, "aulas", f"aula-{aid}.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Aula {aid} page OK")
print("DONE")

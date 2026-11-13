import os, sys, json, subprocess, asyncio
sys.path.insert(0, os.path.dirname(__file__))
from roteiros import AULAS
BASE = r"C:\Users\Windows 11\Documents\Default Project\curso-claude"

def ms_to_vtt(ms):
    h = int(ms // 3600000); m = int((ms % 3600000) // 60000)
    s = int((ms % 60000) // 1000); millis = int(ms % 1000)
    return f"{h:02d}:{m:02d}:{s:02d}.{millis:03d}"

async def gen_boundaries(text):
    import edge_tts
    c = edge_tts.Communicate(text, "pt-BR-FranciscaNeural", rate="+0%", pitch="+0Hz")
    bds = []
    async for chunk in c.stream():
        if chunk["type"] == "SentenceBoundary":
            bds.append({"text": chunk["text"], "offset_ms": chunk["offset"]/10000, "duration_ms": chunk["duration"]/10000})
    return bds

async def main():
    for aula in AULAS:
        aid = aula["id"]
        # cumulative offsets
        work = os.path.join(BASE, "audio", f"_work_{aid}")
        slide_durs = []
        for i in range(len(aula["slides"])):
            p = os.path.join(work, f"slide_{i}.mp3")
            r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1", p], capture_output=True, text=True)
            slide_durs.append(float(r.stdout.strip()))
        cum = 0.0
        lines = ["WEBVTT", "", "NOTE Legendas geradas automaticamente", ""]
        cue = 1
        for i, slide in enumerate(aula["slides"]):
            bds = await gen_boundaries(slide["narracao"])
            if not bds:
                # fallback: one cue whole slide
                end = cum + slide_durs[i]*1000
                lines.append(str(cue)); lines.append(f"{ms_to_vtt(cum)} --> {ms_to_vtt(end)}"); lines.append(slide["narracao"]); lines.append(""); cue+=1
            else:
                for b in bds:
                    start = cum + b["offset_ms"]
                    end = start + b["duration_ms"]
                    lines.append(str(cue)); lines.append(f"{ms_to_vtt(start)} --> {ms_to_vtt(end)}"); lines.append(b["text"]); lines.append(""); cue+=1
            cum += slide_durs[i]*1000 + 400
        out = os.path.join(BASE, "legendas", f"aula-{aid}.vtt")
        with open(out, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"Aula {aid}: VTT regenerado")
    print("DONE")
asyncio.run(main())

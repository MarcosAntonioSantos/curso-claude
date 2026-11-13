import asyncio, os, sys, json, subprocess
sys.path.insert(0, os.path.dirname(__file__))
from roteiros import AULAS

BASE = r"C:\Users\Windows 11\Documents\Default Project\curso-claude"
VOICE = "pt-BR-FranciscaNeural"
RATE = "+0%"
PITCH = "+0Hz"

def ms_to_vtt(ms):
    h = int(ms // 3600000)
    m = int((ms % 3600000) // 60000)
    s = int((ms % 60000) // 1000)
    millis = int(ms % 1000)
    return f"{h:02d}:{m:02d}:{s:02d}.{millis:03d}"

async def gen_slide_audio(text, out_mp3, out_boundaries):
    import edge_tts
    communicate = edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH)
    audio_bytes = bytearray()
    boundaries = []
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_bytes.extend(chunk["data"])
        elif chunk["type"] == "WordBoundary":
            boundaries.append({
                "text": chunk["text"],
                "offset_ms": chunk["offset"] / 10000,  # 100ns units -> ms
                "duration_ms": chunk["duration"] / 10000,
            })
    with open(out_mp3, "wb") as f:
        f.write(audio_bytes)
    with open(out_boundaries, "w", encoding="utf-8") as f:
        json.dump(boundaries, f, ensure_ascii=False)

async def process_aula(aula):
    aid = aula["id"]
    work = os.path.join(BASE, "audio", f"_work_{aid}")
    os.makedirs(work, exist_ok=True)
    slide_offsets = []  # cumulative ms
    cum = 0
    # first pass: generate each slide audio + boundaries
    for i, slide in enumerate(aula["slides"]):
        mp3 = os.path.join(work, f"slide_{i}.mp3")
        bd = os.path.join(work, f"slide_{i}.json")
        text = slide["narracao"]
        await gen_slide_audio(text, mp3, bd)
        # get duration
        probe = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1", mp3],
                               capture_output=True, text=True)
        dur = float(probe.stdout.strip()) if probe.stdout.strip() else 0.0
        slide_offsets.append((i, cum, dur))
        cum += dur * 1000 + 400  # 400ms pause between slides
    # concatenate audio with pauses
    # build ffmpeg concat list with silence gaps
    concat_list = os.path.join(work, "concat.txt")
    with open(concat_list, "w", encoding="utf-8") as f:
        for i, (idx, off, dur) in enumerate(slide_offsets):
            f.write(f"file '{work.replace(chr(92),'/')}/slide_{i}.mp3'\n")
            # add silence gap except last
            if i < len(slide_offsets)-1:
                sil = os.path.join(work, f"silence_{i}.mp3")
                subprocess.run(["ffmpeg","-y","-f","lavfi","-i","anullsrc=r=24000:cl=mono","-t","0.4","-q:a","9","-acodec","libmp3lame", sil],
                               capture_output=True)
                f.write(f"file '{sil.replace(chr(92),'/')}'\n")
    out_mp3 = os.path.join(BASE, "audio", f"aula-{aid}.mp3")
    subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",concat_list,"-c","copy", out_mp3], capture_output=True)
    # build VTT
    vtt_lines = ["WEBVTT", "", "NOTE Gerado automaticamente", ""]
    cue_id = 1
    for i, (idx, off, dur) in enumerate(slide_offsets):
        with open(os.path.join(work, f"slide_{i}.json"), encoding="utf-8") as f:
            bds = json.load(f)
        # group words into cues of ~8 words
        group = []
        group_start = None
        for b in bds:
            if group_start is None:
                group_start = b["offset_ms"]
            group.append(b)
            if len(group) >= 8:
                end = group[-1]["offset_ms"] + group[-1]["duration_ms"]
                text = " ".join(x["text"] for x in group)
                vtt_lines.append(str(cue_id))
                vtt_lines.append(f"{ms_to_vtt(off + group_start)} --> {ms_to_vtt(off + end)}")
                vtt_lines.append(text)
                vtt_lines.append("")
                cue_id += 1
                group = []
                group_start = None
        if group:
            end = group[-1]["offset_ms"] + group[-1]["duration_ms"]
            text = " ".join(x["text"] for x in group)
            vtt_lines.append(str(cue_id))
            vtt_lines.append(f"{ms_to_vtt(off + group_start)} --> {ms_to_vtt(off + end)}")
            vtt_lines.append(text)
            vtt_lines.append("")
            cue_id += 1
    out_vtt = os.path.join(BASE, "legendas", f"aula-{aid}.vtt")
    with open(out_vtt, "w", encoding="utf-8") as f:
        f.write("\n".join(vtt_lines))
    print(f"Aula {aid}: audio+legendas OK. duracao total ~{cum/1000:.1f}s")

async def main():
    for aula in AULAS:
        await process_aula(aula)
    print("DONE")

asyncio.run(main())

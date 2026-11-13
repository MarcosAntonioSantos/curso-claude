import os, sys, subprocess
sys.path.insert(0, os.path.dirname(__file__))
from roteiros import AULAS
BASE = r"C:\Users\Windows 11\Documents\Default Project\curso-claude"
FPS = 30
TRANS = 0.8

def slide_audio_dur(aid, i):
    p = os.path.join(BASE, "audio", f"_work_{aid}", f"slide_{i}.mp3")
    if os.path.exists(p):
        r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1", p],
                           capture_output=True, text=True)
        try: return float(r.stdout.strip())
        except: pass
    return 8.0

def make_slide_clip(aid, i, dur):
    work = os.path.join(BASE, "videos", f"_work_{aid}")
    os.makedirs(work, exist_ok=True)
    img = os.path.join(BASE, "assets", "images", f"aula-{aid}", f"slide-{i:02d}.png")
    out = os.path.join(work, f"clip_{i:02d}.mp4")
    if os.path.exists(out): os.remove(out)
    # ken burns: gradual zoom in (stable expression)
    zexpr = "min(zoom+0.0007,1.10)"
    xexpr = "iw/2-(iw/zoom/2)"
    yexpr = "ih/2-(ih/zoom/2)"
    vf = (f"zoompan=z='{zexpr}':x='{xexpr}':y='{yexpr}':d={int(dur*FPS)}:s=1920x1080:fps={FPS},"
          f"fade=t=in:st=0:d=0.6,fade=t=out:st={max(dur-0.6,0.6):.2f}:d=0.6")
    cmd = ["ffmpeg","-y","-loop","1","-i",img,"-vf",vf,"-t",f"{dur:.2f}",
           "-c:v","libx264","-preset","ultrafast","-crf","24","-pix_fmt","yuv420p","-r",str(FPS), out]
    subprocess.run(cmd, capture_output=True)
    return out

def xfade_chain(aid, clips, durs):
    work = os.path.join(BASE, "videos", f"_work_{aid}")
    # build filter_complex
    inputs = []
    for c in clips:
        inputs += ["-i", c]
    # offsets
    offsets = []
    cum = 0.0
    for i in range(len(durs)-1):
        cum += durs[i] - TRANS
        offsets.append(cum)
    # build filter
    if len(clips) == 1:
        fc = "[0:v]copy[v]"
    else:
        # chain
        parts = []
        prev = "[0:v]"
        for i in range(1, len(clips)):
            outlabel = f"[v{i}]"
            off = offsets[i-1]
            parts.append(f"{prev}[{i}:v]xfade=transition=fade:duration={TRANS}:offset={off:.2f}{outlabel}")
            prev = outlabel
        fc = ";".join(parts)
        fc += ";"+prev+"copy[v]"
    out = os.path.join(work, "video_xfade.mp4")
    cmd = ["ffmpeg","-y"] + inputs + ["-filter_complex", fc, "-map","[v]",
           "-c:v","libx264","-preset","ultrafast","-crf","24","-pix_fmt","yuv420p","-r",str(FPS), out]
    subprocess.run(cmd, capture_output=True)
    return out

def mix_audio(aid):
    work = os.path.join(BASE, "videos", f"_work_{aid}")
    aula = os.path.join(BASE, "audio", f"aula-{aid}.mp3")
    ambient = os.path.join(BASE, "audio", "ambient.mp3")
    out = os.path.join(work, "audio_mix.mp3")
    # loop ambient to match aula duration
    cmd = ["ffmpeg","-y","-i",aula,"-stream_loop","-1","-i",ambient,
           "-filter_complex","[1:a]volume=0.12,afade=t=in:st=0:d=2,afade=t=out:st=0:d=0[a1];[0:a][a1]amix=inputs=2:duration=first:dropout_transition=2[out]",
           "-map","[out]","-c:a","libmp3lame","-q:a","3", out]
    # fix filter: ambient fade out at end unknown; use simple mix
    cmd = ["ffmpeg","-y","-i",aula,"-stream_loop","-1","-i",ambient,
           "-filter_complex","[1:a]volume=0.10[a1];[0:a][a1]amix=inputs=2:duration=first[out]",
           "-map","[out]","-c:a","libmp3lame","-q:a","3", out]
    subprocess.run(cmd, capture_output=True)
    return out

def add_overlays(aid, xfade_path, audio_path, vtt_path):
    work = os.path.join(BASE, "videos", f"_work_{aid}")
    aula = [a for a in AULAS if a["id"]==aid][0]
    title = aula["titulo"]
    final = os.path.join(BASE, "videos", f"aula-{aid}.mp4")
    # lower third text + progress bar + subtitles
    # escape title for drawtext
    safe_title = title.replace(":", "\\:").replace("'", "\\'")
    # total duration
    r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1", xfade_path], capture_output=True, text=True)
    total = float(r.stdout.strip())
    # filter: drawtext lower third (fade in first 2s), progress bar
    # progress bar: drawbox width increasing over time -> use drawbox with w expression
    vf = (f"drawtext=text='{safe_title}':fontcolor=white:fontsize=36:box=1:boxcolor=black@0.5:boxborderw=12:"
          f"x=60:y=h-110:enable='between(t,0.5,6)',"
          f"drawbox=x=0:y=h-8:w='w*t/{total:.2f}':h=8:color=0x7c3aed@0.9:t=fill")
    cmd = ["ffmpeg","-y","-i",xfade_path,"-i",audio_path,"-i",vtt_path,
           "-map","0:v","-map","1:a","-map","2:s?",
           "-vf", vf,
           "-c:v","libx264","-preset","ultrafast","-crf","24","-pix_fmt","yuv420p",
           "-c:a","aac","-b:a","128k",
           "-c:s","mov_text","-metadata:s:s:0","language=por",
           "-shortest", final]
    subprocess.run(cmd, capture_output=True)
    return final

def main():
    for aula in AULAS:
        aid = aula["id"]
        print(f"=== Aula {aid} ===")
        durs = [slide_audio_dur(aid, i)+0.4 for i in range(len(aula["slides"]))]
        # last slide extra
        durs[-1] = slide_audio_dur(aid, len(aula["slides"])-1)+0.6
        clips = []
        for i in range(len(aula["slides"])):
            print(f"  slide {i}: {durs[i]:.2f}s")
            clips.append(make_slide_clip(aid, i, durs[i]))
        xfade = xfade_chain(aid, clips, durs)
        audio_mix = mix_audio(aid)
        vtt = os.path.join(BASE, "legendas", f"aula-{aid}.vtt")
        final = add_overlays(aid, xfade, audio_mix, vtt)
        print(f"  final: {final}")
    print("DONE")

main()

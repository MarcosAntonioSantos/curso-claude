import os, sys, subprocess, json
sys.path.insert(0, os.path.dirname(__file__))
from roteiros import AULAS

BASE = r"C:\Users\Windows 11\Documents\Default Project\curso-claude"
FPS = 30

def slide_audio_dur(aid, i):
    p = os.path.join(BASE, "audio", f"_work_{aid}", f"slide_{i}.mp3")
    if os.path.exists(p):
        r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1", p],
                           capture_output=True, text=True)
        try:
            return float(r.stdout.strip())
        except:
            pass
    return 8.0

def make_slide_clip(aid, i, dur):
    work = os.path.join(BASE, "videos", f"_work_{aid}")
    os.makedirs(work, exist_ok=True)
    img = os.path.join(BASE, "assets", "images", f"aula-{aid}", f"slide-{i:02d}.png")
    out = os.path.join(work, f"clip_{i:02d}.mp4")
    if os.path.exists(out):
        os.remove(out)
    # ken burns zoom + fade
    vf = (f"zoompan=z='min(zoom+0.0006,1.06)':d={int(dur*FPS)}:s=1920x1080:fps={FPS},"
          f"fade=t=in:st=0:d=0.5,fade=t=out:st={max(dur-0.5,0.5):.2f}:d=0.5")
    cmd = ["ffmpeg","-y","-loop","1","-i",img,"-vf",vf,"-t",f"{dur:.2f}",
           "-c:v","libx264","-preset","medium","-crf","22","-pix_fmt","yuv420p","-r",str(FPS), out]
    subprocess.run(cmd, capture_output=True)
    return out

def concat_clips(aid, clips):
    work = os.path.join(BASE, "videos", f"_work_{aid}")
    lst = os.path.join(work, "clips.txt")
    with open(lst, "w", encoding="utf-8") as f:
        for c in clips:
            f.write(f"file '{c.replace(chr(92),'/')}'\n")
    out = os.path.join(work, "video_noaudio.mp4")
    subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",lst,"-c","copy", out], capture_output=True)
    return out

def mux(aid, noaudio, vtt):
    audio = os.path.join(BASE, "audio", f"aula-{aid}.mp3")
    vtt_path = os.path.join(BASE, "legendas", f"aula-{aid}.vtt")
    final = os.path.join(BASE, "videos", f"aula-{aid}.mp4")
    cmd = ["ffmpeg","-y","-i",noaudio,"-i",audio,"-i",vtt_path,
           "-map","0:v","-map","1:a","-map","2:s?",
           "-c:v","copy","-c:a","aac","-b:a","128k",
           "-c:s","mov_text","-metadata:s:s:0","language=por",
           "-shortest", final]
    subprocess.run(cmd, capture_output=True)
    return final

def main():
    for aula in AULAS:
        aid = aula["id"]
        print(f"=== Aula {aid} ===")
        clips = []
        for i, slide in enumerate(aula["slides"]):
            dur = slide_audio_dur(aid, i) + 0.4
            if i == len(aula["slides"])-1:
                dur = slide_audio_dur(aid, i) + 0.6
            print(f"  slide {i}: {dur:.2f}s")
            clip = make_slide_clip(aid, i, dur)
            clips.append(clip)
        noaudio = concat_clips(aid, clips)
        final = mux(aid, noaudio, None)
        print(f"  final: {final}")
    print("DONE")

main()

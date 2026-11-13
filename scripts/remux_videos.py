import os, sys, subprocess
BASE = r"C:\Users\Windows 11\Documents\Default Project\curso-claude"
for aid in [1,2,3,4]:
    noaudio = os.path.join(BASE, "videos", f"_work_{aid}", "video_noaudio.mp4")
    audio = os.path.join(BASE, "audio", f"aula-{aid}.mp3")
    vtt = os.path.join(BASE, "legendas", f"aula-{aid}.vtt")
    final = os.path.join(BASE, "videos", f"aula-{aid}.mp4")
    cmd = ["ffmpeg","-y","-i",noaudio,"-i",audio,"-i",vtt,
           "-map","0:v:0","-map","1:a:0","-map","2:s:0",
           "-c:v","copy","-c:a","aac","-b:a","128k",
           "-c:s","mov_text","-metadata:s:s:0","language=por",
           final]
    subprocess.run(cmd, capture_output=True)
    print(f"Aula {aid} remuxed: {os.path.exists(final)}")
print("DONE")

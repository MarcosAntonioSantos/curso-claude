import os, subprocess
BASE = r"C:\Users\Windows 11\Documents\Default Project\curso-claude"
out = os.path.join(BASE, "audio", "ambient.mp3")
cmd = ["ffmpeg","-y","-f","lavfi","-i","sine=frequency=110:duration=60",
       "-f","lavfi","-i","anoisesrc=color=pink:amplitude=0.02:duration=60",
       "-filter_complex","[0:a]volume=0.08[a0];[1:a]lowpass=f=800,volume=0.04[a1];[a0][a1]amix=inputs=2:duration=first,afade=t=in:st=0:d=3,afade=t=out:st=57:d=3[out]",
       "-map","[out]","-c:a","libmp3lame","-q:a","4", out]
subprocess.run(cmd, capture_output=True)
print("OK" if os.path.exists(out) else "FAIL")
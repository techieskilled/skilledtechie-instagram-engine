import os
import subprocess
from pathlib import Path

out = Path('output')
out.mkdir(exist_ok=True)

def clean(value, default=''):
    return (value or default).replace('\x00', '')

hook = clean(os.getenv('HOOK'), 'THIS AI TOOL IS WILD')
tool = clean(os.getenv('TOOL_NAME'), 'AI TOOL')
cta = 'Follow @skilledtechie for more AI tools'

(out / 'hook.txt').write_text(hook, encoding='utf-8')
(out / 'tool.txt').write_text(tool, encoding='utf-8')
(out / 'cta.txt').write_text(cta, encoding='utf-8')

cmd = [
    'ffmpeg', '-y', '-f', 'lavfi', '-i', 'color=c=black:s=1080x1920:d=15',
    '-vf',
    "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:textfile=output/hook.txt:fontcolor=white:fontsize=82:x=(w-text_w)/2:y=220:box=1:boxcolor=black@0.25:boxborderw=24,"
    "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:textfile=output/tool.txt:fontcolor=white:fontsize=92:x=(w-text_w)/2:y=800:box=1:boxcolor=black@0.25:boxborderw=24,"
    "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:textfile=output/cta.txt:fontcolor=white:fontsize=48:x=(w-text_w)/2:y=1600:box=1:boxcolor=black@0.25:boxborderw=18",
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
    'output/reel.mp4'
]

subprocess.run(cmd, check=True)
print('Rendered output/reel.mp4')

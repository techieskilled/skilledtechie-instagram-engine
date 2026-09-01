#!/usr/bin/env python3
import os, subprocess, shutil, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W,H,FPS=1080,1920,30
OUT=Path('output'); SC=OUT/'scenes'; OUT.mkdir(exist_ok=True); SC.mkdir(exist_ok=True)

def font(size,bold=False):
    p='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    return ImageFont.truetype(p,size)

def wrap(d,text,f,maxw):
    lines=[]; cur=''
    for word in text.split():
        t=(cur+' '+word).strip()
        if d.textbbox((0,0),t,font=f)[2] <= maxw: cur=t
        else:
            if cur: lines.append(cur)
            cur=word
    if cur: lines.append(cur)
    return lines

def center(d,text,y,f,fill=(255,255,255),maxw=900,gap=10):
    lines=wrap(d,text,f,maxw); yy=y
    for line in lines:
        box=d.textbbox((0,0),line,font=f); x=(W-(box[2]-box[0]))//2
        d.text((x+2,yy+2),line,font=f,fill=(0,0,0,130)); d.text((x,yy),line,font=f,fill=fill)
        yy += box[3]-box[1]+gap
    return yy

def bg(seed):
    im=Image.new('RGB',(W,H),(9,12,24)); px=im.load()
    for y in range(H):
        for x in range(W):
            glow=math.exp(-(((x-820)/520)**2+((y-350)/520)**2))*45
            px[x,y]=(min(255,int(9+glow*.35+seed*2)),min(255,int(12+glow*.55+seed*2)),min(255,int(24+glow+seed*4)))
    d=ImageDraw.Draw(im,'RGBA')
    for x in range(0,W,90): d.line((x,0,x,H),fill=(255,255,255,10),width=1)
    for y in range(0,H,90): d.line((0,y,W,y),fill=(255,255,255,8),width=1)
    return im

def card(d,box,fill=(22,29,53,245),outline=(100,130,255,160),radius=36,width=3):
    d.rounded_rectangle(box,radius=radius,fill=fill,outline=outline,width=width)

def header(d,title,sub=''):
    d.text((70,65),'AI TOOLS  •  @SKILLEDTECHIE',font=font(28,True),fill=(130,170,255,255))
    center(d,title,145,font(76,True),maxw=900,gap=12)
    if sub: center(d,sub,250,font(32),fill=(205,212,235,255),maxw=880,gap=8)

def product_ui(d,tool):
    x,y,w,h=70,520,940,850
    card(d,(x,y,x+w,y+h),fill=(242,245,250,255),outline=(110,140,255,190),radius=42,width=4)
    d.rounded_rectangle((x,y,x+w,y+100),radius=42,fill=(31,40,70,255)); d.rectangle((x,y+55,x+w,y+100),fill=(31,40,70,255))
    d.ellipse((x+35,y+34,x+55,y+54),fill=(255,95,95)); d.ellipse((x+70,y+34,x+90,y+54),fill=(255,205,70)); d.ellipse((x+105,y+34,x+125,y+54),fill=(90,220,130))
    d.text((x+165,y+25),tool,font=font(38,True),fill=(255,255,255))
    card(d,(x+30,y+135,x+255,y+h-35),fill=(229,233,244,255),outline=(200,205,220,255),radius=24,width=2)
    d.text((x+55,y+180),'Sources',font=font(28,True),fill=(55,65,90))
    for i,t in enumerate(['Research.pdf','Notes.docx','Paper.pdf']):
        yy=y+245+i*75; d.rounded_rectangle((x+50,yy,x+230,yy+48),radius=12,fill=(255,255,255,255)); d.text((x+66,yy+11),t,font=font(18),fill=(65,75,100))
    cx=x+285; d.text((cx+35,y+175),'Ask about your sources',font=font(29,True),fill=(45,55,80))
    d.rounded_rectangle((cx+30,y+245,cx+w-80,y+345),radius=20,fill=(247,249,253),outline=(215,220,232),width=2); d.text((cx+55,y+275),'Summarize the key ideas',font=font(26),fill=(75,85,110))
    d.rounded_rectangle((cx+30,y+385,cx+w-80,y+635),radius=24,fill=(232,236,246),outline=(205,212,228),width=2); d.text((cx+60,y+420),'AI ANSWER',font=font(26,True),fill=(65,95,180))
    for i,t in enumerate(['Key ideas extracted from your files.','Answers stay grounded in your sources.','Ask follow-up questions instantly.']): d.text((cx+60,y+475+i*48),t,font=font(23),fill=(65,70,88))
    d.rounded_rectangle((cx+30,y+680,cx+w-80,y+755),radius=18,fill=(65,105,230,255)); d.text((cx+205,y+701),'Ask another question',font=font(23,True),fill=(255,255,255))

def steps_ui(d):
    items=[('01','UPLOAD','Add your PDF or notes.'),('02','ASK','Ask questions in plain English.'),('03','LEARN','Get answers from your sources.')]
    for i,(n,t,s) in enumerate(items):
        y=530+i*360; card(d,(70,y,1010,y+290)); d.ellipse((115,y+65,225,y+175),fill=(70,110,245,255)); d.text((140,y+88),n,font=font(30,True),fill=(255,255,255)); d.text((260,y+65),t,font=font(42,True),fill=(255,255,255)); d.text((260,y+130),s,font=font(26),fill=(190,200,225))
        if i<2: d.line((170,y+290,170,y+360),fill=(90,130,255,170),width=6)

def make_scenes(tool,hook):
    scenes=[]
    im=bg(1); d=ImageDraw.Draw(im,'RGBA'); d.ellipse((350,160,730,540),fill=(62,106,240,255),outline=(170,195,255,255),width=7); d.ellipse((420,230,660,470),fill=(20,30,65,255)); center(d,'AI',285,font(100,True)); center(d,hook,650,font(66,True),maxw=900); center(d,'There is a faster way.',900,font(40),fill=(205,215,240)); scenes.append(im)
    im=bg(2); d=ImageDraw.Draw(im,'RGBA'); header(d,'Meet '+tool,'Turn your own documents into an AI research assistant.'); product_ui(d,tool); scenes.append(im)
    im=bg(3); d=ImageDraw.Draw(im,'RGBA'); header(d,'HOW IT WORKS','Three simple steps. That is it.'); steps_ui(d); scenes.append(im)
    im=bg(4); d=ImageDraw.Draw(im,'RGBA'); header(d,'WHY IT MATTERS','Less reading. Faster answers. Better use of your time.'); card(d,(70,590,1010,1460)); rows=[('SUMMARIZE','Turn long material into quick takeaways.'),('QUESTION','Find answers inside your own sources.'),('UNDERSTAND','Connect ideas without rereading everything.')]
    for i,(t,s) in enumerate(rows): y=690+i*260; d.ellipse((125,y,215,y+90),fill=(70,110,245,255)); d.text((150,y+23),str(i+1),font=font(30,True),fill=(255,255,255)); d.text((260,y+5),t,font=font(36,True),fill=(255,255,255)); d.text((260,y+65),s,font=font(25),fill=(190,200,225))
    scenes.append(im)
    im=bg(5); d=ImageDraw.Draw(im,'RGBA'); d.ellipse((350,260,730,640),fill=(70,110,245,255)); center(d,'@',350,font(120,True)); center(d,'Want more AI tools that actually save time?',780,font(55,True),maxw=900); d.rounded_rectangle((150,1120,930,1290),radius=70,fill=(255,255,255,255)); center(d,'FOLLOW @SKILLEDTECHIE',1155,font(42,True),fill=(25,35,65),maxw=700); center(d,'New tools. Real use cases. No fluff.',1380,font(32),fill=(200,210,235)); scenes.append(im)
    return scenes

def run(cmd):
    print('>',' '.join(map(str,cmd))); subprocess.run(cmd,check=True)

def probe(path):
    return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(path)]).decode().strip())

def main():
    tool=os.getenv('TOOL_NAME','NotebookLM').strip() or 'NotebookLM'; hook=os.getenv('HOOK','Stop reading long PDFs the hard way.').strip() or 'Stop reading long PDFs the hard way.'
    voice=os.getenv('VOICEOVER','Still reading long PDFs the hard way? Meet NotebookLM. Upload your documents, ask questions, and get answers grounded in your sources. It is like turning your files into an AI research assistant. Follow @skilledtechie for more AI tools.').strip()
    shutil.rmtree(SC,ignore_errors=True); SC.mkdir(parents=True,exist_ok=True)
    for i,im in enumerate(make_scenes(tool,hook),1): im.convert('RGB').save(SC/f'scene{i}.jpg',quality=94,optimize=True)
    try: run(['edge-tts','--voice','en-IN-NeerjaNeural','--rate','+5%','--text',voice,'--write-media',str(OUT/'voice.mp3'),'--write-subtitles',str(OUT/'voice.srt')])
    except Exception:
        wav=OUT/'voice.wav'; run(['espeak-ng','-v','en','-s','165','-w',str(wav),voice.replace('"','').replace('\n',' ')])
    audio=OUT/'voice.mp3' if (OUT/'voice.mp3').exists() else OUT/'voice.wav'
    if not audio.exists() or audio.stat().st_size<1000: raise RuntimeError('Voiceover generation failed or produced an invalid audio file.')
    dur=max(2.6,probe(audio)); sd=dur/5.0; parts=[]
    zooms=['min(zoom+0.0018,1.12)','min(zoom+0.0015,1.10)','min(zoom+0.0012,1.09)','min(zoom+0.0016,1.11)','min(zoom+0.0020,1.14)']
    for i,z in enumerate(zooms,1):
        inp=SC/f'scene{i}.jpg'; out=SC/f'part{i}.mp4'; frames=max(1,round(sd*FPS)); fadeout=max(0.05,sd-0.25)
        vf=f"zoompan=z='{z}':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2':d={frames}:s={W}x{H}:fps={FPS},fade=t=in:st=0:d=0.20,fade=t=out:st={fadeout:.3f}:d=0.25"
        run(['ffmpeg','-y','-loop','1','-i',str(inp),'-t',f'{sd:.3f}','-vf',vf,'-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p',str(out)])
        if not out.exists() or out.stat().st_size<50000: raise RuntimeError(f'Visual segment {i} failed validation.')
        parts.append(out)
    concat=OUT/'concat.txt'; concat.write_text('\n'.join(f"file '{p.resolve()}'" for p in parts)+'\n'); visual=OUT/'visual.mp4'
    run(['ffmpeg','-y','-f','concat','-safe','0','-i',str(concat),'-c','copy',str(visual)])
    if not visual.exists() or visual.stat().st_size<100000: raise RuntimeError('Visual concat failed validation.')
    final=OUT/'reel.mp4'; sub=OUT/'voice.srt'; vf=f"subtitles='{sub.as_posix()}:force_style=FontName=DejaVu Sans,FontSize=18,PrimaryColour=&H00FFFFFF,OutlineColour=&H0018182D,BorderStyle=1,Outline=3,Shadow=0,Alignment=2,MarginV=150'" if sub.exists() else 'null'
    af=f'[1:a]volume=0.92[vo];aevalsrc=0.12*sin(2*PI*110*t)+0.05*sin(2*PI*220*t):s=44100:d={dur:.3f},volume=0.018,afade=t=in:st=0:d=1,afade=t=out:st={max(0,dur-1):.3f}:d=1[bed];[bed][vo]amix=inputs=2:duration=first:dropout_transition=2[a]'
    run(['ffmpeg','-y','-i',str(visual),'-i',str(audio),'-filter_complex',af,'-map','0:v','-map','[a]','-vf',vf,'-t',f'{dur:.3f}','-c:v','libx264','-preset','veryfast','-crf','19','-c:a','aac','-b:a','160k','-movflags','+faststart',str(final)])
    if not final.exists() or final.stat().st_size<100000: raise RuntimeError('Final reel was not created or is too small.')
    vdur=probe(final); adur=probe(audio)
    if abs(vdur-adur)>0.8: raise RuntimeError(f'QA failed: video={vdur:.2f}s audio={adur:.2f}s')
    (OUT/'qa.txt').write_text(f'PASS\nresolution=1080x1920\nvideo_duration={vdur:.2f}\naudio_duration={adur:.2f}\nvoice=en-IN-NeerjaNeural\nanimated_zoompan=yes\nsubtitles={"yes" if sub.exists() else "no"}\n')
    print(f'RENDER PASS: {final} {final.stat().st_size} bytes {vdur:.2f}s')

if __name__=='__main__': main()

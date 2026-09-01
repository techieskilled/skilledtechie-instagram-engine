#!/usr/bin/env python3
import os, subprocess, math, shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W,H,FPS = 1080,1920,30
OUT=Path('output'); SC=OUT/'scenes'; OUT.mkdir(exist_ok=True); SC.mkdir(exist_ok=True)

def font(size,bold=False):
    p='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    return ImageFont.truetype(p,size)

def wrap(draw,text,f,maxw):
    words=text.split(); lines=[]; cur=''
    for w in words:
        t=(cur+' '+w).strip()
        if draw.textbbox((0,0),t,font=f)[2] <= maxw: cur=t
        else:
            if cur: lines.append(cur)
            cur=w
    if cur: lines.append(cur)
    return lines

def center_text(d,text,y,f,fill=(255,255,255),maxw=900,spacing=10):
    lines=wrap(d,text,f,maxw); yy=y
    for line in lines:
        box=d.textbbox((0,0),line,font=f); x=(W-(box[2]-box[0]))//2
        d.text((x+2,yy+2),line,font=f,fill=(0,0,0,150))
        d.text((x,yy),line,font=f,fill=fill)
        yy += (box[3]-box[1])+spacing
    return yy

def bg(scene):
    im=Image.new('RGBA',(W,H),(10,12,24,255)); p=im.load()
    for y in range(H):
        for x in range(W):
            r=10+int(12*y/H); g=12+int(8*y/H); b=24+int(35*y/H)
            glow=math.exp(-(((x-820)/500)**2+((y-330)/500)**2))*30
            p[x,y]=(int(min(255,r+glow)),int(min(255,g+glow*.6)),int(min(255,b+glow)),255)
    d=ImageDraw.Draw(im)
    # soft tech grid
    for x in range(0,W,90): d.line((x,0,x,H),fill=(255,255,255,10),width=1)
    for y in range(0,H,90): d.line((0,y,W,y),fill=(255,255,255,8),width=1)
    # floating orbs
    for cx,cy,rr,a in [(120,250,90,35),(930,700,140,24),(180,1500,120,22),(900,1600,180,18)]:
        layer=Image.new('RGBA',(W,H),(0,0,0,0)); ld=ImageDraw.Draw(layer); ld.ellipse((cx-rr,cy-rr,cx+rr,cy+rr),fill=(70,120,255,a)); layer=layer.filter(ImageFilter.GaussianBlur(40)); im=Image.alpha_composite(im,layer)
    return im

def card(d,box,fill=(22,27,48,235),outline=(100,130,255,120),radius=36,width=3):
    d.rounded_rectangle(box,radius=radius,fill=fill,outline=outline,width=width)

def header(d,eyebrow,title,sub=''):
    d.text((70,80),eyebrow.upper(),font=font(30,True),fill=(130,170,255,255))
    y=center_text(d,title,150,font(78,True),maxw=900,spacing=12)
    if sub: center_text(d,sub,y+20,font(34),fill=(205,212,235,255),maxw=880,spacing=8)

def notebook_ui(d, y=520, scale=1.0):
    x=90; w=900; h=820
    card(d,(x,y,x+w,y+h),fill=(245,247,252,255),outline=(120,150,255,170),radius=44,width=4)
    d.rounded_rectangle((x,y,x+w,y+100),radius=44,fill=(31,40,70,255))
    d.ellipse((x+35,y+35,x+55,y+55),fill=(255,95,95)); d.ellipse((x+70,y+35,x+90,y+55),fill=(255,200,70)); d.ellipse((x+105,y+35,x+125,y+55),fill=(90,220,130))
    d.text((x+160,y+25),'NotebookLM',font=font(36,True),fill=(255,255,255))
    # sidebar
    d.rounded_rectangle((x+30,y+135,x+260,y+h-35),radius=24,fill=(231,235,245,255))
    d.text((x+55,y+180),'Sources',font=font(28,True),fill=(55,65,90))
    for i,t in enumerate(['Research.pdf','Notes.docx','Paper.pdf']):
        yy=y+245+i*72; d.rounded_rectangle((x+50,yy,x+240,yy+48),radius=12,fill=(255,255,255,255)); d.text((x+65,yy+10),t,font=font(19),fill=(65,75,100))
    # main chat
    d.rounded_rectangle((x+290,y+135,x+w-30,y+h-35),radius=24,fill=(255,255,255,255))
    d.text((x+330,y+180),'Ask about your sources',font=font(30,True),fill=(45,55,80))
    d.rounded_rectangle((x+330,y+250,x+w-80,y+330),radius=18,fill=(243,246,252,255),outline=(210,215,230,255),width=2)
    d.text((x+355,y+273),'Summarize the key ideas',font=font(26),fill=(80,90,115))
    d.rounded_rectangle((x+330,y+390,x+w-80,y+580),radius=22,fill=(236,242,255,255))
    d.text((x+360,y+420),'AI answer',font=font(27,True),fill=(60,90,180))
    lines=['Key ideas extracted from','your uploaded sources.','No random web searching.']
    for i,t in enumerate(lines): d.text((x+360,y+470+i*40),t,font=font(24),fill=(60,65,80))
    d.rounded_rectangle((x+330,y+630,x+w-80,y+710),radius=18,fill=(45,95,220,255)); d.text((x+520,y+652),'Ask another question',font=font(24,True),fill=(255,255,255))

def steps_ui(d,y=560):
    items=[('01','UPLOAD','Add your PDF or notes'),('02','ASK','Ask questions in plain English'),('03','LEARN','Get answers from your sources')]
    for i,(n,t,s) in enumerate(items):
        yy=y+i*330
        card(d,(80,yy,1000,yy+270),fill=(22,29,53,245),outline=(92,130,255,150))
        d.ellipse((120,yy+55,225,yy+160),fill=(70,110,245,255)); d.text((142,yy+82),n,font=font(28,True),fill=(255,255,255))
        d.text((260,yy+55),t,font=font(40,True),fill=(255,255,255)); d.text((260,yy+115),s,font=font(26),fill=(190,200,225))
        if i<2: d.line((172,yy+270,172,yy+330),fill=(90,130,255,170),width=6)

def make_scenes(tool):
    scenes=[]
    # 1 hook
    im=bg(1); d=ImageDraw.Draw(im)
    d.ellipse((370,170,710,510),fill=(62,106,240,255),outline=(170,195,255,255),width=6)
    d.text((480,245),'AI',font=font(105,True),fill=(255,255,255))
    d.arc((420,220,660,460),0,300,fill=(255,255,255,130),width=10)
    center_text(d,'Stop reading long PDFs the hard way.',570,font(66,True),maxw=900)
    center_text(d,'There is an AI shortcut.',820,font(40),fill=(205,215,240),maxw=850)
    scenes.append(im)
    # 2 product
    im=bg(2); d=ImageDraw.Draw(im); header(d,'AI TOOL','Meet NotebookLM','Turn your own documents into an AI research assistant.')
    notebook_ui(d,560); scenes.append(im)
    # 3 workflow
    im=bg(3); d=ImageDraw.Draw(im); header(d,'HOW IT WORKS','Three steps. That’s it.'); steps_ui(d,570); scenes.append(im)
    # 4 result
    im=bg(4); d=ImageDraw.Draw(im); header(d,'WHY IT MATTERS','Ask. Understand. Move faster.','Great for students, researchers and busy professionals.')
    card(d,(90,600,990,1420),fill=(22,29,53,245),outline=(92,130,255,150))
    benefits=[('⚡','Summarize','Turn long material into quick takeaways.'),('🔎','Question','Find answers inside your sources.'),('🧠','Understand','Connect ideas without rereading everything.')]
    for i,(ico,t,s) in enumerate(benefits):
        yy=680+i*230; d.text((145,yy),ico,font=font(55,True),fill=(120,170,255)); d.text((240,yy),t,font=font(38,True),fill=(255,255,255)); d.text((240,yy+60),s,font=font(25),fill=(190,200,225))
    scenes.append(im)
    # 5 CTA
    im=bg(5); d=ImageDraw.Draw(im)
    d.ellipse((350,300,730,680),fill=(70,110,245,255)); d.text((435,405),'@',font=font(120,True),fill=(255,255,255))
    center_text(d,'Want more AI tools that actually save time?',760,font(55,True),maxw=900)
    d.rounded_rectangle((170,1120,910,1285),radius=70,fill=(255,255,255,255)); center_text(d,'FOLLOW @SKILLEDTECHIE',1155,font(42,True),fill=(25,35,65),maxw=700)
    center_text(d,'New tools. Real use cases. No fluff.',1380,font(32),fill=(200,210,235),maxw=850)
    scenes.append(im)
    return scenes

def run(cmd):
    print('>', ' '.join(map(str,cmd)))
    subprocess.run(cmd,check=True)

def probe(path):
    return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(path)]).decode().strip())

def main():
    tool=os.getenv('TOOL_NAME','NotebookLM'); voiceover=os.getenv('VOICEOVER','Still reading long PDFs the hard way? Meet NotebookLM. Upload your documents, ask questions, and get answers grounded in your sources. It is like turning your files into an AI research assistant. Follow @skilledtechie for more AI tools.')
    shutil.rmtree(SC,ignore_errors=True); SC.mkdir(parents=True)
    scenes=make_scenes(tool)
    for i,im in enumerate(scenes,1): im.convert('RGB').save(SC/f'scene{i}.jpg',quality=94)
    # Neural Indian English voice, with free edge-tts client. Falls back to local espeak if network fails.
    try:
        run(['python','-m','pip','install','--quiet','edge-tts'])
        run(['edge-tts','--voice','en-IN-NeerjaNeural','--rate','+5%','--text',voiceover,'--write-media',str(OUT/'voice.mp3'),'--write-subtitles',str(OUT/'voice.srt')])
    except Exception:
        run(['bash','-lc',f"command -v espeak-ng >/dev/null || (sudo apt-get update -qq && sudo apt-get install -y -qq espeak-ng); espeak-ng -v en-in -s 165 -w '{OUT/'voice.wav'}' \"{voiceover.replace(chr(34), '')}\""])
    audio=OUT/'voice.mp3' if (OUT/'voice.mp3').exists() else OUT/'voice.wav'
    dur=max(2.6,probe(audio)); sd=dur/5.0
    parts=[]
    motions=[('1.0+0.10*on/d','(iw-iw/zoom)*on/d','0'),('1.0+0.08*on/d','0','(ih-ih/zoom)*on/d'),('1.0+0.07*on/d','(iw-iw/zoom)*(1-on/d)','0'),('1.0+0.09*on/d','0','(ih-ih/zoom)*(1-on/d)'),('1.0+0.11*on/d','(iw-iw/zoom)*0.5','(ih-ih/zoom)*0.5')]
    for i,m in enumerate(motions,1):
        inp=SC/f'scene{i}.jpg'; out=SC/f'part{i}.mp4'; z,x,y=m
        vf=f"zoompan=z='{z}':x='{x}':y='{y}':d={max(1,int(round(sd*FPS)))}:s={W}x{H}:fps={FPS},fade=t=in:st=0:d=0.20,fade=t=out:st={max(0,sd-0.25):.3f}:d=0.25"
        run(['ffmpeg','-y','-loop','1','-i',str(inp),'-t',f'{sd:.3f}','-vf',vf,'-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p',str(out)])
        parts.append(out)
    concat=OUT/'visual.mp4'
    lst=OUT/'concat.txt'; lst.write_text('\n'.join(f"file '{p.resolve()}'" for p in parts))
    run(['ffmpeg','-y','-f','concat','-safe','0','-i',str(lst),'-c','copy',str(concat)])
    final=OUT/'reel.mp4'
    # Add subtle synthetic pulse bed under narration; no copyrighted music is bundled.
    vf="subtitles='output/voice.srt':force_style='FontName=DejaVu Sans,FontSize=18,PrimaryColour=&H00FFFFFF,OutlineColour=&H0010182D,BorderStyle=1,Outline=3,Shadow=0,Alignment=2,MarginV=150'"
    filter_complex=f"[0:a]volume=0.92[vo];aevalsrc=0.12*sin(2*PI*110*t)+0.05*sin(2*PI*220*t):s=44100:d={dur:.3f},volume=0.025,afade=t=in:st=0:d=1,afade=t=out:st={max(0,dur-1):.3f}:d=1[bed];[vo][bed]amix=inputs=2:duration=first:dropout_transition=2[a]"
    run(['ffmpeg','-y','-i',str(concat),'-i',str(audio),'-filter_complex',filter_complex,'-map','0:v','-map','[a]','-vf',vf,'-t',f'{dur:.3f}','-c:v','libx264','-preset','veryfast','-crf','19','-c:a','aac','-b:a','160k','-movflags','+faststart',str(final)])
    # QA
    vdur=probe(final); size=final.stat().st_size
    if size < 100000 or abs(vdur-dur)>0.6: raise RuntimeError(f'QA failed: size={size}, duration={vdur}, audio={dur}')
    (OUT/'qa.txt').write_text(f'PASS\nresolution=1080x1920\nvideo_duration={vdur:.2f}\naudio_duration={dur:.2f}\nvoice=en-IN-NeerjaNeural\nanimated_zoompan=yes\nsubtitles=yes\n')
    print(f'RENDER PASS: {final} {size} bytes {vdur:.2f}s')

if __name__=='__main__': main()

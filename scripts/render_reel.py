#!/usr/bin/env python3
import json, math, os, subprocess, textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1920
FPS = 30
OUT = Path('output')
FRAMES = OUT / 'frames'
OUT.mkdir(parents=True, exist_ok=True)
FRAMES.mkdir(parents=True, exist_ok=True)

FONT_DIRS = [Path('/usr/share/fonts/truetype/dejavu'), Path('/usr/share/fonts/truetype/liberation2')]
def font(name='DejaVuSans-Bold.ttf', size=64):
    for d in FONT_DIRS:
        p = d / name
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()

BOLD = lambda s: font('DejaVuSans-Bold.ttf', s)
REG = lambda s: font('DejaVuSans.ttf', s)


def wrap(draw, text, fnt, max_width):
    words = text.split()
    lines, cur = [], ''
    for word in words:
        test = word if not cur else cur + ' ' + word
        if draw.textbbox((0,0), test, font=fnt)[2] <= max_width:
            cur = test
        else:
            if cur: lines.append(cur)
            cur = word
    if cur: lines.append(cur)
    return lines


def text_block(draw, text, xy, fnt, fill=(245,247,255), max_width=900, spacing=12, align='left', stroke=0):
    lines = wrap(draw, text, fnt, max_width)
    x, y = xy
    for line in lines:
        box = draw.textbbox((0,0), line, font=fnt, stroke_width=stroke)
        tw = box[2]-box[0]
        tx = x if align == 'left' else x + (max_width-tw)/2 if align == 'center' else x + max_width-tw
        draw.text((tx,y), line, font=fnt, fill=fill, stroke_width=stroke, stroke_fill=(0,0,0))
        y += box[3]-box[1] + spacing
    return y


def rounded_card(draw, box, fill=(24,27,38), outline=(65,70,90), radius=38, width=3):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def gradient_bg(img, top=(9,12,25), bottom=(34,15,60)):
    px = img.load()
    for y in range(H):
        t = y/(H-1)
        r = int(top[0]*(1-t)+bottom[0]*t)
        g = int(top[1]*(1-t)+bottom[1]*t)
        b = int(top[2]*(1-t)+bottom[2]*t)
        for x in range(W): px[x,y] = (r,g,b)
    glow = Image.new('RGBA', (W,H), (0,0,0,0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((-180, 250, 500, 930), fill=(90,65,255,70))
    gd.ellipse((650, 1000, 1250, 1650), fill=(0,210,255,45))
    glow = glow.filter(ImageFilter.GaussianBlur(80))
    img.alpha_composite(glow)


def draw_header(d, label, progress, scene_no):
    d.rounded_rectangle((54,54,330,116), radius=28, fill=(255,255,255,24), outline=(255,255,255,50), width=2)
    d.text((78,68), label, font=BOLD(30), fill=(245,247,255))
    d.text((950,68), f'{scene_no}/5', font=BOLD(28), fill=(190,195,215), anchor='ra')
    d.rounded_rectangle((54,140,1026,150), radius=5, fill=(255,255,255,35))
    d.rounded_rectangle((54,140,54+972*progress,150), radius=5, fill=(120,105,255))


def mock_notebook(d, box):
    x0,y0,x1,y1 = box
    rounded_card(d, box, fill=(248,249,252), outline=(255,255,255), radius=44, width=0)
    d.rounded_rectangle((x0,y0,x1,y0+95), radius=44, fill=(33,36,48))
    d.rectangle((x0,y0+55,x1,y0+95), fill=(33,36,48))
    d.ellipse((x0+30,y0+31,x0+48,y0+49), fill=(255,90,100))
    d.ellipse((x0+60,y0+31,x0+78,y0+49), fill=(255,190,80))
    d.ellipse((x0+90,y0+31,x0+108,y0+49), fill=(90,210,120))
    d.text((x0+145,y0+22),'NotebookLM',font=BOLD(38),fill=(245,247,255))
    d.rounded_rectangle((x0+40,y0+135,x0+300,y1-45),radius=28,fill=(232,235,244))
    d.text((x0+72,y0+170),'Sources',font=BOLD(28),fill=(55,60,75))
    for i,txt in enumerate(['Research.pdf','Lecture notes','Project brief']):
        d.rounded_rectangle((x0+62,y0+235+i*80,x0+280,y0+295+i*80),radius=18,fill=(255,255,255))
        d.text((x0+82,y0+250+i*80),txt,font=REG(22),fill=(75,80,95))
    qx=x0+340
    d.rounded_rectangle((qx,y0+145,x1-35,y0+235),radius=24,fill=(224,226,255))
    d.text((qx+28,y0+170),'Summarize these sources',font=REG(26),fill=(65,55,130))
    d.rounded_rectangle((qx,y0+270,x1-35,y1-55),radius=28,fill=(238,246,240))
    d.text((qx+28,y0+300),'AI summary',font=BOLD(26),fill=(40,95,60))
    for i,w in enumerate([0.88,0.72,0.94,0.63]):
        d.rounded_rectangle((qx+28,y0+360+i*48,qx+28+int((x1-qx-90)*w),y0+378+i*48),radius=8,fill=(120,170,135))


def make_scene(i, scene, total_progress):
    img = Image.new('RGBA',(W,H),(0,0,0,255))
    gradient_bg(img)
    d = ImageDraw.Draw(img)
    draw_header(d, 'AI TOOL • @skilledtechie', total_progress, i+1)
    kind = scene.get('kind','text')
    if i == 0:
        d.text((54,255),'STOP',font=BOLD(126),fill=(255,255,255))
        d.text((54,390),'TAKING NOTES',font=BOLD(96),fill=(135,125,255))
        text_block(d, scene['headline'], (54,555), BOLD(56), max_width=920, spacing=8)
        rounded_card(d,(54,850,1026,1450),fill=(18,21,32),outline=(95,85,170),radius=48)
        for yy in [930,1050,1170,1290]:
            d.rounded_rectangle((110,yy,930,yy+54),radius=27,fill=(38,43,60))
            d.rounded_rectangle((110,yy,110+int(820*(0.78 if yy==930 else 0.58 if yy==1050 else 0.84 if yy==1170 else 0.42)),yy+54),radius=27,fill=(78,82,115))
        d.text((540,1370),'long PDFs  •  messy notes  •  scattered research',font=REG(26),fill=(170,175,195),anchor='mm')
    elif i == 1:
        d.text((54,250),'MEET',font=BOLD(54),fill=(180,185,210))
        d.text((54,320),scene['tool'],font=BOLD(100),fill=(255,255,255))
        text_block(d, scene['headline'], (54,465), BOLD(48), max_width=920, spacing=8)
        mock_notebook(d,(70,760,1010,1690))
    elif i == 2:
        d.text((54,255),'3 SIMPLE STEPS',font=BOLD(62),fill=(255,255,255))
        steps=[('01','Upload your sources'),('02','Ask a question'),('03','Get answers from them')]
        y=440
        for n,t in steps:
            d.rounded_rectangle((60,y,1020,y+290),radius=42,fill=(20,24,37),outline=(65,70,95),width=3)
            d.ellipse((100,y+70,190,y+160),fill=(115,100,255))
            d.text((145,y+115),n,font=BOLD(28),fill=(255,255,255),anchor='mm')
            text_block(d,t,(235,y+70),BOLD(42),max_width=700,spacing=6)
            y+=330
    elif i == 3:
        d.text((54,255),'WHY IT\'S USEFUL',font=BOLD(58),fill=(255,255,255))
        benefits=['Study faster','Research without digging through every page','Keep answers grounded in your own sources']
        y=470
        for b in benefits:
            d.rounded_rectangle((60,y,1020,y+260),radius=42,fill=(20,24,37),outline=(65,70,95),width=3)
            d.ellipse((100,y+85,158,y+143),fill=(95,210,150))
            d.text((129,y+114),'✓',font=BOLD(34),fill=(10,35,25),anchor='mm')
            text_block(d,b,(205,y+58),BOLD(40),max_width=750,spacing=6)
            y+=305
    else:
        d.text((54,290),'WORTH TRYING?',font=BOLD(68),fill=(255,255,255))
        text_block(d,scene['headline'],(54,430),BOLD(52),max_width=920,spacing=10)
        rounded_card(d,(54,870,1026,1260),fill=(28,27,55),outline=(115,105,255),radius=48,width=3)
        d.text((540,965),'Follow',font=REG(40),fill=(190,195,215),anchor='mm')
        d.text((540,1045),'@skilledtechie',font=BOLD(78),fill=(255,255,255),anchor='mm')
        d.text((540,1140),'for more AI tools & workflows',font=REG(32),fill=(175,180,205),anchor='mm')
    d.text((54,1810),'SAVE THIS • SHARE IT WITH SOMEONE WHO NEEDS IT',font=BOLD(25),fill=(185,190,210))
    return img.convert('RGB')


def main():
    raw = os.environ.get('CONTENT_JSON','').strip()
    if raw:
        data=json.loads(raw)
    else:
        data={
          'content_id':'skilledtechie_001','tool':'NotebookLM',
          'scenes':[
            {'headline':'What if your notes could organize themselves?','kind':'hook'},
            {'tool':'NotebookLM','headline':'An AI notebook that can work with the sources you give it.','kind':'product'},
            {'headline':'','kind':'steps'},
            {'headline':'Useful for study, research and quick source-based answers.','kind':'benefits'},
            {'headline':'Try the idea. Save this Reel.','kind':'cta'}
          ],
          'durations':[2.5,3.2,4.0,3.2,2.1]
        }
    scenes=data.get('scenes',[])
    if len(scenes)!=5: raise SystemExit('CONTENT_JSON must contain exactly 5 scenes')
    durations=data.get('durations',[2.5,3.2,4.0,3.2,2.1])
    if len(durations)!=5: raise SystemExit('durations must contain 5 values')
    for i,scene in enumerate(scenes):
        img=make_scene(i,scene,(i+1)/5)
        img.save(FRAMES/f'scene_{i+1}.png',quality=95)
    concat=OUT/'concat.txt'
    with concat.open('w',encoding='utf-8') as f:
        for i,dur in enumerate(durations):
            f.write(f"file 'frames/scene_{i+1}.png'\n")
            f.write(f'duration {dur}\n')
        f.write("file 'frames/scene_5.png'\n")
    subprocess.run(['ffmpeg','-y','-f','concat','-safe','0','-i',str(concat),'-vf',f'fps={FPS},format=yuv420p','-c:v','libx264','-preset','medium','-crf','20','-movflags','+faststart',str(OUT/'reel.mp4')],check=True)
    # Create a simple contact sheet for visual QA.
    thumbs=[]
    for i in range(5):
        im=Image.open(FRAMES/f'scene_{i+1}.png').resize((270,480))
        thumbs.append(im)
    sheet=Image.new('RGB',(270*5,480),(8,8,12))
    for i,im in enumerate(thumbs): sheet.paste(im,(270*i,0))
    sheet.save(OUT/'preview.png')
    print(f"Rendered {OUT/'reel.mp4'} and {OUT/'preview.png'}")

if __name__=='__main__': main()

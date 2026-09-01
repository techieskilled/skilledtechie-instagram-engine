#!/usr/bin/env python3
import argparse,json,os
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter
W,H=1080,1350
ROOT=Path(__file__).resolve().parents[1]
def F(n,b=False):
 p='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if b else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
 return ImageFont.truetype(p,n)
def wrap(d,t,f,m):
 out=[];cur=''
 for w in t.split():
  x=(cur+' '+w).strip()
  if d.textbbox((0,0),x,font=f)[2]<=m:cur=x
  else: out.append(cur);cur=w
 if cur:out.append(cur)
 return out
def block(d,t,x,y,f,fill,m,sp=14):
 for line in wrap(d,t,f,m): d.text((x,y),line,font=f,fill=fill);y+=f.size+sp
 return y
def slide(data,i,path):
 im=Image.new('RGBA',(W,H),(10,12,20,255)); g=Image.new('RGBA',(W,H));gd=ImageDraw.Draw(g)
 gd.ellipse((-180,-180,620,620),fill=(100,70,255,90));gd.ellipse((650,850,1250,1450),fill=(0,210,190,65));g=g.filter(ImageFilter.GaussianBlur(90));im=Image.alpha_composite(im,g);d=ImageDraw.Draw(im)
 d.text((70,62),'@skilledtechie',font=F(34,True),fill=(235,235,245));d.text((865,62),f'{i}/5',font=F(30,True),fill=(165,165,180))
 logo=data.get('logo_text') or data['tool'][:2].upper();d.rounded_rectangle((70,150,230,310),34,fill=(31,34,52),outline=(125,105,255),width=3);d.text((110,190),logo,font=F(64,True),fill='white')
 s=data['slides'][i-1];d.text((70,370),s['title'],font=F(66,True),fill='white');block(d,s['body'],70,500,F(40),(205,208,220),900,18)
 base=1160
 for n in range(5):
  x=70+n*55;h=18+n*15;d.rounded_rectangle((x,base-h,x+38,base),8,fill=(110,95,255) if n<i else (50,52,70))
 if i==5:
  d.rounded_rectangle((70,1020,930,1120),28,fill=(35,38,60),outline=(110,95,255),width=2);d.text((105,1050),'FOLLOW @skilledtechie FOR MORE AI TOOLS',font=F(31,True),fill='white')
 im.convert('RGB').save(path,quality=95,optimize=True)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--input',default='content/current.json');ap.add_argument('--out',default='dist/carousel');a=ap.parse_args();data=json.loads((ROOT/a.input).read_text());o=ROOT/a.out;o.mkdir(parents=True,exist_ok=True)
 for i in range(1,6):slide(data,i,o/f'{i:02d}.jpg')
 print('rendered',len(list(o.glob('*.jpg'))),'slides')
if __name__=='__main__':main()

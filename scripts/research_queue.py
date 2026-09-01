#!/usr/bin/env python3
import json,re,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=ROOT/'content/current.json';d=json.loads(p.read_text())
 url='https://launcharchive.ai/categories/ai-development-tools/2026/august'
 try:
  html=urllib.request.urlopen(url,timeout=15).read().decode('utf-8','ignore')
  d['trend_signal']='agentic AI' if re.search(r'agent',html,re.I) else 'AI tools'
 except Exception:d['trend_signal']='AI tools'
 p.write_text(json.dumps(d,indent=2))
 print('trend_signal=',d['trend_signal'])
if __name__=='__main__':main()

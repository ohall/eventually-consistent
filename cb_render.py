#!/usr/bin/env python3
"""Chatterbox render: chunk 2-3 sentences, clone ref voice, exaggeration 0.7, cfg 0.4; regenerate short chunks.
usage: cb_render.py script.txt out.wav ref.wav"""
import sys,re,time,json,torch,torchaudio as ta
from chatterbox.tts import ChatterboxTTS
src,out,ref=sys.argv[1:4]; text=open(src).read()
sents=[s for p in re.split(r"\n\s*\n",text) for s in re.split(r"(?<=[.!?])\s+",p.strip()) if s]
chunks=[];cur=[]
for s in sents:
    cur.append(s)
    if len(cur)==3 or sum(len(x.split()) for x in cur)>=40: chunks.append(" ".join(cur));cur=[]
if cur: chunks.append(" ".join(cur))
torch.manual_seed(7); m=ChatterboxTTS.from_pretrained(device="cpu"); sr=m.sr
MIN_SPW=0.24  # seconds per word; samples ran ~0.29-0.35
pieces=[];report=[];t0=time.time()
for i,c in enumerate(chunks):
    n=len(c.split()); best=None
    for attempt in range(3):
        w=m.generate(c,audio_prompt_path=ref,exaggeration=0.7,cfg_weight=0.4); d=w.shape[-1]/sr
        if best is None or d>best[1]: best=(w,d)
        if d/n>=MIN_SPW and d/n<=0.9: break
    w,d=best; report.append(dict(chunk=i,words=n,sec=round(d,1),spw=round(d/n,3),attempts=attempt+1,ok=MIN_SPW<=d/n<=0.9))
    print(json.dumps(report[-1]),flush=True)
    pieces+= [w, torch.zeros(1,int(sr*0.45))]
ta.save(out,torch.cat(pieces,dim=-1),sr)
bad=[r for r in report if not r["ok"]]
print(json.dumps(dict(chunks=len(chunks),gen_sec=round(time.time()-t0),suspect=bad)),flush=True)

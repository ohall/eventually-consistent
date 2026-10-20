import time,torch,torchaudio as ta,subprocess
from chatterbox.tts import ChatterboxTTS
m=ChatterboxTTS.from_pretrained(device='cpu'); t=open('samples/opening.txt').read()
for name,ref,ex,cfg in [('default_neutral',None,0.5,0.5),('default_excited',None,0.85,0.3),('clone_heart_expressive','/tmp/af_heart.wav',0.7,0.4)]:
    s=time.time(); w=m.generate(t,audio_prompt_path=ref,exaggeration=ex,cfg_weight=cfg) if ref else m.generate(t,exaggeration=ex,cfg_weight=cfg)
    ta.save(f'/tmp/cb_{name}.wav',w,m.sr)
    subprocess.run(['ffmpeg','-y','-loglevel','error','-i',f'/tmp/cb_{name}.wav','-b:a','96k',f'samples/chatterbox_{name}.mp3'],check=True)
    print(name,round(time.time()-s,1),'s gen,',round(w.shape[-1]/m.sr,1),'s audio',flush=True)

import time,sys,soundfile as sf,numpy as np,subprocess
from kokoro import KPipeline
t=open('samples/opening.txt').read(); p=KPipeline(lang_code='a')
for v in ['af_heart','am_michael','am_fenrir']:
    s=time.time(); a=np.concatenate([x.audio.numpy() for x in p(t,voice=v)]); w=f'/tmp/{v}.wav'; sf.write(w,a,24000)
    subprocess.run(['ffmpeg','-y','-loglevel','error','-i',w,'-b:a','96k',f'samples/kokoro_{v}.mp3'],check=True)
    print(v,round(time.time()-s,1),'s gen,',round(len(a)/24000,1),'s audio',flush=True)

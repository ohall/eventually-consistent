#!/usr/bin/env python3
"""Add one Eventually Consistent episode: render spoken script -> MP3, update episodes.json, regenerate site/feed.xml.
Usage: add_episode.py --date 2026-10-13 --title "Normalization" --day 4 --script scripts/x.txt [--summary "..."]
Then run deploy_prep.py (writes Vercel upload/deploy payload files)."""
import argparse, json, os, subprocess, tempfile, email.utils, datetime, re, html
from pathlib import Path
ROOT=Path(__file__).resolve().parent; SITE=ROOT/"site"; EPS=ROOT/"episodes.json"
BASE=os.environ.get("TB_BASE_URL","https://tech-bites-podcast.vercel.app")
VOICE=ROOT/"voices/en_US-ryan-high.onnx"; PIPER=ROOT/".venv/bin/piper"
def slug(s): return re.sub(r"[^a-z0-9]+","-",s.lower()).strip("-")
REF=ROOT/"voices/ref_af_heart.wav"; CB_PY=ROOT/".venv-cb/bin/python"
def render(text,out):
    with tempfile.TemporaryDirectory() as t:
        wav=Path(t)/"a.wav"
        if os.environ.get("TB_ENGINE","chatterbox")=="piper":
            subprocess.run([str(PIPER),"-m",str(VOICE),"-f",str(wav),"--sentence_silence","0.35"],input=text.encode(),check=True,capture_output=True)
        else:
            tf=Path(t)/"s.txt"; tf.write_text(text)
            subprocess.run([str(CB_PY),str(ROOT/"cb_render.py"),str(tf),str(wav),str(REF)],check=True)
        subprocess.run(["ffmpeg","-y","-loglevel","error","-i",str(wav),"-af","loudnorm=I=-16:TP=-1.5","-ac","1","-ar","44100","-b:a","64k",
            "-metadata","artist=Eventually Consistent","-metadata","album=Eventually Consistent",str(out)],check=True)
    d=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",str(out)]))
    return int(round(d))
def build_feed(eps):
    e=html.escape; now=email.utils.format_datetime(datetime.datetime.now(datetime.timezone.utc))
    items=""
    for ep in sorted(eps,key=lambda x:x["date"],reverse=True):
        url=f"{BASE}/episodes/{ep['file']}"
        items+=f"""  <item>
    <title>{e(ep['title'])}</title>
    <description>{e(ep['summary'])}</description>
    <itunes:summary>{e(ep['summary'])}</itunes:summary>
    <enclosure url="{url}" length="{ep['bytes']}" type="audio/mpeg"/>
    <guid isPermaLink="false">{e(ep['guid'])}</guid>
    <pubDate>{ep['pubDate']}</pubDate>
    <itunes:duration>{ep['duration']}</itunes:duration>
    <itunes:episode>{ep['day']}</itunes:episode>
    <itunes:explicit>false</itunes:explicit>
    <itunes:episodeType>full</itunes:episodeType>
  </item>
"""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:content="http://purl.org/rss/1.0/modules/content/">
<channel>
  <title>Eventually Consistent</title>
  <link>{BASE}/</link>
  <atom:link href="{BASE}/feed.xml" rel="self" type="application/rss+xml"/>
  <language>en-us</language>
  <description>A daily bite-sized explainer of one systems/backend concept.</description>
  <itunes:summary>A daily bite-sized explainer of one systems/backend concept.</itunes:summary>
  <itunes:author>Oakley Hall</itunes:author>
  <itunes:owner><itunes:name>Oakley Hall</itunes:name></itunes:owner>
  <itunes:image href="{BASE}/cover.jpg"/>
  <image><url>{BASE}/cover.jpg</url><title>Eventually Consistent</title><link>{BASE}/</link></image>
  <itunes:category text="Technology"/>
  <itunes:explicit>false</itunes:explicit>
  <itunes:type>episodic</itunes:type>
  <lastBuildDate>{now}</lastBuildDate>
{items}</channel>
</rss>
"""
if __name__=="__main__":
    a=argparse.ArgumentParser(); a.add_argument("--date",required=True); a.add_argument("--title",required=True)
    a.add_argument("--day",type=int,required=True); a.add_argument("--script",required=True); a.add_argument("--summary")
    a=a.parse_args()
    text=Path(a.script).read_text(); fn=f"{a.date}-{slug(a.title)}.mp3"; out=SITE/"episodes"/fn
    out.parent.mkdir(parents=True,exist_ok=True); dur=render(text,out)
    eps=json.loads(EPS.read_text()) if EPS.exists() else []
    eps=[x for x in eps if x["file"]!=fn]
    pub=datetime.datetime.fromisoformat(a.date+"T08:30:00-04:00")
    eps.append(dict(date=a.date,day=a.day,title=f"Day {a.day}: {a.title}",file=fn,bytes=out.stat().st_size,duration=dur,
        guid=f"tech-bites-{a.date}-{slug(a.title)}",pubDate=email.utils.format_datetime(pub),
        summary=a.summary or f"Eventually Consistent day {a.day}: {a.title}, explained in a few minutes."))
    EPS.write_text(json.dumps(eps,indent=1)); (SITE/"feed.xml").write_text(build_feed(eps))
    (SITE/"index.html").write_text(f'<!doctype html><meta charset=utf-8><title>Eventually Consistent</title><h1>Eventually Consistent</h1><p>A daily bite-sized explainer of one systems/backend concept.</p><p>Podcast feed: <a href="/feed.xml">{BASE}/feed.xml</a></p>')
    (SITE/"vercel.json").write_text(json.dumps({"headers":[{"source":"/feed.xml","headers":[{"key":"Content-Type","value":"application/rss+xml; charset=utf-8"}]},
        {"source":"/episodes/(.*)","headers":[{"key":"Content-Type","value":"audio/mpeg"}]}]}))
    print(json.dumps(eps[-1]))

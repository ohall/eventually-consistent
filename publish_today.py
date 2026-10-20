#!/usr/bin/env python3
"""One-command daily step (everything except the Vercel connector calls).
  publish_today.py --script spoken.txt  [--title T --day N --date D --summary S]   (preferred: agent-written spoken script)
  publish_today.py --explainer explainer.md [...]   (fallback: mechanical markdown->speech cleanup)
Title/day default to the latest entry in $TB_STATE (default /workspace/daily-concepts/state.json) history (day = len(history)).
Renders (Chatterbox, cloned af_heart, exaggeration 0.7), rebuilds site/feed.xml, runs deploy_prep.py.
Prints DEPLOY_MANIFEST path; follow README 'Deploy' steps."""
import argparse,json,os,re,subprocess,sys,datetime
from pathlib import Path
R=Path(__file__).resolve().parent; STATE=Path(os.environ.get("TB_STATE","/workspace/daily-concepts/state.json"))
def speechify(md):
    t=re.sub(r"```.*?```","",md,flags=re.S); t=re.sub(r"`([^`]*)`",r"\1",t); t=re.sub(r"\*\*|__|\*|#+ ?","",t)
    t=re.sub(r"\[([^\]]+)\]\([^)]+\)",r"\1",t); t=re.sub(r"^\s*[-•]\s*","",t,flags=re.M)
    for a,b in [("&"," and "),("%"," percent"),("->"," to "),("=>"," to "),("/"," or "),("_"," "),("1NF","first normal form"),("2NF","second normal form"),("3NF","third normal form")]: t=t.replace(a,b)
    return re.sub(r"[ \t]+"," ",t).strip()
a=argparse.ArgumentParser(); g=a.add_mutually_exclusive_group(required=True)
g.add_argument("--script"); g.add_argument("--explainer")
a.add_argument("--title"); a.add_argument("--day",type=int); a.add_argument("--date",default=datetime.date.today().isoformat()); a.add_argument("--summary")
a=a.parse_args()
if not (a.title and a.day):
    h=json.loads(STATE.read_text())["history"]; a.title=a.title or h[-1]["concept"]; a.day=a.day or len(h)
slug=re.sub(r"[^a-z0-9]+","-",a.title.lower()).strip("-"); sp=R/"scripts"/f"{a.date}-{slug}.txt"
if a.script:
    if Path(a.script).resolve()!=sp.resolve(): sp.write_text(Path(a.script).read_text())
else:
    body=speechify(Path(a.explainer).read_text())
    sp.write_text(f"Hey, welcome to Eventually Consistent. This is day {a.day} of 77, and today we're talking about {a.title}.\n\n{body}\n\nThat's it for today. See you tomorrow, eventually.")
cmd=[str(R/".venv/bin/python"),str(R/"add_episode.py"),"--date",a.date,"--title",a.title,"--day",str(a.day),"--script",str(sp)]
if a.summary: cmd+=["--summary",a.summary]
subprocess.run(cmd,check=True); subprocess.run([sys.executable,str(R/"deploy_prep.py")],check=True,stdout=subprocess.DEVNULL)
print("DEPLOY_MANIFEST",R/"deploy/files.json")

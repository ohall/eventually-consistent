#!/usr/bin/env python3
"""Prepare Vercel API deploy: writes deploy/<sha>.b64 per file and deploy/files.json (UploadedFile refs).
Upload each with user-Vercel upload_file(xVercelDigest=sha, contentLength=size, requestBody=$file:deploy/<sha>.b64),
then create_deployment(name=tech-bites-podcast, target=production, files=files.json, projectSettings framework=null)."""
import hashlib,base64,json
from pathlib import Path
R=Path(__file__).resolve().parent; S=R/"site"; D=R/"deploy"; D.mkdir(exist_ok=True)
out=[]
for p in sorted(S.rglob("*")):
    if p.is_file():
        b=p.read_bytes(); h=hashlib.sha1(b).hexdigest(); (D/f"{h}.b64").write_text(base64.b64encode(b).decode())
        out.append({"file":str(p.relative_to(S)),"sha":h,"size":len(b)})
(D/"files.json").write_text(json.dumps(out)); print(json.dumps(out,indent=1))

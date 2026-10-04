#!/usr/bin/env python3
"""Recover only hash-pinned model data from an uploaded simulator HTML."""
from pathlib import Path
import sys,re,json,base64,gzip,hashlib
here=Path(__file__).resolve().parent
src=Path(sys.argv[1]);out=Path(sys.argv[2])if len(sys.argv)>2 else here
manifest=json.loads((here/'assets-manifest.json').read_text());html=src.read_text();payloads=[]
for row in manifest['assets']:
 ident=row['id'];m=re.search(r'<script id="cg52-'+re.escape(ident)+r'" type="application/octet-stream">(.*?)</script>',html,re.S)
 if not m:raise SystemExit('CG52_ASSET_MISSING:'+ident)
 packed=base64.b64decode(m[1],validate=True);raw=packed if ident=='geo'else gzip.decompress(packed)
 if len(raw)!=row['bytes']or hashlib.sha256(raw).hexdigest()!=row['sha256']:raise SystemExit('CG52_ASSET_HASH_MISMATCH:'+ident)
 payloads.append((row['file'],raw))
out.mkdir(parents=True,exist_ok=True)
for filename,raw in payloads:(out/filename).write_bytes(raw)
print(json.dumps({'assets':len(payloads),'output':str(out),'hashesVerified':True}))

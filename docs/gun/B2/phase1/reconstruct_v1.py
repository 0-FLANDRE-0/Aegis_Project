"""Reconstruct rejected physical-v1 exactly from immutable4c +archived diff.
Diagnostic provenance only; output is outside the product/repository root.
"""
from pathlib import Path
import base64,gzip,hashlib,json,re,subprocess,tempfile
P=Path(__file__).resolve().parent;R=P.parents[3];D=P/'development/density-frame-v1';raw=(R/'Aegis_SIM_v48_WIP_AIR_ORIGIN_A.html').read_bytes();sha=lambda b:hashlib.sha256(b).hexdigest();assert sha(raw)=='4c5191753025406697520c63afcc97c116a83c4b6b924a4b605b49233c697eeb'
h=raw.decode();m=re.search(r'data-c55-index="13">([^<]+)</script>',h);main=gzip.decompress(base64.b64decode(m[1]));destination=Path('/tmp/aegis-gun-b2/reconstructed-physical-v1.html');destination.parent.mkdir(parents=True,exist_ok=True)
with tempfile.TemporaryDirectory(prefix='b2-v1-source-',dir='/dev/shm')as temporary:
 file=Path(temporary)/'main.js';file.write_bytes(main);subprocess.run(['patch','--batch','--silent',str(file)],input=(D/'GUN_B2.diff').read_bytes(),check=True);main=file.read_bytes()
assert sha(main)==json.loads((D/'build.json').read_text())['mainSha256'];gz=gzip.compress(main,9,mtime=0);h=h[:m.start(1)]+base64.b64encode(gz).decode()+h[m.end(1):];m=re.search(r'const records=(\[.*?\]);',h,re.S);records=json.loads(m[1]);records[13].update(rawBytes=len(main),gzipBytes=len(gz),sha256=sha(main));h=h[:m.start(1)]+json.dumps(records,separators=(',',':'))+h[m.end(1):];destination.write_bytes(h.encode());assert sha(destination.read_bytes())=='929523d60485adfdea65178188ac6bf3d372dc7036cc3cfa6580f7ce52f84337'
q={'pass':True,'output':str(destination),'htmlSha256':sha(destination.read_bytes()),'sourceSha256':sha(main),'shippingProductModified':False,'status':'REJECTED_DENSITY_FRAME_V1_PROVENANCE_ONLY'};(D/'reconstruction.json').write_text(json.dumps(q,indent=2)+'\n');print(q)

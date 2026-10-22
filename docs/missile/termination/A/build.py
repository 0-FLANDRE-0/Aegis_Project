"""Cumulative ALL4 transplant onto the pinned CURRENT PIP_B, never UI_A1.

The embedded ENV_A source is data, not a third live B4 definition. Isolate it
before applying the supplied fail-closed codemods, then replace it with ENV_B.
The old A diagnostics/results remain in docs/envelope/A unchanged.
"""
import base64,gzip,hashlib,json,re,subprocess,tempfile
from pathlib import Path
H=Path(__file__).resolve().parent
R=H.parents[3]
BASE_SHA='ad6ed26d8011fd1bcab80c66eac06a63c748e52b471eb622ef38a2ad26498a55'
NAME='Aegis_SIM_v48_WIP_ALL4_TERM.html'
def decode(h):return gzip.decompress(base64.b64decode(re.search(r'data-c55-index="13">(.*?)</script>',h,re.S)[1])).decode()
def repack(h,s):
 z=gzip.compress(s.encode(),9,mtime=0);m=re.search(r'data-c55-index="13">(.*?)</script>',h,re.S)
 h=h[:m.start(1)]+base64.b64encode(z).decode()+h[m.end(1):]
 m=re.search(r'const records=(\[.*?\]);',h,re.S);r=json.loads(m[1]);r[13].update(rawBytes=len(s.encode()),gzipBytes=len(z),sha256=hashlib.sha256(s.encode()).hexdigest())
 return h[:m.start(1)]+json.dumps(r,separators=(',',':'))+h[m.end(1):]
def build():
 Path('/tmp/aegis-term').mkdir(parents=True,exist_ok=True)
 base=R/'Aegis_SIM_v48_WIP_PIP_B.html'
 if not base.exists():base=R/'archive/v48/WIP_PIP_B'/base.name
 raw=base.read_bytes();assert hashlib.sha256(raw).hexdigest()==BASE_SHA
 h=raw.decode();s=decode(h);a=s.index('// ENV_A: diagnostic-only source capsule.');b=s.index('\n  completeShipStartup();',a)
 old_env=s[a:b];s=s[:a]+s[b:]
 with tempfile.TemporaryDirectory()as td:
  src=Path(td)/'input.js';out=Path(td)/'output.js';src.write_text(s)
  receipt=json.loads(subprocess.check_output(['node',str(H/'kit/AEGIS_B4_ALL4_Termination_apply.mjs'),'--input',str(src),'--output',str(out)],text=True))
  s=subprocess.check_output(['node','-e',"const fs=require('fs');process.stdout.write(require(process.argv[1]).apply(fs.readFileSync(process.argv[2],'utf8')))",str(H/'support-guard.cjs'),str(out)],text=True)
  Path('/tmp/aegis-term/final-live.js').write_text(s)
 # All live source edits are the supplied three codemods. ENV is diagnostic-only.
 env=R/'docs/envelope/B/adapter.js'
 s=s.replace('\n  completeShipStartup();','\n'+(env.read_text()if env.exists()else old_env)+'\n  completeShipStartup();',1)
 h=repack(h,s).replace('v48_WIP_PIP_B','v48_WIP_ALL4_TERM').replace('V48_WIP_PIP_B','V48_WIP_ALL4_TERM')
 out=R/NAME;out.write_text(h);Path('/tmp/aegis-term/current-main.js').write_text(s)
 print(json.dumps({'html':str(out),'bytes':len(h.encode()),'sha256':hashlib.sha256(h.encode()).hexdigest(),'steps':receipt['steps']}))
if __name__=='__main__':build()

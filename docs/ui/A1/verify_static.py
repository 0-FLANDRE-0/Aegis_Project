from pathlib import Path
import argparse,base64,gzip,hashlib,json,os,re,subprocess,tempfile
from build import build,decoded,BASE_SHA,bounds
R=Path(__file__).resolve().parents[3]
def main():
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);base=a.baseline.read_bytes();raw=a.html.read_bytes();h=raw.decode();s=decoded(h);old=decoded(base.decode());checks={'baselinePinned':hashlib.sha256(base).hexdigest()==BASE_SHA,'exactRebuild':build(base)[0].encode()==raw};rec=lambda x:json.loads(re.search(r'const records=(\[.*?\]);',x,re.S)[1]);checks['other13RecordsExact']=rec(h)[:13]==rec(base.decode())[:13]
 env=os.environ.copy();localDeps=R/'docs/performance/F/node_modules';sharedDeps=Path('/workspace/aegis-performance-f/docs/performance/F/node_modules');env['NODE_PATH']=str(localDeps if localDeps.exists()else sharedDeps)if(localDeps.exists()or sharedDeps.exists())else env.get('NODE_PATH','')
 with tempfile.TemporaryDirectory()as t:
  t=Path(t)
  for i,row in enumerate(rec(h)):
   z=base64.b64decode(re.search(r'data-c55-index="'+str(i)+r'">(.*?)</script>',h,re.S)[1]);b=gzip.decompress(z);f=t/f'{i}.js';f.write_bytes(b);checks[f'packed{i}']=len(z)==row['gzipBytes']and len(b)==row['rawBytes']and hashlib.sha256(b).hexdigest()==row['sha256'];checks[f'syntax{i}']=subprocess.run(['node','--check',str(f)],capture_output=True).returncode==0
  for i,m in enumerate(re.finditer(r'<script\b([^>]*)>(.*?)</script>',h,re.S)):
   if 'application/octet-stream'in m[1]or not m[2].strip():continue
   f=t/f'loader{i}.js';f.write_text(m[2]);checks['loader'+str(i)]=subprocess.run(['node','--check',str(f)],capture_output=True).returncode==0
  b=t/'base.js';c=t/'candidate.js';b.write_text(old);c.write_text(s);run=subprocess.run(['node',str(R/'docs/performance/F/verify_scope.cjs'),str(b),str(c)],env=env,capture_output=True,text=True);scope=json.loads(run.stdout);checks['noNewUnresolved']=scope['pass']
  js=r'''const fs=require('fs'),acorn=require('acorn'),crypto=require('crypto');function funcs(p){const s=fs.readFileSync(p,'utf8'),a=acorn.parse(s,{ecmaVersion:'latest'}),m={};function walk(n){if(!n||typeof n!=='object')return;if(n.type==='FunctionDeclaration'&&n.id){const name=n.id.name;(m[name]??=[]).push(crypto.createHash('sha256').update(s.slice(n.start,n.end).replaceAll('v48_WIP_UI_A1','VERSION').replaceAll('v48_WIP_UI_A','VERSION').replaceAll('v48_WIP_VP_A','VERSION')).digest('hex'));}for(const v of Object.values(n))if(Array.isArray(v))v.forEach(walk);else if(v&&typeof v==='object')walk(v);}walk(a);return m;}const b=funcs(process.argv[1]),c=funcs(process.argv[2]);process.stdout.write(JSON.stringify({total:Object.keys(b).length,changed:Object.keys(b).filter(k=>b[k].some(h=>b[k].filter(x=>x===h).length>(c[k]??[]).filter(x=>x===h).length))}));'''
  functionAudit=json.loads(subprocess.check_output(['node','-e',js,str(b),str(c)],env=env,text=True));allowed=['writeBox','bring','clampWindow','serialize','valid','restore','open','dock','drag','createWindow','applyPreset','reflow','update','activate'];checks['functionChangesPresentationOnly']=all(k in allowed for k in functionAudit['changed'])
 ba,bb=bounds(old);ca,cb=bounds(s);checks['engineOutsideShellExact']=(old[:ba]+old[bb:])==(s[:ca]+s[cb:]).replace('v48_WIP_UI_A1','v48_WIP_UI_A')
 checks['uiStylePresent']='id="uiStyleA"' in h;checks['noControlCloning']=all(x not in (R/'docs/ui/A1/windows.js').read_text() for x in ['cloneNode','innerHTML','outerHTML','insertAdjacentHTML'])
 for id in ['sov-registration-a','sov-meta-a','sov-textures-a','sov-geometry-a']:
  find=lambda x:re.search(r'<script id="'+id+r'"[^>]*>(.*?)</script>',x,re.S)[1]
  checks[id+'Exact']=find(h)==find(base.decode())
 checks['legacyTimerRemoved']='setTimeout(resize, 120)'not in s and 'setTimeout(() => { setTacticalZoom(1)'not in s
 checks['legacyDimensionsRemoved']=not re.search(r'(?<!\.)\b(innerWidth|innerHeight)\b',s)
 checks['distanceNeverSavedAsPixels']='mapZoom'not in old[old.index('function exportOperationalState()'):old.index('function prepareOperationalStateV48Wip11B')]
 checks['allGeometryEventsCentral']=all(x in s for x in ["['resize','orientationchange']","['fullscreenchange','webkitfullscreenchange']","['resize','scroll']",'new ResizeObserver(schedule)'])
 out={'pass':all(checks.values()),'checks':checks,'functionAudit':functionAudit,'scope':scope,'bytes':len(raw),'addedBytes':len(raw)-len(base),'htmlSha256':hashlib.sha256(raw).hexdigest()};(a.out/'static.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'pass':out['pass'],'checks':len(checks),'failed':[k for k,v in checks.items()if not v],'functions':functionAudit}));raise SystemExit(0 if out['pass']else 1)
if __name__=='__main__':main()

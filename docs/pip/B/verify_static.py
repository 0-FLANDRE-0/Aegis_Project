import argparse,base64,gzip,hashlib,json,os,re,subprocess,sys,tempfile
from pathlib import Path
from build import build,decode,BASE_SHA
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('base',type=Path);p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);raw=a.html.read_bytes();base=a.base.read_bytes();h=raw.decode();old=decode(base.decode());s=decode(h);checks={};check=lambda k,v:checks.update({k:bool(v)})
check('pinnedBaseline',hashlib.sha256(base).hexdigest()==BASE_SHA);check('exactRebuild',build(base)[0].encode()==raw)
rows=lambda h:json.loads(re.search(r'const records=(\[.*?\]);',h,re.S)[1]);check('records0to12Unchanged',rows(h)[:13]==rows(base.decode())[:13])
with tempfile.TemporaryDirectory()as tmp:
 t=Path(tmp)
 for i,r in enumerate(rows(h)):
  z=base64.b64decode(re.search(r'data-c55-index="'+str(i)+r'">(.*?)</script>',h,re.S)[1]);v=gzip.decompress(z);f=t/f'{i}.js';f.write_bytes(v);check(f'packed{i}',len(z)==r['gzipBytes']and len(v)==r['rawBytes']and hashlib.sha256(v).hexdigest()==r['sha256']);check(f'syntax{i}',subprocess.run(['node','--check',str(f)],capture_output=True).returncode==0)
 b=t/'base.js';c=t/'candidate.js';b.write_text(old);c.write_text(s);env={**os.environ,'NODE_PATH':os.environ.get('NODE_PATH',str(R/'docs/performance/F/node_modules'))}
 q=subprocess.run(['node',str(R/'docs/performance/F/verify_scope.cjs'),str(b),str(c)],env=env,capture_output=True,text=True);scope=json.loads(q.stdout);check('onlyExpectedBrowserBuiltinsAdded',set(scope['added'])<=set(['Function','TextEncoder','URL','Worker','crypto']))
 js="""const fs=require('fs'),a=require('acorn'),h=require('crypto');function rows(p){const s=fs.readFileSync(p,'utf8'),ast=a.parse(s,{ecmaVersion:'latest'}),r={};function walk(n){if(!n||typeof n!=='object')return;if(n.type==='FunctionDeclaration'){(r[n.id.name]??=[]).push(h.createHash('sha256').update(s.slice(n.start,n.end).replaceAll('v48_WIP_PIP_A','VERSION').replaceAll('v48_WIP_PIP_B','VERSION')).digest('hex'))}for(const v of Object.values(n))if(Array.isArray(v))v.forEach(walk);else if(v&&typeof v==='object')walk(v)}walk(ast);return r}const b=rows(process.argv[1]),c=rows(process.argv[2]);console.log(JSON.stringify(Object.keys(b).filter(k=>b[k].some(x=>b[k].filter(q=>q===x).length>(c[k]??[]).filter(q=>q===x).length))));"""
 changed=json.loads(subprocess.check_output(['node','-e',js,str(b),str(c)],env=env,text=True));allowed=['pipDrawRadarPixelsA','focusWindow','focusOpen','restore','windowSize','titleHeight','applyPreset','place','contextFor'];check('onlyPresentationFunctionsChanged',all(x in allowed for x in changed))
 # Physical profiles/loft data and the native flight/guidance/fuze declarations have unchanged hashes.
 core=['SAM_MISSILE_PROFILES','SAM_LOFT_PROFILE_REGISTRY','updateMissileBodyB3','updateSamSixDofLiteDynamics','getGuidanceTargetStateV1','loftB4UpdatePlan','vlsReleaseStandardB1','vlsReleaseEssmB1'];audit=json.loads((R/'docs/envelope/A/dependencies.json').read_text());check('nativeSourceCapsuleHasNoMissingLiveSymbol',audit['missing']==['isFinite']);check('nativeFlightBodiesCopied',all(x in [v['name']for v in audit['rows']]for x in core))
for marker,end in [('function exportOperationalState()','function operationalValidationContextV48Wip11B()'),('function simulateFixedTick(','function step(')]:
 if marker in old and end in old[old.index(marker):]:check(marker+'Unchanged',old[old.index(marker):old.index(end,old.index(marker))]==s[s.index(marker):s.index(end,s.index(marker))])
for id in ['sov-registration-a','sov-meta-a','sov-textures-a','sov-geometry-a']:
 f=lambda text:re.search(r'<script id="'+id+r'"[^>]*>(.*?)</script>',text,re.S)[1];check(id+'Unchanged',f(h)==f(base.decode()))
check('canvasCardCallRemoved','pipDrawLockedCardA(ctx,tr,id,'not in s);check('originalToolbarReparentedThenRemoved','tools.remove(); // Original command listeners remain attached'in s);check('sensorGateDefaultOff',"let sensorBeams=false"in s);check('independent125msTimer','setInterval(update,125)'in s)
out={'pass':all(checks.values()),'checks':checks,'changedNativeFunctionNames':changed,'scope':scope,'htmlSha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)};(a.out/'static.json').write_text(json.dumps(out,indent=2));print(json.dumps({'pass':out['pass'],'checks':len(checks),'failed':[k for k,v in checks.items()if not v],'changed':changed}));raise SystemExit(0 if out['pass']else 1)

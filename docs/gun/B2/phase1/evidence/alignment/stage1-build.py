"""Cumulative B2 build from the immutable, reviewed AIR_ORIGIN_A product."""
from pathlib import Path
import argparse,base64,difflib,gzip,hashlib,json,re
P=Path(__file__).resolve().parent;R=P.parents[3];BASE=R/'Aegis_SIM_v48_WIP_AIR_ORIGIN_A.html';OUT=R/'Aegis_SIM_v48_WIP_GUN_B2.html';sha=lambda b:hashlib.sha256(b).hexdigest()
parser=argparse.ArgumentParser();parser.add_argument('--stage',choices=['alignment','dispersion','air-window','all'],default='alignment');args=parser.parse_args()
raw=BASE.read_bytes();assert sha(raw)=='4c5191753025406697520c63afcc97c116a83c4b6b924a4b605b49233c697eeb';h=raw.decode();m=re.search(r'data-c55-index="13">([^<]+)</script>',h);before=gzip.decompress(base64.b64decode(m[1])).decode();s=before
begin=s.rindex('function createProfileGunModuleWip13B3(');end=s.index('function gunB1IsAir(',begin);old=s[begin:end];module=old
needle='    if(!gate.ok)return gate;\n    const pointing='
replacement="    if(!gate.ok)return gate;\n    const b2Failure=gunB2PrepareRelease(state,id,ammoId,solveAirTrack,spec);if(b2Failure)return b2Failure;\n    if(gunB2Flags.alignment&&state.solution.airDomain){gate=gunB1ReleaseGate(id,state.solution,{...options,module:spec,mode:options.mode??'MANUAL'});if(!gate.ok)return gate;}\n    const pointing="
assert module.count(needle)==1;module=module.replace(needle,replacement,1)
needle='    const clearance=wip13b1GunClearance(spec,state.bodyAzRad,state.elevationRad,300);'
replacement="    if(gunB2Flags.alignment&&state.solution.airDomain&&state.solution.computedStep!==simStepCounter)return {ok:false,reason:'MOUNT_NOT_ON_SOLUTION',b2Reason:'CURRENT_TICK_SOLUTION_REQUIRED'};\n"+needle
assert module.count(needle)==1;module=module.replace(needle,replacement,1)
needle='    const consent=state.pendingSingleFire.active?'
assert module.count(needle)==1;module=module.replace(needle,'    gunB2RecordRelease(projectile,state.solution);\n'+needle,1)
module=module.replace('wip13b6GunPointingAssessment(', 'gunB2Pointing(')
runtime=(P/'runtime.js').read_text();flags={k:False for k in ['alignment','dispersion','airWindow','fuze','fragments']};flags['alignment']=True
if args.stage in ['dispersion','air-window','all']:flags['dispersion']=True
if args.stage in ['air-window','all']:flags['airWindow']=True
if args.stage=='all':flags.update(fuze=True,fragments=True)
runtime=re.sub(r'/\* B2_DEFAULT_FLAGS \*/\{[^}]+\}',json.dumps(flags,separators=(',',':')),runtime,count=1)
s=s[:begin]+module+runtime+'\n'+s[end:]
gz=gzip.compress(s.encode(),9,mtime=0);h=h[:m.start(1)]+base64.b64encode(gz).decode()+h[m.end(1):];m=re.search(r'const records=(\[.*?\]);',h,re.S);records=json.loads(m[1]);records[13].update(rawBytes=len(s.encode()),gzipBytes=len(gz),sha256=sha(s.encode()));h=h[:m.start(1)]+json.dumps(records,separators=(',',':'))+h[m.end(1):];OUT.write_bytes(h.encode())
(P/'build.json').write_text(json.dumps({'baseline':BASE.name,'baselineSha256':sha(raw),'output':OUT.name,'htmlSha256':sha(OUT.read_bytes()),'mainSha256':sha(s.encode()),'stage':args.stage,'defaultFlags':flags},indent=2)+'\n');(P/'GUN_B2.diff').write_text(''.join(difflib.unified_diff(before.splitlines(True),s.splitlines(True),fromfile=BASE.name+'::main',tofile=OUT.name+'::main')));Path('/tmp/aegis-gun-b2/phase1-current.js').write_text(s);print((P/'build.json').read_text())

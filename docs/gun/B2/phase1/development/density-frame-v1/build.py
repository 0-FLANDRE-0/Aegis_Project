"""Cumulative B2 build from the immutable, reviewed AIR_ORIGIN_A product."""
from pathlib import Path
import argparse,base64,difflib,gzip,hashlib,json,re
P=Path(__file__).resolve().parent;R=P.parents[3];BASE=R/'Aegis_SIM_v48_WIP_AIR_ORIGIN_A.html';OUT=R/'Aegis_SIM_v48_WIP_GUN_B2.html';sha=lambda b:hashlib.sha256(b).hexdigest()
parser=argparse.ArgumentParser();parser.add_argument('--stage',choices=['alignment','dispersion','air-window','all'],default='all');parser.add_argument('--ui-preview',action='store_true');args=parser.parse_args()
if args.ui_preview:OUT=Path('/tmp/aegis-gun-b2/phase1-ui.html')
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
if (P/'dispersion-constants.json').exists():
 calibration=json.loads((P/'dispersion-constants.json').read_text());runtime=runtime.replace('mvSigmaFrac:.0015,elevSigmaMrad:.10','mvSigmaFrac:'+repr(calibration['mvSigmaFrac'])+',elevSigmaMrad:'+repr(calibration['elevSigmaMrad']),1);runtime=runtime.replace("status:'PENDING_NATIVE_CALIBRATION'","status:'NATIVE_ANCHOR_CALIBRATED'",1)
if args.stage in ['dispersion','air-window','all']:flags['dispersion']=True
if args.stage in ['air-window','all']:flags['airWindow']=True
if args.stage=='all':flags.update(fuze=True,fragments=True)
runtime=re.sub(r'/\* B2_DEFAULT_FLAGS \*/\{[^}]+\}',json.dumps(flags,separators=(',',':')),runtime,count=1)
if (P/'range-table.json').exists():
 table=json.loads((P/'range-table.json').read_text());runtime+='\nconst GUN_B2_RANGE_TABLE=deepFreezeShipProfileV48Wip09('+json.dumps(table,separators=(',',':'),ensure_ascii=False)+');\n'+(P/'ring.js').read_text()
s=s[:begin]+module+runtime+'\n'+s[end:]
needle='function gunB1ShellEvent(p,prev,next,dt){';assert s.count(needle)==1;s=s.replace(needle,needle+'\n if(gunB2Flags.fuze)return gunB2ShellEvent(p,prev,next,dt);',1)
needle="gunB1FragmentationPk(arrival.missM,'MFF_127_SIM',row.object.label??'Kh-35U',kin)";assert s.count(needle)==1;s=s.replace(needle,"gunB2FragmentDetail(arrival.missM,'MFF_127_SIM',row.object.label??'Kh-35U',kin,rel,v,tv)",1)
needle='arrivalMissM:arrival.missM,result,pk:detail.pk';assert s.count(needle)==1;s=s.replace(needle,'arrivalMissM:gunB2Flags.fragments?(detail.missDistM??arrival.missM):arrival.missM,result,pk:detail.pk,...(gunB2Flags.fragments?{gunB2FragmentField:detail.gunB2Field??null}:{})',1)
start=before.index('function gunB1FragmentationPk(');stop=before.index('const SHIP_GUN_BUILDER_REGISTRY_V48_WIP13B8',start);pk=before[start:stop].strip().replace('function gunB1FragmentationPk(','function gunB2FragmentationPk(',1)
pk=pk.replace('const w=GUN_B1_SPEC.fragments,tp=', 'const w={...GUN_B1_SPEC.fragments,annularBandHalfAngleDeg:GUN_B2_SPEC.fragments.halfAngleDeg,coneHalfAngleDeg:GUN_B2_SPEC.fragments.halfAngleDeg},tp=',1)
needle="    if(!w||!tp)return {pk:0,reason:'NO_FRAGMENT_PROFILE'};";assert pk.count(needle)==1;pk=pk.replace(needle,needle+"\n    const field=gunB2FragmentField(kin,_wip88GurneyFragmentSpeed(w));if(!field.ok)return {pk:0,reason:field.reason,gunB2Field:field};",1)
pk=pk.replace('Math.max(0.75,Number(missDistM)||0.75)','Math.max(0.75,field.radiusM)',1)
needle='4*Math.PI*r*r*Math.max(0.10,Math.sin(thetaCenter))*Math.max(0.01,Math.sin(half))';assert pk.count(needle)==1;pk=pk.replace(needle,'2*Math.PI*r*r*(Math.cos(field.worldMinRad)-Math.cos(field.worldMaxRad))',1)
pk=pk.replace('return {pk,weaponType,','return {pk,gunB2Field:field,weaponType,',1)
s=s.replace(runtime+'\n',runtime+'\n'+pk+'\n',1)
if (P/'range-table.json').exists():
 start=s.index("  if(s.weapon==='MK45'){const radius=kmToWorld(GUN_B1_SPEC.autoRangeM/1000)")
 end=s.index("\n  if(s.weapon==='HARPOON'&&harpoonRuntimeA()",start)
 s=s[:end]+"\n  if(s.weapon==='MK45')gunB2DrawEffectiveRing(context,view);"+s[end:]
spawns=list(re.finditer(r'^function spawnMainGunProjectileWip13B3\(',s,re.M));assert len(spawns)==2
for spawn in reversed(spawns):
 at=spawn.start();stop=s.index('\n}',at)+2;body=s[at:stop];needle='mainGunProjectilesWip13B3.push(projectile);';assert body.count(needle)==1;body=body.replace(needle,'if(gunB2Flags.dispersion)gunB2ApplyDispersion(projectile,request,trunnion);'+needle,1);s=s[:at]+body+s[stop:]
if (P/'range-table.json').exists() and args.stage=='all':
 table=json.loads((P/'range-table.json').read_text())
 assert table['runtimeTemplateSha256']==sha((P/'runtime.js').read_bytes()),'GUN_B2_RANGE_REMEASUREMENT_REQUIRED:RUNTIME'
 assert table['dispersionConstantsSha256']==sha((P/'dispersion-constants.json').read_bytes()),'GUN_B2_RANGE_REMEASUREMENT_REQUIRED:DISPERSION'
 spec_text=s[s.index('const GUN_B2_SPEC='):s.index('\nlet gunB2Flags')]
 assert sha(spec_text.encode())==table['compiledGunSpecSha256'],'GUN_B2_RANGE_REMEASUREMENT_REQUIRED:COMPILED_SPEC'
 expected={**table['nativeSourceHashes'],'createProfileGunModuleWip13B3':table['nativeFactorySourceSha256']}
 for name,value in expected.items():
  closing=r'\n  }'if name=='gunB2FragmentationPk'else r'\n}'
  functions=list(re.finditer(r'^function '+re.escape(name)+r'\([\s\S]*?'+closing,s,re.M));assert functions and sha(functions[-1].group().encode())==value,'GUN_B2_RANGE_REMEASUREMENT_REQUIRED:'+name
gz=gzip.compress(s.encode(),9,mtime=0);h=h[:m.start(1)]+base64.b64encode(gz).decode()+h[m.end(1):];m=re.search(r'const records=(\[.*?\]);',h,re.S);records=json.loads(m[1]);records[13].update(rawBytes=len(s.encode()),gzipBytes=len(gz),sha256=sha(s.encode()));h=h[:m.start(1)]+json.dumps(records,separators=(',',':'))+h[m.end(1):];OUT.write_bytes(h.encode())
(P/('ui-build.json'if args.ui_preview else'build.json')).write_text(json.dumps({'baseline':BASE.name,'baselineSha256':sha(raw),'output':OUT.name,'htmlSha256':sha(OUT.read_bytes()),'mainSha256':sha(s.encode()),'stage':args.stage,'defaultFlags':flags},indent=2)+'\n');(P/('GUN_B2_UI_PREVIEW.diff'if args.ui_preview else'GUN_B2.diff')).write_text(''.join(difflib.unified_diff(before.splitlines(True),s.splitlines(True),fromfile=BASE.name+'::main',tofile=OUT.name+'::main')));Path('/tmp/aegis-gun-b2/'+('phase1-ui.js'if args.ui_preview else'phase1-current.js')).write_text(s);print((P/('ui-build.json'if args.ui_preview else'build.json')).read_text())

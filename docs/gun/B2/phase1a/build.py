"""Only the three approved B2A changes, plus the measured display-only table."""
from pathlib import Path
import argparse,base64,difflib,gzip,hashlib,json,re
from deadline import check
P=Path(__file__).resolve().parent;R=P.parents[3];sha=lambda b:hashlib.sha256(b).hexdigest();ap=argparse.ArgumentParser();ap.add_argument('--embed',action='store_true');a=ap.parse_args();check()
raw=Path('/tmp/aegis-gun-b2/b2a-baseline.html').read_bytes();assert sha(raw)=='c48c2396932e07c8051b7a07d2da282951587283d768f2caa384a48936a0ed8b';match=json.loads((P/'matching.json').read_text());assert match['within20to80'] and(P/'MATCHING.md').exists();center=match['fixedPolarCenterDeg'];m=re.search(rb'data-c55-index="13">([^<]+)</script>',raw);old=gzip.decompress(base64.b64decode(m[1])).decode();s=old
sigma=json.loads((P.parent/'phase1/dispersion-constants.json').read_text());train=sigma['elevSigmaMrad'];changes=[]
for before,after,reason in [('trainSigmaMrad:.20','trainSigmaMrad:'+repr(train),'Equal angular dispersion; MV/elevation unchanged'),('fuze:{polarCenterDeg:70','fuze:{polarCenterDeg:'+repr(center),'One fixed fuze-warhead match from full G7 burst-speed median')]:
 assert s.count(before)==1;s=s.replace(before,after,1);changes.append({'before':before,'after':after,'reason':reason})
pattern=r'function gunB2Pointing\([\s\S]*?\n}';oldFn=re.search(pattern,s)[0];newFn=oldFn
start=oldFn.index(' const half=');end=oldFn.index('\n if(!solution.ok',start)
newLine=" const half=GUN_B1_SPEC.proxRadiusM*GUN_B2_SPEC.airWindow.radiusFraction,sigmaCross=Math.max(0,Number(solution.fireControlTrackQuality?.predictedImpactSigmaM?.cross)||0),limitM=half,impactWindow={schema:'AEGIS_GUN_B2_AIR_WINDOW',basis:'FUZE_RADIUS_FRACTION_SYMMETRIC',crossHalfM:half,verticalUpM:half,verticalDownM:half,uncertaintyM:0,uncertaintyDeducted:false,effectiveHalfM:limitM,truthUsed:false};"
newFn=oldFn[:start]+newLine+oldFn[end:];s=s.replace(oldFn,newFn,1);changes.append({'symbol':'gunB2Pointing','reason':'Fixed mechanical half-width6.25m; no observation deduction/floor. Existing native quality/release gates unchanged.','oldSha256':sha(oldFn.encode()),'newSha256':sha(newFn.encode())})
namespaceStart=s.index('// GUN_B2: fictional game model.');tableStart=s.index('const GUN_B2_RANGE_TABLE=');runtime=s[namespaceStart:tableStart].rstrip()+'\n';(P/'runtime.js').write_text(runtime)
names=list(json.loads((P.parent/'phase1/measurement-build.json').read_text())['modelFingerprints']['nativeSourceHashes']);model={'factorySha256':None,'runtimeFileSha256':sha(runtime.encode()),'dispersionConstantsSha256':sha((P.parent/'phase1/dispersion-constants.json').read_bytes()),'compiledGunSpecSha256':sha(s[s.index('const GUN_B2_SPEC='):s.index('\nlet gunB2Flags')].encode()),'nativeSourceHashes':{}}
# The factory and native extraction contracts are identical to the Phase1 builder.
f0=s.rindex('function createProfileGunModuleWip13B3(');f1=s.index('// GUN_B2: fictional game model.',f0);model['factorySha256']=sha(s[f0:f1].encode())
for name in names:
 closing=r'\n  }'if name=='gunB2FragmentationPk'else r'\n}';f=list(re.finditer(r'^function '+re.escape(name)+r'\([\s\S]*?'+closing,s,re.M));assert f,name;model['nativeSourceHashes'][name]=sha(f[-1][0].encode())
oldTable=re.search(r'const GUN_B2_RANGE_TABLE=deepFreezeShipProfileV48Wip09\(([^\n]+)\);',old)[0]
if not(P/'previous-range-table.json').exists():(P/'previous-range-table.json').write_text(json.dumps(json.loads(oldTable.split('V48Wip09(',1)[1][:-2]),indent=2)+'\n')
if a.embed:
 table=json.loads((P/'range-table.json').read_text());assert table['measurementModelFingerprints']==model,'B2A_MEASUREMENT_MODEL_MISMATCH_NO_OUTPUT';s=s.replace(oldTable,'const GUN_B2_RANGE_TABLE=deepFreezeShipProfileV48Wip09('+json.dumps(table,separators=(',',':'))+');',1)
# Exact inverse proof of all permitted source edits.
reconstructed=s
if a.embed:reconstructed=reconstructed.replace(re.search(r'const GUN_B2_RANGE_TABLE=deepFreezeShipProfileV48Wip09\(([^\n]+)\);',s)[0],oldTable,1)
reconstructed=reconstructed.replace(newFn,oldFn,1)
for c in changes[:2]:reconstructed=reconstructed.replace(c['after'],c['before'],1)
assert reconstructed==old,'UNAUTHORIZED_SOURCE_CHANGE'
packed=base64.b64encode(gzip.compress(s.encode(),mtime=0));out=raw[:m.start(1)]+packed+raw[m.end(1):];rm=re.search(rb'const records=(\[.*?\]);',out,re.S);records=json.loads(rm[1]);records[13]['sha256']=sha(s.encode());records[13]['rawBytes']=len(s.encode());records[13]['encodedBytes']=len(packed);out=out[:rm.start(1)]+json.dumps(records,separators=(',',':')).encode()+out[rm.end(1):];(R/'Aegis_SIM_v48_WIP_GUN_B2.html').write_bytes(out);Path('/tmp/aegis-gun-b2/b2a-current.js').write_text(s)
q={'baselineCommit':'c1d17cee4eb5d2a7ce00d0fa17b3c46a0908bff9','baselineSha256':sha(raw),'htmlSha256':sha(out),'mainSha256':sha(s.encode()),'modelFingerprints':model,'onlyApprovedChangesInverseExact':True,'embeddedTableState':'B2A_MEASURED'if a.embed else'HISTORICAL_B2_UNTIL_FINAL_EMBED','changes':changes};(P/'build.json').write_text(json.dumps(q,indent=2)+'\n');(P/'GUN_B2A.diff').write_text(''.join(difflib.unified_diff(old.splitlines(True),s.splitlines(True),fromfile='B2_c48c2396::main',tofile='B2A::main')))
if not a.embed:
 assert not(P/'measurement-build.json').exists(),'MEASUREMENT_BUILD_ALREADY_FROZEN';(P/'measurement-build.json').write_text(json.dumps(q,indent=2)+'\n')
print(json.dumps(q,indent=2))

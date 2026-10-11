"""Pinned H4 → H4A. Connect native local RF self-defense and measured EW timing."""
import argparse,base64,gzip,hashlib,json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent
BASE_SHA='602371dfd5be5147c2e04dd4078e3216ca4f47e8ce4e7b0092bd861c3d9a5132'
OLD='v48_WIP_MULTI_SHIP_H4';NEW='v48_WIP_MULTI_SHIP_H4A';PATCHES=[]
def once(s,a,b,label):
 assert s.count(a)==1,(label,s.count(a));PATCHES.append(label);return s.replace(a,b,1)
def extract(s,key):
 q=json.loads((HERE/'patch-index.json').read_text())[key];v=s[q['start']:q['end']];assert hashlib.sha256(v.encode()).hexdigest()==q['sha256'],key;return v
def build(s):
 original=s
 f=extract(original,'createWeaponContextD')
 lo=f.index('function defenseCloseInE(){');hi=f.index('\nfunction defenseSnapshotOwnerE()',lo)
 f=once(f,f[lo:hi],(HERE/'local-defense.js').read_text().rstrip(),'local measured consent alongside existing CMS authority')
 f=once(f,'function defenseSnapshotOwnerE(){',(HERE/'probe.js').read_text()+'\nfunction defenseSnapshotOwnerE(){','diagnostic late-invalidation probe of natural capabilities')
 f=once(f,"wip119CancelPending('AUTO_OFF');defenseE.closeIn.clear();", "wip119CancelPending('AUTO_OFF');for(const mount of ciws)defenseDropMountH4A(mount);",'HOLD releases automatic mount ownership')
 f=once(f,'{c55Bank,phalanxFireControlGate,','{defenseLocalReleaseH4A,c55Bank,phalanxFireControlGate,','actual release rechecks owner-local capability')
 f=once(f,'  return {attackPreviewH3:', '  return {localDefenseGuardProbeH4A,localDefenseCuesH4A:defenseLocalCuesH4A,attackPreviewH3:','detached local RF measurement port and diagnostics')
 s=once(s,extract(original,'createWeaponContextD'),f,'foreign weapon owner closure')
 f=extract(original,'ownerCloseInOneTickE')
 f=once(f,'gate=ownerTrackGateD(r,c.trackId,c),','gate=c.authorityH4A?h.defenseLocalReleaseH4A(mount,p):ownerTrackGateD(r,c.trackId,c),','typed local authority never generic CMS bypass')
 f=once(f,'const local=[...h.c55Bank(mount).files.values()].find(', 'const local=c.authorityH4A?gate.file:[...h.c55Bank(mount).files.values()].find(','native fire-control uses independent measured file')
 s=once(s,extract(original,'ownerCloseInOneTickE'),f,'actual foreign close-in release')
 f=extract(original,'recordOwnerCloseInE')
 f=once(f,"mode:p.command.automatic?'AUTO':'MANUAL',truthUsed:false", "mode:p.command.automatic?'AUTO':'MANUAL',authority:p.command.authorityH4A??'CMS',truthUsed:false",'auditable local versus CMS release')
 s=once(s,extract(original,'recordOwnerCloseInE'),f,'close-in release diagnostics')
 f=extract(original,'createElectronicContextF')
 f=once(f,'function updateSoftKillThreatManager(dt){',"function softKillLocalFusionH4A(trackSeeds,activeEsm,usedEsm){return localDefenseTimingFusionH4A(owner.weapons.executionD.context.localDefenseCuesH4A(),trackSeeds,activeEsm,usedEsm,{xM:worldToMeters(shipNav.positionWorld.x),yM:worldToMeters(shipNav.positionWorld.y)});}\nfunction updateSoftKillThreatManager(dt){",'detached anonymous local RF and passive emitter fusion port')
 f=once(f,'    for(const es of activeEsm){\n      if(usedEsm.has(es.id)) continue;', '    threats.push(...softKillLocalFusionH4A(trackSeeds,activeEsm,usedEsm));\n    for(const es of activeEsm){\n      if(usedEsm.has(es.id)) continue;','EW timing from real local measurements without guessing ESM range')
 s=once(s,extract(original,'createElectronicContextF'),f,'foreign EW owner closure')
 s=once(s,'const NAVAL_WEAPONS_POLICY_D=',(HERE/'local-ew.js').read_text()+'\nconst NAVAL_WEAPONS_POLICY_D=','pure measured-data fusion and boundary selftests')
 s=once(s,'window.__CORE_SELFTEST_FAILURES__=failures.slice();',"const defenseH4A=localDefenseSelfTestH4A();if(!defenseH4A.pass)failures.push('LOCAL_DEFENSE_H4A '+JSON.stringify(defenseH4A.checks));window.__CORE_SELFTEST_FAILURES__=failures.slice();",'built-in H4A transition and ambiguity guards')
 s=once(s,'defenseSnapshotE:defenseSnapshotE,','localDefenseSelfTestH4A:localDefenseSelfTestH4A,defenseSnapshotE:defenseSnapshotE,','detached boundary diagnostics')
 return s
def main():
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('output',type=Path);a=p.parse_args();raw=a.baseline.read_bytes();assert hashlib.sha256(raw).hexdigest()==BASE_SHA
 html=raw.decode();m=re.search(r'<script type="application/octet-stream" data-c55-index="13">(.*?)</script>',html,re.S);src=gzip.decompress(base64.b64decode(m[1])).decode();candidate=build(src).replace(OLD,NEW);gz=gzip.compress(candidate.encode(),mtime=0)
 html=html[:m.start(1)]+base64.b64encode(gz).decode()+html[m.end(1):];row=re.search(r'const records=(\[.*?\]);',html,re.S);records=json.loads(row[1]);records[13].update(rawBytes=len(candidate.encode()),gzipBytes=len(gz),sha256=hashlib.sha256(candidate.encode()).hexdigest());html=html[:row.start(1)]+json.dumps(records,separators=(',',':'))+html[row.end(1):];html=html.replace(OLD,NEW).replace('V48_WIP_MULTI_SHIP_H4','V48_WIP_MULTI_SHIP_H4A')
 a.output.write_text(html);a.output.with_suffix('.main.js').write_text(candidate);manifest={'baselineSha256':BASE_SHA,'htmlSha256':hashlib.sha256(html.encode()).hexdigest(),'mainSha256':hashlib.sha256(candidate.encode()).hexdigest(),'changedPackedRecords':[13],'patches':PATCHES};a.output.with_suffix('.manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({'sha256':manifest['htmlSha256'],'main':manifest['mainSha256'],'bytes':len(html.encode()),'patches':len(PATCHES)}))
if __name__=='__main__':main()

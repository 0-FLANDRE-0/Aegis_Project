"""Pinned G -> H1 utility decisions; only packed record 13 and labels change."""
import argparse,base64,gzip,hashlib,json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent
BASE_SHA='7ffded6480e74e0f9ab6259c2c8a9e4dfd81ad70bb2434d8dcfd711db2e7bda7'
OLD='v48_WIP_MULTI_SHIP_G';NEW='v48_WIP_MULTI_SHIP_H1';PATCHES=[]
def once(s,a,b,label):
 assert s.count(a)==1,(label,s.count(a));PATCHES.append(label);return s.replace(a,b,1)
def extract(s,key):
 q=json.loads((HERE/'patch-index.json').read_text())[key];v=s[q['start']:q['end']];assert hashlib.sha256(v.encode()).hexdigest()==q['sha256'],key;return v
def planner(f):
 f=once(f,'ctx={provisionalReservations:[]},recs=[];','ctx={provisionalReservations:[]},recs=[];tacticalEvaluateH1(ACTIVE_SHIP_RUNTIME,wip118ControlState,inventory,getShipDamageEffects());','native assessment then utility evaluation')
 f=once(f,'for(const th of wip118ThreatRows()){','for(const th of tacticalOrderH1(ACTIVE_SHIP_RUNTIME,wip118ThreatRows())){','utility priority before resource allocation')
 return once(f,"(b.assessment==='THREAT')-(a.assessment==='THREAT')||","(b.assessment==='THREAT')-(a.assessment==='THREAT')||tacticalRecommendationOrderH1(ACTIVE_SHIP_RUNTIME,a,b)||",'utility priority at actual scheduler order')
def salvo(f):
 return f.replace('function wip118SalvoPolicy(','function wip118SalvoPolicyNativeH1(',1)+"\nfunction wip118SalvoPolicy(th,weapon,assessment,plan){return tacticalSalvoH1(ACTIVE_SHIP_RUNTIME,th,weapon,wip118SalvoPolicyNativeH1(th,weapon,assessment,plan));}\n"
def build(s):
 original=s
 def replace(name,f):
  nonlocal s;s=once(s,extract(original,name),f,name)
 context=extract(original,'createWeaponContextD')
 for name,fn in [('wip118BuildEngagementControl',planner),('wip118SalvoPolicy',salvo)]:
  context=once(context,extract(original,'owner/'+name),fn(extract(original,'owner/'+name)),'owner '+name)
 context=once(context,"if(mode==='HOLD'){wip119CancelPending", "if(mode==='HOLD'){tacticalRestoreH1(owner);wip119CancelPending",'foreign HOLD yields tactical effects');replace('createWeaponContextD',context)
 for name,fn in [('wip118BuildEngagementControl',planner),('wip118SalvoPolicy',salvo)]:replace(name,fn(extract(original,name)))
 f=extract(original,'setEngagementControlMode');f=once(f,'engagementControlMode=m;',"engagementControlMode=m;if(m!=='AUTO')tacticalRestoreH1(ACTIVE_SHIP_RUNTIME);",'own manual or semi mode yields tactical effects');replace('setEngagementControlMode',f)
 f=extract(original,'electronicCommandF').replace('function electronicCommandF(id,command){',"function electronicCommandF(id,command,origin='OPERATOR'){")
 f=once(f,'const e=prepareElectronicF(r),own=r===ACTIVE_SHIP_RUNTIME;',"if(origin==='OPERATOR')tacticalNoteOperatorH1(r,[...('emcon'in command?['radar']:[]),...(Object.keys(command).some(k=>k!=='emcon')?['ew']:[])]);const e=prepareElectronicF(r),own=r===ACTIVE_SHIP_RUNTIME;",'manual native EW command ownership')
 f=once(f,'toggleEmcon();','toggleEmcon(origin);','propagate native command origin');replace('electronicCommandF',f)
 for name in ['prepareElectronicF','resetElectronicFleetF']:
  f=extract(original,name)
  f=f.replace('electronicCommandF(r.entityId,r.restoredElectronicF)','electronicCommandF(r.entityId,r.restoredElectronicF,\'LIFECYCLE\')').replace('electronicCommandF(r.entityId,command)','electronicCommandF(r.entityId,command,\'LIFECYCLE\')');replace(name,f)
 f=extract(original,'toggleEmcon');f=once(f,'function toggleEmcon(){',"function toggleEmcon(origin='OPERATOR'){if(origin==='OPERATOR')tacticalNoteOperatorH1(ACTIVE_SHIP_RUNTIME,['radar']);",'native own EMCON manual priority');replace('toggleEmcon',f)
 f=extract(original,'observerCommandC');f=once(f,'const o=observerC(r);',"if('emcon'in cmd)tacticalNoteOperatorH1(r,['radar']);const o=observerC(r);",'native foreign observer command manual priority');replace('observerCommandC',f)
 f=extract(original,'networkExportElectronicG');f=once(f,'const q=electronicSettingsF(r),','const q=tacticalExportElectronicH1(r),','export individual baseline without tactical effects');replace('networkExportElectronicG',f)
 f=extract(original,'networkCommandG');f=once(f,"const n=prepareNetworkG(r);if('groupEmcon'in command", "if('groupEmcon'in command)tacticalYieldRadarH1(r);const n=prepareNetworkG(r);if('groupEmcon'in command",'group command restores individual tactical baseline');replace('networkCommandG',f)
 f=extract(original,'networkAcceptControlG');f=once(f,'if(n.groupBase===null)n.groupBase=observerC(r).emcon;',"if(group.mode!=='INDIVIDUAL')tacticalYieldRadarH1(r);if(n.groupBase===null)n.groupBase=observerC(r).emcon;",'received group consent supersedes individual tactical radar');replace('networkAcceptControlG',f)
 f=extract(original,'restorePreparedPhysicalFleetB');f=once(f,'r.restoredNetworkG=q.network??null;','r.restoredNetworkG=q.network??null;r.restoredTacticalH1=q.tactical??null;','detached owner tactical settings');replace('restorePreparedPhysicalFleetB',f)
 f=extract(original,'exportPhysicalFleetB');f=once(f,'network:networkSettingsG(r),','tactical:tacticalSettingsH1(r),network:networkSettingsG(r),','foreign settings export');replace('exportPhysicalFleetB',f)
 f=extract(original,'exportOperationalState');f=once(f,'ship:{network:','ship:{tactical:tacticalSettingsH1(ACTIVE_SHIP_RUNTIME),network:','own settings export')
 f=once(f,"deferred:['networkReportsLeasesAndGroupRuntime'","deferred:['utilityDecisionsPrioritiesAndEffectOwnership','networkReportsLeasesAndGroupRuntime'",'utility transient excluded');replace('exportOperationalState',f)
 f=extract(original,'prepareOperationalStateV48Wip11B');f=once(f,'migrateNetworkSaveG(src,harpoonMigrations);','migrateNetworkSaveG(src,harpoonMigrations);migrateTacticalSaveH1(src,harpoonMigrations);','explicit tactical legacy migration');replace('prepareOperationalStateV48Wip11B',f)
 f=extract(original,'applyPreparedOperationalStateV48Wip11B');f=once(f,'electronicCommandF(ACTIVE_SHIP_RUNTIME.entityId,src.ship.ew);',"electronicCommandF(ACTIVE_SHIP_RUNTIME.entityId,src.ship.ew,'LIFECYCLE');",'import is not an operator override')
 f=once(f,'if(src.ship.network){',"if(src.ship.tactical){ACTIVE_SHIP_RUNTIME.combatSystem.tacticalH1=null;ACTIVE_SHIP_RUNTIME.restoredTacticalH1=src.ship.tactical;prepareTacticalH1(ACTIVE_SHIP_RUNTIME);}if(src.ship.network){",'settings restored after successful preflight');replace('applyPreparedOperationalStateV48Wip11B',f)
 f=extract(original,'validatePhysicalFleetB');f=once(f,"[MULTISHIP_PHYSICAL_SCHEMA_B,'AEGIS_NAVAL_PHYSICAL_FLEET_F_1'","[MULTISHIP_PHYSICAL_SCHEMA_B,'AEGIS_NAVAL_PHYSICAL_FLEET_G_1','AEGIS_NAVAL_PHYSICAL_FLEET_F_1'",'explicit G fleet compatibility')
 f=once(f,"const fleet=src.fleet,err=x=>errors.push('FLEET_'+x);","const fleet=src.fleet,err=x=>errors.push('FLEET_'+x);validateTacticalSettingsH1(src.ship?.tactical,errors);",'strict own tactical preflight')
 f=once(f,'seen.add(q.entityId);','seen.add(q.entityId);validateTacticalSettingsH1(q.tactical,errors);','strict foreign tactical preflight');replace('validatePhysicalFleetB',f)
 f=extract(original,'migrateNetworkSaveG');f=f.replace("['AEGIS_NAVAL_PHYSICAL_FLEET_F_1'","['AEGIS_NAVAL_PHYSICAL_FLEET_G_1','AEGIS_NAVAL_PHYSICAL_FLEET_F_1'");replace('migrateNetworkSaveG',f)
 f=extract(original,'resetNetworkFleetG');f=once(f,'fleetResetG();','fleetResetG();resetTacticalFleetH1();','clear decisions on reset deployment and import');replace('resetNetworkFleetG',f)
 f=extract(original,'retirePhysicalShipB');f=once(f,'retireNetworkG(r);','r.combatSystem.tacticalH1=null;retireNetworkG(r);','owner tactical retirement');replace('retirePhysicalShipB',f)
 f=extract(original,'mountNetworkUiG');pos=f.rfind('}');replace('mountNetworkUiG',f[:pos]+'mountTacticalUiH1();\n'+f[pos:])
 f=extract(original,'fleetUpdateUiG');pos=f.rfind('}');replace('fleetUpdateUiG',f[:pos]+'tacticalUpdateUiH1();\n'+f[pos:])
 s=once(s,'const NAVAL_WEAPONS_POLICY_D=', '\n'.join((HERE/x).read_text()for x in ['tactical.js','ui.js'])+'\nconst NAVAL_WEAPONS_POLICY_D=','canonical utility modules')
 s=once(s,"const MULTISHIP_PHYSICAL_SCHEMA_B='AEGIS_NAVAL_PHYSICAL_FLEET_G_1';","const MULTISHIP_PHYSICAL_SCHEMA_B='AEGIS_NAVAL_PHYSICAL_FLEET_H1_1';",'H1 fleet schema')
 for anchor in ['setSoftKillAutoDoctrine(!softKillAutoDoctrine);','noiseJamActive = !noiseJamActive;','deceptJamActive = !deceptJamActive;']:
  s=once(s,anchor,anchor+"tacticalNoteOperatorH1(ACTIVE_SHIP_RUNTIME,['ew']);",'native EW button manual priority')
 s=once(s,'fleetSnapshotG:fleetSnapshotG,','tacticalSnapshotH1:tacticalSnapshotH1,tacticalCommandH1:tacticalCommandH1,fleetSnapshotG:fleetSnapshotG,','detached utility diagnostic and operator ports')
 s=once(s,'window.__CORE_SELFTEST_FAILURES__=failures.slice();',"const utilityH1=tacticalSelfTestH1();if(!utilityH1.pass)failures.push('UTILITY_H1 '+JSON.stringify(utilityH1.checks));window.__CORE_SELFTEST_FAILURES__=failures.slice();",'startup utility transition self-test')
 s=once(s,'setEmcon: (on) => { emconActive = !!on;',"setEmcon: (on) => { tacticalNoteOperatorH1(ACTIVE_SHIP_RUNTIME,['radar']);emconActive = !!on;",'diagnostic native own radar command priority')
 return s
def main():
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('output',type=Path);a=p.parse_args();raw=a.baseline.read_bytes();assert hashlib.sha256(raw).hexdigest()==BASE_SHA
 html=raw.decode();m=re.search(r'<script type="application/octet-stream" data-c55-index="13">(.*?)</script>',html,re.S);src=gzip.decompress(base64.b64decode(m[1])).decode();candidate=build(src).replace(OLD,NEW);gz=gzip.compress(candidate.encode(),mtime=0)
 html=html[:m.start(1)]+base64.b64encode(gz).decode()+html[m.end(1):];row=re.search(r'const records=(\[.*?\]);',html,re.S);records=json.loads(row[1]);records[13].update(rawBytes=len(candidate.encode()),gzipBytes=len(gz),sha256=hashlib.sha256(candidate.encode()).hexdigest());html=html[:row.start(1)]+json.dumps(records,separators=(',',':'))+html[row.end(1):];html=html.replace(OLD,NEW).replace('V48_WIP_MULTI_SHIP_G','V48_WIP_MULTI_SHIP_H1')
 a.output.write_text(html);a.output.with_suffix('.main.js').write_text(candidate);manifest={'baselineSha256':BASE_SHA,'htmlSha256':hashlib.sha256(html.encode()).hexdigest(),'mainSha256':hashlib.sha256(candidate.encode()).hexdigest(),'changedPackedRecords':[13],'patches':PATCHES};a.output.with_suffix('.manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest))
if __name__=='__main__':main()

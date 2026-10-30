"""Emit exact native preflight copies, stopping before any spawn/consumption."""
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent
s=json.loads((H/'base-symbols.json').read_text())
names=['surfaceMissileReleaseAssessmentWip13C4','surfaceMissileFireControlQualityWip13C4','surfaceMissileTrackReadinessWip13C4','surfaceMissilePlatformSnapshotWip13C4','networkMemberG','networkProtectionG','networkVlsGateG','updateTrackOperationalStateA3','trackEngagementGateA3','classifyThreats','vlsReleaseB2Snapshot','vlsReleaseB2CycleFeedback','vlsReleaseB2SupportPreflight','shipGameVlsReadyV1','surfaceMissileReleaseGateWip13C4','surfaceSm2LiveReleaseGateWip13C5','surfaceEssmLiveReleaseGateWip13C6']
parts=[];ledger=[]
for n in names:
 parts.append(s[n]['code']);ledger.append({'name':n,'sourceSha256':s[n]['hash'],'copy':'EXACT'})
for n,stop in [('vlsReleaseStandardB1','  const v0Mps'),('vlsReleaseEssmB1','    const tx = tr.x;')]:
 c=s[n]['code'];assert c.count(stop)==1;c=c[:c.index(stop)]+'\nreturn {ok:true};\n}'
 parts.append(c);ledger.append({'name':n,'sourceSha256':s[n]['hash'],'copy':'PREFIX_THROUGH_ALL_GATES','stopBefore':stop})
c=s['vlsReleaseB2Request']['code'];stop='    const before=missiles.length;s.busy=true;';assert c.count(stop)==1;c=c[:c.index(stop)]+"\nreturn release();\n}"
parts.append(c);ledger.append({'name':'vlsReleaseB2Request','sourceSha256':s['vlsReleaseB2Request']['hash'],'copy':'PREFIX_THROUGH_ALL_GATES','stopBefore':stop})
(H/'native_preview.inc.js').write_text('\n'.join(parts))
(H/'native-preview-ledger.json').write_text(json.dumps(ledger,indent=2)+'\n')

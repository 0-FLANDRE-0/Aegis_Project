"""Unmodified product bytes and live lexical functions; no flight or tuning."""
from pathlib import Path
import json,hashlib,sys
from playwright.sync_api import sync_playwright
T=Path(__file__).resolve().parent;R=T.parents[3]
sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'))
from browser_tools import launch,load_fleet,instrument
files={'DZT':R/'archive/v48/WIP_FUZE_ZEM_A/Aegis_SIM_v48_WIP_FUZE_ZEM_A.html','HANDOFF':R/'Aegis_SIM_v48_WIP_LAUNCH_HANDOFF_A.html'}
names=['getArhTargetStateV1','getGuidanceTargetStateV1','_arhAssociateMeasurements','_arhEkfUpdate','computeKappaMidcourseAccelV2','applyAccelCommandToAutopilotV1','updateSamSixDofLiteDynamics','samNavB1ReanchorRelativeCandidate','_v1SelectGuidanceSource','_v1SourceMeets','_arhBuildMeasurementSet','_arhReceiverState','_arhV2MonopulseMeasurement','_v1UpdateArhMeasurementCore']
obj=','.join(n+':'+n+'.toString()'for n in names)
helper='window.__RF_KIT_META__={rfModel:getArhSeekerModel(),receiverPlatformType:typeof _sarhPlatformState,receiverPlatformSource:typeof _sarhPlatformState==="function"?_sarhPlatformState.toString():null,functions:{'+obj+'}};'
rows=[];errors=[]
with sync_playwright()as pw:
 b=launch(pw)
 for variant,file in files.items():
  p=load_fleet(b,instrument(file.read_bytes(),helper),own='DDG_119_LATE_FLIGHT_IIA',errors=errors);q=p.evaluate('__RF_KIT_META__');q.update(variant=variant,htmlSha256=hashlib.sha256(file.read_bytes()).hexdigest());q['functionHashes']={k:hashlib.sha256(s.encode()).hexdigest()for k,s in q['functions'].items()};rows.append(q);p.close()
 b.close()
(T/'analysis/live-source-provenance-v2.json').write_text(json.dumps({'records':rows,'errors':errors},indent=2)+'\n')
print([(r['variant'],r['rfModel'],r['receiverPlatformSource'])for r in rows]);assert not errors

"""Read-only/private geometry proof of own-SPY AIR origin metadata loss.

No live track insertion, sensor patch, coefficient change, or FCS correction.
Synthetic Cartesian/polar measurements use known test inputs. The existing
plot adapter and EKF prediction functions execute directly from the product.
"""
from pathlib import Path
import json,sys,time
from playwright.sync_api import sync_playwright
from build_fixture import build,R,B
from http_browser import serve,load_http
sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'))
from browser_tools import launch
helper=r'''
window.__G2_ORIGIN__=()=>{
 __GB_TEST__.reset(419010);const rng=SIM_RNG_STATE,records=[],own={xM:worldToMeters(aircraft.x()),yM:worldToMeters(aircraft.y()),zM:OWN_ALT_M};
 const privateTrack=p=>({_kfX:new Float64Array([p.xM,p.yM,p.zM,0,0,0]),_kfP:Float64Array.from({length:36},(_,i)=>i%7===0?25:0),sensorAge:0,confirmed:true});
 for(const face of ['F1','F2','F3','F4'])for(const bearing of [0,90]){const rx=spySurfaceOriginWip13B9({face}),target={xM:own.xM+10000*Math.cos(deg(bearing)),yM:own.yM+10000*Math.sin(deg(bearing)),zM:12},dx=target.xM-worldToMeters(rx.x),dy=target.yM-worldToMeters(rx.y),dz=target.zM-rx.z,rangeM=Math.hypot(dx,dy,dz),azRad=Math.atan2(dy,dx),elRad=Math.atan2(dz,Math.hypot(dx,dy)),echo={x:metersToWorld(target.xM),y:metersToWorld(target.yM),z:target.zM,rangeM,azRad,elRad,radialMps:0,quality:1,rangeSigmaM:1,azSigmaDeg:.01,elSigmaDeg:.01,radialVelSigmaMps:1,sensorXWorld:rx.x,sensorYWorld:rx.y,sensorVxMps:0,sensorVyMps:0},air=shipboardRadarEchoToAirPlotWip13B13(echo,{air:1,missile:1,surface:0},'SPY1DV_DIAGNOSTIC'),withKnownOrigin={...air,sensorXWorld:rx.x,sensorYWorld:rx.y,sensorZM:rx.z,sensorVxMps:0,sensorVyMps:0,sensorVzMps:0},lever={x:worldToMeters(rx.x)-own.xM,y:worldToMeters(rx.y)-own.yM,z:rx.z-own.zM},wrongPoint={xM:target.xM-lever.x,yM:target.yM-lever.y,zM:target.zM-lever.z},a=privateTrack(target),b=privateTrack(wrongPoint),predTrueDropped=trackRadarPrediction(a,air),predWrongDropped=trackRadarPrediction(b,air),predTrueKnown=trackRadarPrediction(a,withKnownOrigin),values=[rangeM,azRad,elRad,0],residual=p=>p.h.map((v,i)=>i===1||i===2?angNorm(v-values[i]):v-values[i]);
  trackSyncLegacyFromEkf(b);records.push({face,bearing,receiver:{xM:worldToMeters(rx.x),yM:worldToMeters(rx.y),zM:rx.z},own,leverM:lever,targetM:target,airMetadataPresent:['sensorXWorld','sensorYWorld','sensorZM','sensorVxMps','sensorVyMps','sensorVzMps'].filter(k=>Object.hasOwn(air,k)),truePointResidualDropped:residual(predTrueDropped),wrongPointResidualDropped:residual(predWrongDropped),truePointResidualKnownOrigin:residual(predTrueKnown),wrongPointM:wrongPoint,wrongLegacyAltitudeM:b.z,privateFilterAltitudeM:b._kfX[2]});
 }
 return {records,rngBefore:rng,rngAfter:SIM_RNG_STATE,worldTracks:tracks.size};
};
'''
raw=build(False,helper);server,url=serve(raw);out=B/'evidence/origin-contract';out.mkdir(parents=True,exist_ok=True);rows=[];errors=[];start=time.perf_counter()
with sync_playwright()as pw:
 b=launch(pw)
 for ship in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']:
  p=load_http(b,url,own=ship,errors=errors);q=p.evaluate('__G2_ORIGIN__()');rows.append({'ship':ship,**q});p.close()
 b.close()
server.shutdown();checks={'metadataDropped':all(not x['airMetadataPresent']for r in rows for x in r['records']),'wrongPointFitsUnchangedConsumer':all(max(abs(v)for v in x['wrongPointResidualDropped'])<1e-8 for r in rows for x in r['records']),'knownOriginMakesTruePointFit':all(max(abs(v)for v in x['truePointResidualKnownOrigin'])<1e-8 for r in rows for x in r['records']),'truePointDoesNotFitDroppedOrigin':all(abs(x['truePointResidualDropped'][0])>1e-3 or abs(x['truePointResidualDropped'][1])>1e-6 or abs(x['truePointResidualDropped'][2])>1e-6 for r in rows for x in r['records']),'worldUntouched':all(r['rngBefore']==r['rngAfter']and r['worldTracks']==0 for r in rows),'errors0':not errors};report={'pass':all(checks.values()),'checks':checks,'rows':rows,'errors':errors,'elapsedS':time.perf_counter()-start,'policy':'Diagnostic private objects only; no repair applied to a live measurement or shipped function.'};(out/'results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'pass':report['pass'],'checks':checks,'elapsedS':report['elapsedS']}));raise SystemExit(not report['pass'])

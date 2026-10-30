"""Pinned F2_0 -> F2: optional ISAR RF branch, anonymous information transport/UI."""
import argparse,base64,gzip,hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
BASE_SHA='abb0423050d974d878714510cf5356ad9913b4371d04ccc757602782e8d74b86'
def decoded(s,i=13):return gzip.decompress(base64.b64decode(re.search(r'data-c55-index="'+str(i)+r'">(.*?)</script>',s,re.S)[1])).decode()
def patch(s):
 def edit(a,b,n=1):
  nonlocal s
  assert s.count(a)==n,(a[:130],s.count(a),n);s=s.replace(a,b)
 lib=json.loads((HERE/'library.json').read_text())['entries'];model=(HERE/'model.js').read_text().replace('/*__ISAR_LIBRARY_F2__*/','const ISAR_LIBRARY_F2=Object.freeze('+json.dumps(lib,ensure_ascii=False,separators=(',',':'))+'.map(e=>Object.freeze({...e,heightsM:Object.freeze(e.heightsM)})));')
 module='\n'.join([model]+[(HERE/f).read_text()for f in ['physical.js','sensor.js','transport.js','ui.js','diagnostic.js']])
 edit('ISAR:{reserved:true},ARPDD:{reserved:true}',"ISAR:{prfHz:2491,rpm:0,minM:9300,maxM:296000,resolutionM:2,m:0,n:0},ARPDD:{reserved:true}")
 edit("resolutionM:mode==='PERI'?'APS137_ANALOG':'APS143_FAMILY_ANALOG'","resolutionM:mode==='ISAR'?'GENERIC_RADAR_PRINCIPLE':mode==='PERI'?'APS137_ANALOG':'APS143_FAMILY_ANALOG'")
 edit("if(!m?.rpm)return {instrumentM:0,horizonM:","if(!m?.rpm&&mode!=='ISAR')return {instrumentM:0,horizonM:")
 edit('function heloRadarSnapshotE(h){const mode=apsModeF(h),',"function heloRadarSnapshotE(h){if(apsModeF(h)==='ISAR')return isarRadarSnapshotF2(h);const mode=apsModeF(h),")
 edit('surfaceOnly:true,geometryOnlyLimit:true','surfaceOnly:true,geometryOnlyLimit:true,isar:isarSnapshotF2(h)')
 edit("if(mode==='STBY'&&!old)continue;const q=heloRadarStateE(h);", "isarTransportStepF2(h);if(mode==='ISAR'){isarFixedStepF2(h,heloRadarStateE(h),dt);continue;}if(mode==='STBY'&&!old)continue;const q=heloRadarStateE(h);")
 edit("  if(action==='SET_IFF'||action==='SET_RADAR'){", "  if(action==='SET_RADAR_MODE'&&point?.mode==='ISAR'){if(Object.keys(point).join(',')!=='mode')return bad('INVALID_RADAR_MODE');return isarBeginF2(h);}\n  if(action==='ISAR_TARGET')return isarSelectPositionF2(h,point);\n  if(action==='CANCEL_ISAR')return isarLeaveF2(h);\n  if(action==='SET_IFF'||action==='SET_RADAR'){")
 edit("if(action==='SET_RADAR'){h.radarMode=point.enabled?'LONG':'STBY';", "if(action==='SET_RADAR'){if(h.radarMode==='ISAR')isarLeaveF2(h,point.enabled?'LONG':'STBY','MODE_CHANGE');h.radarMode=point.enabled?'LONG':'STBY';")
 edit("    h.radarMode=point.mode;h.radarOn=point.mode!=='STBY';", "    if(h.radarMode==='ISAR')isarLeaveF2(h,point.mode,'MODE_CHANGE');h.radarMode=point.mode;h.radarOn=point.mode!=='STBY';")
 # Operational saves restore operator search mode, not in-progress tactical ISAR.
 edit('function heloExportA(){if(!heloSupportedA())', 'function heloExportA(){if(!heloSupportedA())')
 edit('launch:ACTIVE_SHIP_RUNTIME.aviation.heloLaunchA,aircraft:[...heloWorldA().values()]}));}', "launch:ACTIVE_SHIP_RUNTIME.aviation.heloLaunchA,aircraft:[...heloWorldA().values()].map(h=>h.radarMode==='ISAR'?{...h,radarMode:isarExistingF2(h)?.previousMode??'LONG',radarOn:isarExistingF2(h)?.previousMode!=='STBY'}:h)}));}")
 # Shared RF: optional receiver and anonymous feature extraction only for ISAR.
 edit("receiverF=opts.aps153F?apsCfarPhysicalF({", "receiverF=opts.isarF?isarReceiverF2({opts,rangeM:q.rangeM,horizontalRangeM:q.h,signal:q.signal,localClutter,distributed:q.distributed,beamGain:q.beamGain,weatherQ:maritimeRfWeatherPathFactorWip13A3(band,2*q.rangeM/1000)}):opts.aps153F?apsCfarPhysicalF({")
 edit("echoes.push({...(opts.aps153F?{scanOrdinalF:q.scanOrdinalF}:{}),schema:","echoes.push({...(opts.isarF?{isarFeatures:isarPhysicalSampleF2(q.ref,{azRad:q.az},opts.isarF,normal,snr)}:{}),...(opts.aps153F?{scanOrdinalF:q.scanOrdinalF}:{}),schema:")
 # Distinct, strict schema; old plot validation/age/no-buffer semantics unchanged.
 edit('function heloSensorResetE(owner){', 'function heloSensorResetE(owner){isarResetF2(owner);')
 edit('function ingestOffboardReportC(r,report){',"function ingestOffboardReportC(r,report){\n  if(report?.schema==='AEGIS_OFFBOARD_ISAR_C_1')return ingestOffboardIsarF2(r,report);")
 edit('  o.offboard.queue=pending;\n}', '  o.offboard.queue=pending;drainIsarOffboardF2(r);\n}')
 edit("tr.identificationEvidence=trackCompositionF1(tr)==='OFFBOARD'?'OPERATOR_ONLY':'LOCAL_SENSOR';",'isarIdentificationDecisionF2(tr);',3)
 edit('identificationEvidence:tr?trackIdentificationEvidenceF1(tr):null,rangeKm:', 'identificationEvidence:tr?trackIdentificationEvidenceF1(tr):null,identificationIsar:tr?.identificationIsarF2?JSON.parse(JSON.stringify({...tr.identificationIsarF2,ageAtLaunchS:simStepCounter*SIM_FIXED_DT-tr.identificationIsarF2.measuredAtS})):null,rangeKm:')
 edit("${q.identificationEvidence??'—'} | ${q.rangeKm", "${q.identificationEvidence??'—'}${q.identificationIsar?' ('+q.identificationIsar.label+' '+q.identificationIsar.confidence.toFixed(2)+' · '+q.identificationIsar.ageAtLaunchS.toFixed(1)+'s)':''} | ${q.rangeKm")
 edit('classification:tr.classification,identity:tr.identity,threatStatus:tr.threatStatus,engagementAuthority:tr.engagementAuthority,confirmed:!!tr.confirmed,sensorAgeS:', 'classification:tr.classification,identity:tr.identity,...(tr.isarEvidence?{isarEvidence:jsonSafeCloneV48Wip11A(tr.isarEvidence),identificationEvidence:tr.identificationEvidence??null,identificationIsar:tr.identificationIsarF2?jsonSafeCloneV48Wip11A(tr.identificationIsarF2):null}:{}),threatStatus:tr.threatStatus,engagementAuthority:tr.engagementAuthority,confirmed:!!tr.confirmed,sensorAgeS:')
 edit('identificationEvidence:tr.identificationEvidence??null,surfaceSensorContributors:', 'identificationEvidence:tr.identificationEvidence??null,...(tr.isarEvidence?{isarEvidence:jsonSafeCloneV48Wip11A(tr.isarEvidence)}:{}),surfaceSensorContributors:')
 edit("  // ISAR is reserved; no observation in F1 can generate that evidence.","  // ISAR is an operator decision based on separately received measured evidence.")
 edit("const q=observationReportViewC(tr);if(!q?.remote.length)return networkTrackLabelG(tr);", "const q=observationReportViewC(tr),isar=isarTrackLabelF2(tr);if(!q?.remote.length)return [networkTrackLabelG(tr),isar].filter(Boolean).join(' · ');")
 edit("+(latest.connected?'LINK':'LINK LOST');", "+(latest.connected?'LINK':'LINK LOST')+(isar?' · '+isar:'');")
 # UI command adapter (no simulation writes in render/update).
 edit("function heloMapTapA(x,y){if(controlDeckActiveTabWip13C", "function heloMapTapA(x,y){if(isarMapTapF2(x,y))return;if(controlDeckActiveTabWip13C")
 edit('  apsMountPerformanceUiF(panel);','  apsMountPerformanceUiF(panel);isarMountUiF2(panel);')
 edit("document.getElementById('airResultA').textContent=heloUiA.lastResult;", "document.getElementById('airResultA').textContent=heloUiA.lastResult;isarUpdateUiF2(selected);")
 edit('function heloDrawMapA(){','function heloDrawMapA(){\n  isarDrawMapF2();')
 edit('for(const v of r.visuals.values())v.root.removeFromParent();', 'for(const v of r.visuals.values()){v.isarTexture?.dispose();v.root.removeFromParent();}')
 edit('v.root.userData.mode=radar.mode;', 'isarVisualLabelF2(view,v,h,radar);v.root.userData.mode=radar.mode;')
 edit('v.root.removeFromParent();for(const g of v.geometries)', 'v.isarTexture?.dispose();v.root.removeFromParent();for(const g of v.geometries)')
 edit("(line!==v.minimum||radar.mode==='PERI')", "(line!==v.minimum||radar.mode==='PERI'||radar.mode==='ISAR')")
 edit('function heloRadarNewStateE(h)',module+'\nfunction heloRadarNewStateE(h)')
 return s

def build(raw):
 assert hashlib.sha256(raw).hexdigest()==BASE_SHA;html=raw.decode();main=patch(decoded(html)).replace('v48_WIP_HELI_F2_0','v48_WIP_HELI_F2');z=gzip.compress(main.encode(),9,mtime=0)
 m=re.search(r'data-c55-index="13">(.*?)</script>',html,re.S);html=html[:m.start(1)]+base64.b64encode(z).decode()+html[m.end(1):]
 m=re.search(r'const records=(\[.*?\]);',html,re.S);records=json.loads(m[1]);records[13].update(rawBytes=len(main.encode()),gzipBytes=len(z),sha256=hashlib.sha256(main.encode()).hexdigest());html=html[:m.start(1)]+json.dumps(records,separators=(',',':'))+html[m.end(1):]
 return html.replace('v48_WIP_HELI_F2_0','v48_WIP_HELI_F2').replace('V48_WIP_HELI_F2_0','V48_WIP_HELI_F2'),main
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('output',type=Path);a=p.parse_args();html,main=build(a.baseline.read_bytes());a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(html);a.output.with_suffix('.main.js').write_text(main);d={'baselineSha256':BASE_SHA,'htmlSha256':hashlib.sha256(html.encode()).hexdigest(),'mainSha256':hashlib.sha256(main.encode()).hexdigest(),'bytes':len(html.encode()),'addedBytes':len(html.encode())-a.baseline.stat().st_size};a.output.with_suffix('.manifest.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d))

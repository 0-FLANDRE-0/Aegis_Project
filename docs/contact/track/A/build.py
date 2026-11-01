"""TRACK-A: additive, default-off measurement views and passive native-decision traces.
All replacements are exact and reversible; no filter/RF/weapon kernel is rewritten.
"""
from pathlib import Path
import base64,difflib,gzip,hashlib,json,re
P=Path(__file__).resolve().parent;R=P.parents[3]
BASE=R/'Aegis_SIM_v48_WIP_FRIENDLY_CONTACT_A.html';OUT=R/'Aegis_SIM_v48_WIP_TRACK_A.html'
PIN='cfc74427e3d30efafec187c3fd99924f5063e74d8dbe3f8e36caebd68d149cda'
sha=lambda b:hashlib.sha256(b).hexdigest()
def unpack(raw):return gzip.decompress(base64.b64decode(re.search(rb'data-c55-index="13">([^<]+)',raw)[1])).decode()
def pack(raw,s):
 m=re.search(rb'data-c55-index="13">([^<]+)',raw);z=gzip.compress(s.encode(),9,mtime=0);out=raw[:m.start(1)]+base64.b64encode(z)+raw[m.end(1):];m=re.search(rb'const records=(\[.*?\]);',out,re.S);rs=json.loads(m[1]);rs[13].update(rawBytes=len(s.encode()),gzipBytes=len(z),sha256=sha(s.encode()))
 if'encodedBytes'in rs[13]:rs[13]['encodedBytes']=len(base64.b64encode(z))
 return out[:m.start(1)]+json.dumps(rs,separators=(',',':')).encode()+out[m.end(1):]
def transform(s):
 before=s;changes=[];hooks=[]
 def replace(a,b,label,count=1):
  nonlocal s
  assert s.count(a)==count,(label,s.count(a),count,a[:160]);s=s.replace(a,b);changes.append({'label':label,'before':a,'after':b,'count':count})
 def scoped(name,fn,occurrence=0):
  nonlocal s
  matches=list(re.finditer(r'^( *)function '+re.escape(name)+r'\(',s,re.M));assert len(matches)>occurrence,(name,len(matches));m=matches[occurrence];a=m.start();indent=m[1];next_=re.search(r'^'+re.escape(indent)+r'function [A-Za-z_$]',s[m.end():],re.M);assert next_,name;b=m.end()+next_.start();old=s[a:b];new=fn(old);assert new!=old,name;replace(old,new,name);hooks.append({'function':name,'occurrence':occurrence,'baselineLine':before.count('\n',0,before.find(old))+1,'baselineSha256':sha(old.encode()),'traceOnly':True})
 def edit(t,a,b):assert t.count(a)==1,(a[:160],t.count(a));return t.replace(a,b,1)
 context=lambda kind,source,owner:f'trackATraceContextA({kind},{source},{owner},meas)' if kind=='trackAKindA(meas,source)' else f'trackATraceContextA({kind},{source},{owner})'
 own='ACTIVE_SHIP_RUNTIME.entityId'
 # Initialize diagnostics before any startup self-test. It reads no native state here.
 anchor='window.__AEGIS_STARTUP_PROMISE__=(async () => {'
 replace(anchor,anchor+'\n// TRACK_A_DIAGNOSTICS_BEGIN\n'+(P/'measurement-contract.js').read_text()+'\n// TRACK_A_DIAGNOSTICS_END\n','measurement-contract-module')
 def own_update(t):
  t=edit(t,"    const truthRef=normalizeTrackTruthRefV27(meta.truthRef);","    const trackABefore=TRACK_A_DIAG.enabled?trackAStateA(id==null?null:tracks.get(id)):null;\n    if(TRACK_A_DIAG.enabled)trackATraceEventA('RECEIVED',meas,{..."+context('trackAKindA(meas,source)','source',own)+",route:'PLAYER_MEASUREMENT',trackId:id,decision:'PENDING'});\n    const truthRef=normalizeTrackTruthRefV27(meta.truthRef);")
  t=edit(t,"    const isVisual=source==='VISUAL';","    let trackAAppliedGate=null;\n    const isVisual=source==='VISUAL';")
  t=edit(t,"      if(!trackEkfUpdateSurfaceRadar2D", "      if(TRACK_A_DIAG.enabled)trackAAppliedGate=gate;\n      if(!trackEkfUpdateSurfaceRadar2D")
  t=edit(t,"      if(!trackEkfUpdateRadar", "      if(TRACK_A_DIAG.enabled)trackAAppliedGate=nisGate;\n      if(!trackEkfUpdateRadar")
  t=edit(t,"if(!trackEkfUpdateSurfaceRadar2D(tr,meas,{nisGate:gate})){if(created)tracks.delete(id);return null;}","if(!trackEkfUpdateSurfaceRadar2D(tr,meas,{nisGate:gate})){if(TRACK_A_DIAG.enabled)trackATraceEventA('UPDATE',meas,{..."+context("'SURFACE_RADAR'",'source',own)+",route:'PLAYER_MEASUREMENT',trackId:id,decision:'REJECT',reason:'NATIVE_FILTER_REJECT',nis:tr._kfNis,gate,before:trackABefore,after:trackAStateA(tr)});if(created)tracks.delete(id);return null;}")
  t=edit(t,"if(!trackEkfUpdateRadar(tr,meas,{nisGate})){if(created)tracks.delete(id);return null;}","if(!trackEkfUpdateRadar(tr,meas,{nisGate})){if(TRACK_A_DIAG.enabled)trackATraceEventA('UPDATE',meas,{..."+context("'AIR_RADAR'",'source',own)+",route:'PLAYER_MEASUREMENT',trackId:id,decision:'REJECT',reason:'NATIVE_FILTER_REJECT',nis:tr._kfNis,gate:nisGate,before:trackABefore,after:trackAStateA(tr)});if(created)tracks.delete(id);return null;}")
  t=edit(t,'    return tr;','    if(TRACK_A_DIAG.enabled)trackATraceEventA(\'UPDATE\',meas,{...'+context('trackAKindA(meas,source)','source',own)+",route:'PLAYER_MEASUREMENT',trackId:tr.trackId,decision:created?'CREATE':'ACCEPT',nis:isRadar||isSurfaceRadar?tr._kfNis:null,gate:trackAAppliedGate,nativeHitIncrement:1,finalSource:tr.sensorSource,before:trackABefore,after:trackAStateA(tr)});\n    return tr;")
  return t
 scoped('updateSensorTrackMeasurement',own_update)
 def spy_global(t):
  old="...trackEntries.map(([,tr])=>{if(!trackMayAcceptAirPlotCrossDomainWip13B14(tr,plots[i]))return blockedCost;const nis=trackRadarAssociationNisV31(tr,plots[i]),cross=trackSurfaceBackedWip13B14(tr);return nis<=Math.min(gate,cross?WIP13B14_CROSS_DOMAIN_ASSOCIATION_CONTRACT.airToSurfaceNisGate:gate)?nis:blockedCost;}),"
  new="...trackEntries.map(([,tr])=>{if(!trackMayAcceptAirPlotCrossDomainWip13B14(tr,plots[i])){if(TRACK_A_DIAG.enabled)trackATraceEventA('CANDIDATE',plots[i],{..."+context("'AIR_RADAR'","plots[i].source",own)+",route:'SPY_BATCH',appliedModel:'AIR_POLAR_DOPPLER',appliedDimension:4,appliedFields:['rangeM','azRad','elRad','radialMps'],gateUnits:'NIS',trackId:tr.trackId,decision:'REJECT',reason:'NATIVE_CROSS_DOMAIN_PARTITION',gate});return blockedCost;}const nis=trackRadarAssociationNisV31(tr,plots[i]),cross=trackSurfaceBackedWip13B14(tr);if(TRACK_A_DIAG.enabled)trackATraceEventA('CANDIDATE',plots[i],{..."+context("'AIR_RADAR'","plots[i].source",own)+",route:'SPY_BATCH',appliedModel:'AIR_POLAR_DOPPLER',appliedDimension:4,appliedFields:['rangeM','azRad','elRad','radialMps'],gateUnits:'NIS',trackId:tr.trackId,nis,gate:Math.min(gate,cross?WIP13B14_CROSS_DOMAIN_ASSOCIATION_CONTRACT.airToSurfaceNisGate:gate),decision:nis<=Math.min(gate,cross?WIP13B14_CROSS_DOMAIN_ASSOCIATION_CONTRACT.airToSurfaceNisGate:gate)?'ELIGIBLE':'REJECT',reason:'NATIVE_NIS'});return nis<=Math.min(gate,cross?WIP13B14_CROSS_DOMAIN_ASSOCIATION_CONTRACT.airToSurfaceNisGate:gate)?nis:blockedCost;}),"
  return edit(t,old,new)
 scoped('spyGlobalAssignmentsV36',spy_global)
 def spy_best(t):
  old='const nis=trackRadarAssociationNisV31(tr,plots[i]);if(nis<=spyAssociationGateV31(task)'
  # The original condition evaluates the gate once per tested plot. Cache that
  # same result so the diagnostic cannot call a native helper a second time.
  new="const nis=trackRadarAssociationNisV31(tr,plots[i]),trackAGate=spyAssociationGateV31(task);if(TRACK_A_DIAG.enabled)trackATraceEventA('CANDIDATE',plots[i],{..."+context("'AIR_RADAR'","plots[i].source",own)+",route:'SPY_FOCUSED',appliedModel:'AIR_POLAR_DOPPLER',appliedDimension:4,appliedFields:['rangeM','azRad','elRad','radialMps'],gateUnits:'NIS',trackId,nis,gate:trackAGate,decision:nis<=trackAGate?'ELIGIBLE':'REJECT',reason:'NATIVE_NIS'});if(nis<=trackAGate"
  t=edit(t,old,new)
  return edit(t,'    return best;',"    if(TRACK_A_DIAG.enabled)trackATraceEventA('ASSIGNMENT',best?plots[best.index]:{}, {..."+context("'AIR_RADAR'","'SPY1DV'",own)+",route:'SPY_FOCUSED',appliedModel:'AIR_POLAR_DOPPLER',appliedDimension:4,appliedFields:['rangeM','azRad','elRad','radialMps'],gateUnits:'NIS',trackId,decision:best?'ASSIGN':'NO_ASSIGNMENT',nis:best?.nis,reason:'NATIVE_FOCUSED_WINNER'});\n    return best;")
 scoped('spyBestPlotForTrackV31',spy_best)
 def surface(t):
  a="...trackEntries.map(([,tr])=>{if(cross&&!trackMayAcceptSurfacePlotCrossDomainWip13B14(tr,plots[i]))return blockedCost;const nis=nisFn(tr,plots[i]);return nis<=stageGate?nis:blockedCost;})"
  b="...trackEntries.map(([,tr])=>{if(cross&&!trackMayAcceptSurfacePlotCrossDomainWip13B14(tr,plots[i])){if(TRACK_A_DIAG.enabled)trackATraceEventA('CANDIDATE',plots[i],{..."+context("'SURFACE_RADAR'","plots[i].source",own)+",route:'SURFACE_BATCH',appliedModel:'SURFACE_ASSOCIATION',appliedDimension:nisFn===trackSurfacePositionAssociationNisWip13B9?2:(Number.isFinite(plots[i].radialMps)?3:2),appliedFields:nisFn===trackSurfacePositionAssociationNisWip13B9||!Number.isFinite(plots[i].radialMps)?['rangeM','azRad']:['rangeM','azRad','radialMps'],gateUnits:'NIS',trackId:tr.trackId,decision:'REJECT',reason:'NATIVE_CROSS_DOMAIN_PARTITION',gate:stageGate});return blockedCost;}const nis=nisFn(tr,plots[i]);if(TRACK_A_DIAG.enabled)trackATraceEventA('CANDIDATE',plots[i],{..."+context("'SURFACE_RADAR'","plots[i].source",own)+",route:'SURFACE_BATCH',appliedModel:'SURFACE_ASSOCIATION',appliedDimension:nisFn===trackSurfacePositionAssociationNisWip13B9?2:(Number.isFinite(plots[i].radialMps)?3:2),appliedFields:nisFn===trackSurfacePositionAssociationNisWip13B9||!Number.isFinite(plots[i].radialMps)?['rangeM','azRad']:['rangeM','azRad','radialMps'],gateUnits:'NIS',trackId:tr.trackId,nis,gate:stageGate,decision:nis<=stageGate?'ELIGIBLE':'REJECT',reason:'NATIVE_NIS'});return nis<=stageGate?nis:blockedCost;})"
  return edit(t,a,b)
 scoped('surfaceAssignmentsPreferEstablishedWip13B14',surface)
 def spq(t):
  a='      if(nis<=gate&&(!best||nis<best.nis))best={trackId:id,nis,cross};'
  b="      if(TRACK_A_DIAG.enabled)trackATraceEventA('CANDIDATE',plot,{..."+context("'AIR_RADAR'","plot.source",own)+",route:'SPQ_AIR_GREEDY',appliedModel:'AIR_POLAR_DOPPLER',appliedDimension:4,appliedFields:['rangeM','azRad','elRad','radialMps'],gateUnits:'NIS',trackId:id,nis,gate,decision:nis<=gate?'ELIGIBLE':'REJECT',reason:'NATIVE_NIS'});\n"+a
  return edit(t,a,b)
 scoped('spq9bBestTrackForPlotV34',spq)
 def spq_suppress(t):
  a='        existing._spq9bFreshS=0;'
  b="        if(TRACK_A_DIAG.enabled)trackATraceEventA('ASSIGNMENT',plot,{..."+context("'AIR_RADAR'","'SPQ9B_AIR'",own)+",route:'SPQ_SPY_PREFERRED',trackId:existing.trackId,decision:'ASSOCIATE_WITHOUT_HIT',independentHit:false,nis:match.nis,finalSource:existing.sensorSource});\n"+a
  return edit(t,a,b)
 scoped('spq9bAcceptAnonymousPlotsV34',spq_suppress)
 def npc(t):
  a="    if(surface(plots[i])?!trackMayAcceptSurfacePlotCrossDomainWip13B14(tr,plots[i]):!trackMayAcceptAirPlotCrossDomainWip13B14(tr,plots[i]))continue;"
  b="    if(surface(plots[i])?!trackMayAcceptSurfacePlotCrossDomainWip13B14(tr,plots[i]):!trackMayAcceptAirPlotCrossDomainWip13B14(tr,plots[i])){if(TRACK_A_DIAG.enabled)trackATraceEventA('CANDIDATE',plots[i],{..."+context("surface(plots[i])?'SURFACE_RADAR':'AIR_RADAR'","plots[i].source",'r.entityId')+",route:'NPC_OBSERVER',trackId:id,decision:'REJECT',reason:'NATIVE_CROSS_DOMAIN_PARTITION'});continue;}"
  t=edit(t,a,b)
  a='    if(nis<=64)pairs.push({i,id,nis});'
  t=edit(t,a,"    if(TRACK_A_DIAG.enabled)trackATraceEventA('CANDIDATE',plots[i],{..."+context("surface(plots[i])?'SURFACE_RADAR':'AIR_RADAR'","plots[i].source",'r.entityId')+",route:'NPC_OBSERVER',appliedModel:surface(plots[i])?'SURFACE_POSITION_ONLY':'AIR_POLAR_DOPPLER',appliedDimension:surface(plots[i])?2:4,appliedFields:surface(plots[i])?['rangeM','azRad']:['rangeM','azRad','elRad','radialMps'],gateUnits:'NIS',trackId:id,nis,gate:64,decision:nis<=64?'ELIGIBLE':'REJECT',reason:'NATIVE_NIS'});\n"+a)
  a='    const tr=created?observerNewTrackC(o,meas,surface(meas)):o.tracks.get(id);'
  t=edit(t,a,a+"\n    const trackABefore=TRACK_A_DIAG.enabled?trackAStateA(created?null:tr):null;")
  a='if(!ok){o.stats.rejected++;return null;}'
  t=edit(t,a,"if(!ok){if(TRACK_A_DIAG.enabled)trackATraceEventA('UPDATE',meas,{..."+context("surface(meas)?'SURFACE_RADAR':'AIR_RADAR'",'meas.source','r.entityId')+",route:'NPC_OBSERVER',trackId:id,decision:'REJECT',reason:'NATIVE_FILTER_REJECT',before:trackABefore,after:trackAStateA(tr)});o.stats.rejected++;return null;}")
  a='    if(created)o.stats.initiated++;else o.stats.associated++;return tr;'
  t=edit(t,a,"    if(TRACK_A_DIAG.enabled)trackATraceEventA('UPDATE',meas,{..."+context("surface(meas)?'SURFACE_RADAR':'AIR_RADAR'",'meas.source','r.entityId')+",route:'NPC_OBSERVER',trackId:tr.trackId,decision:created?'CREATE':'ACCEPT',nis:tr._kfNis,finalSource:tr.sensorSource,before:trackABefore,after:trackAStateA(tr)});\n"+a)
  return t
 scoped('observerAcceptPlotsC',npc)
 def ciws(t,owner):
  a='      if(!meas?.attempted)continue;CIWS_C55.stats.attempted++;if(!meas.accepted)continue;CIWS_C55.stats.accepted++;'
  b="      if(TRACK_A_DIAG.enabled&&meas?.attempted)trackATraceEventA('RECEIVED',meas,{..."+context("'CIWS_LOCAL_RF'","'LOCAL_RF'",owner)+",route:'C55',appliedModel:'RELATIVE_POSITION_DISTANCE',appliedDimension:3,appliedFields:['rxM','ryM','rzM'],gateUnits:'m',mountId:m.id,knownOwnLaunch:!!src.own,decision:meas.accepted?'DETECTED':'NO_DETECTION'});\n"+a
  t=edit(t,a,b)
  a='        if(seen.has(r.id)||!!r.ownFireEvidence!==!!src.own)continue;const s=r.st,d=Math.hypot(s.rxM-meas.rxM,s.ryM-meas.ryM,s.rzM-meas.rzM);'
  b="        if(seen.has(r.id)||!!r.ownFireEvidence!==!!src.own){if(TRACK_A_DIAG.enabled)trackATraceEventA('CANDIDATE',meas,{..."+context("'CIWS_LOCAL_RF'","'LOCAL_RF'",owner)+",route:'C55',appliedModel:'RELATIVE_POSITION_DISTANCE',appliedDimension:3,appliedFields:['rxM','ryM','rzM'],gateUnits:'m',mountId:m.id,trackId:r.id,knownOwnLaunch:!!src.own,decision:'REJECT',reason:seen.has(r.id)?'NATIVE_ONE_TO_ONE':'NATIVE_OWN_FIRE_PARTITION'});continue;}const s=r.st,d=Math.hypot(s.rxM-meas.rxM,s.ryM-meas.ryM,s.rzM-meas.rzM);"
  t=edit(t,a,b)
  a='        if(d<gate&&d<error){best=r;error=d;}'
  t=edit(t,a,"        if(TRACK_A_DIAG.enabled)trackATraceEventA('CANDIDATE',meas,{..."+context("'CIWS_LOCAL_RF'","'LOCAL_RF'",owner)+",route:'C55',appliedModel:'RELATIVE_POSITION_DISTANCE',appliedDimension:3,appliedFields:['rxM','ryM','rzM'],gateUnits:'m',mountId:m.id,trackId:r.id,distanceM:d,gate,knownOwnLaunch:!!src.own,decision:d<gate?'ELIGIBLE':'REJECT',reason:'NATIVE_DISTANCE_GATE'});\n"+a)
  a='      if(!best){if(b.files.size>=CIWS_C55_POLICY.maxFiles)continue;'
  t=edit(t,a,'      const trackABefore=TRACK_A_DIAG.enabled?trackAStateA(best):null;\n'+a)
  a='      best.ownFireEvidence=best.ownFireEvidence||src.own;c55UpdateFile(best,meas,m,mode,dt);'
  t=edit(t,a,a+"\n      if(TRACK_A_DIAG.enabled)trackATraceEventA('UPDATE',meas,{..."+context("'CIWS_LOCAL_RF'","'LOCAL_RF'",owner)+",route:'C55',appliedModel:'RELATIVE_POSITION_DISTANCE',appliedDimension:3,appliedFields:['rxM','ryM','rzM'],gateUnits:'m',mountId:m.id,trackId:best.id,knownOwnLaunch:!!src.own,decision:trackABefore?'ACCEPT':'CREATE',finalSource:'LOCAL_RF',before:trackABefore,after:trackAStateA(best)});")
  return t
 # Two physically separate C55 execution contexts; never use target/source IDs.
 scoped('c55SensorSweep',lambda t:ciws(t,'owner.entityId'),0)
 scoped('c55SensorSweep',lambda t:ciws(t,own),1)
 def offboard(t):
  a='  let match=null;for(const [id,tr]of o.tracks)'
  t=edit(t,a,"  if(TRACK_A_DIAG.enabled)TRACK_A_DIAG.origins.set(meas,{measuredAtS:report.measuredAtS,receivedAtS:now,sourceId:report.sourceId,sequence:report.sequence});\n"+a)
  a='  let match=null;for(const [id,tr]of o.tracks){const nis=trackCartesianAssociationNisV33(tr,meas);if(nis<=25&&(!match||nis<match.nis))match={id,nis};}'
  cx="{..."+context("'OFFBOARD_PLOT'","'OFFBOARD_C'",'r.entityId')+",measuredAtS:report.measuredAtS,sourceId:report.sourceId,sequence:report.sequence"
  b="  if(TRACK_A_DIAG.enabled)trackATraceEventA('RECEIVED',report,"+cx+",route:'HAWKLINK_RECEIVE',appliedModel:'REPORTED_CARTESIAN_POSITION',appliedDimension:3,appliedFields:['reported.xM','reported.yM','reported.zM'],gateUnits:'NIS',decision:'PENDING'});\n  let match=null;for(const [id,tr]of o.tracks){const nis=trackCartesianAssociationNisV33(tr,meas);if(TRACK_A_DIAG.enabled)trackATraceEventA('CANDIDATE',report,"+cx+",route:'HAWKLINK_RECEIVE',appliedModel:'REPORTED_CARTESIAN_POSITION',appliedDimension:3,appliedFields:['reported.xM','reported.yM','reported.zM'],gateUnits:'NIS',trackId:id,nis,gate:25,decision:nis<=25?'ELIGIBLE':'REJECT',reason:'NATIVE_NIS'});if(nis<=25&&(!match||nis<match.nis))match={id,nis};}"
  t=edit(t,a,b)
  a="  if(existing?.observationReportsC?.remote[report.sourceId]?.measuredAtS>=report.measuredAtS)return false;"
  t=edit(t,a,"  if(existing?.observationReportsC?.remote[report.sourceId]?.measuredAtS>=report.measuredAtS){if(TRACK_A_DIAG.enabled)trackATraceEventA('ASSIGNMENT',report,"+cx+",route:'HAWKLINK_RECEIVE',appliedModel:'REPORTED_CARTESIAN_POSITION',appliedDimension:3,appliedFields:['reported.xM','reported.yM','reported.zM'],gateUnits:'NIS',trackId:existing.trackId,decision:'REJECT',reason:'NATIVE_REPEATED_FIX'});return false;}\n  const trackABefore=TRACK_A_DIAG.enabled?trackAStateA(existing):null;")
  a="o.offboard.sources.get(report.sourceId).lastReportS=report.measuredAtS;return true;"
  t=edit(t,a,"o.offboard.sources.get(report.sourceId).lastReportS=report.measuredAtS;if(TRACK_A_DIAG.enabled)trackATraceEventA('UPDATE',report,"+cx+",route:'HAWKLINK_RECEIVE',appliedModel:'REPORTED_CARTESIAN_POSITION',appliedDimension:3,appliedFields:['reported.xM','reported.yM','reported.zM'],gateUnits:'NIS',trackId:tr.trackId,decision:existing?'ACCEPT':'CREATE',finalSource:tr.sensorSource,before:trackABefore,after:trackAStateA(tr)});return true;")
  return t
 scoped('acceptOffboardC',offboard)
 def network(t):
  a="  if(file?.sources.get(key).measuredAtS>=report.measuredAtS){"
  t=edit(t,a,"  if(TRACK_A_DIAG.enabled)trackATraceEventA('RECEIVED',report,{..."+context("report.kind==='SELF'?'NETWORK_SELF':'NETWORK_TRACK'","'LINK16'",'r.entityId')+",route:'NETWORK_RECEIVE',appliedModel:'REPORTED_FILTER_STATE',appliedDimension:6,appliedFields:['reported.xM','reported.yM','reported.zM','reported.vxMps','reported.vyMps','reported.vzMps'],gateUnits:'NIS',senderShip:senderId,sourceTrackUid:report.fileId,measuredAtS:report.measuredAtS,decision:'PENDING'});\n"+a)
  a="    const q=file.sources.get(key);q.bid={...report.bid};q.assessment=report.assessment;q.identity=report.identity;return;"
  t=edit(t,a,"    if(TRACK_A_DIAG.enabled)trackATraceEventA('ASSIGNMENT',report,{..."+context("report.kind==='SELF'?'NETWORK_SELF':'NETWORK_TRACK'","'LINK16'",'r.entityId')+",route:'NETWORK_RECEIVE',appliedModel:'REPORTED_FILTER_STATE',appliedDimension:6,appliedFields:['reported.xM','reported.yM','reported.zM','reported.vxMps','reported.vyMps','reported.vzMps'],gateUnits:'NIS',senderShip:senderId,sourceTrackUid:report.fileId,measuredAtS:report.measuredAtS,decision:'STATUS_ONLY',independentHit:false,reason:'NATIVE_REPEATED_FIX'});\n"+a)
  a="if(nis<=36)candidates.push({f,nis});"
  t=edit(t,a,"if(TRACK_A_DIAG.enabled)trackATraceEventA('CANDIDATE',report,{..."+context("report.kind==='SELF'?'NETWORK_SELF':'NETWORK_TRACK'","'LINK16'",'r.entityId')+",route:'NETWORK_RECEIVE',appliedModel:'REPORTED_FILTER_STATE',appliedDimension:6,appliedFields:['reported.xM','reported.yM','reported.zM','reported.vxMps','reported.vyMps','reported.vzMps'],gateUnits:'NIS',senderShip:senderId,sourceTrackUid:report.fileId,measuredAtS:report.measuredAtS,trackId:f.id,nis,gate:36,decision:nis<=36?'ELIGIBLE':'REJECT',reason:'NATIVE_NIS'});"+a)
  a="  file.sources.set(key,{...jsonSafeCloneV48Wip11A(report),senderId});file.hits++;"
  t=edit(t,a,a+"\n  if(TRACK_A_DIAG.enabled)trackATraceEventA('ASSIGNMENT',report,{..."+context("report.kind==='SELF'?'NETWORK_SELF':'NETWORK_TRACK'","'LINK16'",'r.entityId')+",route:'NETWORK_RECEIVE',appliedModel:'REPORTED_FILTER_STATE',appliedDimension:6,appliedFields:['reported.xM','reported.yM','reported.zM','reported.vxMps','reported.vyMps','reported.vzMps'],gateUnits:'NIS',senderShip:senderId,sourceTrackUid:report.fileId,measuredAtS:report.measuredAtS,trackId:file.id,decision:'ACCEPT',nativeHitIncrement:1,finalSource:'LINK16'});")
  return t
 scoped('networkAcceptReportG',network)
 def network_reconcile(t):
  a="if(nis<=36)pairs.push({file,id,tr,e,estimate,nis});"
  t=edit(t,a,"if(TRACK_A_DIAG.enabled)trackATraceEventA('CANDIDATE',{stateM:estimate.x,covariance:estimate.P},{..."+context("'NETWORK_TRACK'","'LINK16_CI'",'r.entityId')+",route:'NETWORK_RECONCILE',appliedModel:'REPORTED_FILTER_STATE',appliedDimension:6,appliedFields:['reported.xM','reported.yM','reported.zM','reported.vxMps','reported.vyMps','reported.vzMps'],gateUnits:'NIS',sourceTrackUid:file.id,trackId:id,nis,gate:36,decision:nis<=36?'ELIGIBLE':'REJECT',reason:'NATIVE_NIS'});"+a)
  a="p.file.fusedAtS=now;used.add(p.id);n.stats.associated++;"
  t=edit(t,a,a+"if(TRACK_A_DIAG.enabled)trackATraceEventA('ASSIGNMENT',{stateM:p.estimate.x,covariance:p.estimate.P},{..."+context("'NETWORK_TRACK'","'LINK16_CI'",'r.entityId')+",route:'NETWORK_RECONCILE',appliedModel:'REPORTED_FILTER_STATE',appliedDimension:6,appliedFields:['reported.xM','reported.yM','reported.zM','reported.vxMps','reported.vyMps','reported.vzMps'],gateUnits:'NIS',sourceTrackUid:p.file.id,trackId:p.id,nis:p.nis,gate:36,decision:'ASSIGN_TO_LOCAL_DISPLAY',independentHit:false,finalSource:'LINK16_CI'});")
  return t
 scoped('networkReconcileG',network_reconcile)
 def esm(t):
  a='  for(const q of plots){'
  return edit(t,a,a+"\n    if(TRACK_A_DIAG.enabled)trackATraceEventA('RECEIVED',q,{..."+context("'ESM_BEARING'","'PASSIVE_RF_F'",'r.entityId')+",route:'ESM_RECEIVE',measuredAtS:q.measuredAtS,decision:'BEARING_ONLY'});")
 scoped('electronicAcceptPlotsF',esm)
 def isar(t):
  a="const now=simStepCounter*SIM_FIXED_DT;"
  return edit(t,a,a+"if(TRACK_A_DIAG.enabled)trackATraceEventA('RECEIVED',p,{..."+context("'ISAR_EVIDENCE'","'ISAR'",'r.entityId')+",route:'ISAR_INGEST',measuredAtS:p?.measuredAtS,sourceId:p?.sourceId,sequence:p?.sequence,independentHit:false,decision:'EVIDENCE_ONLY'});")
 scoped('ingestOffboardIsarF2',isar)
 def iff(t):
  a='    state.lastReply={...out[out.length-1]};'
  return edit(t,a,"    if(TRACK_A_DIAG.enabled)trackATraceEventA('RECEIVED',out[out.length-1],{..."+context("'IFF_REPLY'","'AIR_IFF_E'",'ship.entityId')+",route:'IFF_REPLY',decision:'REPLY_EVIDENCE'});\n"+a)
 scoped('heloMeasureIffRepliesE',iff)
 def helo(t):
  a='const m=APS_MODES_F[q.mode],out=[],nmask=(1<<m.n)-1;'
  if a not in t:raise AssertionError(t[:240])
  return edit(t,a,a+"if(TRACK_A_DIAG.enabled)for(const p of rows)trackATraceEventA('RECEIVED',p,{..."+context("'HELO_RADAR'","'AN/APS-153'",'h.ownerEntityId')+",route:'HELO_CONTACT_INPUT',measuredAtS:p.measuredAtS,decision:'PENDING_CONFIRMATION'});")
 scoped('apsContactStepF',helo)
 restored=s
 for c in reversed(changes):assert restored.count(c['after'])==c['count'],c['label'];restored=restored.replace(c['after'],c['before'])
 assert restored==before
 return s,changes,hooks
if __name__=='__main__':
 raw=BASE.read_bytes();assert sha(raw)==PIN;before=unpack(raw);s,changes,hooks=transform(before);OUT.write_bytes(pack(raw,s));(P/'changes.diff').write_text(''.join(difflib.unified_diff(before.splitlines(True),s.splitlines(True),fromfile=BASE.name+'::main',tofile=OUT.name+'::main')));(P/'BUILD.json').write_text(json.dumps({'baseBranch':'friendly-contact-a','baseCommit':'4ba64ba0cace9124497a710d00df1b174984ffdc','baselineSha256':PIN,'baselineMainSha256':sha(before.encode()),'output':OUT.name,'htmlSha256':sha(OUT.read_bytes()),'mainSha256':sha(s.encode()),'inverseByteExact':True,'defaultTraceEnabled':False,'behaviorChanges':False,'coefficientChanges':False,'expectationChanges':False,'changes':changes},indent=2)+'\n');(P/'hook-locations.json').write_text(json.dumps(hooks,indent=2)+'\n');print(sha(OUT.read_bytes()))

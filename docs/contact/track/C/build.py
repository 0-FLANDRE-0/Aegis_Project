"""Reversible TRACK-C delta on approved R4, no RF/EKF/weapon coefficient edits."""
from pathlib import Path
import argparse,difflib,hashlib,importlib.util,json,re,subprocess
P=Path(__file__).resolve().parent;R=P.parents[3]
BASE=R/'Aegis_SIM_v48_WIP_TRACK_B_STABLE_D.html'
PIN='48b023c580db02b08f165fa7ac68f973734d82e8fb4daa5981dcc90b7e04e4ab'
MAIN_PIN='6163ada1a49dc86ce8b179b81650fa2da78ecc8d9273015142a721748abf6a64'
sha=lambda b:hashlib.sha256(b).hexdigest()
spec=importlib.util.spec_from_file_location('frozen_b_packer',P.with_name('B')/'build.py');util=importlib.util.module_from_spec(spec);spec.loader.exec_module(util)


def transform(source,mode):
    changes=[];s=source
    def replace(before,after,label,count=1):
        nonlocal s
        assert s.count(before)==count,(label,s.count(before));s=s.replace(before,after)
        changes.append({'label':label,'before':before,'after':after,'count':count})
    def scoped(name,fn,occurrence=0):
        nonlocal s
        a,b=util.scope_span(s,{'function':name,'occurrence':occurrence});old=s[a:b];new=fn(old);assert old!=new
        s=s[:a]+new+s[b:]
        changes.append({'label':name+':'+str(occurrence),'before':old,'after':new,'count':1,'offset':a})
    def edit(t,a,b):assert t.count(a)==1,(a[:100],t.count(a));return t.replace(a,b,1)
    module=(P/'lifecycle.js').read_text().replace("const TRACK_C_IMPLEMENTATION_MODE='ACTIVE';",f"const TRACK_C_IMPLEMENTATION_MODE='{mode}';")
    anchor='window.__AEGIS_STARTUP_PROMISE__=(async () => {'
    replace(anchor,anchor+'\n// TRACK_C_DIAGNOSTICS_BEGIN\n'+module+'\n// TRACK_C_DIAGNOSTICS_END\n','READ_ONLY_LIFECYCLE_MODULE')
    def spq(t):
        t=edit(t,'    const usedTracks=new Set();let accepted=0;let trackBSequenceIndex=-1;',
          '''    const usedTracks=new Set();let accepted=0;let trackBSequenceIndex=-1;
    const trackCSelection=trackCSpqAssignmentsC(observations),trackCMatches=new Map(trackCSelection.pairs.map(p=>[p.i,p]));
    if(TRACK_C_DIAG.enabled&&observations.length)trackCRecordC({event:'SPQ_AIR_COMMON_EPOCH',mode:TRACK_C_IMPLEMENTATION_MODE,timeS:trackCTimeC(),ownerEntityId:ACTIVE_SHIP_RUNTIME.entityId,pairs:trackCSelection.pairs.map(p=>({i:p.i,id:p.id,nis:p.nis})),heldPlots:[...trackCSelection.heldPlots],heldTracks:[...trackCSelection.heldTracks]});
    let trackCIndex=-1;''')
        t=edit(t,'    for(const obs of observations){','''    for(const obs of observations){
      trackCIndex++;
      if(TRACK_C_IMPLEMENTATION_MODE==='ACTIVE'&&trackCSelection.heldPlots.has(trackCIndex)){SPQ9B_ASSOC_STATS_V34.rejected++;continue;}''')
        old='      const match=spq9bBestTrackForPlotV34(plot,usedTracks,trackBPlotIndex),existing=match?tracks.get(match.trackId):null;'
        new='''      const selected=trackCMatches.get(trackCIndex),
        match=TRACK_C_IMPLEMENTATION_MODE==='ACTIVE'?(selected?{trackId:selected.id,nis:selected.nis,cross:trackSurfaceBackedWip13B14(tracks.get(selected.id))}:null):spq9bBestTrackForPlotV34(plot,usedTracks,trackBPlotIndex),existing=match?tracks.get(match.trackId):null;
      if(TRACK_C_IMPLEMENTATION_MODE==='ACTIVE'&&match&&(usedTracks.has(match.trackId)||trackCSelection.heldTracks.has(match.trackId))){SPQ9B_ASSOC_STATS_V34.rejected++;continue;}'''
        return edit(t,old,new)
    scoped('spq9bAcceptAnonymousPlotsV34',spq)
    def alias(t):
        t=edit(t,'if(!si)return null;let best=null;','if(!si)return null;let best=null;const trackCCandidates=[];')
        t=edit(t,'if(!best||score<best.score)best={oldId,newId,score,dp,dv,posGate,velGate};',
          'trackCCandidates.push({oldId,newId,score,dp,dv,posGate,velGate,coast:ps});if(!best||score<best.score)best={oldId,newId,score,dp,dv,posGate,velGate};')
        t=edit(t,'    if(!best)return null;const oldA=', '''    if(TRACK_C_IMPLEMENTATION_MODE==='ACTIVE'){
      const lineage=trackCAliasDecisionC(trackCCandidates,newId,tr,tracks,wip118TrackStateSI);
      if(TRACK_C_DIAG.enabled)trackCRecordC({event:'ALIAS_INHERITANCE',ownerEntityId:ACTIVE_SHIP_RUNTIME.entityId,timeS:trackCTimeC(),newId,oldId:lineage.pick?.oldId??null,candidateCount:trackCCandidates.length,accepted:lineage.ok,reason:lineage.reason});
      if(!lineage.ok)return null;
      const q=lineage.pick;best={oldId:q.oldId,newId:q.newId,score:q.score,dp:q.dp,dv:q.dv,posGate:q.posGate,velGate:q.velGate};
    }
    if(!best)return null;const oldA=''')
        return t
    scoped('wip121TryAliasReacquire',alias,0)
    scoped('wip121TryAliasReacquire',alias,1)
    def c55(t,owner):
        t=edit(t,'    const trackBShadow=TRACK_B_DIAG.enabled?trackBC55BeginB(b):null;',
          '''    const trackBShadow=TRACK_B_DIAG.enabled?trackBC55BeginB(b):null;const trackCRows=[];
    const trackCFilePrior=TRACK_C_DIAG.enabled&&TRACK_C_IMPLEMENTATION_MODE==='SHADOW'?new Map([...b.files].map(([id,r])=>[id,{id,ownFireEvidence:!!r.ownFireEvidence,st:{rxM:r.st.rxM,ryM:r.st.ryM,rzM:r.st.rzM,localHits:r.st.localHits,localAgeS:r.st.localAgeS,_c55P:r.st._c55P?.map(q=>q.slice())}}])):null;''')
        needle='      const trackBShadowPlot=trackBShadow?trackBC55CaptureB(trackBShadow,meas,!!src.own,seen):null;'
        t=edit(t,needle,needle+"\n      const trackCRow={src,meas,mode,shadowPlot:trackBShadowPlot,nativeId:null};trackCRows.push(trackCRow);\n      if(TRACK_C_IMPLEMENTATION_MODE==='ACTIVE')continue;")
        t=edit(t,'      if(trackBShadowPlot)trackBShadowPlot.nativeTrackId=best.id;','      if(trackBShadowPlot)trackBShadowPlot.nativeTrackId=best.id;trackCRow.nativeId=best.id;')
        needle='    if(trackBShadow)trackBC55AnalyzeB('
        addition='''    if(TRACK_C_IMPLEMENTATION_MODE==='ACTIVE'){
      const selection=trackCC55AssignmentsC(trackCRows.map(q=>({measurement:q.meas,knownOwnLaunch:!!q.src.own})),b.files,cfg),selected=new Map(selection.pairs.map(p=>[p.i,p.id]));
      if(TRACK_C_DIAG.enabled&&trackCRows.length)trackCRecordC({event:'C55_NATIVE_COVARIANCE_BATCH',ownerEntityId:OWNER_TOKEN,mountId:m.id,timeS:trackCTimeC(),costUnits:'NIS',dimensions:3,delta:TRACK_B_POLICY.ambiguityDeltaNis,plots:trackCRows.length,pairs:selection.pairs.map(p=>({i:p.i,id:p.id,nis:p.nis})),heldPlots:[...selection.heldPlots],heldTracks:[...selection.heldTracks],reason:selection.reason??null});
      for(let i=0;i<trackCRows.length;i++){
        if(selection.heldPlots.has(i))continue;
        const {src,meas,mode,shadowPlot}=trackCRows[i],e=src.e,id=selected.get(i);let best=id==null?null:b.files.get(id);
        if(id!=null&&(!best||seen.has(id)||selection.heldTracks.has(id)))continue;
        const trackABefore=TRACK_A_DIAG.enabled?trackAStateA(best):null;
        if(!best){if(b.files.size>=CIWS_C55_POLICY.maxFiles)continue;const id=-5500000-(++CIWS_C55.serial);
          best={id,st:c55BlankState(),proxy:{id:e.id,alive:true,_c55Id:id},firstSeenS:CIWS_C55.clockS,confirmed:false,approachS:0,samples:[],cmsTrackId:null,protectedIdentity:null,ownFireEvidence:false};b.files.set(id,best);CIWS_C55.stats.created++;
        }
        seen.add(best.id);CIWS_C55_SENSOR_LINKS.set(best,src);best.proxy.id=e.id;
        best.ownFireEvidence=best.ownFireEvidence||src.own;c55UpdateFile(best,meas,m,mode,dt);
        if(shadowPlot)shadowPlot.nativeTrackId=best.id;
        if(TRACK_A_DIAG.enabled)trackATraceEventA('UPDATE',meas,{...trackATraceContextA('CIWS_LOCAL_RF','LOCAL_RF',OWNER_TOKEN),route:'C55',appliedModel:'RELATIVE_POSITION_NATIVE_AXIS_KF_NIS',appliedDimension:3,appliedFields:['rxM','ryM','rzM'],gateUnits:'NIS_COST_WITH_NATIVE_METRE_ELIGIBILITY',mountId:m.id,trackId:best.id,knownOwnLaunch:!!src.own,decision:trackABefore?'ACCEPT':'CREATE',finalSource:'LOCAL_RF',before:trackABefore,after:trackAStateA(best)});
      }
    }
'''.replace('OWNER_TOKEN',owner)
        shadow='''    if(TRACK_C_DIAG.enabled&&TRACK_C_IMPLEMENTATION_MODE==='SHADOW'&&trackCRows.length){
      const proposal=trackCC55AssignmentsC(trackCRows.map(q=>({measurement:q.meas,knownOwnLaunch:!!q.src.own})),trackCFilePrior,cfg);
      trackCRecordC({event:'C55_NATIVE_COVARIANCE_SHADOW',ownerEntityId:OWNER_TOKEN,mountId:m.id,timeS:trackCTimeC(),costUnits:'NIS',dimensions:3,delta:TRACK_B_POLICY.ambiguityDeltaNis,nativeAssignments:trackCRows.map((q,i)=>({i,id:q.nativeId})),pairs:proposal.pairs.map(p=>({i:p.i,id:p.id,nis:p.nis})),heldPlots:[...proposal.heldPlots],heldTracks:[...proposal.heldTracks],reason:proposal.reason??null});
    }
'''.replace('OWNER_TOKEN',owner)
        return edit(t,needle,addition+shadow+needle)
    scoped('c55SensorSweep',lambda t:c55(t,'owner.entityId'),0)
    scoped('c55SensorSweep',lambda t:c55(t,'ACTIVE_SHIP_RUNTIME.entityId'),1)
    restored=s
    for c in reversed(changes):
        if 'offset'in c:
            a=c['offset'];assert restored[a:a+len(c['after'])]==c['after'];restored=restored[:a]+c['before']+restored[a+len(c['after']):]
        else:
            assert restored.count(c['after'])==c['count'];restored=restored.replace(c['after'],c['before'])
    assert restored==source
    return s,changes


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=['ACTIVE','SHADOW'],default='ACTIVE');a=ap.parse_args()
    raw=BASE.read_bytes();assert sha(raw)==PIN;source=util.unpack(raw);assert sha(source.encode())==MAIN_PIN
    transformed,changes=transform(source,a.mode)
    out=R/('Aegis_SIM_v48_WIP_TRACK_C'+('_SHADOW'if a.mode=='SHADOW'else'')+'.html');out.write_bytes(util.pack(raw,transformed))
    assert util.unpack(out.read_bytes())==transformed
    # Every non-module edit is confined to the three reviewed association/alias functions.
    changed=[c['label']for c in changes if c['label']!='READ_ONLY_LIFECYCLE_MODULE']
    assert changed==['spq9bAcceptAnonymousPlotsV34:0','wip121TryAliasReacquire:0','wip121TryAliasReacquire:1','c55SensorSweep:0','c55SensorSweep:1']
    scope={'schema':'AEGIS_TRACK_C_SCOPE_1','pass':True,'baselineHtmlSha256':PIN,'baselineMainSha256':MAIN_PIN,
      'candidateHtmlSha256':sha(out.read_bytes()),'candidateMainSha256':sha(transformed.encode()),'changedFunctions':changed,
      'rfPhysicsFunctionsByteIdentical':True,'ekfFunctionsAndCoefficientsByteIdentical':True,'iffRoeIdentityFunctionsByteIdentical':True,
      'weaponDamageAiPhysicsByteIdenticalExceptReviewedAliasBookkeeping':True,'coefficientChanges':0,'saveSchemaChanges':0,
      'inverseByteExact':True,'c55Active':a.mode=='ACTIVE','c55Reason':'Native distance eligibility preserved; cost uses exact existing per-axis P+R innovation denominator. Shared delta1. No native KF/RF coefficient changes.',
      'mode':a.mode,'newModuleDiagnosticDefaultOff':True,'approved':False,'release':False}
    suffix=''if a.mode=='ACTIVE'else'_SHADOW'
    (P/('BUILD'+suffix+'.json')).write_text(json.dumps({'schema':'AEGIS_TRACK_C_BUILD_1','baselineMain':'d328c941d71e39ef616d4136c70bed0eeebe7f06','baselineHtmlSha256':PIN,'html':out.name,'htmlSha256':sha(out.read_bytes()),'mainSha256':sha(transformed.encode()),'mode':a.mode,'inverseByteExact':True,'changes':changes},ensure_ascii=False,indent=2)+'\n')
    (P/('SCOPE'+suffix+'.json')).write_text(json.dumps(scope,indent=2)+'\n')
    (P/('changes'+suffix+'.diff')).write_text(''.join(difflib.unified_diff(source.splitlines(True),transformed.splitlines(True),fromfile=BASE.name+'::MAIN',tofile=out.name+'::MAIN')))
    Path('/dev/shm/track-c-'+a.mode.lower()+'.js').write_text(transformed)
    print(json.dumps({'html':out.name,'sha256':sha(out.read_bytes()),'mode':a.mode,'inverseByteExact':True}))


if __name__=='__main__':main()

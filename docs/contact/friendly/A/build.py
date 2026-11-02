"""Bounded contact-contract repair over unchanged CG_TURRET_A physics/RF."""
from pathlib import Path
import json,gzip,base64,hashlib,re,difflib
P=Path(__file__).resolve().parent;R=P.parents[3];BASE=R/'Aegis_SIM_v48_WIP_CG_TURRET_A.html';OUT=R/'Aegis_SIM_v48_WIP_FRIENDLY_CONTACT_A.html'
sha=lambda b:hashlib.sha256(b).hexdigest()
def pack(raw,s):
 m=re.search(rb'data-c55-index="13">([^<]+)',raw);z=gzip.compress(s.encode(),9,mtime=0);enc=base64.b64encode(z);out=raw[:m.start(1)]+enc+raw[m.end(1):];m=re.search(rb'const records=(\[.*?\]);',out,re.S);rs=json.loads(m[1]);rs[13].update(rawBytes=len(s.encode()),gzipBytes=len(z),sha256=sha(s.encode()))
 if'encodedBytes'in rs[13]:rs[13]['encodedBytes']=len(enc)
 return out[:m.start(1)]+json.dumps(rs,separators=(',',':')).encode()+out[m.end(1):]
def transform(s):
 before=s;changes=[]
 def sub(a,b,count=1):
  nonlocal s
  assert s.count(a)==count,(a[:130],s.count(a),count);s=s.replace(a,b);changes.append({'before':a,'after':b,'count':count})
 # Both player and detached NPC CIWS sensor contexts use the same contract.
 sub('if(seen.has(r.id))continue;const s=r.st,d=Math.hypot(s.rxM-meas.rxM,s.ryM-meas.ryM,s.rzM-meas.rzM);',
     'if(seen.has(r.id)||!!r.ownFireEvidence!==!!src.own)continue;const s=r.st,d=Math.hypot(s.rxM-meas.rxM,s.ryM-meas.ryM,s.rzM-meas.rzM);',2)
 # Preserve observation dimensions. A surface waveform cannot observe height
 # or undo a genuine accepted 3-D AIR solution merely by routing its plot.
 sub('  function trackApplySurfaceDomainConstraint(tr,refZM=8){\n    if(!tr?._kfX||!tr?._kfP)return;',
     '  function trackApplySurfaceDomainConstraint(tr,refZM=8){\n    if(!tr?._kfX||!tr?._kfP||trackHasAirObservationFC(tr))return;')
 anchor='  // ===== WIP13B14 CROSS-DOMAIN ASSOCIATION CONTINUITY ====='
 sub(anchor,(P/'observation-contract.js').read_text()+'\n'+anchor)
 sub("function trackSurfaceBackedWip13B14(tr){return !!tr&&(","function trackSurfaceBackedWip13B14(tr){return !trackHasAirObservationFC(tr)&&!!tr&&(")
 sub("  function trackMayAcceptSurfacePlotCrossDomainWip13B14(tr,plot={}){\n    if(!tr||tr.sensorDetected===false||tr.truthEnded)return false;",
     "  function trackMayAcceptSurfacePlotCrossDomainWip13B14(tr,plot={}){\n    if(!tr||tr.sensorDetected===false||tr.truthEnded)return false;\n    if(trackHasAirObservationFC(tr))return true; // 2-D contribution; same native NIS gate, no height/domain overwrite.")
 sub("  function trackMayAcceptAirPlotCrossDomainWip13B14(tr,plot={}){\n    if(!tr||tr.sensorDetected===false||tr.truthEnded)return false;",
     "  function trackMayAcceptAirPlotCrossDomainWip13B14(tr,plot={}){\n    if(!tr||tr.sensorDetected===false||tr.truthEnded)return false;\n    if(tr._surface2DOnlyFC&&Number.isFinite(plot.elRad))return true; // An assumed surface height is not a measured domain partition; native 4-D NIS still decides.")
 sub("    if(truthRef)bindTrackTruthV27(tr,truthRef);\n    tr.truthEnded=false;tr.truthEndReason=null;tr.sensorHits=",
     "    if(isRadar&&!isSurfaceRadar)trackNoteAirObservationFC(tr);\n    else if(created&&isSurfaceRadar)tr._surface2DOnlyFC=true;\n    if(truthRef)bindTrackTruthV27(tr,truthRef);\n    tr.truthEnded=false;tr.truthEndReason=null;tr.sensorHits=")
 sub('    updateTrackClassification(tr,{...meta,domainEvidence:meta.domainEvidence??meas.domainEvidence});',
     '    if(!(isSurfaceRadar&&trackHasAirObservationFC(tr)))updateTrackClassification(tr,{...meta,domainEvidence:meta.domainEvidence??meas.domainEvidence});')
 sub("wasSurface=tr.domain==='SURFACE'||tr.classification==='SURFACE'||!!tr._surfaceMotionPriorWip13B13||!!tr._surfaceSensorContributorsWip13B9,wasAir=",
     "wasSurface=trackSurfaceBackedWip13B14(tr),wasAir=")
 # NPC observer association shares the same measured-dimension policy.
 sub("    if(surface(plots[i])!==(tr.domain==='SURFACE'))continue;",
     "    if(surface(plots[i])?!trackMayAcceptSurfacePlotCrossDomainWip13B14(tr,plots[i]):!trackMayAcceptAirPlotCrossDomainWip13B14(tr,plots[i]))continue;")
 sub('    if(created)o.tracks.set(tr.trackId,tr);',
     '    if(!surface(meas))trackNoteAirObservationFC(tr);else if(created)tr._surface2DOnlyFC=true;\n    if(created)o.tracks.set(tr.trackId,tr);')
 sub('function observerClassifyC(tr,meas){\n  const e=',
     "function observerClassifyC(tr,meas){\n  if(trackHasAirObservationFC(tr)&&!Number.isFinite(meas.elRad)){tr.identity=heloFriendlyIffEvidenceE(tr)?'FRIEND':tr._operatorIdentity??'UNKNOWN';tr.engagementAuthority='WITHHELD';return;}\n  const e=")
 # Reverse substitutions prove every unlisted byte (including all weapon/RF
 # coefficients, EKF matrices/gains and covariance formulas) is unchanged.
 restored=s
 for c in reversed(changes):
  assert restored.count(c['after'])==c['count'];restored=restored.replace(c['after'],c['before'])
 assert restored==before
 return s,changes
if __name__=='__main__':
 raw=BASE.read_bytes();assert sha(raw)=='af105075c65bf9c8774c8b1d347273476e53a3a5869c12387b2cd8d46824d933';before=gzip.decompress(base64.b64decode(re.search(rb'data-c55-index="13">([^<]+)',raw)[1])).decode();s,changes=transform(before);OUT.write_bytes(pack(raw,s));(P/'changes.diff').write_text(''.join(difflib.unified_diff(before.splitlines(True),s.splitlines(True),fromfile=BASE.name+'::main',tofile=OUT.name+'::main')));(P/'BUILD.json').write_text(json.dumps({'baseBranch':'cg-turret-a','baseCommit':'6d306849f290f987cd39c31c901adb4478b07edd','baselineSha256':sha(raw),'output':OUT.name,'htmlSha256':sha(OUT.read_bytes()),'mainSha256':sha(s.encode()),'inverseByteExact':True,'changes':changes,'coefficientChanges':False},indent=2)+'\n');print(sha(OUT.read_bytes()))

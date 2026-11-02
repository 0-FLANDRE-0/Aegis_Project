"""Test-only AFTER_ACTION probes inside RF physical boundaries, no kernel edits."""
from pathlib import Path
import hashlib,importlib.util,json
P=Path(__file__).resolve().parent;R=P.parents[3]
spec=importlib.util.spec_from_file_location('b_exact_pack_util_c_test',P.with_name('B')/'build.py');u=importlib.util.module_from_spec(spec);spec.loader.exec_module(u)

def physical_probe(raw):
 s=u.unpack(raw);original=s;changes=[]
 def patch(name,old,new,occurrence=0):
  nonlocal s
  a,b=u.scope_span(s,{'function':name,'occurrence':occurrence});text=s[a:b];assert text.count(old)==1,(name,text.count(old));text=text.replace(old,new,1);changes.append({'function':name,'occurrence':occurrence,'originalFunctionSha256':hashlib.sha256(s[a:b].encode()).hexdigest()});s=s[:a]+text+s[b:]
 needle='sensorVxMps:rxVx,sensorVyMps:rxVy,sensorVzMps:rxVz});'
 patch('shipboardRadarEchoFieldWip13B13',needle,needle+"\n      window.__TRACK_C_AA_INTERNAL__?.rf(echoes[echoes.length-1],q.ref,opts.observerShipId??ACTIVE_SHIP_RUNTIME.entityId,radarId);")
 for occurrence,owner in [(0,'owner.entityId'),(1,'ACTIVE_SHIP_RUNTIME.entityId')]:
  needle="      if(TRACK_A_DIAG.enabled&&meas?.attempted)"
  patch('c55SensorSweep',needle,"      window.__TRACK_C_AA_INTERNAL__?.local(meas,src,"+owner+",m.id);\n"+needle,occurrence)
 # Callback changes are diagnostics only. Every original expression/RNG call remains byte-for-byte.
 return u.pack(raw,s),{'schema':'AEGIS_TRACK_C_PHYSICAL_TEST_PROBES_1','productSha256':hashlib.sha256(raw).hexdigest(),'instrumentedSha256':hashlib.sha256(u.pack(raw,s)).hexdigest(),'hooks':changes,'productFileModified':False,'nativePhysicsExpressionsChanged':False,'afterActionOnly':True}

def battle_helper():
 s=(P.with_name('B_statistics_r4')/'test_support/statistical_battle.js').read_text()
 needle="  active=true;emit('FIXTURE_START'";assert s.count(needle)==1;s=s.replace(needle,"  window.__TRACK_C_AA_INTERNAL__?.begin({record:c.lineageOn!==false});\n"+needle,1)
 needle=' function observe(force=false){safeObserve(()=>{';assert s.count(needle)==1;s=s.replace(needle,needle+'\n  window.__TRACK_C_AA_INTERNAL__?.sample(initial,statEgress);',1)
 needle="  return {schema:'AEGIS_TRACK_B_STABILIZATION_NATURAL_BATTLE_1'";assert s.count(needle)==1;s=s.replace(needle,"  const trackCLineage=window.__TRACK_C_AA_INTERNAL__?.finish()??null;\n  return {trackCLineage,schema:'AEGIS_TRACK_B_STABILIZATION_NATURAL_BATTLE_1'",1)
 return (P/'after_action.js').read_text()+'\n'+s

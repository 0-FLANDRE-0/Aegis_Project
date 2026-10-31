from pathlib import Path
H=Path(__file__).resolve().parent

def apply(main):
 changes=[]
 def change(a,b):
  nonlocal main
  assert main.count(a)==1,(main.count(a),a[:100]);main=main.replace(a,b);changes.append({'phase':'GUN_B1_OPERATOR_TAKEOVER','anchor':a[:100]})
 change("{hpQueue=null;gunOps=[];ownedCues.clear();}","{for(const c of ownedCues.values())gunB1ReserveManual(c.g,false);hpQueue=null;gunOps=[];ownedCues.clear();}")
 change("if(c.owner!==own())continue;const q=c.g.snapshot();", "if(c.owner!==own())continue;gunB1ReserveManual(c.g,false);if(gunB1IsAutoOwned(c.g))continue;const q=c.g.snapshot();")
 change("const a=ammoId??g.snapshot().loadedAmmoId,q=g.command(id,a);ownedCues.set(key,{g,owner:own(),trackId:id});metrics.cue++;note('GUN_CUE',q.reason??null,{mount:key,trackId:id,ok:!!q.ok});", "const a=ammoId??g.snapshot().loadedAmmoId,preview=gunB1IsAutoOwned(g),q=preview?(gunB1IsAir(tr)?g.solveAirTrack(id,a):g.solveTrack(id,a)):g.command(id,a);ownedCues.set(key,{g,owner:own(),trackId:id});metrics.cue++;note(preview?'GUN_PREVIEW':'GUN_CUE',q.reason??null,{mount:key,trackId:id,ok:!!q.ok,readOnly:preview});")
 change("return{id:key,g,q,eligible,clearance,gate,fcq,", "return{id:key,g,q,eligible,clearance,gate,fcq,autoOwned:gunB1IsAutoOwned(g),canTakeover:gunB1IsAutoOwned(g)&&eligible&&gate.ok&&(q.magazine[q.loadedAmmoId]??0)>0,")
 change("allowed=rows.some(r=>r.canFire),qualityReady=", "allowed=rows.some(r=>r.canFire||r.canTakeover),qualityReady=")
 change("tone=!allowed?'blocked':qualityReady.some", "tone=!allowed?'blocked':rows.some(r=>r.canTakeover)?'warning':qualityReady.some")
 change("reason=allowed?null:rows.find(r=>r.eligible)?.refusal", "reason=allowed?(rows.some(r=>r.canTakeover)?'AUTO_GUN_HANDOFF_REQUIRED':null):rows.find(r=>r.eligible)?.refusal")
 change("continuous=a.rows.filter(r=>r.q.continuousFire.active&&", "continuous=a.rows.filter(r=>!r.autoOwned&&r.q.continuousFire.active&&")
 change("if(gunOps.some(q=>q.owner===own())){gunOps=[];note('GUN_QUEUE_CANCEL','OPERATOR_CANCEL');return true;}", "if(gunOps.some(q=>q.owner===own())){const takeover=gunOps.some(q=>q.owner===own()&&q.takeoverMounts?.length);gunOps=[];if(takeover){clearOwned('OPERATOR_CANCEL');const o=mapObservedObjectsA().find(o=>trackId(o)===m?.d?.id&&o.kind==='TRACK');if(o)cue(o,s.ammoId);}note('GUN_QUEUE_CANCEL','OPERATOR_CANCEL');return true;}")
 change("createdStep:simStepCounter,ammoId:s.ammoId});note('GUN_QUEUE'", "createdStep:simStepCounter,ammoId:s.ammoId,takeoverMounts:m.rows.filter(r=>r.autoOwned&&r.eligible&&r.gate.ok).map(r=>r.id),pendingMounts:m.rows.filter(r=>r.eligible&&r.gate.ok).map(r=>r.id)});note('GUN_QUEUE'")
 naive="for(const{id,g}of guns()){let q=g.snapshot();if(op.action==='FIRE'){gunB1ManualIntent(g);q=g.snapshot();const ammoId=op.ammoId??q.loadedAmmoId;if(q.loadedAmmoId!==ammoId){const f=g.selectAmmo(ammoId);if(!f.ok){note('GUN_WITHHELD',f.reason,{mount:id});continue;}}if(q.commandTrackId!==op.trackId||q.loadedAmmoId!==ammoId)g.command(op.trackId,ammoId);q=g.snapshot();}let result;if(op.action==='STOP')"
 change(naive,"if(op.action==='FIRE'&&op.takeoverMounts?.length){if(runGunTakeover(op))gunOps.push(op);continue;}\n   for(const{id,g}of guns()){const q=g.snapshot();let result;if(op.action==='STOP')")
 change(" function step(){\n  scope();observeHp();",(H/'handoff.js').read_text()+"\n function step(){\n  scope();observeHp();")
 change("({AIR_TRACK_NOT_CONFIRMED:", "({AUTO_GUN_HANDOFF_REQUIRED:'자동 대공 → 수동 사격 인계',AIR_TRACK_NOT_CONFIRMED:")
 return main,changes

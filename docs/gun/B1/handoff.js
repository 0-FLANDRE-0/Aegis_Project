 // GUN_B1: fixed-tick operator takeover, never bypasses native cycle/selection/fire gates.
 // This queue is used only when the operator takes over an autonomous mount.
 function runGunTakeover(op){
  const remaining=[];
  for(const id of op.pendingMounts??[]){
   const entry=guns().find(r=>r.id===id);if(!entry)continue;const g=entry.g,tr=mapBObservedTrack(op.trackId),q0=g.snapshot();
   const policy=gunB1IsAir(tr)?gunB1AirPolicy(tr):tr?wip13b1SurfaceReleasePolicy(normalizeTrackOperatorIdentityA3(tr._operatorIdentity??tr.identity),'MANUAL',g.spec):{ok:false,reason:'NO_TRACK'};
   if(!policy.ok||(simStepCounter-op.createdStep)*SIM_FIXED_DT>g.spec.fireControl.singleFireConsentHoldS){gunB1ReserveManual(g,false);note('GUN_WITHHELD',policy.reason??'FIRE_CONSENT_EXPIRED',{mount:id,trackId:op.trackId});continue;}
   gunB1ReserveManual(g,true);
   let q=g.snapshot();if(q.cycleRemainingS>1e-9){remaining.push(id);continue;}
   const ammoId=op.ammoId??q.loadedAmmoId;
   if(q.loadedAmmoId!==ammoId){const selected=g.selectAmmo(ammoId);if(!selected.ok){if(selected.reason==='FEED_CYCLING')remaining.push(id);else gunB1ReserveManual(g,false);note('GUN_WITHHELD',selected.reason,{mount:id});continue;}}
   q=g.snapshot();if(q.commandTrackId!==op.trackId||q.solution?.ammoId!==ammoId||!q.solution?.ok){const c=g.command(op.trackId,ammoId);if(!c.ok){gunB1ReserveManual(g,false);note('GUN_WITHHELD',c.reason,{mount:id,trackId:op.trackId});continue;}}
   const result=op.mode==='CONTINUOUS'?g.startContinuousFire(op.trackId,{mode:'MANUAL',ammoId}):g.requestFire(op.trackId,{mode:'MANUAL',ammoId});metrics.gunRequests++;if(op.mode==='CONTINUOUS'&&result.ok)metrics.continuousStarts++;
   if(!result.ok&&result.reason==='FEED_CYCLING')remaining.push(id);else gunB1ReserveManual(g,false);
   note('GUN_COMMAND',result.reason??null,{mount:id,trackId:op.trackId,action:'FIRE',ok:!!result.ok,fired:!!result.projectileId||result.fired===true,queued:!!result.queued,takeover:true});
  }
  op.pendingMounts=remaining;return remaining.length>0;
 }

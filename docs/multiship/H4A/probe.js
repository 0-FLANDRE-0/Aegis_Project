// DIAGNOSTIC_ONLY: test late invalidation of an existing naturally acquired
// pending capability. No target lookup, measurement creation or forced hit.
function localDefenseGuardProbeH4A(action){
  if(!['PROTECTED','STALE','UNCONFIRMED','FILE_REPLACED','CAPABILITY_CLONED','EXPIRED','HOLD','EMCON'].includes(action))return {ok:false,reason:'PROBE_ACTION_REQUIRED'};
  const p=[...defenseE.closeIn.values()].find(q=>q.command.authorityH4A),mount=ciws.find(m=>m.id===p?.mountId);
  if(!p||!mount)return {ok:false,reason:'NATURAL_LOCAL_CAPABILITY_REQUIRED'};
  const e=owner.weapons.executionD,file=p.localFileH4A,bank=c55Bank(mount),mode=defenseE.mode,emcon=observerC(owner).emcon,protectedIdentity=file.protectedIdentity,confirmed=file.confirmed,age=file.st.localAgeS,expires=p.expiresStep,entries=[...defenseE.closeIn],hold=e.closeInHoldD,
    before={ammo:mount.ammo,bullets:e.bullets.length,ram:e.ram.length,log:defenseE.closeInLog.length,rng:JSON.stringify(e.weaponRng)};
  let tested=p,result;
  try{
    // The diagnostic runs between full ticks; the real release runs before
    // the counter advances. Align that phase, then prove the unmodified
    // natural file/capability is admitted before testing a late invalidation.
    p.expiresStep=simStepCounter+1;
    const baseline=defenseLocalReleaseH4A(mount,p);
    if(!baseline.ok)return {ok:false,reason:'BASELINE_LOCAL_GATE_DENIED',baselineReason:baseline.reason};
    if(action==='PROTECTED')file.protectedIdentity='FRIEND';
    if(action==='STALE')file.st.localAgeS=CIWS_C55_POLICY.releaseFreshS;
    if(action==='UNCONFIRMED')file.confirmed=false;
    if(action==='FILE_REPLACED')bank.files.set(file.id,{...file});
    if(action==='CAPABILITY_CLONED')tested={...p,command:{...p.command}};
    if(action==='EXPIRED')p.expiresStep--;
    if(action==='HOLD')defenseE.mode='HOLD';
    if(action==='EMCON')observerC(owner).emcon=true;
    const gate=defenseLocalReleaseH4A(mount,tested);
    ownerCloseInOneTickE(owner,SIM_FIXED_DT,{defenseLocalReleaseH4A},tested);
    result={ok:true,action,baselineAdmitted:true,gate:{ok:gate.ok,reason:gate.reason},actualAmmoDelta:before.ammo-mount.ammo,actualProjectileDelta:e.bullets.length+e.ram.length-before.bullets-before.ram,actualLogDelta:defenseE.closeInLog.length-before.log,rngUnchanged:JSON.stringify(e.weaponRng)===before.rng};
  }finally{
    defenseE.mode=mode;observerC(owner).emcon=emcon;file.protectedIdentity=protectedIdentity;file.confirmed=confirmed;file.st.localAgeS=age;p.expiresStep=expires;bank.files.set(file.id,file);defenseE.closeIn.clear();for(const [id,q]of entries)defenseE.closeIn.set(id,q);e.closeInHoldD=hold;
  }
  return result;
}

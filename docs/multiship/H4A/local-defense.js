// LIVE_CANONICAL: inserted inside the existing foreign weapon-owner closure.
// Local RF files remain sensor-owned. This gate proves immediate measured
// self-defense; it does not invent a CMS file or change operator identity.
function defenseLocalMeasurementH4A(mount,id){
  const bad=reason=>({ok:false,reason});
  if(!ciws.includes(mount))return bad('OWNER_MOUNT_REQUIRED');
  if(emconActive||observerC(owner).emcon)return bad('EMCON_BLOCK');
  if(shipEquipmentOfflineV1()||getShipDamageEffects().ciwsPowerFac<=.15)return bad('SHIP_EQUIPMENT_OFFLINE');
  if(!ciwsB3Performance(mount).operational||ciwsMountStateM(mount).zM<=0)return bad('MOUNT_OFFLINE');
  const file=c55Bank(mount).files.get(id),st=file?.st;
  if(!Number.isInteger(id)||id>=0||!file||!file.confirmed||!st?.valid||!Number.isFinite(st.localAgeS)||st.localAgeS<0||st.localAgeS>=CIWS_C55_POLICY.releaseFreshS)return bad('LOCAL_MEASUREMENT_REQUIRED');
  if(file.protectedIdentity||file.ownFireEvidence)return bad('PROTECTED_LOCAL_CONTACT');
  const tr=file.cmsTrackId==null?null:tracks.get(file.cmsTrackId);
  if(tr&&(['FRIEND','NEUTRAL'].includes(tr.identity)||['FRIEND','NEUTRAL'].includes(normalizeTrackOperatorIdentityA3(tr._operatorIdentity))||['KILL_ASSESSMENT','DESTROYED','HARMLESS'].includes(tr.threatStatus)))return bad('PROTECTED_CMS_CONTACT');
  const audit=c55ContactAudit(mount,file);
  if(!audit.accepted||audit.reason!=='LOCAL_SELF_DEFENCE')return bad(audit.reason);
  return {ok:true,reason:'LOCAL_SELF_DEFENCE_H4A',file,st,audit};
}
function defenseLocalReleaseH4A(mount,p){
  const c=p?.command;
  if(defenseE.mode!=='AUTO'||engagementControlMode!=='AUTO')return {ok:false,reason:'AUTO_OFF'};
  if(!c?.automatic||c.authorityH4A!=='LOCAL_SELF_DEFENCE_H4A'||defenseE.closeIn.get(mount?.id)!==p||p.expiresStep!==simStepCounter+1)return {ok:false,reason:'LOCAL_CAPABILITY_REQUIRED'};
  const q=defenseLocalMeasurementH4A(mount,c.localIdH4A);
  if(q.ok&&(q.file!==p.localFileH4A||c.trackId!==q.file.id))return {ok:false,reason:'LOCAL_FILE_CHANGED'};
  return q;
}
function defenseLocalCuesH4A(){
  const rows=[];
  for(const mount of ciws)for(const file of c55Bank(mount).files.values()){
    const q=defenseLocalMeasurementH4A(mount,file.id);if(!q.ok)continue;
    const st=q.st,o=ciwsMountStateM(mount),kin=q.audit.row;
    rows.push({localId:file.id,mountId:mount.id,cmsTrackId:file.cmsTrackId,
      xM:o.xM+st.rxM,yM:o.yM+st.ryM,zM:o.zM+st.rzM,
      vxMps:o.vxMps+st.rvxMps,vyMps:o.vyMps+st.rvyMps,vzMps:o.vzMps+st.rvzMps,
      rangeM:kin.rangeM,closingMps:kin.closingSpd,cpaM:kin.cpaM,ttcS:kin.tti,
      positionSigmaM:Math.sqrt(Math.max(...st._c55P.map(p=>p[0]))),velocitySigmaMps:st.velocitySigmaMps,
      quality:st.quality,ageS:st.localAgeS,source:'LOCAL_RF'});
  }
  return rows;
}
function defenseDropMountH4A(mount){
  const previous=defenseE.closeIn.get(mount.id);defenseE.closeIn.delete(mount.id);
  if(previous&&owner.weapons.executionD.closeInPending?.mountId!==mount.id){mount.trackingTrackId=null;mount.cuedTarget=null;mount.tracking=false;mount.firing=false;mount.state='IDLE';}
}
function defenseCloseInE(){
  if(defenseE.mode!=='AUTO'){for(const mount of ciws)defenseDropMountH4A(mount);return;}
  const ranks=wip118ThreatRows().filter(th=>wip118ControlState.assessments.get(th.id)?.state==='THREAT'&&trackEngagementGateA3(th.id,{automatic:true,mode:'AUTO'}).ok);
  for(const mount of ciws){
    if(mount.ammo<=(mount.type==='RAM'?HARD_KILL_DOCTRINE.ramReserveRounds:0)){defenseDropMountH4A(mount);continue;}
    const bank=c55Bank(mount),rows=ranks.filter(th=>th.dKm<=mount.engageRangeKm&&th.dKm>=(mount.minEngageKm??.1)&&hardKillMountGeometry(mount,th.tr).ok&&[...bank.files.values()].some(q=>q.cmsTrackId===th.id&&q.confirmed&&q.audit?.accepted&&!q.protectedIdentity&&q.st.valid&&q.st.localAgeS<CIWS_C55_POLICY.releaseFreshS));
    const th=rows[0],pending=defenseE.closeIn.get(mount.id);
    let command,localFileH4A=null;
    if(th){
      if(mount.type==='RAM'&&hardKillExistingEngagementCounts(th.id).RAM>0){defenseDropMountH4A(mount);continue;}
      command={trackId:th.id,weapon:mount.type==='RAM'?'RAM':'PHALANX',mountId:mount.id,automatic:true,mode:'AUTO'};
    }else{
      const local=[...bank.files.values()].map(f=>defenseLocalMeasurementH4A(mount,f.id)).filter(q=>q.ok&&q.st.rangeM<=mount.engageRangeKm*1000&&q.st.rangeM>=(mount.minEngageKm??.1)*1000).sort((a,b)=>a.audit.row.score-b.audit.row.score||a.file.id-b.file.id)[0];
      if(!local){defenseDropMountH4A(mount);continue;}
      if(mount.type==='RAM'&&ramMissiles.some(m=>m.alive&&m.targetId===local.file.id)){defenseDropMountH4A(mount);continue;}
      localFileH4A=local.file;
      command={trackId:local.file.id,localIdH4A:local.file.id,authorityH4A:'LOCAL_SELF_DEFENCE_H4A',weapon:mount.type==='RAM'?'RAM':'PHALANX',mountId:mount.id,automatic:true,mode:'AUTO'};
    }
    defenseE.closeIn.set(mount.id,{command,localFileH4A,mountId:mount.id,expiresStep:simStepCounter+1,issuedStep:pending?.command.trackId===command.trackId?pending.issuedStep:simStepCounter});
    mount.trackingTrackId=command.trackId;mount.cuedTarget=command.trackId;
    if(localFileH4A){mount.tracking=true;mount.state='TRACK';}
  }
}

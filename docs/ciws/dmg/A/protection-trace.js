// Supplemental read-only causal observation. No data is written to a native file.
const cdNativeSweepProtection=c55SensorSweep,cdProtectionLast=new Map();
c55SensorSweep=function(m,b,dt){
 const q=cdNativeSweepProtection.apply(this,arguments);
 if(CD_A.active)for(const r of b.files.values()){
  const link=CIWS_C55_SENSOR_LINKS.get(r),data={mount:m.id,localId:r.id,proxyId:r.proxy?.id,sourceKey:link?.key??null,sourceOwn:!!link?.own,ownFireEvidence:!!r.ownFireEvidence,protectedIdentity:r.protectedIdentity??null,protectedCmsId:r.protectedCmsId??null,cmsTrackId:r.cmsTrackId??null,rangeM:r.st.rangeM,localAgeS:r.st.localAgeS};
  const key=m.id+':'+r.id,sign=JSON.stringify([data.sourceKey,data.ownFireEvidence,data.protectedIdentity,data.protectedCmsId,data.cmsTrackId]);
  if(cdProtectionLast.get(key)!==sign){cdProtectionLast.set(key,sign);cdEmit('PROTECTION_ASSOCIATION',data);}
 }
 return q;
};

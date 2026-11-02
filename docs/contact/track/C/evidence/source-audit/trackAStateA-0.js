function trackAStateA(tr){
 if(!tr)return null;
 const q=trackAFieldsA(tr,['trackId','trackNumber','sensorSource','sensorAge','sensorHits','confirmed','domain','classification','identity','threatStatus','engagementAuthority','memActive','trackLifecycle','ttl','_radar3dAirStepFC','_surface2DOnlyFC','_surfaceMotionPriorWip13B13']);
 q.stateM=trackANumbersA(tr._kfX,6);q.covariance=trackANumbersA(tr._kfP,36);
 if(tr.st){q.local=trackAFieldsA(tr.st,['rxM','ryM','rzM','rvxMps','rvyMps','rvzMps','localHits','localAgeS','quality','valid']);Object.assign(q,trackAFieldsA(tr,['id','ownFireEvidence','protectedIdentity','cmsTrackId','confirmed']));}
 return q;
}

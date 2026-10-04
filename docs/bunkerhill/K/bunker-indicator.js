// Display-only projections are authored offline from the same CG-52 geometry
// and neutral joint placement used by the 3D source renderer. Never read live
// WebGL vertices into physics or construct a second damage state for this view.
function bunkerDrawShipProjection(ctx,view,W,H,ox,oy,sx,sy){
  const q=BUNKER_2D_PROJECTION[view],key='CG52_SOURCE_2D_IMAGE:'+view;
  let image=WIP202_SHIP_DRAWING_CACHE.get(key);
  if(!image){image=new Image();image.onload=()=>drawShipDetail();image.src=q.image;WIP202_SHIP_DRAWING_CACHE.set(key,image);}
  if(!image.complete||!image.naturalWidth)return;
  const [x0,v0,x1,v1]=q.bounds;
  // Body +X is the bow: mirror the source bitmap horizontally so TOP and
  // SIDE both place the bow on the left, using the same damage coordinates.
  ctx.save();ctx.translate(ox-x0*sx,oy-v1*sy);ctx.scale(-(x1-x0)*sx/q.width,(v1-v0)*sy/q.height);
  ctx.drawImage(image,0,0);ctx.restore();
}
function bunkerShipSideClip(ctx,tx,scy,ssc){
  ctx.beginPath();for(const [x0,x1,z0,z1]of BUNKER_2D_PROJECTION.side.clipRects)
    ctx.rect(tx(x1),scy-z1*ssc,tx(x0)-tx(x1),(z1-z0)*ssc);
}
function bunkerIndicatorCriticalBoxes(){
  return buildShipHitBoxes().filter(q=>/^(COMBAT_CENTER|BOILER_|GEN_|ENGINE_|AMMO_|STEERING)/.test(q.system??''));
}
function bunkerIndicatorAudit(){
  if(!IS_BUNKER)return {schema:'AEGIS_SELECTED_SHIP_2D_INDICATOR_AUDIT_V1',profileId:ACTIVE_SHIP_PROFILE.id,
    projectionSchema:WIP202_SHIP_DRAWINGS.schema,legacyDdgProjection:true,physicsFeedback:false,pass:true};
  const q=BUNKER_2D_PROJECTION,g=ACTIVE_SHIP_PROFILE.geometry,scars=shipDamageVisualStateV1().scars,
    checks={profile:q.profileId===ACTIVE_SHIP_PROFILE.id,source:q.sourceHtmlSha256===BUNKER_REGISTRATION.sourceHtmlSha256,
      sourceTriangles:q.indexedSourceTriangles===740819,independentProjection:q.schema==='AEGIS_CG52_SOURCE_2D_PROJECTION_V1',
      topAndSideReady:['top','side'].every(k=>q[k].width>0&&q[k].height>0&&q[k].clipRects.length>0),
      sourceHullExtent:q.top.bounds[0]<=g.sternXM&&q.top.bounds[2]>=g.bowXM,
      readonly:q.physicsFeedback===false};
  return {schema:'AEGIS_SELECTED_SHIP_2D_INDICATOR_AUDIT_V1',profileId:ACTIVE_SHIP_PROFILE.id,
    projectionSchema:q.schema,checks,pass:Object.values(checks).every(Boolean),physicsFeedback:false,
    sourceHtmlSha256:q.sourceHtmlSha256,sourceTriangles:q.indexedSourceTriangles,
    imagesReady:['top','side'].map(view=>({view,ready:!!WIP202_SHIP_DRAWING_CACHE.get('CG52_SOURCE_2D_IMAGE:'+view)?.naturalWidth})),
    bounds:{top:q.top.bounds,side:q.side.bounds},criticalModules:bunkerIndicatorCriticalBoxes().map(b=>({name:b.name,x:b.oX,y:b.oY,hL:b.hL,hW:b.hW})),
    scars:scars.map(s=>({id:s.id,p:{...s.p},openingKind:s.openingKind})),
    overlays:{guns:ACTIVE_SHIP_PROFILE.weapons.gunMounts.map(gun=>({...ACTIVE_SHIP_PROFILE.geometry.hardpoints[gun.hardpointId],id:gun.id})),
      closeIn:ciws.map(m=>({id:m.id,name:m.moduleName,x:m.posOffsetM,y:ACTIVE_SHIP_PROFILE.geometry.hardpoints[m.installation.hardpointId].y})),
      illuminators:SPG62_ILLUMINATORS.map(i=>({id:i.id,name:i.moduleName,x:i.oX,y:i.oY,height:i.height}))}};
}
Object.assign(window.__NAVAL_SIM_DIAG__,{bunkerIndicatorAudit});

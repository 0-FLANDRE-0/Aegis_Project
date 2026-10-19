function harpoonDrawCicA(ctx,sym){
  const draft=harpoonRuntimeA().routeDraft;if(!draft.pointsM.length)return;
  const cfg=HARPOON_PROFILE_A.sim,origin={x:aircraft.x(),y:aircraft.y()},program=harpoonRouteProgramE(draft.pointsM,{x:worldToMeters(origin.x),y:worldToMeters(origin.y)});
  ctx.save();ctx.strokeStyle='#ffbf67';ctx.fillStyle='#ffda9a';ctx.lineWidth=tacticalLineWidthWorld(1.5,.42);ctx.setLineDash([7*sym,5*sym]);
  ctx.beginPath();ctx.moveTo(origin.x,origin.y);for(const p of draft.pointsM)ctx.lineTo(metersToWorld(p.x),metersToWorld(p.y));ctx.stroke();ctx.setLineDash([]);
  ctx.font=(10*sym)+'px monospace';ctx.textAlign='left';ctx.textBaseline='bottom';
  draft.pointsM.forEach((p,i)=>{const x=metersToWorld(p.x),y=metersToWorld(p.y);ctx.beginPath();ctx.arc(x,y,4*sym,0,Math.PI*2);ctx.stroke();ctx.fillText('H-WP'+(i+1)+(i===draft.pointsM.length-1?' · SEARCH':''),x+7*sym,y-5*sym);});
  if(program){const p=program.searchCenterM;ctx.globalAlpha=.45;ctx.setLineDash([4*sym,4*sym]);ctx.beginPath();ctx.arc(metersToWorld(p.x),metersToWorld(p.y),metersToWorld(cfg.seekerSearchBasketM),0,Math.PI*2);ctx.stroke();}
  ctx.restore();
}
function drawRescueRaftsCicK(){
  const rows=ENGAGEMENT_RUNTIME.world.entities.lifeRafts.filter(q=>q.ownerEntityId===ACTIVE_SHIP_RUNTIME.entityId);if(!rows.length)return;
  ctx.save();ctx.strokeStyle='#ffb458';ctx.fillStyle='#ffb458';ctx.lineWidth=tacticalLineWidthWorld(1.1,.5);
  const r=tacticalWorldPx(3,4,2.5,4),detail=currentTacticalViewKm()<=5;ctx.font=`${tacticalFontWorldSize(7,5)}px monospace`;ctx.textAlign='left';
  for(const q of rows){const x=metersToWorld(q.positionM.x),y=metersToWorld(q.positionM.y);ctx.beginPath();ctx.arc(x,y,r,0,TAU);ctx.stroke();
    ctx.beginPath();ctx.moveTo(x-r*.6,y);ctx.lineTo(x+r*.6,y);ctx.moveTo(x,y-r*.6);ctx.lineTo(x,y+r*.6);ctx.stroke();
    if(detail)ctx.fillText(`RAFT ${q.personIds.length}/${q.capacityPersons}`,x+r+2,y-r-2);
  }
  if(!detail){const x=rows.reduce((s,q)=>s+metersToWorld(q.positionM.x),0)/rows.length,y=rows.reduce((s,q)=>s+metersToWorld(q.positionM.y),0)/rows.length,people=rows.reduce((s,q)=>s+q.personIds.length,0);
    ctx.fillText(`RAFT ${rows.length} · ${people}명`,x+r+2,y-r-2);}
  ctx.restore();
}
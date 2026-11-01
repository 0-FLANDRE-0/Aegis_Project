// Presentation only: measured native single-shot curve; never a release gate.
function gunB2EffectiveRing(){
 if(!Object.values(gunB2Flags).every(Boolean))return null;
 return GUN_B2_RANGE_TABLE.profiles?.[ACTIVE_SHIP_PROFILE.id]?.proposal??null;
}
function gunB2DrawEffectiveRing(context,view){
 const q=gunB2EffectiveRing();if(!q)return;const z=mapZoom,own=mapOwnShipA(),r=view.rect,c=worldToScreen(own.x,own.y,view),km=q.rangeKm;
 if(Number.isFinite(km)&&km>0){context.strokeStyle='#79dfa4';context.setLineDash([8/z,4/z]);context.beginPath();context.arc(own.x,own.y,kmToWorld(km),0,Math.PI*2);context.stroke();}
 const label=Number.isFinite(km)?'대공 유효 '+(q.rightCensored?'≥':'')+km+'km (SIM)':'대공 유효 미확정 (SIM)',p=screenToWorld(r.x+r.w-8,window.__MAP_C__.labelBase(view)+44,view);
 context.fillStyle='#79dfa4';context.textAlign='right';context.fillText(label,p.x,p.y);
}

function drawNetworkPictureG(){
  const r=ACTIVE_SHIP_RUNTIME,n=r.combatSystem.networkG;if(!n)return;const now=networkNowG();
  ctx.save();ctx.font=`${tacticalFontWorldSize(8,5)}px monospace`;ctx.lineWidth=tacticalLineWidthWorld(1.1,.45);ctx.textAlign='left';
  for(const q of networkPictureG(r)){
    if(q.localTrackId!==null||!q.positionM)continue;const x=metersToWorld(q.positionM.x),y=metersToWorld(q.positionM.y),friend=q.identity==='FRIEND',color=q.coasting?'rgba(145,165,180,.55)':friend?'rgba(90,220,245,.86)':'rgba(170,165,255,.86)',size=tacticalWorldPx(5,10,3,10);
    ctx.strokeStyle=color;ctx.fillStyle=color;ctx.setLineDash(q.coasting?[3,4]:[4,2]);ctx.strokeRect(x-size,y-size,size*2,size*2);ctx.setLineDash([]);
    const label=(friend?'ALLY':'NET '+q.id)+' '+q.ageS.toFixed(1)+'s'+(q.coasting?' COAST':' · 공유만');ctx.fillText(label,x+size+2,y-size-2);
    if(q.covariance){const rx=metersToWorld(2*Math.sqrt(q.covariance[0])),ry=metersToWorld(2*Math.sqrt(q.covariance[7]));if(rx>1&&ry>1){ctx.globalAlpha=.25;ctx.beginPath();ctx.ellipse(x,y,rx,ry,0,0,TAU);ctx.stroke();ctx.globalAlpha=1;}}
  }ctx.restore();
}
function tacticalViewportWorldBounds(rw,rh){
    const v=AEGIS_VIEWPORT.twoD,a=screenToWorld(v.x,v.y),b=screenToWorld(v.x+v.w,v.y+v.h);return {minX:a.x,maxX:b.x,minY:a.y,maxY:b.y};
  }
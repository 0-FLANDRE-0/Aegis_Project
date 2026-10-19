function drawTerrainChartLayer(ctx){
    for(const isl of terrainIslands){
      if(!isl.points?.length) continue;
      const prof=ensureTerrainChartProfile(isl);
      // very faint land tint so the player reads charted land, not literal terrain fill
      ctx.beginPath();
      ctx.moveTo(isl.points[0].x, isl.points[0].y);
      for(let i=1;i<isl.points.length;i++) ctx.lineTo(isl.points[i].x, isl.points[i].y);
      ctx.closePath();
      ctx.fillStyle = isl.kind==='MAJOR_LANDMASS' ? 'rgba(112,124,96,0.085)' : 'rgba(112,124,96,0.06)';
      ctx.fill();
      ctx.strokeStyle = 'rgba(184,210,176,0.62)';
      ctx.lineWidth = tacticalLineWidthWorld(1.15,0.45);
      ctx.stroke();

      // Relief-driven contours from marching-squares segments of the actual terrain field.
      if(mapZoom>0.24 && prof.contours?.length){
        const n=prof.contours.length;
        for(let li=0; li<n; li++){
          const contour=prof.contours[li], level=contour.level, segments=contour.segments;
          if(!segments?.length) continue;
          const t=(li+1)/(n+1);
          const alpha=(mapZoom>0.7?0.34:0.22) * (1-0.35*t);
          ctx.beginPath();
          for(const seg of segments){ctx.moveTo(seg.a.x,seg.a.y);ctx.lineTo(seg.b.x,seg.b.y);}
          ctx.strokeStyle = `rgba(165,196,155,${alpha.toFixed(3)})`;
          ctx.lineWidth = tacticalLineWidthWorld(li===n-1?0.9:0.7,0.30);
          ctx.lineJoin='round';ctx.lineCap='round';
          ctx.stroke();
          if(mapZoom>0.75 && (li===0 || li===n-1 || (n>4 && li===Math.floor(n*0.5)))){
            const seg=segments[(li*7+Math.floor(segments.length*0.23))%segments.length];
            const lx=(seg.a.x+seg.b.x)*0.5,ly=(seg.a.y+seg.b.y)*0.5;
            ctx.font=`${tacticalFontWorldSize(6,4)}px monospace`;
            ctx.fillStyle=`rgba(188,214,178,${Math.min(0.42,alpha+0.08).toFixed(3)})`;
            ctx.textAlign='left';
            ctx.fillText(String(level),lx+3,ly-1);
          }
        }
      }

      if(mapZoom>0.42 && prof.peaks.length){
        ctx.font=`${tacticalFontWorldSize(7,4)}px monospace`;
        ctx.fillStyle='rgba(205,228,196,0.48)';
        ctx.textAlign='center';
        for(const pk of prof.peaks){
          ctx.fillText('△', pk.x, pk.y+2);
          if(mapZoom>0.68) ctx.fillText(String(pk.h), pk.x, pk.y-4);
        }
      }

      if(mapZoom>0.95){
        ctx.font=`${tacticalFontWorldSize(6,4)}px monospace`;
        ctx.fillStyle='rgba(190,212,180,0.30)';
        ctx.textAlign='center';
        const label = isl.kind==='MAJOR_LANDMASS' ? `${isl.id} △${Math.round(isl.heightM)}m` : `${isl.id}`;
        ctx.fillText(label, isl.cx, isl.cy);
      }
    }
  }
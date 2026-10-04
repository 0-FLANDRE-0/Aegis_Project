"""Checked E fixes: selected-source 2D drawing and rough-sea clutter regression."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
def refine_e(s):
    def patch(a,b,count=1):
        nonlocal s
        n=s.count(a)
        if n!=count:raise RuntimeError(f'E patch context expected {count}, got {n}: {a[:120]}')
        s=s.replace(a,b)
    patch('let BUNKER_RENDER_META=null,BUNKER_RENDER_BUFFER=null,BUNKER_RENDER_COMPONENTS=null;',
          'let BUNKER_RENDER_META=null,BUNKER_RENDER_BUFFER=null,BUNKER_RENDER_COMPONENTS=null,BUNKER_2D_PROJECTION=null;')
    patch("BUNKER_RENDER_COMPONENTS=await readBunkerAsset('cg52-components');",
          "BUNKER_RENDER_COMPONENTS=await readBunkerAsset('cg52-components');BUNKER_2D_PROJECTION=deepFreezeShipProfileV48Wip09(await readBunkerAsset('cg52-projection'));")
    patch('function wip202DrawShipProjection(ctx,view,W,H,ox,oy,sx,sy){',
          'function wip202DrawShipProjection(ctx,view,W,H,ox,oy,sx,sy){if(IS_BUNKER)return bunkerDrawShipProjection(ctx,view,W,H,ox,oy,sx,sy);')
    patch('function wip202ShipSideClip(c,tx,scy,ssc){',
          'function wip202ShipSideClip(c,tx,scy,ssc){if(IS_BUNKER)return bunkerShipSideClip(c,tx,scy,ssc);')
    patch('const sc = 1.8;', 'const sc = IS_BUNKER?Math.min(1.8,(W-20)/ACTIVE_SHIP_PROFILE.geometry.lengthM):1.8;')
    patch('const criticalDmg = [', 'const criticalDmg = IS_BUNKER?bunkerIndicatorCriticalBoxes():[')
    patch('c.strokeRect(x1 + 1, ty(7) + 1, ic.hL*2*sc - 2, 14*sc - 2);',
          'c.strokeRect(x1 + 1, ty(IS_BUNKER?(ic.oY??0)+(ic.hW??7):7) + 1, ic.hL*2*sc - 2, (IS_BUNKER?(ic.hW??7)*2*sc:14*sc) - 2);')
    patch('c.fillRect(x1, ty(7), ic.hL*2*sc, 14*sc);',
          'c.fillRect(x1, ty(IS_BUNKER?(ic.oY??0)+(ic.hW??7):7), ic.hL*2*sc, IS_BUNKER?(ic.hW??7)*2*sc:14*sc);')
    patch('  completeShipStartup();',(HERE/'bunker-indicator.js').read_text()+'\n  completeShipStartup();')
    return s

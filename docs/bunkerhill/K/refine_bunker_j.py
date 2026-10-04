"""Exact CG-52 VLS addresses and installed-cell exhaust-module membership."""
def refine_j(source):
    s=source
    def replace(old,new):
        nonlocal s
        if s.count(old)!=1:raise RuntimeError('J patch context: '+old[:100])
        s=s.replace(old,new)
    replace(""" const sec=meta.section==='aft'?'aft':'fwd',r=Math.max(0,Math.min(sec==='aft'?7:3,Number(meta.row)||0)),col=Math.max(0,Math.min(7,Number(meta.col)||0));
 const c=shipCellRegistration(sec,r,col);let x=c.x,y=c.y;""", """ const sec=meta.section==='aft'?'aft':'fwd';
 // CG-52 has eight physical rows in BOTH banks and three crane gaps per bank.
 // A valid address is never clamped or relocated to a different installed cell.
 // Keep the DDG compatibility normalization exactly as before.
 const r=IS_BUNKER?Number(meta.row):Math.max(0,Math.min(sec==='aft'?7:3,Number(meta.row)||0)),col=IS_BUNKER?Number(meta.col):Math.max(0,Math.min(7,Number(meta.col)||0));
 const c=Number.isInteger(r)&&Number.isInteger(col)?shipCellRegistration(sec,r,col):null;
 if(!c)throw Error('VLS_UNINSTALLED_SLOT:'+sec+':'+r+':'+col);
 let x=c.x,y=c.y;""")
    replace("""      for(const r of [pr,pr+1])for(let c=c0;c<c0+4;c++){const L=wip148VlsCellLocal({section:m.section,row:r,col:c});ux+=L.xM;uy+=L.zM;uz+=L.deckM;n++;}
      e.ub={x:ux/n,y:uy/n,z:uz/n+.12};}""", """      for(const r of [pr,pr+1])for(let c=c0;c<c0+4;c++){
        // CG-52 crane positions have no launch-cell registration. The existing
        // SIM-TUNED module-centre effect averages only installed neighbours.
        if(IS_BUNKER&&!shipCellRegistration(m.section==='aft'?'aft':'fwd',r,c))continue;
        const L=wip148VlsCellLocal({section:m.section,row:r,col:c});ux+=L.xM;uy+=L.zM;uz+=L.deckM;n++;
      }
      if(!n)throw Error('VLS_UPTAKE_NO_INSTALLED_CELLS');
      e.ub={x:ux/n,y:uy/n,z:uz/n+.12};}""")
    return s

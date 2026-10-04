"""Checked patches for native 3D continuity and stable installation slots."""
from pathlib import Path
HERE=Path(__file__).resolve().parent

def refine_g(s):
    def patch(a,b,count=1):
        nonlocal s
        n=s.count(a)
        if n!=count:raise RuntimeError(f'G patch context expected {count}, got {n}: {a[:120]}')
        s=s.replace(a,b)
    gate='''// WIP16B: finish mandatory aperture geometry before another expensive WebGL draw.
      // Preserve the previous canvas while this cooperative job advances. Simulation ticks continue.
      const openingPending=!!this._damageJobV3&&this._damageQuickV11&&(st.shipDamageVisual?.scars??[]).some(s=>(s.impactRole==='ENTRY'||s.impactRole==='EXIT')&&s.hole&&s.sealed<=.9&&!this.damageScarVisuals?.get(s.id)?.group?.userData.actualHole);
      if(openingPending)this._wip16bOpeningDrawDeferrals=(this._wip16bOpeningDrawDeferrals||0)+1;
      else this.renderer.render(this.scene,this.camera);'''
    patch(gate,'''// Display the last committed surfaces while cooperative cutting advances.
      // buildDamageScarsV3 publishes its completed geometry atomically, so a
      // pending aperture never needs to hold the camera, ocean or scene canvas.
      this.renderer.render(this.scene,this.camera);''')
    patch('while(steps<256&&performance.now()-start<c12Limit)', 'while(steps<8192&&performance.now()-start<c12Limit)')
    # Layout revision migration runs only on a detached, fully preflighted clone.
    patch('Object.freeze([ACTIVE_SHIP_PROFILE.revision])', "Object.freeze(IS_BUNKER?[ACTIVE_SHIP_PROFILE.revision,'BUNKERHILL_LATE_D_1']:[ACTIVE_SHIP_PROFILE.revision])")
    patch("const validation={schema:'AEGIS_OPERATIONAL_PREFLIGHT_V48_WIP11B',ok:errors.length===0,errors,codecs};return {validation,source:validation.ok?src:null};",
      """const migrations=[];if(errors.length===0&&IS_BUNKER){try{const migration=migrateBunkerOperationalInteriorG(src);if(migration)migrations.push(migration);}catch(_err){operationalErrorV48Wip11B(errors,'CG52_INTERIOR_MIGRATION');}}
    const validation={schema:'AEGIS_OPERATIONAL_PREFLIGHT_V48_WIP11B',ok:errors.length===0,errors,codecs,...(migrations.length?{migrations}:{})};return {validation,source:validation.ok?src:null};""")
    patch('  function wip125LoadoutSnapshot(){', '''  function wip125InstallationSlot(section,index){
    const cfg=ACTIVE_SHIP_PROFILE.weapons.vls.sections[section];
    if(!cfg||!Number.isInteger(index)||index<0||index>=cfg.cells)return null;
    return cfg.cellLayout?.[index]??{row:Math.floor(index/cfg.cols),col:index%cfg.cols};
  }
  function wip125MakeInstalledCell(section,index,type){
    const slot=wip125InstallationSlot(section,index);if(!slot)throw Error('VLS_INSTALLATION_INDEX:'+section+':'+index);
    return wip125MakeVlsCell(type,slot.row,slot.col);
  }
  function wip125LoadoutSnapshot(){''')
    patch("row:Math.floor(i/8),col:i%8,essmCount:c.type==='ESSM4'?", "row:wip125InstallationSlot(sec,i).row,col:wip125InstallationSlot(sec,i).col,essmCount:c.type==='ESSM4'?")
    patch("cells[i]={type,row:Math.floor(i/8),col:i%8,essmCount:type==='ESSM4'?4:0,destroyed:false};", "cells[i]=wip125MakeInstalledCell(section,i,type);")
    patch("const n=String(name??'STANDARD').toUpperCase();", "const n=String(name??'STANDARD').toUpperCase();if(!['STANDARD','LONG','CLOSE','DISTRIBUTED','ER_TEST','SM6_TEST'].includes(n))return false;")
    patch("wip125MakeVlsCell(type,Math.floor(i/8),i%8)", "wip125MakeInstalledCell(sec,i,type)")
    patch("const markEssm=(sec,idxs)=>{for(const i of idxs)vlsCells[sec][i]=wip125MakeVlsCell('ESSM4',Math.floor(i/8),i%8);};", "const markEssm=(sec,idxs)=>{for(const i of idxs)vlsCells[sec][i]=wip125MakeInstalledCell(sec,i,'ESSM4');};")
    patch("Array.from({length:24},(_,k)=>40+k)", "Array.from({length:24},(_,k)=>vlsCells.aft.length-24+k)")
    patch("Array.from({length:12},(_,k)=>52+k)", "Array.from({length:12},(_,k)=>vlsCells.aft.length-12+k)")
    patch("Array.from({length:16},(_,k)=>16+k)", "Array.from({length:16},(_,k)=>vlsCells.fwd.length-16+k)")
    patch("Array.from({length:32},(_,k)=>32+k)", "Array.from({length:32},(_,k)=>vlsCells.aft.length-32+k)")
    patch('wip125EvenIndices(32,12)','wip125EvenIndices(vlsCells.fwd.length,12)')
    patch('wip125EvenIndices(64,12)','wip125EvenIndices(vlsCells.aft.length,12)')
    patch('wip125EvenIndices(32,8)','wip125EvenIndices(vlsCells.fwd.length,8)',2)
    patch('wip125EvenIndices(64,16)','wip125EvenIndices(vlsCells.aft.length,16)',2)
    for kind in ['SM2ER','SM6']:
        patch(f"wip125MakeVlsCell('{kind}',Math.floor(i/8),i%8);for",f"wip125MakeInstalledCell('fwd',i,'{kind}');for")
        patch(f"wip125MakeVlsCell('{kind}',Math.floor(i/8),i%8);markEssm",f"wip125MakeInstalledCell('aft',i,'{kind}');markEssm")
    patch("Array.from({length:16},(_,k)=>48+k)","Array.from({length:16},(_,k)=>vlsCells.aft.length-16+k)",2)
    patch("if(IS_BUNKER){b.style.gridRowStart=c.row+1;b.style.gridColumnStart=c.col+1;}grid.appendChild(b);", "if(IS_BUNKER){const slot=wip125InstallationSlot(sec,i);b.style.gridRowStart=slot.row+1;b.style.gridColumnStart=slot.col+1;}grid.appendChild(b);")
    # A missing physical slot is distinct from an installed cell painted EMPTY.
    patch("grid.appendChild(b);}}", """grid.appendChild(b);}if(IS_BUNKER){const cfg=ACTIVE_SHIP_PROFILE.weapons.vls.sections[sec],installed=new Set(cfg.cellLayout.map(q=>q.row+':'+q.col));
      for(let row=0;row<cfg.rows;row++)for(let col=0;col<cfg.cols;col++)if(!installed.has(row+':'+col)){
        const gap=document.createElement('span');gap.className='wip125-slot-gap';gap.dataset.section=sec;gap.dataset.row=row;gap.dataset.col=col;
        gap.title=`${sec==='fwd'?'전방':'후방'} R${row+1} C${col+1} · 미장착`;gap.setAttribute('aria-label',gap.title);gap.textContent='—';
        gap.style.cssText=`grid-row:${row+1};grid-column:${col+1};width:26px;height:26px;box-sizing:border-box;display:grid;place-items:center;color:#53616a;border:1px dashed #35434b;background:#10191f;font:10px monospace;pointer-events:none;`;
        grid.appendChild(gap);}}}""")
    patch('  completeShipStartup();',(HERE/'bunker-detail-audit.js').read_text()+'\n  completeShipStartup();')
    return s

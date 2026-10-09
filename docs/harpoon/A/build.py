"""Reproducible Harpoon candidate from the approved Bunker Hill K artifact.

During development use --out /workspace/aegis-harpoon-a-work/experimental.html.
The approved K HTML and records 0..12 remain byte-identical.
"""
import argparse, base64, gzip, hashlib, json, re
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
BASE=ROOT/'archive/v48/WIP_BUNKERHILL_K/Aegis_SIM_v48_WIP_BUNKERHILL_K.html'
if not BASE.is_file():BASE=ROOT/'Aegis_SIM_v48_WIP_BUNKERHILL_K.html'
BASE_SHA='efe1a0994f172da878733023826e9383ed0aed3c8c9601d10177a5d9faf287df'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    raw=BASE.read_bytes();assert hashlib.sha256(raw).hexdigest()==BASE_SHA
    html=raw.decode();match=re.search(r'<script type="application/octet-stream" data-c55-index="13">(.*?)</script>',html,re.S)
    js=gzip.decompress(base64.b64decode(match[1])).decode()
    def patch(old,new,count=1):
        nonlocal js
        assert js.count(old)==count,(old[:90],js.count(old),count)
        js=js.replace(old,new)
    patch('function makeBunkerShipProfile(){',(HERE/'profile.js').read_text()+'\nfunction makeBunkerShipProfile(){')
    patch("revision:'BUNKERHILL_LATE_G_1'","revision:'BUNKERHILL_HARPOON_A_1'")
    patch("['ordnance.misc','ORDNANCE_FIXED',6600,{x:0,y:0,z:3}]","['ordnance.misc','ORDNANCE_FIXED',1080,{x:0,y:0,z:3}]")
    patch('  return deepFreezeShipProfileV48Wip09(p);\n}\nconst CG_52_LATE_TICONDEROGA_PROFILE',
          "  p.weapons.harpoon=harpoonInstallationA();p.equipment.harpoon={moduleId:HARPOON_PROFILE_A.id,launchers:['A','B'],tubes:8};\n"
          "  for(const bank of ['A','B']){const rows=p.weapons.harpoon.tubes.filter(t=>t.bank===bank),avg=k=>rows.reduce((s,t)=>s+t.massCenterM[k],0)/rows.length;hp['harpoon'+bank]={name:'Mk 141('+bank+')',x:avg('x'),y:avg('y'),z:avg('z'),hL:1.1,hW:2.8,hH:2.1};}\n"
          '  return deepFreezeShipProfileV48Wip09(p);\n}\nconst CG_52_LATE_TICONDEROGA_PROFILE')
    patch("weapons:{mainGun:null,vls:null,closeIn:null,magazines:null,", "weapons:{harpoon:createHarpoonLauncherRuntimeA(profile),mainGun:null,vls:null,closeIn:null,magazines:null,")
    patch("world:{frame:WIP14A_WORLD_FRAME,entities:{aircraft:null", "world:{antiShipSerial:0,frame:WIP14A_WORLD_FRAME,entities:{antiShipOrdnance:[],harpoonBoosters:[],aircraft:null")
    patch("['mastAft','MAST_AFT'],['flightDeck','FLIGHT_DECK']", "['mastAft','MAST_AFT'],['flightDeck','FLIGHT_DECK'],['harpoonA','HARPOON_A'],['harpoonB','HARPOON_B']")
    patch('  out.push(...skExtraMassNodes15B(make));',"  for(const tube of harpoonRuntimeA().tubes)if(tube.loaded)out.push(make('harpoon.'+tube.id,'ORDNANCE_DYNAMIC',HARPOON_PROFILE_A.public.launchMassKg,harpoonTubeSpecA(tube.id).massCenterM,'PUBLIC_MASS_SOURCE_MESH_POSITION'));\n  out.push(...skExtraMassNodes15B(make));")
    patch('  function resetEngagementTransientV48Wip11A(){','  function resetEngagementTransientV48Wip11A(){\n    harpoonResetA(false);')
    patch('  function resetEntireSessionV48Wip11A(){','  function resetEntireSessionV48Wip11A(){\n    harpoonResetA(true);')
    patch('    updateSurfaceContacts(dt);\n', "    updateSurfaceContacts(dt);\n    SIM_SUBSYSTEM_PROFILER_V48_WIP11A.phase(_wip11aProfileTick,'harpoon');\n    harpoonStepA(dt);\n    SIM_SUBSYSTEM_PROFILER_V48_WIP11A.phase(_wip11aProfileTick,'sensors_tracks_ew');\n")
    # Outbound missiles join the physical RF pool; source IDs never cross measurement adapters.
    patch("    for(const [rows,prefix] of [[getOwnChaffRadarReturns()", "    for(const m of harpoonWorldA()){if(!m.alive||m===exclude)continue;const id='HARPOON:'+m.id;push({rfId:id,x:m.x,y:m.y,z:m.z,vx:m.vx,vy:m.vy,vz:m.vz,rcsM2:m.rcsM2,extentRangeM:1.9,extentCrossM:.45,extentVerticalM:.18,dopplerSpreadMps:1,_sourceSeed:rfSeedWip13A2(id),_truthObject:m,_physicsKind:'RF_ORDNANCE',_debugSourceKind:'RF_OBJECT',_debugSourceId:id});}\n    for(const [rows,prefix] of [[getOwnChaffRadarReturns()")
    patch('  function wip13cUpdateMissileControlLabels(){','  function wip13cUpdateMissileControlLabels(){\n    harpoonUpdateUIA();')
    patch("  bindPress(document.getElementById('debugSpawnKh35Btn')", "  harpoonBindUIA();\n  bindPress(document.getElementById('debugSpawnKh35Btn')")
    patch("IS_BUNKER?[ACTIVE_SHIP_PROFILE.revision,'BUNKERHILL_LATE_D_1']", "IS_BUNKER?[ACTIVE_SHIP_PROFILE.revision,'BUNKERHILL_LATE_G_1','BUNKERHILL_LATE_D_1']")
    patch('inventory:{vls:jsonSafeCloneV48Wip11A(vlsCells)', 'inventory:{harpoon:harpoonExportA(),vls:jsonSafeCloneV48Wip11A(vlsCells)')
    patch('    mk36ValidateSnapshotWip15A(inventory,ctx,errors);','    harpoonValidateA(inventory,errors);mk36ValidateSnapshotWip15A(inventory,ctx,errors);')
    patch('    const errors=[],codecs=[];let ctx;',
          "    const harpoonMigrations=[];if(IS_BUNKER&&['BUNKERHILL_LATE_G_1','BUNKERHILL_LATE_D_1'].includes(src.profileRevision)&&src.ship?.inventory&&!('harpoon' in src.ship.inventory)){src.ship.inventory.harpoon={schema:'MK141_INVENTORY_A1',selectedTubeId:harpoonRuntimeA().tubes[0].id,tubes:harpoonRuntimeA().tubes.map(t=>({id:t.id,loaded:true}))};harpoonMigrations.push({id:'LEGACY_CG52_MK141_INITIAL_LOAD_A1',policy:'EXPLICIT_EIGHT_ROUNDS_OLD_SCHEMA_HAD_NO_HARPOON_INVENTORY'});}\n    const errors=[],codecs=[];let ctx;")
    patch('    const migrations=[];if(errors.length===0&&IS_BUNKER)', '    const migrations=[...harpoonMigrations];if(errors.length===0&&IS_BUNKER)')
    patch('    mk36RestoreSnapshotWip15A(src.ship.inventory.mk36);','    harpoonRestoreA(src.ship.inventory.harpoon);mk36RestoreSnapshotWip15A(src.ship.inventory.mk36);')
    patch('world:{ships:[...ENGAGEMENT_RUNTIME.ships.keys()]','world:{harpoonIds:harpoonWorldA().map(m=>m.id),harpoonBoosterIds:harpoonBoostersA().map(b=>b.id),harpoonPending:harpoonCopyA(harpoonRuntimeA().pending),harpoonSerial:ENGAGEMENT_RUNTIME.world.antiShipSerial,ships:[...ENGAGEMENT_RUNTIME.ships.keys()]')
    patch('return {lifeRafts:ENGAGEMENT_RUNTIME.world.entities.lifeRafts.length','return {harpoons:harpoonWorldA().filter(m=>m.alive).length,harpoonBoosters:harpoonBoostersA().length,lifeRafts:ENGAGEMENT_RUNTIME.world.entities.lifeRafts.length')
    patch('checks={runtimeSchema:r.schema', "checks={harpoonOwned:r.weapons.harpoon?.schema==='MK141_RUNTIME_A1'&&Array.isArray(e.world.entities.antiShipOrdnance)&&Array.isArray(e.world.entities.harpoonBoosters),runtimeSchema:r.schema")
    patch('  function get3DRenderState(){',(HERE/'core.js').read_text()+'\n  function get3DRenderState(){')
    patch('    window.__CORE_SELFTEST_FAILURES__=failures.slice();', "    try{const audit=harpoonCoreAuditA();if(!audit.pass)failures.push('HARPOON_A '+JSON.stringify(audit.checks));}catch(e){failures.push('HARPOON_A '+String(e));}\n    window.__CORE_SELFTEST_FAILURES__=failures.slice();")
    patch('    // missiles\n    for(const m of missiles){','    // missiles\n    harpoonDrawCicA(ctx,sym);\n    for(const m of missiles){')
    patch("      enemyAsms:enemyMissiles.filter", "      harpoons:harpoonRenderStatesA(),harpoonBoosters:harpoonBoosterRenderStatesA(),harpoonInventory:{tubes:harpoonRuntimeA().tubes.map(t=>({...t}))},\n      enemyAsms:enemyMissiles.filter")
    patch('  window.get3DRenderState=get3DRenderState;', '  window.get3DRenderState=get3DRenderState;\n  window.__HARPOON_DIAG_A__=harpoonDiagnosticsA();')
    patch('function installBunkerRenderer(view){',(HERE/'renderer.js').read_text()+'\nfunction installBunkerRenderer(view){')
    patch("      let o=mesh(stat.meshes[i],`CG52_${stat.cat}_${i}`,stat.cat);", "      let o=mesh(stat.meshes[i],`CG52_${stat.cat}_${i}`,stat.cat);\n      if(stat.cat==='weapons'&&i===1)harpoonDetachSourceCapsA(T,o,root,this);")
    patch('installBunkerRenderer(WIP148_EXTERNAL_3D);','installBunkerRenderer(WIP148_EXTERNAL_3D);\ninstallHarpoonRendererA(WIP148_EXTERNAL_3D);')
    # Make Harpoon available to existing camera follow/status without entering SAM visual builders.
    patch("...(st?.missiles??[]).filter(q=>!q.dead)", "...[...(st?.missiles??[]),...(st?.harpoons??[])].filter(q=>!q.dead)")
    patch("arr=(st.missiles??[]).filter(m=>!m.dead)", "arr=[...(st.missiles??[]),...(st.harpoons??[])].filter(m=>!m.dead)")
    patch("visualForFollowKey(key){if(!key)return null;", "visualForFollowKey(key){if(!key)return null;if(String(key).startsWith('HARPOON:'))return this.harpoonVisualsA?.get(String(key).slice(8))??null;")
    patch("for(const ms of st?.missiles??[])", "for(const ms of [...(st?.missiles??[]),...(st?.harpoons??[])])")
    main_bytes=js.encode();packed=gzip.compress(main_bytes,9,mtime=0)
    match=re.search(r'<script type="application/octet-stream" data-c55-index="13">(.*?)</script>',html,re.S)
    html=html[:match.start(1)]+base64.b64encode(packed).decode()+html[match.end(1):]
    match=re.search(r'const records=(\[.*?\]);',html,re.S);records=json.loads(match[1]);records[13].update(rawBytes=len(main_bytes),gzipBytes=len(packed),sha256=hashlib.sha256(main_bytes).hexdigest())
    html=html[:match.start(1)]+json.dumps(records,separators=(',',':'))+html[match.end(1):]
    assets=[('harpoon-launch-registration','launcher-registration.json',True),('harpoon-model-meta','model-meta.json',True),('harpoon-model-geo','model-geo.gz',False)]
    asset_tags=[]
    for id,name,is_json in assets:
        data=(HERE/name).read_bytes();gz=gzip.compress(data,9,mtime=0)if is_json else data
        asset_tags.append('<script id="'+id+'" type="application/octet-stream">'+base64.b64encode(gz).decode()+'</script>')
    html=html.replace('<script id="cg52-registration"', '\n'.join(asset_tags)+'\n<script id="cg52-registration"',1)
    assert 'id="harpoon-model-meta"' in html
    controls='''<div id="harpoonControlsA" hidden style="margin-top:4px">
          <div class="control-deck-heading">MK 141 / HARPOON</div>
          <div class="control-deck-grid"><select id="harpoonTubeA" aria-label="하푼 발사관" style="min-width:0;background:#07161f;color:#80d8d2;border:1px solid #28505a;font:inherit"></select><button id="harpoonFireA" class="wep-btn fire">HARPOON FIRE</button></div>
          <div id="harpoonStatusA" class="control-deck-note" role="status" style="overflow-wrap:anywhere">INS → ARH</div>
          <a href="https://sketchfab.com/3d-models/missiles-37899978144a45d0bd03c3538957b145" target="_blank" rel="noopener" class="control-deck-note" style="font-size:6px;color:#6ba29f" title="Missiles by Civorsky, CC BY 4.0; 날개·꼬리날개 분리, 날개폭·재질 수정. https://creativecommons.org/licenses/by/4.0/">MODEL · Civorsky · CC BY 4.0</a>
        </div>'''
    anchor='<button class="wep-btn fire control-deck-fire" id="fireBtn">SM-2 FIRE</button>'
    assert html.count(anchor)==1;html=html.replace(anchor,anchor+'\n        '+controls)
    html=html.replace('V48_WIP_BUNKERHILL_K','V48_WIP_HARPOON_A').replace('WIP BUNKERHILL K','WIP HARPOON A')
    args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(html)
    (args.out.parent/'harpoon-main.js').write_bytes(main_bytes)
    print(json.dumps(dict(output=str(args.out),bytes=args.out.stat().st_size,sha256=hashlib.sha256(args.out.read_bytes()).hexdigest(),mainSha256=hashlib.sha256(main_bytes).hexdigest())))

if __name__=='__main__':main()

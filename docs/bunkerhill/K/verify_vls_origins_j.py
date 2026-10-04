"""Independent source-cell checks, physical release and sparse C17 effects."""
from pathlib import Path
import argparse,hashlib,json
from playwright.sync_api import sync_playwright
from browser_i import launch,load,served_bytes
p=argparse.ArgumentParser();p.add_argument('html');p.add_argument('out');p.add_argument('--baseline-i');a=p.parse_args()
out=Path(a.out);out.mkdir(parents=True,exist_ok=True);errors=[];checks={};details={}
registration=json.loads((Path(__file__).resolve().parent/'registration.json').read_text())
inspect='''R=>{const d=window.__NAVAL_SIM_DIAG__,f=window.__WIP148_VISUAL_DIAG__,v=window.__WIP148_3D_VIEW__,fingerprint=()=>JSON.stringify(d.operationalImportMutationFingerprintV48Wip11B()),before=fingerprint(),rows=[],gaps=[];
 const distance=(a,b)=>Math.hypot(a.x-b.x,a.y-b.y,a.z-b.z);let id=770000;
 for(const section of ['fwd','aft'])for(const cell of R.cells[section]){
   const meta={section,row:cell.row,col:cell.col,weaponType:'SM2'},row={...meta,lidId:cell.lidId};
   try{const q=f.vlsCellLocal(meta);row.originErrorM=distance({x:q.xM,y:q.zM,z:q.deckM},cell);}catch(e){row.originError=String(e)}
   row.quads=[];for(let quadIndex=0;quadIndex<4;quadIndex++){const offset=[[-.22,-.22],[.22,-.22],[-.22,.22],[.22,.22]][quadIndex];try{const q=f.vlsCellLocal({...meta,weaponType:'ESSM',quadIndex});row.quads.push(distance({x:q.xM,y:q.zM,z:q.deckM},{x:cell.x+offset[0]*.649,y:cell.y+offset[1]*.649,z:cell.z}));}catch(e){row.quads.push(String(e))}}
   const moduleCells=R.cells[section].filter(c=>Math.floor(c.row/2)===Math.floor(cell.row/2)&&Math.floor(c.col/4)===Math.floor(cell.col/4)),expected=key=>moduleCells.reduce((n,c)=>n+c[key],0)/moduleCells.length;
   row.installedModuleCells=moduleCells.length;
   try{const key=++id;v.spawnLaunchTransient({id:key,kind:'SM2',lifeS:.2,motorActive:true,launchMeta:meta});const e=v.deckSmokeEmitters.find(e=>e.id==='SM2:'+key);if(!e)throw Error('NO_LAUNCH_EMITTER');row.exhaustBodyErrorM=distance(e.body,{x:cell.x,y:cell.y,z:cell.z+.16});row.uptakeErrorM=distance(e.ub,{x:expected('x'),y:expected('y'),z:expected('z')+.12});}catch(e){row.exhaustError=String(e)}
   rows.push(row);
 }
 for(const section of ['fwd','aft'])for(let row=0;row<8;row++)for(let col=0;col<8;col++)if(!R.cells[section].some(c=>c.row===row&&c.col===col)){
   let rejected=false,message='';try{f.vlsCellLocal({section,row,col,weaponType:'SM2'})}catch(e){rejected=true;message=String(e)}gaps.push({section,row,col,rejected,message});
 }
 return {rows,gaps,physicsUnchanged:before===fingerprint()};}'''
release='''R=>{const d=window.__NAVAL_SIM_DIAG__,w=window.__WIP125_DIAG__,api=window.__AEGIS_WIP14B2__,rows=[];
 for(const section of ['fwd','aft'])for(const row of [0,3,4,5,6,7]){
   d.resetEntireSessionV48Wip11A();api.prepareReleaseProbe('SM2','MANUAL',.8,142002);d.ciwsB1Closure.setPaused(true);w.forcePreSail();const inventory=w.snapshot().loadout;
   for(const sec of ['fwd','aft'])for(let i=0;i<inventory[sec].length;i++)w.setCell(sec,i,'EMPTY');
   const cell=R.cells[section].find(c=>c.row===row&&c.col===(row===7?7:4)),index=inventory[section].findIndex(c=>c.row===cell.row&&c.col===cell.col);w.setCell(section,index,'SM2');const departure=w.confirmDeparture();
   const before=window.get3DRenderState(),id=d.fireSM2(),s=window.get3DRenderState().missiles.find(m=>m.id===id),frame=before.shipBodyFrame,r=frame.rotation,o=frame.originM;
   const expected={x:o.x+r[0]*cell.x+r[1]*cell.y+r[2]*cell.z,y:o.y+r[3]*cell.x+r[4]*cell.y+r[5]*cell.z,z:o.z+r[6]*cell.x+r[7]*cell.y+r[8]*cell.z};
   rows.push({section,row:cell.row,col:cell.col,id,departure,scheduler:api.vlsSnapshot(),meta:s?.launchMeta??null,renderPosition:s?{x:s.xM,y:s.zM,z:s.yM}:null,expected,errorM:s?Math.hypot(s.xM-expected.x,s.zM-expected.y,s.yM-expected.z):null,remaining:w.snapshot().counts.sm2Total});
 }return rows;}'''
with sync_playwright()as pw:
    b=launch(pw,webgl=True)
    if a.baseline_i:
        page=load(b,served_bytes(a.baseline_i),webgl=True,errors=errors);old=page.evaluate(inspect,registration);details['baselineI']=old
        checks['OldForwardRowsRelocated']=any(r.get('originErrorM',0)>.1 for r in old['rows']if r['section']=='fwd'and r['row']>=4)
        checks['OldLegalUptakeThrowsOnGap']=any('exhaustError'in r for r in old['rows']if r['section']=='aft'and r['installedModuleCells']==5)
        page.close()
    page=load(b,served_bytes(a.html),webgl=True,errors=errors);q=page.evaluate(inspect,registration);details['candidate']=q
    checks['All122SourceCellOriginsExact']=len(q['rows'])==122 and all(r.get('originErrorM',1)<1e-9 for r in q['rows'])
    checks['All488ESSMTubeOffsetsExact']=all(len(r['quads'])==4 and all(isinstance(n,(int,float))and n<1e-9 for n in r['quads'])for r in q['rows'])
    checks['All122LegalLaunchEffects']=all(r.get('exhaustBodyErrorM',1)<1e-9 and r.get('uptakeErrorM',1)<1e-9 for r in q['rows'])
    checks['TwoFiveCellModulesHandled']=sum(r['installedModuleCells']==5 for r in q['rows'])==10
    checks['SixUninstalledSlotsRejected']=len(q['gaps'])==6 and all(r['rejected']and'VLS_UNINSTALLED_SLOT'in r['message']for r in q['gaps'])
    checks['PresentationQueriesNoPhysicsMutation']=q['physicsUnchanged']
    physical=page.evaluate(release,registration);details['physicalReleases']=physical
    checks['TwelvePhysicalReleasesMatchSource']=len(physical)==12 and all(r['id']is not None and r['errorM']is not None and r['errorM']<1e-7 and r['meta']['section']==r['section']and r['meta']['row']==r['row']and r['meta']['col']==r['col']for r in physical)
    checks['NoRuntimeFault']=page.evaluate('window.__WIP125_DIAG__.wip150RuntimeFault()')is None
    checks['NoPresentationFault']=page.evaluate('window.__WIP125_DIAG__.wip150PresentationFault()')is None
    checks['CoreZero']=page.evaluate('window.__CORE_SELFTEST_FAILURES__')==[];page.close();b.close()
checks['PageErrorsZero']=not errors
result={'schema':'AEGIS_VLS_SOURCE_ORIGINS_AND_SPARSE_EXHAUST_J','html':Path(a.html).name,'sha256':hashlib.sha256(Path(a.html).read_bytes()).hexdigest(),'baselineI':Path(a.baseline_i).name if a.baseline_i else None,'checks':checks,'details':details,'errors':errors,'pass':all(checks.values())}
(out/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'checks':checks,'errors':errors,'pass':result['pass']}),flush=True)
if not result['pass']:raise SystemExit(1)

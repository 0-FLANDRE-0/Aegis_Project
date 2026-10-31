from pathlib import Path
import re,base64,gzip,json,hashlib,difflib
H=Path(__file__).resolve().parent;R=H.parents[2];sha=lambda b:hashlib.sha256(b).hexdigest();raw=(R/'Aegis_SIM_v48_WIP_MAP_D.html').read_bytes();assert sha(raw)=='5be55bdc1390d79f7b74bbfa5f128af916ffecdcf28693d0524578646955f40f';html=raw.decode();p=re.search(r'data-c55-index="13">([^<]+)</script>',html);base=gzip.decompress(base64.b64decode(p[1])).decode();main=base;changes=[]
def change(a,b):
 global main
 assert main.count(a)==1,(main.count(a),a[:140]);main=main.replace(a,b);changes.append({'anchor':a[:140],'beforeSha256':sha(a.encode()),'afterSha256':sha(b.encode())})
# Only actual main-scope own ship entry points. The NPC lexical kernel is exact.
syms=json.loads((H/'base-functions.json').read_text())
def fn(name,transform):
 global main
 q=syms[name];a=q['code'];b=transform(a);assert a!=b,name
 ordinal=q['ordinal'];matches=list(re.finditer(re.escape(a),main));assert len(matches)==base.count(a),(name,len(matches));m=matches[ordinal];main=main[:m.start()]+b+main[m.end():];changes.append({'function':name,'beforeSha256':sha(a.encode()),'afterSha256':sha(b.encode())})
change('let softKillAutoDoctrine = false;', 'let softKillAutoDoctrine = false;\n'+(H/'own_ecm.js').read_text())
fn('nulkaAuto15B',lambda s:s.replace('if(!softKillAutoDoctrine||','if(ownEcmLevelE()!==\'FULL\'||!softKillAutoDoctrine||'))
fn('updateSoftKillDoctrine',lambda s:s.replace('if(cand){','if(cand&&ownEcmLevelE()===\'FULL\'){'))
# Keep exact original listeners and non-UI side effects using detached references.
legacy=['updateNulkaUi15B','networkSetRadarG','emconDesignationSnapshotF2','toggleEmcon','updateMk36ButtonLabel','updateSoftKillAutoButtonLabel','updateSlq32EaButtonLabels','updateModeButtonLabel','updateEngagementControlButtonLabel','updateTrackIdentityButtonLabelA3','wip13b5UpdateGunButtonLabels','wip14a14Refresh3dQuickControls','wip13cUpdateMissileControlLabels','harpoonUpdateUIA','harpoonBindUIA','wip14a14UiSnapshot','bunkerRestoreGunInventory','harpoonRouteUndoMapA']
for name in legacy:
 q=syms[name];a=q['code'];b=a.replace('document.getElementById(', 'mapELegacyNodeE(')
 if a!=b:fn(name,lambda s:s.replace('document.getElementById(', 'mapELegacyNodeE('))
change('let softKillAutoDoctrine = false;','const MAP_E_LEGACY_NODES=new Map();\nfunction mapELegacyNodeE(id){return document.getElementById(id)??MAP_E_LEGACY_NODES.get(id)??null;}\nlet softKillAutoDoctrine = false;')
# Preserve native binding, detach only after bindings/CG control creation.
detach="""// MAP_E user decision: CG individual gun UI retired; native gun commands remain.
// EMCON non-radiating designation UI deferred; lockByCursor's native branch stays.
{const page=document.querySelector('.control-deck-page[data-page="ARM"]'),aim=document.getElementById('modeAimBtn'),arms=document.getElementById('armsBtn');
 for(const e of [page,aim,...(page?.querySelectorAll('[id]')??[])])if(e?.id)MAP_E_LEGACY_NODES.set(e.id,e);
 const credit=page?.querySelector('#harpoonControlsA a[href]');if(credit)document.querySelector('.control-deck-page[data-page="DEBUG"]').append(credit);
 if(arms){MAP_E_LEGACY_NODES.set('armsBtn',arms);arms.remove();}page?.remove();aim?.remove();}
"""
change('// UI_A shell: UI_A1',detach+'\n// UI_A shell: UI_A1')
change("['ARM','ARM · 교전'],",'')
# Empty ARM presets must not reserve any viewport panel; retain NAV/CIC geometry.
a="const n=windows.get('NAV'),a=windows.get('ARM'),c=windows.get('CIC');n.open=a.open=true;"
change(a,"const n=windows.get('NAV'),a={open:false,w:0,h:0},c=windows.get('CIC');n.open=true;")
change("emconChip=button('',()=>{document.getElementById('emconBtn')?.click();refreshChips();})","emconChip=button('',()=>{window.__MAP_E__?.toggleMenu();refreshChips();})")
change("emconChip.title='EMCON 직접 전환 · '+(emconActive?'레이더 방사 통제':'레이더 사용');", "emconChip.title='레이더/ECM 조작';window.__MAP_E__?.refreshChip();")
change("if(!addList.querySelector('button'))addList.append", "const arms=mapELegacyNodeE('armsBtn');if(arms){arms.textContent='ARMS STATUS';addList.append(arms);}if(!addList.querySelector('button'))addList.append")
change("else{window.__UI_A__.open('ARM');setControlDeckTabWip13C('ARM');}","else{/* MAP_E: non-weapon inventory has no legacy ARM routing. */}")
change("window.__MAP_B__?.inventoryRendered();}clockText", "window.__MAP_B__?.inventoryRendered();window.__MAP_E__?.inventoryRendered();}clockText")
fn('harpoonRouteEditingE',lambda s:s.replace("inputMode==='AIM'&&",''))
change("function routeToggle(){if(inputMode!=='AIM')document.getElementById('modeAimBtn').click();",'function routeToggle(){')
change("function appendSearchPoint(xM,yM){if(inputMode!=='AIM')document.getElementById('modeAimBtn').click();",'function appendSearchPoint(xM,yM){')
change('mapDHarpoonPreview(id,{mode:engagementControlMode,',"mapDHarpoonPreview(id,{mode:'MANUAL',")
change('options={mode:engagementControlMode,...(q.routeProgram?',"options={mode:'MANUAL',...(q.routeProgram?")
change('return harpoonAutoTubeGateD(trackId,{mode:engagementControlMode,...options});',"return harpoonAutoTubeGateD(trackId,{mode:'MANUAL',...options});")
# Legacy mode keeps its other meanings but route editing no longer depends on tab.
change("if(controlDeckActiveTabWip13C==='AIR')heloMapTapA(worldX,worldY);else if(harpoonRouteEditingE()&&controlDeckActiveTabWip13C!=='FLEET')harpoonRouteAddE(worldX,worldY);", "if(harpoonRouteEditingE())harpoonRouteAddE(worldX,worldY);else if(controlDeckActiveTabWip13C==='AIR')heloMapTapA(worldX,worldY);")
# Main legacy branch is multiline.
mainold="""if(controlDeckActiveTabWip13C==='AIR'){
      heloMapTapA(worldX,worldY);
    } else if(harpoonRouteEditingE()&&controlDeckActiveTabWip13C!=='FLEET'){
      harpoonRouteAddE(worldX,worldY);"""
change(mainold,"""if(harpoonRouteEditingE()){
      harpoonRouteAddE(worldX,worldY);
    } else if(controlDeckActiveTabWip13C==='AIR'){
      heloMapTapA(worldX,worldY);""")
change('// MAP_B_UI_BEGIN','// MAP_E_UI_BEGIN\n'+(H/'map_e.js').read_text()+'\n// MAP_E_UI_END\n// MAP_B_UI_BEGIN')
change('window.__MAP_C__.mount();window.__MAP_D__.mount();','window.__MAP_C__.mount();window.__MAP_D__.mount();window.__MAP_E__.mount();')
assert re.search(r'// ENV_D_DATA_BEGIN[\s\S]*?// ENV_D_DATA_END',main)[0]==re.search(r'// ENV_D_DATA_BEGIN[\s\S]*?// ENV_D_DATA_END',base)[0]
gz=gzip.compress(main.encode(),9,mtime=0);html=html[:p.start(1)]+base64.b64encode(gz).decode()+html[p.end(1):];m=re.search(r'const records=(\[.*?\]);',html,re.S);rs=json.loads(m[1]);rs[13].update(rawBytes=len(main.encode()),gzipBytes=len(gz),sha256=sha(main.encode()));html=html[:m.start(1)]+json.dumps(rs,separators=(',',':'))+html[m.end(1):];out=R/'Aegis_SIM_v48_WIP_MAP_E.html';out.write_text(html);Path('/tmp/aegis-map-e').mkdir(parents=True,exist_ok=True);Path('/tmp/aegis-map-e/current.js').write_text(main)
q={'output':out.name,'sha256':sha(out.read_bytes()),'bytes':out.stat().st_size,'baseCommit':'7b9ca6e3e2d2dd26406b93c395d376f7f1b30c06','baseHtmlSha256':sha(raw),'mainSha256':sha(main.encode()),'gameCoreWithoutEnvelopeSha256':sha(re.sub(r'// ENV_D_DATA_BEGIN[\s\S]*?// ENV_D_DATA_END','',main).encode()),'envelopeBlockByteExact':True,'changes':changes};(H/'build.json').write_text(json.dumps(q,indent=2)+'\n');(H/'MAP_E.diff').write_text(''.join(difflib.unified_diff(re.sub(r'// ENV_D_DATA_BEGIN[\s\S]*?// ENV_D_DATA_END','// ENV_D byte identical',base).splitlines(True),re.sub(r'// ENV_D_DATA_BEGIN[\s\S]*?// ENV_D_DATA_END','// ENV_D byte identical',main).splitlines(True),fromfile='MAP_D/main.js',tofile='MAP_E/main.js')));print(json.dumps({k:v for k,v in q.items()if k!='changes'}))

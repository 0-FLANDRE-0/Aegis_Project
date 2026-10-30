from pathlib import Path
import json,re,gzip,base64,hashlib
H=Path(__file__).resolve().parent;R=H.parents[2]
sha=lambda b:hashlib.sha256(b).hexdigest()
raw=(R/'Aegis_SIM_v48_WIP_CLEAN_B.html').read_bytes();assert sha(raw)=='ab614891a44f05addc20aed8ac0822da1b997bc766478f2cc1ba3dc76d70fef8'
html=raw.decode();p=re.search(r'data-c55-index="13">([^<]+)</script>',html);main=gzip.decompress(base64.b64decode(p[1])).decode();base=main
s=json.loads((H/'base-symbols.json').read_text());changes=[]
def change(a,b):
 global main
 assert main.count(a)==1,(a[:100],main.count(a))
 main=main.replace(a,b);changes.append({'beforeSha256':sha(a.encode()),'afterSha256':sha(b.encode()),'anchor':a[:120]})
change(s['mapLegacyCursorBridgeA']['code']+'\n','')
change('mapLegacyCursorBridgeA(o);lockByCursor(o.id);','lockCursor.x=o.x;lockCursor.y=o.y;lockCursor.nx=clamp((o.x-aircraft.x())/Math.max(1e-9,lockCursor.rx),-1,1);lockCursor.ny=clamp((o.y-aircraft.y())/Math.max(1e-9,lockCursor.ry),-1,1);lockByCursor(o.id);')
change("function show(o){if(!o)return;lookup=o.key;lastRecord=o;mapLegacyCursorBridgeA(o);actionSignature='';window.__UI_A__.open('INFO');refresh(true);}","function show(o,inspection=false){if(!o)return;if(!inspection&&window.__MAP_B__?.pickObject(o,inputSurface))return;lookup=o.key;lastRecord=o;actionSignature='';window.__UI_A__.open('INFO');refresh(true);}")
change("action('정보 보기',closeCall(()=>show(o)))","action('정보 보기',closeCall(()=>show(o,true)))")
change('return Object.freeze({setMode,showControlInfo,attachSurface,preparePaint()',"return Object.freeze({setFiringTarget(key){firingTarget=key;selectionRevision++;window.__PIP_A__?.invalidate();},setMode,showControlInfo,attachSurface,preparePaint()")
change("const inventory=button('',()=>{open('ARM');setControlDeckTabWip13C('ARM');});inventory.id='uiInventoryA';","const inventory=make('div');inventory.id='uiInventoryA';")
# Preserve every existing inventory node lifecycle, then decorate the SAM entries.
anchor='inventory.append(cell);}'
assert main.count(anchor)==1
change(anchor,'inventory.append(cell);}window.__MAP_B__?.inventoryRendered();')
change('    pipDrawTerrainA(ctx);','    pipDrawTerrainA(ctx);\n    window.__MAP_B__?.draw(ctx,pipRenderContextA);')
# The explicitly retired quick controls are excluded from the preservation census.
anchor=',#wip14a14QuickEngage3D button'
change(anchor,'')
addon=(H/'map_b.js').read_text().replace('/* NATIVE_PREFLIGHT_COPIES */',(H/'native_preview.inc.js').read_text())
change('\n  completeShipStartup();','\n// MAP_B_UI_BEGIN\n'+addon+'\n// MAP_B_UI_END\n  completeShipStartup();')
assert 'MAP_A_LEGACY_CURSOR_BRIDGE' not in main
z=gzip.compress(main.encode(),9,mtime=0);html=html[:p.start(1)]+base64.b64encode(z).decode()+html[p.end(1):];m=re.search(r'const records=(\[.*?\]);',html,re.S);rs=json.loads(m[1]);rs[13].update(rawBytes=len(main.encode()),gzipBytes=len(z),sha256=sha(main.encode()));html=html[:m.start(1)]+json.dumps(rs,separators=(',',':'))+html[m.end(1):]
out=R/'Aegis_SIM_v48_WIP_MAP_B.html';out.write_text(html)
Path('/tmp/aegis-map-b').mkdir(parents=True,exist_ok=True)
Path('/tmp/aegis-map-b/current.js').write_text(main)
receipt={'output':out.name,'sha256':sha(out.read_bytes()),'bytes':out.stat().st_size,'baseHtmlSha256':sha(raw),'mainSha256':sha(main.encode()),'gameCoreWithoutEnvelopeSha256':sha(re.sub(r'// ENV_D_DATA_BEGIN[\s\S]*?// ENV_D_DATA_END','',main).encode()),'changes':changes,'lowAltM':30,'highAltM':15000,'envelopeBlockByteExact':re.search(r'// ENV_D_DATA_BEGIN[\s\S]*?// ENV_D_DATA_END',main)[0]==re.search(r'// ENV_D_DATA_BEGIN[\s\S]*?// ENV_D_DATA_END',base)[0]}
(H/'build.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items()if k!='changes'}))

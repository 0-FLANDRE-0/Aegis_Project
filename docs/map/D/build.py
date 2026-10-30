from pathlib import Path
import re,base64,gzip,json,hashlib,subprocess
H=Path(__file__).resolve().parent;R=H.parents[2];sha=lambda b:hashlib.sha256(b).hexdigest();baseFile=R/'Aegis_SIM_v48_WIP_MAP_C.html';raw=baseFile.read_bytes();assert sha(raw)=='84fa5df960772cdb9c9904310ca7af752e3cedae025fd864dc1b27a9de6f8d7b';html=raw.decode();p=re.search(r'data-c55-index="13">([^<]+)</script>',html);base=gzip.decompress(base64.b64decode(p[1])).decode();main=base;changes=[]
def change(a,b):
 global main
 assert main.count(a)==1,(main.count(a),a[:130]);main=main.replace(a,b);changes.append({'anchor':a[:130],'beforeSha256':sha(a.encode()),'afterSha256':sha(b.encode())})
# Preserve original SAM implementation as the fallback for every extension hook.
a=main.index('// MAP_B_UI_BEGIN');z=main.index('// MAP_B_UI_END',a)+len('// MAP_B_UI_END');ui=main[a:z];old=ui
ui=ui.replace("labels={SM2:'SM-2MR',SM2ER:'SM-2ER',SM6:'SM-6',ESSM:'ESSM'}", "labels={SM2:'SM-2MR',SM2ER:'SM-2ER',SM6:'SM-6',ESSM:'ESSM',HARPOON:'RGM-84',MK45:'5in'}")
ui=ui.replace("function ready(w){const a=availability(w);", "function ready(w){if(window.__MAP_D__.handles(w))return window.__MAP_D__.ready(w);const a=availability(w);")
ui=ui.replace("window.__MAP_C__?.stabilizeInventory();if(pending)", "window.__MAP_D__?.highlight(selection);window.__MAP_C__?.stabilizeInventory();if(pending)")
ui=ui.replace("if(!w)continue;let b=e;", "if(!w)continue;const fontD=window.__MAP_D__.handles(w)?getComputedStyle(e).font:null;let b=e;")
ui=ui.replace("b.dataset.weaponB=w;b.setAttribute", "if(fontD)b.style.font=fontD;b.dataset.weaponB=w;b.setAttribute")
ui=ui.replace("function clear(){selection=null;", "function clear(){window.__MAP_D__.cancelled(selection);selection=null;")
ui=ui.replace("function countMenu(w,anchor){pending=w;chooser.replaceChildren();", "function commitExtendedD(next){window.__MAP_D__.selectionChanging(selection,next);selection=next;pending=null;chooser.hidden=true;if(target)window.__MAP_D__.chosen(selection,target,trackView());highlight();repaint();}\n function countMenu(w,anchor){pending=w;chooser.classList.remove('map-gun-menu-d');if(window.__MAP_D__.menu(w,anchor,commitExtendedD))return;chooser.replaceChildren();")
ui=ui.replace("if(ready(w)<n)return;selection={weapon:w,count:n};", "if(ready(w)<n)return;window.__MAP_D__.selectionChanging(selection,{weapon:w,count:n});selection={weapon:w,count:n};")
ui=ui.replace("window.__MAP_A__.setFiringTarget(o.key);pane.hidden=false;repaint();", "window.__MAP_A__.setFiringTarget(o.key);window.__MAP_D__.chosen(selection,target,o);pane.hidden=false;repaint();")
ui=ui.replace("function cancelTarget(){target=null;", "function cancelTarget(){window.__MAP_D__.cancelled(selection);target=null;")
ui=ui.replace("function calculate(){if(!selection)return null;", "function calculate(){if(window.__MAP_D__.handles(selection?.weapon))return window.__MAP_D__.calculate(selection,target,trackView());if(!selection)return null;")
ui=ui.replace("model=calculate();highlight();if(target&&selection)", "model=calculate();highlight();if(window.__MAP_D__.render(selection,target,model,{pane,titleText,tagDot,summary,verdict,reason})){window.__MAP_C__.setFireState(selection,model,queue);positionPane();return;}if(target&&selection)")
ui=ui.replace("fire.addEventListener('click',()=>{refresh(true);if(!model?.allowed||queue)return;", "fire.addEventListener('click',()=>{refresh(true);if(window.__MAP_D__.fireClick(selection,target,model))return;if(!model?.allowed||queue)return;")
ui=ui.replace("function draw(context,view){if(!selection||!model)return;", "function draw(context,view){if(window.__MAP_D__.draw(context,view,selection,model))return;if(!selection||!model)return;")
ui=ui.replace("initial:!!model.initial,verdict:", "initial:!!model.initial,path:model.path,tone:model.tone,mountLabel:model.mountLabel,timeOfFlightS:model.timeOfFlightS,verdict:")
assert ui!=old
# Native SAM queue/gates/lookup and entire existing ring draw body remain exact suffixes.
for marker,end in [(' function lookup(d,w){',' function nativeReason('),(' function nativeReason(d){',' function classify('),(' function stepCommands(){'," fire.addEventListener('click'")]:
 x=old.index(marker);y=ui.index(marker);assert old[x:old.index(end,x)]==ui[y:ui.index(end,y)],marker
change(old,ui);(H/'engagement_ui.generated.js').write_text(ui)
preview=(H/'preview.js').read_text().replace('/* MAP_D_NATIVE_GATE_COPIES */',(H/'native_preview.inc.js').read_text());extension=preview+'\n'+(H/'map_d.js').read_text()
change('// MAP_B_UI_BEGIN','// MAP_D_EXTENSION_BEGIN\n'+extension+'\n// MAP_D_EXTENSION_END\n// MAP_B_UI_BEGIN')
change("base+(e.dataset.weaponB?' ×4':'')", "base+(e.dataset.weaponB&&!window.__MAP_D__?.handles(e.dataset.weaponB)?' ×4':'')")
change('function setFireState(selection,model,queue){if(!mounted)return;', 'function setFireState(selection,model,queue){if(window.__MAP_D__?.fireState(selection,model))return;if(!mounted)return;')
change('window.__MAP_C__.mount();\n  completeShipStartup();','window.__MAP_C__.mount();window.__MAP_D__.mount();\n  completeShipStartup();')
assert re.search(r'// ENV_D_DATA_BEGIN[\s\S]*?// ENV_D_DATA_END',main)[0]==re.search(r'// ENV_D_DATA_BEGIN[\s\S]*?// ENV_D_DATA_END',base)[0]
gz=gzip.compress(main.encode(),9,mtime=0);html=html[:p.start(1)]+base64.b64encode(gz).decode()+html[p.end(1):];m=re.search(r'const records=(\[.*?\]);',html,re.S);rs=json.loads(m[1]);rs[13].update(rawBytes=len(main.encode()),gzipBytes=len(gz),sha256=sha(main.encode()));html=html[:m.start(1)]+json.dumps(rs,separators=(',',':'))+html[m.end(1):];out=R/'Aegis_SIM_v48_WIP_MAP_D.html';out.write_text(html);Path('/tmp/aegis-map-d/current.js').write_text(main)
q={'output':out.name,'sha256':sha(out.read_bytes()),'bytes':out.stat().st_size,'baseCommit':'9f8e77f96a39cafe017728a0734bc8dd0102a4f6','baseHtmlSha256':sha(raw),'mainSha256':sha(main.encode()),'gameCoreWithoutEnvelopeSha256':sha(re.sub(r'// ENV_D_DATA_BEGIN[\s\S]*?// ENV_D_DATA_END','',main).encode()),'envelopeBlockByteExact':True,'changes':changes};(H/'build.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='changes'}))

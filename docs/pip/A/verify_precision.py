"""0.1 km common chart at an actual charted shoreline; inspect finite canvas
geometry and fixed CSS-pixel strokes under the real DPR transform, read-only.
"""
import argparse,base64,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'docs/helicopter/H'));from browser import load_fleet,launch
ap=argparse.ArgumentParser();ap.add_argument('html',type=Path);ap.add_argument('out',type=Path);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True);raw=a.html.read_bytes();checks={};errors=[]
with sync_playwright()as pw:
 b=launch(pw);native=b.new_page
 def page(**kw):
  kw.update(device_scale_factor=2.8125,has_touch=True);p=native(**kw);p.add_init_script("Element.prototype.requestFullscreen=()=>Promise.reject(Error('fixture'))");return p
 b.new_page=page;p=load_fleet(b,raw,width=832,height=384,errors=errors);p.evaluate("()=>{for(const k of Object.keys(__UI_A__.snapshot().windows))__UI_A__.close(k);__WIP148_3D_VIEW__.active=true;__UI_A__.open('CIC');}");p.wait_for_timeout(300)
 result=p.evaluate('''()=>{const readState=()=>JSON.stringify({cursor:__NAVAL_SIM_DIAG__.wip13cControlDeckSnapshot().state.lockCursor,ui:__MAP_A__.snapshot(),trail:__AEGIS_ACTIVE_SHIP_RUNTIME__.navigation.trail,alerts:document.querySelectorAll('#toastWrap>*').length});const island=__NAVAL_SIM_DIAG__.battlespaceSnapshot().islandState[0],origin=island.points[0],rows=[];__PIP_A__.setCenter(origin);__PIP_A__.prepare();for(const km of [.5,.1]){__PIP_A__.setDistance(km);const v=__PIP_A__.view(),c=v.context,undo=[],calls={},texts=[],widths=[];let nonfinite=0;for(const key of ['moveTo','lineTo','arc','ellipse','stroke','fillText']){const native=c[key];undo.push(()=>c[key]=native);c[key]=function(...args){calls[key]=(calls[key]??0)+1;for(const a of args)if(typeof a==='number'&&!Number.isFinite(a))nonfinite++;if(key==='fillText')texts.push(String(args[0]));if(key==='stroke')widths.push(this.lineWidth*Math.hypot(this.getTransform().a,this.getTransform().b)/devicePixelRatio);return native.apply(this,args);};}const before=readState();let unchanged=false;try{__PIP_A__.paint();unchanged=before===readState();}finally{undo.forEach(f=>f());}const filtered=widths.filter(n=>n>0&&n<10).sort((a,b)=>a-b);rows.push({km,unchanged,nonfinite,calls,meterLabels:texts.filter(t=>/m$/.test(t)),strokeCssPx:filtered,canvas:__PIP_A__.snapshot().canvas});}return {islandId:island.id,origin,rows};}''')
 for row in result['rows']:
  k=str(row['km']);checks[k+'.cursorSelectionTrailAlertsUnchanged']=row['unchanged'];checks[k+'.finite']=row['nonfinite']==0;checks[k+'.coastAndContours']=row['calls']['lineTo']>10;checks[k+'.rings']=row['calls']['arc']>3;checks[k+'.meterLabels']=bool(row['meterLabels']);checks[k+'.strokesBounded']=max(row['strokeCssPx'])<=10
 # Coastline itself is drawn at 1.15*.72=.828 CSS px at both distances.
 checks['coastlineConstantPx']=all(any(abs(n-.828)<1e-6 for n in row['strokeCssPx'])for row in result['rows'])
 p.wait_for_timeout(80);s=p.context.new_cdp_session(p)
 try:(a.out/'coast-100m.png').write_bytes(base64.b64decode(s.send('Page.captureScreenshot',{'format':'png','fromSurface':True,'captureBeyondViewport':False})['data']))
 finally:s.detach()
 b.close()
checks['pageErrors']=not errors;d={'pass':all(checks.values()),'checks':checks,'records':result,'errors':errors,'htmlSha256':hashlib.sha256(raw).hexdigest()};(a.out/'precision.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'pass':d['pass'],'checks':len(checks),'failed':[k for k,v in checks.items()if not v],'errors':errors}));raise SystemExit(0 if d['pass']else 1)

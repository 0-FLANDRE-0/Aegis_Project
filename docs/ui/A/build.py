"""Deterministic presentation-only patch, pinned to the user's VP_A SHA-256."""
from pathlib import Path
import argparse,base64,gzip,hashlib,json,re
HERE=Path(__file__).resolve().parent
BASE_SHA='432de9b88566d6198da0a21856ab85d1febda8106fcd28f6d8f13fd8801e67b9'
def decoded(h):return gzip.decompress(base64.b64decode(re.search(r'data-c55-index="13">(.*?)</script>',h,re.S)[1])).decode()
def build(raw):
 assert hashlib.sha256(raw).hexdigest()==BASE_SHA
 h=raw.decode();s=decoded(h)
 def edit(a,b):
  nonlocal s
  assert s.count(a)==1,(a[:100],s.count(a));s=s.replace(a,b)
 edit(" const EDGE_PANELS=Object.freeze([{id:'controlDeckPanel',screen:'twoD',edge:'bottom',minSpan:.9,maxEdgeGapPx:32}]);", " const EDGE_PANELS=new Map(); // UI_A explicit membership: only the bar and docked windows.")
 a=s.index('  let twoD={...layout};const panels=[];');b=s.index('  const add=r=>',a)
 s=s[:a]+'''  const root=document.getElementById('external3DView'),rootBox=root&&root.getBoundingClientRect().width>0?box(root):raw;
  let twoD={...layout},threeD=intersection(layout,rootBox);const panels=[];
  for(const p of EDGE_PANELS.values()){
   const el=document.getElementById(p.id);if(!el)continue;const r=box(el),css=window.getComputedStyle(el),visible=css.display!=='none'&&css.visibility!=='hidden'&&el.getBoundingClientRect().height>0;
   const reduces=visible&&r.x<layout.x+layout.w&&r.x+r.w>layout.x&&r.y<layout.y+layout.h&&r.y+r.h>layout.y;panels.push({...p,...r,reduces});if(!reduces)continue;
   const reduce=v=>{const right=v.x+v.w,bottom=v.y+v.h;if(p.edge==='left')return rect(Math.min(right-1,Math.max(v.x,r.x+r.w)),v.y,Math.max(1,right-Math.max(v.x,r.x+r.w)),v.h);if(p.edge==='right')return rect(v.x,v.y,Math.max(1,Math.min(right,r.x)-v.x),v.h);if(p.edge==='top')return rect(v.x,Math.min(bottom-1,Math.max(v.y,r.y+r.h)),v.w,Math.max(1,bottom-Math.max(v.y,r.y+r.h)));return rect(v.x,v.y,v.w,Math.max(1,Math.min(bottom,r.y)-v.y));};
   if(p.screen==='both'||p.screen==='twoD')twoD=reduce(twoD);if(p.screen==='both'||p.screen==='threeD')threeD=reduce(threeD);
  }
  const extras=[...observed].filter(e=>e.isConnected).map(e=>({id:e.id,...box(e)}));
'''+s[b:]
 edit('observe,schedule,intersection,edgePanels:EDGE_PANELS',"observe,schedule,intersection,registerPanel(p){if(!p||!['left','right','top','bottom'].includes(p.edge))throw Error('Invalid UI edge');const q={id:p.id,edge:p.edge,screen:p.screen??'both'};if(JSON.stringify(EDGE_PANELS.get(p.id))!==JSON.stringify(q)){EDGE_PANELS.set(p.id,q);observe(document.getElementById(p.id));schedule();}},unregisterPanel(id){if(EDGE_PANELS.delete(id))schedule();},get edgePanels(){return [...EDGE_PANELS.values()].map(p=>({...p}));}")
 a=s.index('async function toggleFullscreen(){');b=s.index("fullscreenBtn?.addEventListener",a);s=s[:a]+(HERE/'fullscreen.js').read_text()+'\n'+s[b:]
 edit('document.body.appendChild(root);update();',"document.body.appendChild(root);window.__UI_A_SETTINGS__.mount(root.firstElementChild,'selection');root.addEventListener('click',e=>{if(e.target.closest('button'))window.__UI_A_SETTINGS__.firstButton(e);},{capture:true});update();")
 edit('  return {tab:next,inputMode};', '  window.__UI_A__?.activate(next);\n  return {tab:next,inputMode};')
 edit("panels.find(p=>p.id==='controlDeckPanel')", "panels.find(p=>p.id==='uiStatusBarA')")
 edit('const vp=AEGIS_VIEWPORT.layout,W=Math.min(360,Math.max(300,vp.w*.30)),H=151,x=vp.cx-W*.5,y=vp.y+6;', 'const vp=AEGIS_VIEWPORT.twoD,W=Math.min(360,Math.max(220,vp.w-12)),H=151,x=vp.x+6,y=vp.y+172;')
 edit('  completeShipStartup();',(HERE/'windows.js').read_text()+'\n  completeShipStartup();')
 s=s.replace('v48_WIP_VP_A','v48_WIP_UI_A');h=h.replace('@media (pointer:coarse), (max-width:640px)','@media (max-width:640px)').replace('.external3d-btn { min-height:44px; padding:8px 12px; font-size:10px; }','/* UI_A: PC density for every pointer. */');h=h.replace('</head>','<style id="uiStyleA">'+(HERE/'ui.css').read_text()+'</style>\n</head>')
 z=gzip.compress(s.encode(),9,mtime=0);m=re.search(r'data-c55-index="13">(.*?)</script>',h,re.S);h=h[:m.start(1)]+base64.b64encode(z).decode()+h[m.end(1):]
 m=re.search(r'const records=(\[.*?\]);',h,re.S);rows=json.loads(m[1]);rows[13].update(rawBytes=len(s.encode()),gzipBytes=len(z),sha256=hashlib.sha256(s.encode()).hexdigest());h=h[:m.start(1)]+json.dumps(rows,separators=(',',':'))+h[m.end(1):]
 return h.replace('v48_WIP_VP_A','v48_WIP_UI_A').replace('V48_WIP_VP_A','V48_WIP_UI_A'),s
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('baseline',type=Path);ap.add_argument('output',type=Path);a=ap.parse_args();h,s=build(a.baseline.read_bytes());a.output.write_text(h);Path('/tmp/ui-a-main.js').write_text(s);print(json.dumps({'bytes':len(h.encode()),'sha256':hashlib.sha256(h.encode()).hexdigest()}))

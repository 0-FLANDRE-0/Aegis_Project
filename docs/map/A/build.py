"""MAP_A presentation/input overlay. Legacy pointerup remains byte-identical."""
from pathlib import Path
import argparse,base64,gzip,hashlib,json,re
HERE=Path(__file__).resolve().parent
BASE_SHA='fd7079e9154e8778f7f5a340e6102c8843930b9865d4dc1135714c4847cdc3b8'
def decoded(h):return gzip.decompress(base64.b64decode(re.search(r'data-c55-index="13">(.*?)</script>',h,re.S)[1])).decode()
def legacy(s):return s[s.index("canvas.addEventListener('pointerup', e => {"):s.index("canvas.addEventListener('pointercancel', e => {")]
def patch(s):
 def one(a,b):
  nonlocal s
  assert s.count(a)==1,a[:100];s=s.replace(a,b,1)
 one('function lockByCursor(){','function lockByCursor(exactTrackId=null){')
 one('    for(const [id, tr] of tracks){\n      if(!trackIsDisplayable(tr)) continue;','    for(const [id, tr] of tracks){\n      if(exactTrackId!==null&&id!==exactTrackId)continue; // MAP_A explicit precision command only; legacy has no filter.\n      if(!trackIsDisplayable(tr)) continue;')
 # Information window uses the existing UI_A manager and retains all prior controls.
 one("q.id!=='CIC'&&controlDeckActiveTabWip13C", "q.id!=='CIC'&&q.id!=='INFO'&&controlDeckActiveTabWip13C")
 one("function focusOpen(id){if(id==='CIC')open(id);", "function focusOpen(id){if(id==='CIC'||id==='INFO')open(id);")
 one("CIC:[224,170],engage:[230,102]", "CIC:[224,170],INFO:[280,300],engage:[230,102]")
 one("[...windows.keys()].every(id=>valid(entry.windows?.[id]))", "[...windows.keys()].every(id=>id==='INFO'&&!entry.windows?.INFO||valid(entry.windows?.[id]))")
 one("for(const[id,q]of windows)Object.assign(q,entry.windows[id]);", "for(const[id,q]of windows)if(entry.windows[id])Object.assign(q,entry.windows[id]);")
 one("const ship=button('',()=>{open('NAV');setControlDeckTabWip13C('NAV');});", "const ship=button('',()=>window.__MAP_A__?.showControlInfo());")
 one("ship.title=hull+' '+(identity.shipName??'')", "if(window.__MAP_A__)ship.textContent=window.__MAP_A__.controlLabel(hull)+'\\n'+speed+' · '+heading;ship.title=hull+' '+(identity.shipName??'')")
 a="const ticks=width/settings.scale>=280?[-30,-20,-10,0,10,20,30]:[-10,0,10];tape.textContent=ticks.map(n=>((Math.round(bearing+n)+360)%360).toString().padStart(3,'0')+(n===0?'▼':'')).join('  ')+'\\nHDG '+(Math.round(shipHdgDeg())%360).toString().padStart(3,'0')+'°';"
 one(a,"window.__MAP_A__?.updateTape(tape,bearing,shipHdgDeg());")
 one('return Object.freeze({open,close(id){const q=windows.get(id);', '''return Object.freeze({open,register(id,title,content,minW=240,minH=160){if(windows.has(id))throw Error('DUPLICATE_UI_WINDOW');const q=createWindow(id,title,content,minW,minH),size=compact()?windowSize(q):[330,360];Object.assign(q,{x:AEGIS_VIEWPORT.layout.x+28,y:AEGIS_VIEWPORT.layout.y+100,w:size[0]*settings.scale,h:size[1]*settings.scale});try{const v=JSON.parse(window.localStorage.getItem(KEY)||'null');const item=v?.schema===SCHEMA?v.layouts?.[layoutKey]?.windows?.[id]:null;if(valid(item))Object.assign(q,item);}catch(_){}clampWindow(q);refreshList();return q.el;},close(id){const q=windows.get(id);''')
 # Hook only chart paint. The simulation loop/renderer and native commands remain intact.
 one('    drawRescueRaftsCicK();drawNetworkPictureG();heloDrawMapA();','    drawRescueRaftsCicK();drawNetworkPictureG();heloDrawMapA();window.__MAP_A__?.draw(ctx);')
 end='\n  completeShipStartup();';assert s.count(end)==1
 s=s.replace(end,'\n'+(HERE/'observations.js').read_text()+'\n'+(HERE/'map.js').read_text()+end,1)
 return s

def build(raw):
 assert hashlib.sha256(raw).hexdigest()==BASE_SHA
 h=raw.decode();old=decoded(h);s=patch(old);assert legacy(s)==legacy(old);s=s.replace('v48_WIP_UI_A1','v48_WIP_MAP_A')
 z=gzip.compress(s.encode(),9,mtime=0);m=re.search(r'data-c55-index="13">(.*?)</script>',h,re.S);h=h[:m.start(1)]+base64.b64encode(z).decode()+h[m.end(1):];m=re.search(r'const records=(\[.*?\]);',h,re.S);rows=json.loads(m[1]);rows[13].update(rawBytes=len(s.encode()),gzipBytes=len(z),sha256=hashlib.sha256(s.encode()).hexdigest());h=h[:m.start(1)]+json.dumps(rows,separators=(',',':'))+h[m.end(1):]
 pos=h.index('</style>',h.index('<style id="uiStyleA">'));h=h[:pos]+'\n'+(HERE/'map.css').read_text()+h[pos:];return h.replace('v48_WIP_UI_A1','v48_WIP_MAP_A').replace('V48_WIP_UI_A1','V48_WIP_MAP_A'),s
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('base',type=Path);ap.add_argument('out',type=Path);a=ap.parse_args();h,s=build(a.base.read_bytes());a.out.write_text(h);Path('/tmp/map-a-main.js').write_text(s);print(json.dumps({'bytes':len(h.encode()),'sha256':hashlib.sha256(h.encode()).hexdigest()}))

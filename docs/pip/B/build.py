"""Pinned PIP_A -> PIP_B. Only UI/render adapters plus diagnostic-only code."""
import argparse,base64,gzip,hashlib,json,re
from pathlib import Path
H=Path(__file__).resolve().parent
BASE_SHA='76c77b5c80835f87654c8aa39cd6a82c1ad66de8bc408ebad675997157024847'
def decode(h):return gzip.decompress(base64.b64decode(re.search(r'data-c55-index="13">(.*?)</script>',h,re.S)[1])).decode()
def patch(s):
 def one(a,b):
  nonlocal s
  assert s.count(a)==1,(s.count(a),a[:120]);s=s.replace(a,b,1)
 # The old pixel card remains DEAD_LEGACY for comparison but has no call site.
 one('pipDrawLockedCardA(ctx,tr,id,drawX,drawY,isSURFACE,col,rw,rh);',"// PIP_B: the old card heading owned the only track number. Keep it here.\n        ctx.font=`${tacticalFontWorldSize(8,5.2)}px system-ui`;ctx.textAlign='left';ctx.fillStyle=col;ctx.fillText(`T${tr.trackNumber??id}`,drawX+14*sym,drawY-12*sym);")
 one("        if(tag){\n          ctx.font","        if(tag&&!isLock){\n          ctx.font")
 one("    ctx.strokeStyle = 'rgba(56,180,140,0.22)';\n      ctx.lineWidth = 1.5;", "    ctx.strokeStyle = 'rgba(56,180,140,0.22)';\n      // PIP_B: a world-unit stroke became a ~200m cyan disk while stopped.\n      ctx.lineWidth = screenPxToWorld(1.5);")
 # Sensor-display gate wraps the unchanged PIP_A drawing block, not its data.
 one('    // ===== SELECTED SHIP SPY 4-FACE PESA RADAR VISUALIZATION =====\n    if(emconActive){','    // PIP_B: display only; no sensor/track/measurement change.\n    if(window.__PIP_B__?.beams()){window.__PIP_B__.beam();\n    // ===== SELECTED SHIP SPY 4-FACE PESA RADAR VISUALIZATION =====\n    if(emconActive){')
 one('    } // end EMCON else\n\n    ctx.restore();','    } // end EMCON else\n    } // PIP_B sensor visualization\n\n    ctx.restore();')
 one('      // seeker / SARH fan display\n      {','      // seeker / SARH fan display\n      if(window.__PIP_B__?.beams()){window.__PIP_B__.beam();')
 one('      if(isGun && cw.tracking){','      if(window.__PIP_B__?.beams() && isGun && cw.tracking){')
 one("if((m.state==='ACTIVE' && m.seekerLocked) || m.state==='SARH' || m.terminalSARH){","if(window.__PIP_B__?.beams() && ((m.state==='ACTIVE' && m.seekerLocked) || m.state==='SARH' || m.terminalSARH)){")
 # Independent utility windows must not activate a non-existent deck tab.
 one("q.id!=='CIC'&&q.id!=='INFO'&&controlDeckActiveTabWip13C!==q.id","!['CIC','INFO','LOCKED'].includes(q.id)&&controlDeckActiveTabWip13C!==q.id")
 one("if(id==='CIC'||id==='INFO')open(id)","if(['CIC','INFO','LOCKED'].includes(id))open(id)")
 one("id==='INFO'&&!entry.windows?.INFO","['INFO','LOCKED'].includes(id)&&!entry.windows?.[id]")
 one('INFO:[280,300],engage:','INFO:[220,280],LOCKED:[260,220],engage:')
 one("w:Math.min(b.w,360*s),h:Math.min(b.h-64,400*s)","w:Math.min(b.w,(q.id==='INFO'?220:q.id==='LOCKED'?280:360)*s),h:Math.min(b.h-64,400*s)")
 one('function titleHeight(){return compact()?28:40;}','function titleHeight(){return 36;}')
 one("const q=createWindow(id,title,content,minW,minH),size=compact()?windowSize(q):[330,360]","const q=createWindow(id,title,content,minW,minH),size=compact()?windowSize(q):id==='INFO'?[220,320]:id==='LOCKED'?[280,240]:[330,360]")
 one("'정보',body,240,160","'정보',body,220,160")
 one("node.style.minWidth=Math.min(170,Math.max(1,v.w-8)/scale)+'px';","node.style.minWidth=Math.min(node===candidates?200:180,Math.max(1,v.w-8)/scale)+'px';")
 one("  menu.hidden=false;place(menu,x,y);\n }","  if(!o&&inputSurface==='PIP'){menu.append(action('중심(자함 추적)',closeCall(()=>window.__PIP_A__.recenter()),'','pipContextCenterB'));menu.append(action('주화면 전환',closeCall(()=>window.__PIP_A__.swap()),'','pipContextSwapB'));}\n  menu.hidden=false;place(menu,x,y);\n }")
 a=s.index(" const tools=",s.index('window.__PIP_A__='));b=s.index(' const row=',a)
 originalTools=s[a:b]
 s=s[:a]+originalTools+''' // PIP_B: retain native menu/header nodes and their listeners. No map toolbar.
 const menu=win.querySelector('.ui-window-menu-a'),header=win.querySelector('.ui-title-a');
 const max=menu.querySelector('button[title="최대화 / 복원"]');if(max)header.insertBefore(max,header.querySelector('button[title="닫기"]'));
 for(const[id,label]of [['pipCenterA','중심(자함 추적)'],['pipSwapA','주화면 전환']]){const e=tools.querySelector('#'+id);e.textContent=label;menu.append(e);e.addEventListener('click',()=>{menu.hidden=true;});}tools.remove(); // Original command listeners remain attached to their very same nodes.
 const fold=header.querySelector('button[title="접기 / 펼치기"]');if(fold)menu.append(fold);
''' +s[b:]
 one('\n  completeShipStartup();','\n'+(H/'ui.js').read_text()+'\n  completeShipStartup();')
 # ENV_A capsule is generated from unchanged native source, never active on boot.
 env=H.parents[1]/'envelope/A/adapter.js'
 if env.exists():one('\n  completeShipStartup();','\n'+env.read_text()+'\n  completeShipStartup();')
 return s
def build(raw):
 assert hashlib.sha256(raw).hexdigest()==BASE_SHA
 h=raw.decode();s=patch(decode(h)).replace('v48_WIP_PIP_A','v48_WIP_PIP_B');z=gzip.compress(s.encode(),9,mtime=0);m=re.search(r'data-c55-index="13">(.*?)</script>',h,re.S);h=h[:m.start(1)]+base64.b64encode(z).decode()+h[m.end(1):];m=re.search(r'const records=(\[.*?\]);',h,re.S);r=json.loads(m[1]);r[13].update(rawBytes=len(s.encode()),gzipBytes=len(z),sha256=hashlib.sha256(s.encode()).hexdigest());h=h[:m.start(1)]+json.dumps(r,separators=(',',':'))+h[m.end(1):];i=h.index('</style>',h.index('<style id="uiStyleA">'));h=h[:i]+'\n'+(H/'dense.css').read_text()+h[i:];return h.replace('v48_WIP_PIP_A','v48_WIP_PIP_B').replace('V48_WIP_PIP_A','V48_WIP_PIP_B'),s
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('base',type=Path);p.add_argument('out',type=Path);a=p.parse_args();h,s=build(a.base.read_bytes());a.out.write_text(h);Path('/tmp/pip-b-main.js').write_text(s);print(json.dumps({'bytes':len(h.encode()),'sha256':hashlib.sha256(h.encode()).hexdigest()}))

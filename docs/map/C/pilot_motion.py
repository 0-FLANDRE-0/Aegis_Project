from pathlib import Path
import sys,json
from playwright.sync_api import sync_playwright
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path.insert(0,str(R/'docs/map/B'));from verify_map_helpers import *
with sync_playwright()as pw:
 b=launch(pw);errors=[];raw=instrument((R/'Aegis_SIM_v48_WIP_MAP_C.html').read_bytes(),(R/'docs/map/B/test-helper.js').read_text()+'\n'+(H/'motion-helper.js').read_text());p=load_fleet(b,raw,width=832,height=384,errors=errors);reset(p);select(p,'SM6');tid=p.evaluate('__MB_TEST__.add({rangeKm:10,altM:1000})');target(p,tid);p.evaluate('id=>__MC_TEST__.startMotion(id)',tid);p.locator('.time-btn[data-tw="8"]').click()
 q=p.evaluate('''async()=>{const a=[];let first=null;await new Promise(done=>{function f(t){if(first===null)first=t;const s=__MAP_C__.snapshot(),p=s.painted.MAIN;if(p&&s.tag.anchor)a.push({t,x:p.screen.x,y:p.screen.y,anchor:s.tag.anchor,rect:s.tag.rect});if(t-first<3000)requestAnimationFrame(f);else done();}requestAnimationFrame(f)});document.getElementById('uiPauseA').click();return{frames:a.length,maxError:Math.max(...a.map(q=>Math.hypot(q.x-q.anchor.x,q.y-q.anchor.y))),samples:a};}''');print(json.dumps({'frames':q['frames'],'maxError':q['maxError'],'errors':errors}));(H/'evidence/pilot-motion.json').write_text(json.dumps(q));p.close();b.close()

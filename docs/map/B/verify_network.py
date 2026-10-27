from pathlib import Path
import sys,json,hashlib
from playwright.sync_api import sync_playwright
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path.insert(0,str(H));from verify_map_helpers import *
helper=(H/'test-helper.js').read_text()+r'''
window.__MB_TEST__.netFixture=()=>{const n=prepareNetworkG(ACTIVE_SHIP_RUNTIME),P=new Array(36).fill(0);for(let i=0;i<6;i++)P[i*6+i]=i<3?400:16;const now=networkNowG();n.files.set('MB_NET',{id:'MB_NET',localTrackId:null,domain:'AIR',fused:{x:[10000,0,1000,-250,0,0],P,atS:now},sources:new Map([['PEER',{senderId:'ALLY_TEST',fileId:3,kind:'TRACK',classification:'ASM',identity:'HOSTILE',domain:'AIR',stateM:[10000,0,1000,-250,0,0],covariance:P,measuredAtS:now,stateAtS:now,bid:{eligible:false,cost:1e6,weapon:null,inFlight:0}}]])});return __MAP_A__.objects().find(o=>o.key==='NET:MB_NET');};
'''
errors=[]
with sync_playwright()as pw:
 b=launch(pw);p=load_fleet(b,instrument((R/'Aegis_SIM_v48_WIP_MAP_B.html').read_bytes(),helper),width=1400,height=900,errors=errors);reset(p);select(p,'SM6');o=p.evaluate('__MB_TEST__.netFixture()');p.wait_for_timeout(150);pos=p.evaluate('o=>__VIEWPORT_A__.worldToScreen(o.x,o.y)',o);p.mouse.click(pos['x'],pos['y']);p.wait_for_timeout(200);q=snap(p);before=p.evaluate('__MB_TEST__.commandState()');p.locator('#mapFireB').evaluate('e=>e.click()');after=p.evaluate('__MB_TEST__.commandState()');out={'pass':q['model']['row']is not None and q['model']['prediction']is not None and q['model']['reason']=='NO_TRACK'and not q['model']['allowed']and before==after and not errors,'snapshot':q,'noCommandStateChange':before==after,'errors':errors,'htmlSha256':hashlib.sha256((R/'Aegis_SIM_v48_WIP_MAP_B.html').read_bytes()).hexdigest()};p.close();b.close()
(H/'evidence/network-only.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out));assert out['pass']

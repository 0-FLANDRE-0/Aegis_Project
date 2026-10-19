"""Extreme docked-map menu bounds; presentation-only native pointer probe."""
import argparse,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'docs/helicopter/H'))
from browser import launch,load_fleet
ap=argparse.ArgumentParser();ap.add_argument('html',type=Path);ap.add_argument('out',type=Path);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True)
raw=a.html.read_bytes();checks={};rows=[];errors=[]
with sync_playwright()as pw:
 b=launch(pw);p=load_fleet(b,raw,width=900,height=900,errors=errors)
 p.evaluate("()=>{for(const k of Object.keys(__UI_A__.snapshot().windows))__UI_A__.close(k);for(const [k,e]of [['NAV','left'],['ARM','right']]){__UI_A__.open(k);document.querySelector('#uiWindowA-'+k+' [title=\"최대화 / 복원\"]').click();__UI_A__.dock(k,e);}}")
 p.wait_for_timeout(450)
 for scale in [85,100,130]:
  p.evaluate('s=>__UI_A__.setScale(s)',scale);p.wait_for_timeout(450);v=p.evaluate('AEGIS_VIEWPORT.twoD')
  p.mouse.click(v['cx'],v['cy'],button='right');p.wait_for_timeout(100)
  q=p.evaluate("()=>{const e=document.querySelector('#mapContextMenuA:not([hidden]),#mapCandidatesA:not([hidden])');return e?.getBoundingClientRect().toJSON()}")
  checks['J.narrowBounds'+str(scale)]=bool(q and q['x']>=v['x']-.1 and q['y']>=v['y']-.1 and q['right']<=v['x']+v['w']+.1 and q['bottom']<=v['y']+v['h']+.1)
  rows.append({'scale':scale,'viewport':v,'menu':q});p.keyboard.press('Escape')
 p.close();b.close()
checks['pageErrors']=not errors
d={'pass':all(checks.values()),'checks':checks,'rows':rows,'errors':errors,'htmlSha256':hashlib.sha256(raw).hexdigest()};(a.out/'bounds.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'pass':d['pass'],'checks':len(checks),'errors':errors}));raise SystemExit(0 if d['pass']else 1)

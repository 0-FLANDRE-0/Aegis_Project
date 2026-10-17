"""Final-artifact equal fixed ticks and real pointer DEBUG controls."""
import argparse,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'docs/multiship/G'))
from browser import launch,load_fleet
from verify_native import SETUP
CLOCK='scale=>{'+SETUP+r'''
 d.createWip13aSurfaceTargetFixture({rangeKm:8,bearingDeg:0,headingDeg:90,speedKt:0});const tr=establish();d.a3SetOperatorIdentity(tr.trackId,'HOSTILE');const fire=har.fire(tr.trackId);const run=d.runFramesToTicks(60,scale,640);return {fire,run,missiles:har.snapshot().missiles,log:journal.snapshot(),rng:har.snapshot().rng,core:__CORE_SELFTEST_FAILURES__};}'''
def main():
 p=argparse.ArgumentParser();p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);raw=a.html.read_bytes();errors=[];checks={};rows=[]
 with sync_playwright()as pw:
  b=launch(pw)
  for scale in [1,8,16,64]:
   page=load_fleet(b,raw,own='CG_52_LATE_TICONDEROGA',ally=None,enemy=None,errors=errors);page.evaluate('window.requestAnimationFrame=()=>0');rows.append(page.evaluate(CLOCK,scale));page.close()
  for width,height in [(1000,760),(390,1000)]:
   page=load_fleet(b,raw,own='CG_52_LATE_TICONDEROGA',ally=None,enemy=None,width=width,height=height,errors=errors)
   page.evaluate("document.getElementById('modeDebugBtn').click()")
   before=page.evaluate('JSON.stringify(__HARPOON_DIAG_A__.snapshot())');page.locator('#harpoonJournalF1').click();text=page.locator('#harpoonJournalTextF1');checks[str(width)+'.modal']=page.locator('#harpoonJournalDialogF1').is_visible();checks[str(width)+'.readonly']=text.get_attribute('readonly')is not None
   box=page.locator('#harpoonJournalDialogF1').bounding_box();checks[str(width)+'.fitsViewport']=box['x']>=0 and box['y']>=0 and box['x']+box['width']<=width+.1 and box['y']+box['height']<=height+.1
   page.locator('#harpoonJournalCopyF1').click();checks[str(width)+'.selectionCopy']=page.evaluate("(()=>{const t=document.getElementById('harpoonJournalTextF1');return t.selectionEnd-t.selectionStart===t.value.length})()")
   checks[str(width)+'.readOnlyState']=before==page.evaluate('JSON.stringify(__HARPOON_DIAG_A__.snapshot())');page.screenshot(path=str(a.out/f'journal-{width}.png'));page.locator('#harpoonJournalCloseF1').click();checks[str(width)+'.close']=not page.locator('#harpoonJournalDialogF1').is_visible();page.close()
  b.close()
 signature=lambda r:{k:r[k]for k in ['missiles','log','rng']}
 for i,s in enumerate([1,8,16,64]):checks[str(s)+'.fixedTicksExact']=signature(rows[i])==signature(rows[0]);checks[str(s)+'.actualRelease']=rows[i]['fire']['ok']and len(rows[i]['missiles'])==1 and len(rows[i]['log']['records'])==1;checks[str(s)+'.core']=not rows[i]['core']
 out={'pass':all(checks.values())and not errors,'checks':checks,'rows':rows,'errors':errors,'htmlSha256':hashlib.sha256(raw).hexdigest()};(a.out/'ui-clock.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n');print(json.dumps({'pass':out['pass'],'checks':len(checks),'failed':[k for k,v in checks.items()if not v],'errors':errors}));raise SystemExit(0 if out['pass']else 1)
if __name__=='__main__':main()

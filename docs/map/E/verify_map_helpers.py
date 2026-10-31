from pathlib import Path
import sys
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'docs/map/E'));from legacy_test_adapter import install;install();sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'));from browser_tools import launch,load_fleet,instrument

def snap(p):p.evaluate('__MAP_B__.refresh(true)');return p.evaluate('__MAP_B__.snapshot()')
def reset(p):p.evaluate('__MB_TEST__.reset()');p.wait_for_timeout(320)
def select(p,w='SM2',n=1):p.locator('[data-weapon-b="'+w+'"]').click();p.locator('[data-salvo-b="'+str(n)+'"]').click();p.wait_for_timeout(80)
def target(p,id,surface='MAIN'):
 p.wait_for_timeout(150);o=p.evaluate('id=>__MAP_A__.objects().find(o=>o.key==="TRACK:"+id)',id);pt=p.evaluate('(a)=>a.surface==="PIP"?__PIP_A__.worldToScreen(a.o.x,a.o.y):__VIEWPORT_A__.worldToScreen(a.o.x,a.o.y)',{'o':o,'surface':surface});p.mouse.click(pt['x'],pt['y']);p.wait_for_timeout(160)
 if p.evaluate('__MAP_A__.snapshot().candidatesOpen'):
  p.locator('#mapCandidatesA button').filter(has_text=o['label']).first.click();p.wait_for_timeout(100)
 return snap(p)

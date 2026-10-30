from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[2];B=R/'docs/map/B'
# Retain the original fixtures, command helpers and assertions; migrate only output/version paths.
for name in ['test-helper.js','warning-helper.js','verify_map_helpers.py','verify_ui88.py','verify_extra.py','verify_network.py','verify_warnings.py','verify_emcon_ui.py','c2_browser.py','verify_delivery_world.py','run_domain.py']:
 s=(B/name).read_text().replace('Aegis_SIM_v48_WIP_MAP_B.html','Aegis_SIM_v48_WIP_MAP_C.html');(H/name).write_text(s)
# Our MAP_C fixture extends, never replaces, the original observed-track fixture.
(H/'legacy-test-helper.js').write_bytes((B/'test-helper.js').read_bytes())
# Keep 91 original checks, migrating M9 to the explicitly requested split layout.
s=(B/'verify_map_b.py').read_text().replace('Aegis_SIM_v48_WIP_MAP_B.html','Aegis_SIM_v48_WIP_MAP_C.html')
s=s.replace("ck(tag+'.M9.fire40gap8',f['height']>=40 and c['x']-(f['x']+f['width'])>=8-.1)","hit=p.locator('#mapFireB').evaluate(\"e=>parseFloat(getComputedStyle(e,'::after').height)*__UI_A_SETTINGS__.scale\");em=p.locator('#uiEmconChipA').bounding_box();ck(tag+'.M9.fire40gap8',hit>=40-.1 and em['x']-(f['x']+f['width'])>=12-.1)")
s=s.replace("ck(tag+'.M9.paneInside',g['x']>=0 and g['y']>=0 and g['x']+g['width']<=width+1 and g['y']+g['height']<=height+1)","sr=p.evaluate('__PIP_A__.view().rect');ck(tag+'.M9.paneInside',g['x']>=sr['x']-1 and g['y']>=sr['y']-1 and g['x']+g['width']<=sr['x']+sr['w']+1 and g['y']+g['height']<=sr['y']+sr['h']+1)")
assert 'hit=p.locator' in s and 'sr=p.evaluate' in s;(H/'verify_map_b.py').write_text(s)
q=json.loads((B/'approved-raid-baselines.json').read_text());q['gameCoreWithoutEnvelopeSha256']=json.loads((H/'build.json').read_text())['gameCoreWithoutEnvelopeSha256'];q['uiRebindingReason']='MAP_C UI-only layout, observed presentation and tap selection. All prior DDG/CG expected physical states unchanged.';(H/'approved-raid-baselines.json').write_text(json.dumps(q,indent=2)+'\n')
(H/'test-migrations.json').write_text(json.dumps({'base':'map-b 06d668abf457a8dd3a98659e3b4535ee69612612','changes':[{'source':'docs/map/B/verify_map_b.py','sha256':hashlib.sha256((B/'verify_map_b.py').read_bytes()).hexdigest(),'assertionsKept':91,'changes':'Only M9 geometry: visible 40px FIRE next to CANCEL becomes actual >=40px pseudo hit box and >=12px EMCON gap; tag box must fit its PiP canvas. Count and all M1-M8 conditions unchanged.'},{'sources':'UI88/warnings23/extra13/network/termination300/natural8/world120/domain420','changes':'Product filename and output paths only. Existing inherited UI container-navigation adapters retained. No acceptance weakened.'}],'approvedRaidEntriesUnchanged':q['entries']==json.loads((B/'approved-raid-baselines.json').read_text())['entries']},indent=2)+'\n')

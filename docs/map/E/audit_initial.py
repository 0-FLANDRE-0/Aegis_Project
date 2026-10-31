"""Read-only census of the shipped MAP_D DOM before MAP_E implementation."""
from pathlib import Path
import sys,json,hashlib
from playwright.sync_api import sync_playwright
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path.insert(0,str(R/'docs/map/D'));from verify_map_helpers import launch,load_fleet
raw=(R/'Aegis_SIM_v48_WIP_MAP_D.html').read_bytes();rows=[];errors=[]
with sync_playwright()as pw:
 b=launch(pw)
 for own in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']:
  p=load_fleet(b,raw,own=own,width=1400,height=900,errors=errors)
  q=p.evaluate('''()=>{const root=document.querySelector('#uiWindowA-ARM .ui-body-a');const info=e=>({id:e.id,tag:e.tagName,type:e.type,text:(e.textContent||e.getAttribute('aria-label')||'').replace(/\\s+/g,' ').trim(),title:e.title,group:e.closest('[data-arm-group]')?.dataset.armGroup,options:e.tagName==='SELECT'?[...e.options].map(o=>({value:o.value,text:o.textContent})):null,parent:e.parentElement?.id,window:e.closest('.ui-window-a')?.id,ancestors:(()=>{let q=e,a=[];while(q&&q!==document.body){if(q.id)a.push(q.id);q=q.parentElement;}return a;})()});return{root:root?.id,controls:root?[...root.querySelectorAll('button,input,select,textarea,a[href],[role=button]')].map(info):[],special:Object.fromEntries(['scenarioModeBtn','newSeaBtn','resetBtn','debugSpawnKh35Btn','debugSpawnKh32Btn','debugToggle','missileSelectSm2Btn','missileSelectSm2ErBtn','missileSelectSm6Btn','missileSelectEssmBtn','modeAimBtn','armsBtn','armsPanel','autoTgtBtn','cg52GunSelect'].map(id=>{const e=document.getElementById(id);return[id,e?info(e):null]})),windows:__UI_A__.snapshot().windows,armsMarkup:document.getElementById('armsPanel')?.outerHTML.slice(0,2400)}}''');rows.append({'profile':own,**q});print(own,len(q['controls']),json.dumps(q['special'],ensure_ascii=False),flush=True);p.close()
 b.close()
out={'baseHtmlSha256':hashlib.sha256(raw).hexdigest(),'profiles':rows,'errors':errors};(H/'evidence/arm-dom-before.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');lines=['profile\tid\ttag\tgroup\ttext\tparent']
for q in rows:
 for e in q['controls']:lines.append('\t'.join(str(v or'').replace('\t',' ').replace('\n',' ')for v in[q['profile'],e['id'],e['tag'],e['group'],e['text'],e['parent']]))
(H/'ARM_CONTROLS_BEFORE.tsv').write_text('\n'.join(lines)+'\n');assert not errors

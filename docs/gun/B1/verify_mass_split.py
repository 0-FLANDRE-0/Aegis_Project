"""Read-only attribution of CG floating-point changes to split magazine nodes."""
from pathlib import Path
import sys,json,hashlib
from playwright.sync_api import sync_playwright
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'))
from browser_tools import launch,load_fleet,instrument
raw=(R/'Aegis_SIM_v48_WIP_GUN_B1.html').read_bytes();fixture='''window.__GB_MASS__=()=>{const q=getShipMassLedgerV32().snapshot({detail:true}),nodes=q.nodes.map(x=>({...x})),merged=nodes.filter(n=>!n.id.endsWith('.MFF_127_SIM')).map(n=>({...n}));for(const m of nodes.filter(n=>n.id.endsWith('.MFF_127_SIM'))){const h=merged.find(n=>n.id===m.id.replace('.MFF_127_SIM','.HE_127_SIM'));h.massKg+=m.massKg;}const calc=ns=>{let massKg=0,mx=0,my=0,mz=0;for(const n of ns){massKg+=n.massKg;mx+=n.massKg*n.x;my+=n.massKg*n.y;mz+=n.massKg*n.z;}return {massKg,mx,my,mz,cgM:{x:mx/massKg,y:my/massKg,z:mz/massKg}};};return {actual:calc(nodes),merged:calc(merged),gunNodes:nodes.filter(n=>n.id.startsWith('gun.')),massEvaluatorUnmodified:true};};'''
errors=[]
with sync_playwright()as pw:
 b=launch(pw);p=load_fleet(b,instrument(raw,fixture),own='CG_52_LATE_TICONDEROGA',errors=errors);q=p.evaluate('__GB_MASS__()');p.close();b.close()
q.update(errors=errors,htmlSha256=hashlib.sha256(raw).hexdigest(),note='Counterfactual merges only colocated equal-mass HE/MFF nodes in a copied node list. Native mass/physics functions and live state are never changed. Magazine split changes IEEE-754 accumulation order despite identical physical mass. Exact historic comparison remains failed; no tolerance or approved expectation update.')
q['pass']=not errors and q['actual']['massKg']==q['merged']['massKg'] and q['actual']['cgM']!=q['merged']['cgM'];(H/'evidence/mass-split.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q));raise SystemExit(not q['pass'])

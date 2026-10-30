"""Existing soft-kill/logistics and H3 authority fixtures, unchanged, D/E A/B."""
from pathlib import Path
import ast,sys,json,hashlib,time
from playwright.sync_api import sync_playwright
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'));from browser_tools import launch,load_fleet
E=H/'evidence/ew-h3';E.mkdir(parents=True,exist_ok=True);errors=[];rows=[];start=time.perf_counter()
def source_fixture(file):
 p=R/file;t=ast.parse(p.read_text());v=next(x.value for x in t.body if isinstance(x,ast.Assign)and any(isinstance(a,ast.Name)and a.id=='FIXTURE'for a in x.targets));return ast.literal_eval(v)
with sync_playwright()as pw:
 b=launch(pw)
 for name,file in [('ew','docs/multiship/F/verify.py'),('h3','docs/multiship/H3/verify_attack.py')]:
  script=source_fixture(file)
  if name=='h3':
   old="checks.currentStrictSchema=current.fleet.schema==='AEGIS_NAVAL_PHYSICAL_FLEET_H3_1'";new="checks.currentStrictSchema=current.fleet.schema==='AEGIS_NAVAL_PHYSICAL_FLEET_H4_1'";assert script.count(old)==1;script=script.replace(old,new)
   (E/'test-migration.json').write_text(json.dumps({'source':file,'change':'Expected current schema H3→H4; H4 already present in MAP_D; original D/E both fail only this historical expectation','assertionsPreserved':True,'allOtherFixtureBytesUnchanged':True},indent=2)+'\n')
  for ship in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']:
   pair={}
   for version in ['D','E']:
    raw=(R/f'Aegis_SIM_v48_WIP_MAP_{version}.html').read_bytes();p=load_fleet(b,raw,own=ship,ally='CG_52_LATE_TICONDEROGA'if ship.startswith('DDG')else'DDG_119_LATE_FLIGHT_IIA',enemy='CG_52_LATE_TICONDEROGA',errors=errors);p.set_default_timeout(240000);q=p.evaluate(script);pair[version]=q;p.close();print(name,ship,version,'checks',len(q['checks']),'failed',[k for k,v in q['checks'].items()if not v],flush=True)
   # Same native business checks and raw deterministic fixture evidence.
   same=pair['D']==pair['E'];row={'suite':name,'ship':ship,'same':same,'sameChecks':pair['D']['checks']==pair['E']['checks'],'baseline':pair['D'],'candidate':pair['E']};rows.append(row);(E/(name+'-'+ship+'.json')).write_text(json.dumps(row,indent=2)+'\n')
 b.close()
out={'pass':not errors and all(r['same']and r['sameChecks']and r['candidate']['pass']for r in rows),'rows':[{'suite':r['suite'],'ship':r['ship'],'same':r['same'],'sameChecks':r['sameChecks'],'checks':len(r['candidate']['checks']),'failed':[k for k,v in r['candidate']['checks'].items()if not v]}for r in rows],'errors':errors,'htmlSha256':hashlib.sha256((R/'Aegis_SIM_v48_WIP_MAP_E.html').read_bytes()).hexdigest(),'elapsedS':time.perf_counter()-start};(E/'summary.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out));assert out['pass']

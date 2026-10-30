"""Stale-table warning without mutating a missile profile or starting a sweep."""
import argparse,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
sys.path.insert(0,str(Path(__file__).resolve().parents[3]/"docs/pip/B"));import browser_backend;browser_backend.install()
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'docs/helicopter/H'));from browser import launch,load_fleet
ap=argparse.ArgumentParser();ap.add_argument('html',type=Path);ap.add_argument('out',type=Path);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True);errors=[]
with sync_playwright()as pw:
 b=launch(pw);p=load_fleet(b,a.html.read_bytes(),errors=errors);q=p.evaluate('''async()=>{const before=await __ENV_A__.status(),old=WIP86_KAPPA_AZ_TAU_S;window.WIP86_KAPPA_AZ_TAU_S=old+.001;const stale=await __ENV_A__.status();window.WIP86_KAPPA_AZ_TAU_S=old;const restored=await __ENV_A__.status();return {before,stale,restored,rows:__ENV_A__.table().rows.length}}''');b.close()
checks={'tableMatchesLiveProfile':not q['before']['recalculationRequired'],'allNativeFunctionsMatch':q['before']['changedNativeFunctions']==[],'changedSettingWarns':q['stale']['recalculationRequired']and q['stale']['message']=='재계산 필요','restoreClearsWarning':not q['restored']['recalculationRequired'],'tableContains96Rows':q['rows']==96,'pageErrors':not errors};out={'pass':all(checks.values()),'checks':checks,'records':q,'errors':errors,'htmlSha256':hashlib.sha256(a.html.read_bytes()).hexdigest()};(a.out/'status.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(json.dumps(out));raise SystemExit(0 if out['pass']else 1)

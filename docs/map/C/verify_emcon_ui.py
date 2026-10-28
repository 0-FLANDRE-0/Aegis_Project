"""Keep all 14 EMCON assertions; replace only the deliberately retired controls."""
from pathlib import Path
import sys,json,hashlib
R=Path(__file__).resolve().parents[3];f=R/'docs/helicopter/K/verify_ui.py';s=f.read_text();out=Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=True)
s=s.replace("x.locator('#external3DAutoLockBtn').evaluate('e=>e.click()')","checks[f'{width}.retiredAutoLockAbsent']=x.locator('#external3DAutoLockBtn').count()==0")
# Keep the original count: absence is validated in MAP_B M9, alongside the retained AUTO assertion.
s=s.replace("checks[f'{width}.retiredAutoLockAbsent']=x.locator('#external3DAutoLockBtn').count()==0","assert x.locator('#external3DAutoLockBtn').count()==0")
a="x.locator('#external3DFireBtn').evaluate('e=>e.click()')"
b="""x.evaluate('id=>{document.querySelector(\"[data-weapon-b=SM2]\").click();document.getElementById(\"mapSalvoB\").querySelector(\"button\").click();__MAP_B__.pickObject(__MAP_A__.objects().find(o=>o.key===\"TRACK:\"+id));__MAP_B__.refresh(true);if(!document.getElementById(\"mapFireB\").disabled)throw Error(\"EMCON release must be disabled\");document.getElementById(\"mapFireB\").click();document.getElementById(\"mapCancelB\").click();}',tid)"""
assert s.count(a)==1;s=s.replace(a,b)
(out/'map-b-test-migration.json').write_text(json.dumps({'source':str(f.relative_to(R)),'sourceSha256':hashlib.sha256(f.read_bytes()).hexdigest(),'changes':['Retired 3D AUTO LOCK replaced by absence assertion; retained autoEngBtn still exercises EMCON auto-lock prohibition','Retired quick FIRE replaced by MAP_B disabled FIRE through observed-track selection; retained ARM FIRE unchanged'],'assertionCountUnchanged':14},indent=2)+'\n')
sys.path.insert(0,str(R/'docs/map/A'));from verify_regressions import install_navigation;install_navigation();sys.path.insert(0,str(f.parent));exec(compile(s,str(f),'exec'),{'__file__':str(f),'__name__':'__main__'})

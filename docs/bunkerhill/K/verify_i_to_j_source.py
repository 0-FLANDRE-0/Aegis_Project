"""Pin I, account for both J changes, and preserve all other source bytes."""
from pathlib import Path
import base64,gzip,hashlib,json,re,sys
from refine_bunker_j import refine_j
old,new,out=map(Path,sys.argv[1:]);checks={}
def read(path):
    html=path.read_text();records={int(i):base64.b64decode(b)for i,b in re.findall(r'data-c55-index="(\d+)">(.*?)</script>',html,re.S)}
    assets={i:base64.b64decode(b)for i,b in re.findall(r'<script id="cg52-([^"]+)" type="application/octet-stream">(.*?)</script>',html,re.S)}
    return records,assets,gzip.decompress(records[13]).decode()
ir,ia,i=read(old);jr,ja,j=read(new)
checks['ExactImmutableI']=hashlib.sha256(old.read_bytes()).hexdigest()=='ea7a50cc63d503c20c37a09e6c7853306396d86bf39cce558d6df77791d4177a'
checks['ThirteenOriginalPackedRecordsIdentical']=all(ir[k]==jr[k]for k in range(13))
checks['SixOriginalCGAssetsIdentical']=len(ia)==len(ja)==6 and ia==ja
checks['OnlyTwoDeclaredVLSContextsChanged']=refine_j(i)==j
checks['OperationalInstallationRevisionCompatible']="revision:'BUNKERHILL_LATE_G_1'"in i and "revision:'BUNKERHILL_LATE_G_1'"in j
r={'schema':'AEGIS_I_TO_J_SOURCE_AUDIT','checks':checks,'htmls':{k:{'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'mainSha256':hashlib.sha256(s.encode()).hexdigest()}for k,p,s in [('I',old,i),('J',new,j)]},'scope':'CG exact physical VLS address and installed-only C17 exhaust averaging. All other main source bytes identical, including sensors, SPG rigid parts, CIWS physics, GPU retirement and recovery. CG missile origins change where old forward rows were clamped.','pass':all(checks.values())}
out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'checks':checks,'pass':r['pass']}))
if not r['pass']:raise SystemExit(1)

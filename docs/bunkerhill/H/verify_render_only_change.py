"""Prove H preserves G's non-renderer main and all embedded source assets."""
from pathlib import Path
import base64,gzip,hashlib,json,re,sys

if len(sys.argv)!=4:raise SystemExit('usage: verify_render_only_change.py EXACT_G.html H.html OUTPUT.json')
old,new,out=map(Path,sys.argv[1:]);checks={};details={}
def read(path):
    html=path.read_text();blobs={int(i):base64.b64decode(b)for i,b in re.findall(r'data-c55-index="(\d+)">(.*?)</script>',html,re.S)}
    assets={i:base64.b64decode(b)for i,b in re.findall(r'<script id="cg52-([^"]+)" type="application/octet-stream">(.*?)</script>',html,re.S)}
    return html,blobs,assets,gzip.decompress(blobs[13]).decode()
_,gb,ga,g=read(old);_,hb,ha,h=read(new)
checks['exactG']=hashlib.sha256(old.read_bytes()).hexdigest()=='55fc258fb53ef8bb0e9967a939695ec527ddcc376dce64d9d40ef19466b3e5ac'
checks['thirteenOriginalRecordsIdentical']=all(gb[i]==hb[i]for i in range(13))
checks['allSixCgAssetsIdentical']=len(ga)==len(ha)==6 and ga==ha
anchor="    .replaceAll('SPQ-9B','SPQ-9').replaceAll('BridgeMaster E','AN/SPS-73').replaceAll('SeaRAM','Phalanx 좌현');\n}\n"
def remove_renderer(main):
    start=main.index('function installBunkerRenderer(view){');end=main.index(anchor,start)+len(anchor)
    return main[:start]+main[end:]
checks['outsideRendererByteIdentical']=remove_renderer(g)==remove_renderer(h)
checks['profileRevisionUnchanged']="revision:'BUNKERHILL_LATE_G_1'"in g and "revision:'BUNKERHILL_LATE_G_1'"in h
details={'htmls':{k:{'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'mainSha256':hashlib.sha256(s.encode()).hexdigest()}for k,p,s in [('G',old,g),('H',new,h)]},'change':'CG upper-envelope classification and rendered deck coverage; build label H'}
result={'schema':'AEGIS_G_TO_H_RENDER_ONLY_SOURCE_AUDIT_V1','checks':checks,'details':details,'passed':sum(checks.values()),'total':len(checks),'pass':all(checks.values())}
out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'checks':checks,'pass':result['pass']}))
if not result['pass']:raise SystemExit(1)

#!/usr/bin/env python3
"""Verify the frozen upload, every executable script, and exact reconstruction."""
from pathlib import Path
import base64,gzip,hashlib,json,re,subprocess,sys,tempfile

HERE=Path(__file__).resolve().parent
if len(sys.argv)!=3: raise SystemExit('usage: verify_package.py RESULT.html BASELINE.html')
result,baseline=map(lambda p:Path(p).resolve(),sys.argv[1:])
checks=[]
def check(name,ok,detail=None):checks.append({'name':name,'pass':bool(ok),'detail':detail})
def digest(b):return hashlib.sha256(b).hexdigest()

check('uploaded candidate SHA256',digest(result.read_bytes())=='6fba8ad6225e83fc86c7f07d275ab58feb4b8027d83a29aabeba3f6fa2382f24')
check('uploaded candidate bytes',result.stat().st_size==7354882)
check('stable baseline SHA256',digest(baseline.read_bytes())=='9e786ddb1331fcd496b6b9604cec87317667ebc501e99270cc33fd6ba1ab9e83')
p=subprocess.run([sys.executable,str(HERE/'package16a.py'),str(result),str(baseline)],capture_output=True,text=True)
original=json.loads(p.stdout)
check('original package acceptance',p.returncode==0 and original['pass'],{'passed':original['passed'],'total':original['total']})
h=result.read_text(encoding='utf-8');records=json.loads(re.search(r'const records=(\[.*?\]);',h,re.S).group(1))
blobs={int(i):base64.b64decode(s) for i,s in re.findall(r'<script type="application/octet-stream" data-c55-index="(\d+)">(.*?)</script>',h,re.S)}
check('complete C55 record set',set(blobs)==set(range(14)) and len(records)==14)
with tempfile.TemporaryDirectory() as tmp:
    tmp=Path(tmp)
    scripts=[]
    for i,record in enumerate(records):
        if record['type'] in ('text/javascript','application/javascript','module'):
            scripts.append((record['id'],gzip.decompress(blobs[i]).decode('utf-8')))
    for attrs,source in re.findall(r'<script\b([^>]*)>(.*?)</script\s*>',h,re.S|re.I):
        if 'application/octet-stream' not in attrs and 'application/json' not in attrs and 'text/plain' not in attrs:
            ident=re.search(r'id="([^"]+)"',attrs)
            scripts.append((ident.group(1) if ident else 'inline',source))
    for i,(name,source) in enumerate(scripts):
        js=tmp/f'script-{i}.js';js.write_text(source,encoding='utf-8')
        syntax=subprocess.run(['node','--check',str(js)],capture_output=True,text=True)
        check('syntax '+name,syntax.returncode==0,syntax.stderr[-1000:] or None)
    rebuilt=tmp/'rebuilt.html'
    b=subprocess.run([sys.executable,str(HERE.parent/'build_wip16a.py'),str(baseline),str(rebuilt)],capture_output=True,text=True)
    check('exact rebuild',b.returncode==0 and rebuilt.exists() and rebuilt.read_bytes()==result.read_bytes(),b.stdout.strip() or b.stderr.strip())
out={'schema':'AEGIS_WIP16A_CLOSEOUT_PACKAGE','originalPackage':{'passed':original['passed'],'total':original['total'],'pass':original['pass']},'additionalChecks':{'passed':sum(q['pass'] for q in checks),'total':len(checks),'rows':checks},'pass':all(q['pass'] for q in checks)}
print(json.dumps(out,ensure_ascii=False,indent=2))
if not out['pass']:raise SystemExit(1)

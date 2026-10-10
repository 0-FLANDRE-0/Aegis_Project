"""Pinned rebuild, packing/asset integrity and unchanged live simulation spans."""
import argparse,base64,gzip,hashlib,json,re,subprocess,tempfile
from pathlib import Path
from build import BASE_SHA,build,OLD,NEW
def decoded(html):return gzip.decompress(base64.b64decode(re.search(r'data-c55-index="13">(.*?)</script>',html,re.S)[1])).decode()
def main():
    p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('candidate',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    baseline=a.baseline.read_text();candidate=a.candidate.read_text();b=decoded(baseline);c=decoded(candidate);checks={}
    checks['pinnedBaseline']=hashlib.sha256(baseline.encode()).hexdigest()==BASE_SHA
    checks['exactDeclaredMain']=build(b).replace(OLD,NEW)==c
    def rows(h):return json.loads(re.search(r'const records=(\[.*?\]);',h,re.S)[1])
    checks['unchangedRecords0to12']=rows(baseline)[:13]==rows(candidate)[:13]
    for i,r in enumerate(rows(candidate)):
        encoded=re.search('data-c55-index="'+str(i)+'">(.*?)</script>',candidate,re.S)[1];raw=gzip.decompress(base64.b64decode(encoded));checks['packedRecord'+str(i)]=len(raw)==r['rawBytes'] and hashlib.sha256(raw).hexdigest()==r['sha256']
    def assets(h):return {m[1]:m[2]for m in re.finditer(r'<script id="([^"]+)" type="application/octet-stream">(.*?)</script>',h,re.S)}
    checks['shipAndWeaponAssetsExact']=assets(baseline)==assets(candidate)
    modules='\n'.join(Path(__file__).with_name(n).read_text()for n in ['runtime.js','state.js','renderer.js'])
    checks['noObserverTruthInjection']=not re.search(r'tracks\.set|sensorDwellTimers\.set|spyScheduler\.step',modules)
    checks['noProfileSwap']=not re.search(r'ACTIVE_SHIP_PROFILE\s*=|IS_BUNKER\s*=',modules)
    checks['singleWeatherTick']=c.count('updateMaritimeEnvironmentWip13A3(dt);')==b.count('updateMaritimeEnvironmentWip13A3(dt);')
    checks['foreignWorldLayer']="PHYSICAL_NAVAL_SHIPS_B" in c
    strip=lambda h:re.sub(r'data-c55-index="13">.*?</script>','data-c55-index="13">MAIN</script>',re.sub(r'const records=\[.*?\];','const records=ROWS;',h,flags=re.S),flags=re.S)
    checks['outerHtmlExact']=strip(baseline).replace(OLD,NEW).replace("C55Packaging.build='V48_WIP_MULTI_SHIP_A'","C55Packaging.build='V48_WIP_MULTI_SHIP_B'")==strip(candidate)
    for start in ['function applyInterceptResult(','function updateMissileBodyB3(']:
        if start not in b:continue
        aa=b.index(start);indent=b[b.rfind('\n',0,aa)+1:aa];end=re.search(r'\n'+re.escape(indent)+r'\}(?=\n|;)',b[aa:]);assert end,start
        bb=aa+end.end();span=b[aa:bb];checks[start]=span in c
    with tempfile.TemporaryDirectory() as tmp:
        for i,m in enumerate(re.finditer(r'<script\b([^>]*)>(.*?)</script>',candidate,re.S)):
            if 'application/octet-stream' in m[1] or not m[2].strip():continue
            f=Path(tmp)/f'script{i}.mjs';f.write_text(m[2]);checks['syntax'+str(i)]=subprocess.run(['node','--check',str(f)],capture_output=True).returncode==0
        f=Path(tmp)/'main.mjs';f.write_text(c);checks['mainSyntax']=subprocess.run(['node','--check',str(f)],capture_output=True).returncode==0
        rebuilt=Path(tmp)/'rebuild.html';subprocess.run(['python',str(Path(__file__).with_name('build.py')),str(a.baseline),str(rebuilt)],check=True,capture_output=True);checks['exactHtmlRebuild']=rebuilt.read_bytes()==a.candidate.read_bytes()
    report={'sha256':hashlib.sha256(a.candidate.read_bytes()).hexdigest(),'checks':checks,'pass':all(checks.values())};(a.out/'static.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));raise SystemExit(0 if report['pass'] else 1)
if __name__=='__main__':main()

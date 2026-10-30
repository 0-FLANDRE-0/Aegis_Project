"""Reproducible patch, all packed resources, lexical scope and changed-function gate."""
import argparse,base64,gzip,hashlib,json,os,re,subprocess,tempfile
from pathlib import Path
from build import BASE_SHA,build,decoded
ROOT=Path(__file__).resolve().parents[3]
CHANGED=set('networkSetRadarG toggleEmcon updateModeButtonLabel lockByCursor updateRadar harpoonJournalReleaseF1 harpoonJournalTextF1'.split())
REMOVED=set()
AST=r'''const fs=require('fs'),acorn=require('acorn');function f(file){const s=fs.readFileSync(file,'utf8'),o={};function w(n){if(!n||typeof n!=='object')return;if(n.type==='FunctionDeclaration')(o[n.id.name]??=[]).push(s.slice(n.start,n.end));for(const[k,v]of Object.entries(n))if(!['start','end'].includes(k)){if(Array.isArray(v))v.forEach(w);else if(v&&typeof v==='object')w(v);}}w(acorn.parse(s,{ecmaVersion:2022}));return o;}const b=f(process.argv[1]),c=f(process.argv[2]);console.log(JSON.stringify({existingCount:Object.keys(b).length,changed:Object.keys(b).filter(k=>c[k]&&JSON.stringify(b[k])!==JSON.stringify(c[k])),removed:Object.keys(b).filter(k=>!c[k])}));'''
def main():
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);b=a.baseline.read_bytes();c=a.html.read_bytes();bs=b.decode();cs=c.decode();checks={'baselinePinned':hashlib.sha256(b).hexdigest()==BASE_SHA,'exactRebuild':build(b)[0].encode()==c};records=lambda h:json.loads(re.search(r'const records=(\[.*?\]);',h,re.S)[1]);checks['other13AssetsExact']=records(bs)[:13]==records(cs)[:13];env=os.environ.copy();env['NODE_PATH']=str(Path('/workspace/aegis-performance-f/docs/performance/F/node_modules')if Path('/workspace/aegis-performance-f/docs/performance/F/node_modules').exists()else ROOT/'docs/performance/F/node_modules')
 with tempfile.TemporaryDirectory()as t:
  t=Path(t)
  for i,row in enumerate(records(cs)):
   z=base64.b64decode(re.search(r'data-c55-index="'+str(i)+r'">(.*?)</script>',cs,re.S)[1]);raw=gzip.decompress(z);checks[f'packed{i}']=len(z)==row['gzipBytes']and len(raw)==row['rawBytes']and hashlib.sha256(raw).hexdigest()==row['sha256'];f=t/f'{i}.js';f.write_bytes(raw);checks[f'syntax{i}']=subprocess.run(['node','--check',str(f)],capture_output=True).returncode==0
  for i,m in enumerate(re.finditer(r'<script\b([^>]*)>(.*?)</script>',cs,re.S)):
   if 'application/octet-stream'in m[1]or not m[2].strip():continue
   f=t/f'loader{i}.js';f.write_text(m[2]);checks[f'loader{i}']=subprocess.run(['node','--check',str(f)],capture_output=True).returncode==0
  bf=t/'baseline.js';cf=t/'candidate.js';bf.write_text(decoded(bs));cf.write_text(decoded(cs));q=subprocess.run(['node',str(ROOT/'docs/performance/F/verify_scope.cjs'),str(bf),str(cf)],env=env,capture_output=True,text=True);scope=json.loads(q.stdout);checks['noNewUnresolvedIdentifiers']=scope['pass'];q=subprocess.run(['node','-e',AST,str(bf),str(cf)],env=env,capture_output=True,text=True);ast=json.loads(q.stdout);checks['onlyDeclaredFunctionChanges']=set(ast['changed'])==CHANGED;checks['onlyRetiredSimplificationsRemoved']=set(ast['removed'])==REMOVED
 checks['emconDesignationHelper']=(ROOT/'docs/helicopter/K/designation.js').read_text()in decoded(cs)
 checks['shipAndHeloRuntimeUnchanged']=(ROOT/'docs/helicopter/J/runtime.js').read_text()in decoded(cs)
 checks['radarPhysicsUnchanged']=(ROOT/'docs/helicopter/G/radar.js').read_text()in decoded(cs)
 checks['hawklinkTransportUnchanged']=(ROOT/'docs/helicopter/F/publisher.js').read_text()in decoded(cs)
 checks['harpoonPolicyUnchanged']=not(set(['harpoonGateA','harpoonReleaseA','harpoonFlightStepA','attackAuthorityH3'])&set(ast['changed']))
 report={'pass':all(checks.values()),'checks':checks,'scope':scope,'functions':ast,'htmlSha256':hashlib.sha256(c).hexdigest(),'bytes':len(c),'addedBytes':len(c)-len(b)};(a.out/'static.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'pass':report['pass'],'checks':len(checks),'failed':[k for k,v in checks.items()if not v]}));raise SystemExit(0 if report['pass']else 1)
if __name__=='__main__':main()

"""Pinned PERF_B → PERF_C: exact-input observation association kernels only."""
import argparse,base64,gzip,hashlib,json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent
BASE_SHA='292622e556192d3c954917437709a0f1e4489e1636cd6263a4b7737832013faf'
OLD='v48_WIP_PERF_B';NEW='v48_WIP_PERF_C';PATCHES=[]
def once(s,a,b,label):
 assert s.count(a)==1,(label,s.count(a));PATCHES.append(label);return s.replace(a,b,1)
def extract(s,key,index=0):
 q=json.loads((HERE/'patch-index.json').read_text())[key][index];v=s[q['start']:q['end']];assert hashlib.sha256(v.encode()).hexdigest()==q['sha256'],key;return v
def build(s):
 f=extract(s,'trackRadarAssociationNisV31')
 f=once(f,'P=tr._kfP,pr=trackRadarPrediction(tr,meas),H=trackEkfRadarJacobian(pr),Ht=_matTranspose(H,m,n);','P=tr._kfP,kernel=trackRadarAssociationKernelPerfC(tr,meas),pr=kernel.pr;','exact-input association kernel')
 f=once(f,'const PHt=_matMul(P,n,n,Ht,m),S=_matAdd(_matMul(H,m,n,PHt,m),R),Sinv=_matInv(S,m);','const Sinv=trackRadarAssociationInversePerfC(kernel,R,sr,sa,se,sv);','exact-noise inverse; native NIS arithmetic retained')
 q=json.loads((HERE/'patch-index.json').read_text())['trackRadarAssociationNisV31'][0]
 s=s[:q['start']]+(HERE/'radar-cache.js').read_text()+'\n'+f+s[q['end']:]
 s=once(s,'window.__CORE_SELFTEST_FAILURES__=failures.slice();',"const perfC=performanceCSelfTest();if(!perfC.pass)failures.push('PERF_C '+JSON.stringify(perfC.checks));window.__CORE_SELFTEST_FAILURES__=failures.slice();",'isolated cache selftest')
 s=once(s,'performanceBSelfTest:performanceBSelfTest,','performanceCSelfTest:performanceCSelfTest,performanceBSelfTest:performanceBSelfTest,','detached selftest export')
 return s
def decoded(html):return gzip.decompress(base64.b64decode(re.search(r'data-c55-index="13">(.*?)</script>',html,re.S)[1])).decode()
def main():
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('output',type=Path);a=p.parse_args();raw=a.baseline.read_bytes();assert hashlib.sha256(raw).hexdigest()==BASE_SHA
 html=raw.decode();candidate=build(decoded(html)).replace(OLD,NEW);gz=gzip.compress(candidate.encode(),mtime=0)
 m=re.search(r'data-c55-index="13">(.*?)</script>',html,re.S);html=html[:m.start(1)]+base64.b64encode(gz).decode()+html[m.end(1):]
 row=re.search(r'const records=(\[.*?\]);',html,re.S);records=json.loads(row[1]);records[13].update(rawBytes=len(candidate.encode()),gzipBytes=len(gz),sha256=hashlib.sha256(candidate.encode()).hexdigest());html=html[:row.start(1)]+json.dumps(records,separators=(',',':'))+html[row.end(1):]
 html=html.replace(OLD,NEW).replace('V48_WIP_PERF_B','V48_WIP_PERF_C');a.output.write_text(html);a.output.with_suffix('.main.js').write_text(candidate)
 manifest={'baselineSha256':BASE_SHA,'htmlSha256':hashlib.sha256(html.encode()).hexdigest(),'mainSha256':hashlib.sha256(candidate.encode()).hexdigest(),'changedPackedRecords':[13],'patches':PATCHES};a.output.with_suffix('.manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({'sha256':manifest['htmlSha256'],'main':manifest['mainSha256'],'bytes':len(html.encode()),'patches':len(PATCHES)}))
if __name__=='__main__':main()

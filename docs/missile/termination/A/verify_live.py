"""Whole-game Chromium actual native flight/RF/fuze regression, not unit mocks."""
import argparse,base64,gzip,hashlib,json,re,sys,time
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[3]
sys.path.insert(0,str(R/'docs/pip/B'));import browser_backend;browser_backend.install()
sys.path.insert(0,str(R/'docs/helicopter/H'));from browser import launch,load_fleet
from playwright.sync_api import sync_playwright
def instrument(raw):
 h=raw.decode();m=re.search(r'data-c55-index="13">(.*?)</script>',h,re.S);s=gzip.decompress(base64.b64decode(m[1])).decode();s=s.replace('\n  completeShipStartup();','\n'+(H/'live-fixture.js').read_text()+'\n  completeShipStartup();');z=gzip.compress(s.encode(),9,mtime=0);h=h[:m.start(1)]+base64.b64encode(z).decode()+h[m.end(1):];m=re.search(r'const records=(\[.*?\]);',h,re.S);q=json.loads(m[1]);q[13].update(rawBytes=len(s.encode()),gzipBytes=len(z),sha256=hashlib.sha256(s.encode()).hexdigest());return(h[:m.start(1)]+json.dumps(q,separators=(',',':'))+h[m.end(1):]).encode()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('html',type=Path);ap.add_argument('out',type=Path);ap.add_argument('--cases',type=Path);ap.add_argument('--batch',type=int,default=1);a=ap.parse_args();a.out.parent.mkdir(parents=True,exist_ok=True)
 cases=json.loads(a.cases.read_text())if a.cases else[{'weapon':w,'rangeKm':15 if w=='ESSM'else 60,'altM':5000,'samples':False}for w in['SM2','SM2ER','SM6','ESSM']]
 raw=a.html.read_bytes();errors=[];rows=[];start=time.monotonic()
 with sync_playwright()as pw:
  b=launch(pw);p=load_fleet(b,instrument(raw),own='DDG_119_LATE_FLIGHT_IIA',errors=errors);p.set_default_timeout(180000)
  for i in range(0,len(cases),max(1,a.batch)):
   t=time.monotonic();batch=p.evaluate('cs=>cs.map(c=>__TERM_LIVE_TEST__.run(c))',cases[i:i+max(1,a.batch)])
   for r in batch:
    rows.append(r);print(json.dumps({k:r.get(k)for k in['weapon','scenario','enabled','rangeKm','altM','success','reason','flightTimeS','firstTrackS','reacquired']}),round(time.monotonic()-t,2),flush=True)
   a.out.write_text(json.dumps({'htmlSha256':hashlib.sha256(raw).hexdigest(),'results':rows,'errors':errors,'elapsedS':time.monotonic()-start},separators=(',',':')))
  b.close()
if __name__=='__main__':main()

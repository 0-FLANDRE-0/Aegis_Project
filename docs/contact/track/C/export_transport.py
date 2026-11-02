"""Post-battle only, lossless bounded export of large AFTER_ACTION data.

No scenario, RNG, sampling, solver, outcome or acceptance test is changed.
"""
from pathlib import Path
import gzip,hashlib,json
def install(runner,out,save):
 import fast_http
 original_load=fast_http.load_fast_http;original_js=runner.CAPTURE_EXPORT_JS
 needle='const r=__TRACK_STABLE_BATTLE__.run(c);r.passiveFinalState='
 assert original_js.count(needle)==1
 adapted=original_js.replace(needle,"const r=__TRACK_STABLE_BATTLE__.run(c);window.__TRACK_C_EXPORT_PENDING__=r.trackCLineage;delete r.trackCLineage;r.passiveFinalState=",1)
 runner.CAPTURE_EXPORT_JS=adapted
 save(out/'EXPORT_TRANSPORT.json',{'schema':'AEGIS_TRACK_C_POST_BATTLE_EXPORT_ADAPTATION_1','originalExporterSha256':hashlib.sha256(original_js.encode()).hexdigest(),'exporterSha256':hashlib.sha256(adapted.encode()).hexdigest(),'onlyChangedOperation':'Move already-completed AFTER_ACTION field out of original whole-object stringify/columnar roundtrip; stream separately after battle.','simulationOrFixtureEdits':0,'originalLegacyCaptureLimitBytes':10*1024*1024,'allLegacyAssertionsAndLosslessRoundTripsPreserved':True})
 class Page:
  def __init__(self,page):self.page=page
  def __getattr__(self,key):return getattr(self.page,key)
  def evaluate(self,expression,*args,**kwargs):
   value=self.page.evaluate(expression,*args,**kwargs)
   if expression!=adapted:return value
   manifest=stream(self.page,out);q=json.loads(value);q['trackCLineage']={'schema':'AEGIS_TRACK_C_LINEAGE_EXTERNAL_GZIP_1',**manifest};return json.dumps(q,separators=(',',':'))
 def load(*args,**kwargs):return Page(original_load(*args,**kwargs))
 fast_http.load_fast_http=load

def stream(page,out):
 path=Path(out)/'TRACK_C_LINEAGE.json.gz';assert not path.exists();digest=hashlib.sha256();size=chunks=0;arrays=[]
 query=r'''async q=>{let v=window.__TRACK_C_EXPORT_PENDING__;for(const k of q.path)v=v[k];if(q.start!=null)v=v.slice(q.start,q.end);const text=JSON.stringify(v),bytes=new TextEncoder().encode(text),sha256=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),n=>n.toString(16).padStart(2,'0')).join('');return {text,sha256,bytes:bytes.length};}'''
 def read(parts,start=None,end=None):
  nonlocal chunks
  q=page.evaluate(query,{'path':parts,'start':start,'end':end});raw=q['text'].encode();assert len(raw)==q['bytes']and hashlib.sha256(raw).hexdigest()==q['sha256'];chunks+=1;return raw
 with path.open('wb')as handle,gzip.GzipFile(filename='',fileobj=handle,mode='wb',compresslevel=6,mtime=0)as gz:
  def write(raw):
   nonlocal size
   digest.update(raw);size+=len(raw);gz.write(raw)
  def object_value(parts):
   keys=page.evaluate('p=>{let v=window.__TRACK_C_EXPORT_PENDING__;for(const k of p)v=v[k];return Object.keys(v)}',parts);write(b'{')
   for i,key in enumerate(keys):
    if i:write(b',')
    write(json.dumps(key,ensure_ascii=False,separators=(',',':')).encode()+b':');sub=parts+[key]
    if key=='records':
     length=page.evaluate('p=>{let v=window.__TRACK_C_EXPORT_PENDING__;for(const k of p)v=v[k];return v.length}',sub);write(b'[')
     for start in range(0,length,500):
      if start:write(b',')
      raw=read(sub,start,min(length,start+500));assert raw[:1]==b'['and raw[-1:]==b']';write(raw[1:-1])
     write(b']');assert page.evaluate('p=>{let v=window.__TRACK_C_EXPORT_PENDING__;for(const k of p)v=v[k];return v.length}',sub)==length;arrays.append({'path':sub,'records':length})
    elif key=='candidateTrace'and page.evaluate('p=>{let v=window.__TRACK_C_EXPORT_PENDING__;for(const k of p)v=v[k];return v!==null}',sub):object_value(sub)
    else:write(read(sub))
   write(b'}')
  object_value([])
 compressed=hashlib.sha256(path.read_bytes()).hexdigest()
 # Independent disk roundtrip verifies every stored byte without a whole-browser stringify.
 verify=hashlib.sha256();verified_size=0
 with gzip.open(path,'rb')as f:
  while True:
   block=f.read(1024*1024)
   if not block:break
   verify.update(block);verified_size+=len(block)
 assert verify.hexdigest()==digest.hexdigest()and verified_size==size
 manifest={'path':path.name,'compressedSha256':compressed,'jsonSha256':digest.hexdigest(),'jsonBytes':size,'verifiedChunks':chunks,'arrayCounts':arrays,'omittedRecords':0,'omittedFields':0,'allChunkUtf8Sha256Verified':True,'gzipRoundTripExact':True,'postBattleOnly':True};(Path(out)/'LINEAGE_EXPORT.json').write_text(json.dumps(manifest,indent=2)+'\n');return manifest

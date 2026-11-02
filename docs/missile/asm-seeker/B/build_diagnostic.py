"""Build ASM_SEEKER_B test-only diagnostic HTML from the pinned A product."""
from pathlib import Path
import base64,gzip,hashlib,json,os,re
P=Path(__file__).resolve().parent;R=P.parents[3]
BASE=R/'Aegis_SIM_v48_WIP_ASM_SEEKER_A.html'
OUT=Path(os.environ.get('ASM_B_DIAG_OUT','/dev/shm/Aegis_SIM_v48_WIP_ASM_SEEKER_B_DIAG.html'))
BASE_SHA='9a00c8c02bd88ef1322b1b47882a2299184e174230391f9a608347f2b4fb3e5f'
sha=lambda b:hashlib.sha256(b).hexdigest()
def unpack(raw):
 m=re.search(rb'data-c55-index="13">([^<]+)',raw);assert m;return gzip.decompress(base64.b64decode(m[1])).decode(),m
def pack(raw,source,m):
 z=gzip.compress(source.encode(),9,mtime=0);enc=base64.b64encode(z);out=raw[:m.start(1)]+enc+raw[m.end(1):]
 meta=re.search(rb'const records=(\[.*?\]);',out,re.S);assert meta;rows=json.loads(meta[1]);rows[13].update(rawBytes=len(source.encode()),gzipBytes=len(z),sha256=sha(source.encode()))
 if 'encodedBytes' in rows[13]:rows[13]['encodedBytes']=len(enc)
 return out[:meta.start(1)]+json.dumps(rows,separators=(',',':')).encode()+out[meta.end(1):]
def main():
 raw=BASE.read_bytes();assert sha(raw)==BASE_SHA;source,m=unpack(raw);module=(P/'diagnostic.js').read_text();anchor='  window.__NAVAL_SIM_DIAG__ = {';assert source.count(anchor)==1
 candidate=source.replace(anchor,module+'\n'+anchor,1);output=pack(raw,candidate,m);check,_=unpack(output);assert check==candidate;OUT.write_bytes(output)
 receipt={'schema':'AEGIS_ASM_SEEKER_B_DIAGNOSTIC_BUILD_1','base':BASE.name,'baseSha256':sha(raw),'baseMainSha256':sha(source.encode()),'output':str(OUT),'outputSha256':sha(output),'outputMainSha256':sha(candidate.encode()),'moduleSha256':sha(module.encode()),'inverseByteExact':candidate.replace(module+'\n','',1)==source,'productBehaviorChanged':False,'testOnlyInstrumentation':True};(P/'DIAGNOSTIC_BUILD.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()

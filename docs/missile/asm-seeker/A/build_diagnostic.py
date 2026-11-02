"""Build the test-only ASM_SEEKER_A diagnostic artifact from the pinned TRACK-C HTML."""
from pathlib import Path
import base64,gzip,hashlib,json,re

P=Path(__file__).resolve().parent;R=P.parents[3]
BASE=R/'Aegis_SIM_v48_WIP_TRACK_C.html';OUT=R/'Aegis_SIM_v48_WIP_ASM_SEEKER_A_DIAG.html'
BASE_SHA='3f2af4c1e18ef30ce4b8dfe4cc2b28f2b91cf96c62306e8f9c55df4a8c508c81'
MAIN_SHA='b036ce98279685c884896b918f9fc05f26b2980811c05e3eed39b25016d5827f'
sha=lambda b:hashlib.sha256(b).hexdigest()

def unpack(raw):
 m=re.search(rb'data-c55-index="13">([^<]+)',raw);assert m
 return gzip.decompress(base64.b64decode(m[1])).decode(),m

def pack(raw,source,m):
 z=gzip.compress(source.encode(),9,mtime=0);encoded=base64.b64encode(z);out=raw[:m.start(1)]+encoded+raw[m.end(1):]
 meta=re.search(rb'const records=(\[.*?\]);',out,re.S);assert meta
 rows=json.loads(meta[1]);rows[13].update(rawBytes=len(source.encode()),gzipBytes=len(z),sha256=sha(source.encode()))
 if 'encodedBytes' in rows[13]:rows[13]['encodedBytes']=len(encoded)
 return out[:meta.start(1)]+json.dumps(rows,separators=(',',':')).encode()+out[meta.end(1):]

def main():
 raw=BASE.read_bytes();assert sha(raw)==BASE_SHA
 source,m=unpack(raw);assert sha(source.encode())==MAIN_SHA
 module=(P/'diagnostic.js').read_text();anchor='  window.__NAVAL_SIM_DIAG__ = {';assert source.count(anchor)==1
 candidate=source.replace(anchor,module+'\n'+anchor,1);assert candidate.replace(module+'\n','',1)==source
 output=pack(raw,candidate,m);check,_=unpack(output);assert check==candidate
 OUT.write_bytes(output)
 receipt={'schema':'AEGIS_ASM_SEEKER_A_DIAGNOSTIC_BUILD_1','base':BASE.name,'baseSha256':sha(raw),'baseMainSha256':sha(source.encode()),'output':OUT.name,'outputSha256':sha(output),'outputMainSha256':sha(candidate.encode()),'moduleSha256':sha(module.encode()),'inverseByteExact':True,'productBehaviorChanged':False,'testOnlyInstrumentation':True}
 (P/'DIAGNOSTIC_BUILD.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))

if __name__=='__main__':main()

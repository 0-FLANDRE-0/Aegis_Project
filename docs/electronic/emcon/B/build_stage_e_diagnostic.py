#!/usr/bin/env python3
"""Build a disposable Commit-E diagnostic copy; the release product stays uninstrumented."""
from __future__ import annotations
import base64,gzip,hashlib,json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
PRODUCT=ROOT/'Aegis_SIM_v48_WIP_EMCON_B.html';OUT=Path('/tmp/Aegis_SIM_v48_WIP_EMCON_B_E_DIAGNOSTIC.html')
def sha(data:bytes)->str:return hashlib.sha256(data).hexdigest()
def main():
 raw=PRODUCT.read_bytes();m=re.search(rb'data-c55-index="13">([^<]+)',raw)
 if not m:raise AssertionError('packed main missing')
 source=gzip.decompress(base64.b64decode(m[1])).decode();modules=[ROOT/'docs/electronic/emitter/A/baseline_diagnostic.js',HERE/'stage_e_diagnostic.js',HERE/'correction_2_diagnostic.js',HERE/'correction_3_diagnostic.js'];payload='\n'.join(p.read_text().rstrip() for p in modules)+'\n'
 anchor='  window.__NAVAL_SIM_DIAG__ = {'
 if source.count(anchor)!=1:raise AssertionError('diagnostic anchor mismatch')
 candidate=source.replace(anchor,payload+anchor,1);packed=gzip.compress(candidate.encode(),9,mtime=0);encoded=base64.b64encode(packed);output=raw[:m.start(1)]+encoded+raw[m.end(1):]
 meta=re.search(rb'const records=(\[.*?\]);',output,re.S);rows=json.loads(meta[1]);rows[13].update(rawBytes=len(candidate.encode()),gzipBytes=len(packed),sha256=sha(candidate.encode()))
 if 'encodedBytes' in rows[13]:rows[13]['encodedBytes']=len(encoded)
 output=output[:meta.start(1)]+json.dumps(rows,separators=(',',':')).encode()+output[meta.end(1):];OUT.write_bytes(output)
 receipt={'schema':'AEGIS_EMCON_B_E_DIAGNOSTIC_BUILD_1','productSha256':sha(raw),'outputSha256':sha(output),'modules':{str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in modules},'inverseByteExact':candidate.replace(payload,'',1)==source,'testOnly':True,'output':str(OUT)}
 (HERE/'E_DIAGNOSTIC_BUILD.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()

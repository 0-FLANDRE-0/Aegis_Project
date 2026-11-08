#!/usr/bin/env python3
"""Build disposable ESM_A diagnostic copies; product files remain clean."""
from __future__ import annotations
import argparse,base64,gzip,hashlib,json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent
def sha(data:bytes)->str:return hashlib.sha256(data).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--product',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--modules',nargs='+',required=True);p.add_argument('--receipt',type=Path,required=True);a=p.parse_args()
 raw=a.product.read_bytes();m=re.search(rb'data-c55-index="13">([^<]+)',raw)
 if not m:raise AssertionError('packed main missing')
 source=gzip.decompress(base64.b64decode(m[1])).decode();paths=[HERE/q for q in a.modules];payload='\n'.join(q.read_text().rstrip() for q in paths)+'\n';anchor='  window.__NAVAL_SIM_DIAG__ = {'
 if source.count(anchor)!=1:raise AssertionError('diagnostic anchor mismatch')
 candidate=source.replace(anchor,payload+anchor,1);packed=gzip.compress(candidate.encode(),9,mtime=0);encoded=base64.b64encode(packed);output=raw[:m.start(1)]+encoded+raw[m.end(1):]
 meta=re.search(rb'const records=(\[.*?\]);',output,re.S);rows=json.loads(meta[1]);rows[13].update(rawBytes=len(candidate.encode()),gzipBytes=len(packed),sha256=sha(candidate.encode()))
 if 'encodedBytes'in rows[13]:rows[13]['encodedBytes']=len(encoded)
 output=output[:meta.start(1)]+json.dumps(rows,separators=(',',':')).encode()+output[meta.end(1):];a.out.write_bytes(output);receipt={'schema':'AEGIS_ESM_A_DIAGNOSTIC_BUILD_1','productSha256':sha(raw),'outputSha256':sha(output),'inverseByteExact':candidate.replace(payload,'',1)==source,'testOnly':True,'modules':{q.name:sha(q.read_bytes()) for q in paths}};a.receipt.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()

#!/usr/bin/env python3
from pathlib import Path
import sys,re,base64,gzip,json,hashlib,io
HERE=Path(__file__).resolve().parent
BASE_SHA='6fba8ad6225e83fc86c7f07d275ab58feb4b8027d83a29aabeba3f6fa2382f24'
FINAL_SHA='7b63a62bb1cad123b7d7eb17c1fbe26452194c3ff2c637c09b4c48a2a6c8d76d'
TITLE='AEGIS v48 WIP16B — Imported Model Rendering Integration'
def sha(b): return hashlib.sha256(b).hexdigest()
def build(src,out):
    src=Path(src);out=Path(out);blob=src.read_bytes()
    if sha(blob)!=BASE_SHA: raise SystemExit(f'BASELINE_SHA_MISMATCH {sha(blob)}')
    h=blob.decode('utf-8')
    m=re.search(r'(<script type="application/octet-stream" data-c55-index="13">)(.*?)(</script>)',h,re.S)
    if not m: raise SystemExit('C55_RECORD_13_NOT_FOUND')
    main=gzip.decompress(base64.b64decode(m.group(2))).decode('utf-8')
    edits=json.loads((HERE/'edits.json').read_text(encoding='utf-8'))
    if sha(main.encode())!=edits['baseline_main_sha256']: raise SystemExit('BASELINE_MAIN_SHA_MISMATCH')
    lines=main.splitlines(keepends=True)
    for op in reversed(edits['ops']):
        old=''.join(lines[op['i1']:op['i2']])
        if sha(old.encode())!=op['before_sha256']: raise SystemExit(f'EDIT_CONTEXT_MISMATCH {op["i1"]}:{op["i2"]}')
        lines[op['i1']:op['i2']]=[op['replacement']] if op['replacement'] else []
    final=''.join(lines)
    if sha(final.encode())!=edits['final_main_sha256']: raise SystemExit('FINAL_MAIN_SHA_MISMATCH')
    # GzipFile writes OS=255 consistently; gzip.compress(mtime=0) can expose
    # the platform OS byte on Python 3.11/3.12. Keep the uploaded HTML exact.
    buffer=io.BytesIO()
    with gzip.GzipFile(filename='',mode='wb',fileobj=buffer,compresslevel=9,mtime=0) as stream:
        stream.write(final.encode('utf-8'))
    packed=buffer.getvalue()
    h=h[:m.start(2)]+base64.b64encode(packed).decode()+h[m.end(2):]
    mf=re.search(r'const records=(\[.*?\]);',h,re.S)
    records=json.loads(mf.group(1));records[13].update(rawBytes=len(final.encode()),gzipBytes=len(packed),sha256=sha(final.encode()))
    h=h[:mf.start(1)]+json.dumps(records,separators=(',',':'))+h[mf.end(1):]
    h=re.sub(r'<title>.*?</title>',f'<title>{TITLE}</title>',h,count=1,flags=re.S)
    out.write_bytes(h.encode('utf-8'))
    got=sha(out.read_bytes())
    print(json.dumps({'output':str(out),'bytes':out.stat().st_size,'sha256':got,'mainSha256':sha(final.encode())},ensure_ascii=False))
    if FINAL_SHA and got!=FINAL_SHA: raise SystemExit('FINAL_HTML_SHA_MISMATCH')
if __name__=='__main__':
    if len(sys.argv)!=3: raise SystemExit('usage: build_wip16b.py BASE_WIP16A.html OUTPUT.html')
    build(sys.argv[1],sys.argv[2])

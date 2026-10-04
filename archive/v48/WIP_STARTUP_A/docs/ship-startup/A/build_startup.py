#!/usr/bin/env python3
from pathlib import Path
import sys,re,base64,gzip,json,hashlib,io
HERE=Path(__file__).resolve().parent
BASE_SHA='7b63a62bb1cad123b7d7eb17c1fbe26452194c3ff2c637c09b4c48a2a6c8d76d'
FINAL_SHA='94f5e9321fe1f04c5b43c4d8dca5b0762014c1cffe358ad92a81b8ffe70e7c92'
def sha(b):return hashlib.sha256(b).hexdigest()
def build(src,out):
    src=Path(src);out=Path(out);blob=src.read_bytes()
    if sha(blob)!=BASE_SHA:raise SystemExit('BASELINE_SHA_MISMATCH')
    h=blob.decode();m=re.search(r'(<script type="application/octet-stream" data-c55-index="13">)(.*?)(</script>)',h,re.S)
    if not m:raise SystemExit('C55_RECORD_13_NOT_FOUND')
    main=gzip.decompress(base64.b64decode(m[2])).decode()
    edits=json.loads((HERE/'edits.json').read_text())
    if sha(main.encode())!=edits['baseline_main_sha256']:raise SystemExit('BASELINE_MAIN_SHA_MISMATCH')
    lines=main.splitlines(keepends=True)
    for op in reversed(edits['ops']):
        if sha(''.join(lines[op['i1']:op['i2']]).encode())!=op['before_sha256']:raise SystemExit('EDIT_CONTEXT_MISMATCH')
        lines[op['i1']:op['i2']]=[op['replacement']]if op['replacement']else []
    final=''.join(lines)
    if sha(final.encode())!=edits['final_main_sha256']:raise SystemExit('FINAL_MAIN_SHA_MISMATCH')
    buf=io.BytesIO()
    with gzip.GzipFile(filename='',mode='wb',fileobj=buf,compresslevel=9,mtime=0)as stream:stream.write(final.encode())
    packed=buf.getvalue();h=h[:m.start(2)]+base64.b64encode(packed).decode()+h[m.end(2):]
    mf=re.search(r'const records=(\[.*?\]);',h,re.S);records=json.loads(mf[1])
    records[13].update(rawBytes=len(final.encode()),gzipBytes=len(packed),sha256=sha(final.encode()))
    h=h[:mf.start(1)]+json.dumps(records,separators=(',',':'))+h[mf.end(1):]
    def replace(old,new):
        nonlocal h
        if h.count(old)!=1:raise SystemExit('ENVELOPE_CONTEXT_MISMATCH')
        h=h.replace(old,new,1)
    replace("(function(){'use strict';\n const records=","(async function(){'use strict';\n const records=")
    replace(" if(!window.WIP13C5_5)throw new Error('C55 runtime did not initialize');"," window.C55Packaging.stageStatus='WAITING_FOR_SHIP_SELECTION';\n await window.__AEGIS_STARTUP_PROMISE__;\n if(!window.WIP13C5_5)throw new Error('C55 runtime did not initialize');")
    replace("window.C55Packaging.build='V48_WIP14B4';window.C55Packaging.stageStatus='14B4_STATEFUL_GAME_TRAJECTORY_CANDIDATE';","window.C55Packaging.build='V48_WIP_STARTUP_A';window.C55Packaging.stageStatus='PREDEPARTURE_SHIP_READY';")
    replace("badge.textContent='WIP14B4 · STATEFUL LOFT · B3 DL / GPS'","badge.textContent='함선 선택 · 출항 준비'")
    h=re.sub(r'<title>.*?</title>','<title>AEGIS v48 — Pre-departure Ship Initialization</title>',h,count=1,flags=re.S)
    result=h.encode()
    if sha(result)!=FINAL_SHA:raise SystemExit('FINAL_HTML_SHA_MISMATCH')
    out.write_bytes(result)
    print(json.dumps({'output':str(out),'bytes':len(result),'sha256':sha(result),'mainSha256':sha(final.encode())}))
if __name__=='__main__':
    if len(sys.argv)!=3:raise SystemExit('usage: build_startup.py BASE_WIP16B.html OUTPUT.html')
    build(sys.argv[1],sys.argv[2])

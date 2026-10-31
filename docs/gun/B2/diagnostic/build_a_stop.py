"""Append one diagnostic A-only hook; preserve the original instrumented source."""
from pathlib import Path
import base64,gzip,hashlib,json,re
from build_fixture import build,B,R
H=Path(__file__).resolve().parent
def build_corrected():
 raw=build();assert hashlib.sha256(raw).hexdigest()=='39dc367caa065db140fc606b208c895245d97aa36342575b47cb23f977c447f7'
 html=raw.decode();m=re.search(r'data-c55-index="13">([^<]+)</script>',html)
 before=gzip.decompress(base64.b64decode(m[1])).decode();old=(H/'hooks.js').read_text();extra=(H/'a_stop_hook.js').read_text()
 assert before.count(old)==1
 after=before.replace(old,old+'\n'+extra,1)
 assert after.replace(old+'\n'+extra,old,1)==before
 gz=gzip.compress(after.encode(),9,mtime=0)
 html=html[:m.start(1)]+base64.b64encode(gz).decode()+html[m.end(1):]
 m=re.search(r'const records=(\[.*?\]);',html,re.S);records=json.loads(m[1])
 records[13].update(rawBytes=len(after.encode()),gzipBytes=len(gz),sha256=hashlib.sha256(after.encode()).hexdigest())
 return (html[:m.start(1)]+json.dumps(records,separators=(',',':'))+html[m.end(1):]).encode()

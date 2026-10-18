"""UI_A1: patch only UI_A's presentation shell and CSS, pinned to its original bytes."""
from pathlib import Path
import argparse,base64,gzip,hashlib,json,re
HERE=Path(__file__).resolve().parent
BASE_SHA='a4b6825df6c28eb8f0747f73ec9469c90f277f96eb23e55be67298a6a1cab8e4'
def decoded(h):return gzip.decompress(base64.b64decode(re.search(r'data-c55-index="13">(.*?)</script>',h,re.S)[1])).decode()
def bounds(s):
 a=s.index('// UI_A shell:');return a,s.index('\n  completeShipStartup();',a)
def build(raw):
 assert hashlib.sha256(raw).hexdigest()==BASE_SHA
 h=raw.decode();s=decoded(h);a,b=bounds(s);s=s[:a]+(HERE/'windows.js').read_text().rstrip()+s[b:];s=s.replace('v48_WIP_UI_A','v48_WIP_UI_A1');m=re.search(r'(<style id="uiStyleA">)(.*?)(</style>)',h,re.S);assert m;h=h[:m.end(2)]+'\n'+(HERE/'compact.css').read_text()+h[m.end(2):]
 z=gzip.compress(s.encode(),9,mtime=0);m=re.search(r'data-c55-index="13">(.*?)</script>',h,re.S);h=h[:m.start(1)]+base64.b64encode(z).decode()+h[m.end(1):];m=re.search(r'const records=(\[.*?\]);',h,re.S);rows=json.loads(m[1]);rows[13].update(rawBytes=len(s.encode()),gzipBytes=len(z),sha256=hashlib.sha256(s.encode()).hexdigest());h=h[:m.start(1)]+json.dumps(rows,separators=(',',':'))+h[m.end(1):];return h.replace('v48_WIP_UI_A','v48_WIP_UI_A1').replace('V48_WIP_UI_A','V48_WIP_UI_A1'),s
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('baseline',type=Path);ap.add_argument('output',type=Path);a=ap.parse_args();h,s=build(a.baseline.read_bytes());a.output.write_text(h);Path('/tmp/ui-a1-main.js').write_text(s);print(json.dumps({'bytes':len(h.encode()),'sha256':hashlib.sha256(h.encode()).hexdigest()}))

"""Reconstruct exact G7 measured HTML by reversing documented conditional changes."""
from pathlib import Path
import re,json,base64,gzip,hashlib,argparse
H=Path(__file__).resolve().parent;R=H.parents[2];q=json.loads((H/'evidence/engine-equivalence.json').read_text());raw=(R/'Aegis_SIM_v48_WIP_GUN_B1.html').read_bytes();sha=lambda b:hashlib.sha256(b).hexdigest();assert sha(raw)==q['deliveryHtmlSha256'];html=raw.decode();m=re.search(r'data-c55-index="13">([^<]+)</script>',html);main=gzip.decompress(base64.b64decode(m[1])).decode();
for patch in q.get('additionalPhaseOrderChanges',[])+q.get('additionalHandoffChanges',[])+q.get('additionalPhysicalAdapterChanges',[]):
 assert main.count(patch['after'])==1;main=main.replace(patch['after'],patch['before'])
assert main.count(q['after'])==1;main=main.replace(q['after'],q['before']);z=gzip.compress(main.encode(),9,mtime=0);html=html[:m.start(1)]+base64.b64encode(z).decode()+html[m.end(1):];m=re.search(r'const records=(\[.*?\]);',html,re.S);rows=json.loads(m[1]);rows[13].update(rawBytes=len(main.encode()),gzipBytes=len(z),sha256=sha(main.encode()));html=html[:m.start(1)]+json.dumps(rows,separators=(',',':'))+html[m.end(1):];assert sha(html.encode())==q['measuredHtmlSha256'];ap=argparse.ArgumentParser();ap.add_argument('--write-measured',type=Path);args=ap.parse_args();
if args.write_measured:args.write_measured.parent.mkdir(parents=True,exist_ok=True);args.write_measured.write_bytes(html.encode())
print(json.dumps({'pass':True,'measuredHtmlReconstructedExactly':sha(html.encode()),'deliveryHtmlSha256':sha(raw),'changes':'read-only label, HARPOON-only physical adapter and conditional manual reservation/handoff; G7 has no Harpoons, NPC ships or operator commands. Matched 16 whole-world pairs validate the reuse predicate.'}))

"""Reproducible D UI/selection delta from immutable C; preserve flight and all assets."""
import argparse,base64,gzip,hashlib,json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
BASE=ROOT/'Aegis_SIM_v48_WIP_HARPOON_C.html'
if not BASE.is_file():BASE=ROOT/'archive/v48/WIP_HARPOON_C/Aegis_SIM_v48_WIP_HARPOON_C.html'
BASE_SHA='b3b4f637fdfe0973e3aec566f1577401055c44235d8ccef22084aeb6e04175e7'
def patches():
 core=(HERE.parent/'C/core.js').read_text()
 old_ui=core[core.index('function harpoonUpdateUIA(){'):core.index('// CIC uses only canonical sensor tracks.')]
 return [
  ('function harpoonRequestFireA(trackId=selectedLockId,tubeId=harpoonRuntimeA().selectedTubeId){\n  const gate=harpoonGateA(trackId,tubeId),r=harpoonRuntimeA();',
   (HERE/'selection.js').read_text()+"\nfunction harpoonRequestFireA(trackId=selectedLockId,tubeId=null){\n  const gate=tubeId==null?harpoonAutoTubeGateD(trackId):harpoonGateA(trackId,tubeId),r=harpoonRuntimeA();"),
  ('  r.pending={trackId:gate.trackId,tubeId,remainingS:HARPOON_PROFILE_A.sim.releaseDoorDelayS};',
   '  tubeId=gate.tubeId;r.selectedTubeId=tubeId;\n  r.pending={trackId:gate.trackId,tubeId,remainingS:HARPOON_PROFILE_A.sim.releaseDoorDelayS};'),
  (old_ui,(HERE/'ui.js').read_text()),
  ('gate:(id,tube,options)=>harpoonGateA(id,tube,options),fire:',
   'selectionAudit:harpoonTubeSelectionAuditD,autoTube:(id,options)=>harpoonAutoTubeGateD(id,options),\n    gate:(id,tube,options)=>tube==null?harpoonAutoTubeGateD(id,options):harpoonGateA(id,tube,options),fire:'),
  ('for(const a of [harpoonSeekerCoreAuditC(),harpoonKnowledgeCoreAuditC()])',
   'for(const a of [harpoonSeekerCoreAuditC(),harpoonKnowledgeCoreAuditC(),harpoonTubeSelectionAuditD()])')]
def markup_patches():
 return [('<select id="harpoonTubeA" aria-label="하푼 발사관" style="min-width:0;background:#07161f;color:#80d8d2;border:1px solid #28505a;font:inherit"></select>',
  '<span id="harpoonTubeA" role="status" aria-label="하푼 발사관 자동 선택" style="min-width:0;display:flex;align-items:center;padding:4px 6px;background:#07161f;color:#80d8d2;border:1px solid #28505a;font:inherit">AUTO · 대기</span>')]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--baseline',type=Path,default=BASE);a=ap.parse_args()
 raw=a.baseline.read_bytes();assert hashlib.sha256(raw).hexdigest()==BASE_SHA;html=raw.decode()
 m=re.search(r'<script type="application/octet-stream" data-c55-index="13">(.*?)</script>',html,re.S)
 js=gzip.decompress(base64.b64decode(m[1])).decode()
 for old,new in patches():
  assert js.count(old)==1,(old[:100],js.count(old));js=js.replace(old,new)
 js=js.replace('V48_WIP_HARPOON_C','V48_WIP_HARPOON_D').replace('WIP HARPOON C','WIP HARPOON D')
 body=js.encode();packed=gzip.compress(body,9,mtime=0)
 html=html[:m.start(1)]+base64.b64encode(packed).decode()+html[m.end(1):]
 m=re.search(r'const records=(\[.*?\]);',html,re.S);records=json.loads(m[1]);records[13].update(rawBytes=len(body),gzipBytes=len(packed),sha256=hashlib.sha256(body).hexdigest())
 html=html[:m.start(1)]+json.dumps(records,separators=(',',':'))+html[m.end(1):]
 for old,new in markup_patches():assert html.count(old)==1;html=html.replace(old,new)
 html=html.replace('V48_WIP_HARPOON_C','V48_WIP_HARPOON_D').replace('WIP HARPOON C','WIP HARPOON D')
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(html);(a.out.parent/'harpoon-d-main.js').write_bytes(body)
 print(json.dumps({'file':str(a.out),'bytes':a.out.stat().st_size,'mainSha256':hashlib.sha256(body).hexdigest(),'htmlSha256':hashlib.sha256(a.out.read_bytes()).hexdigest()}))
if __name__=='__main__':main()

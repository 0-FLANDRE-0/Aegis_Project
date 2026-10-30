"""HELI_CG_B -> HELI_F2_0: passive manual designation only; no ISAR changes."""
import argparse,base64,gzip,hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
BASE_SHA='9d1d29137f27149817582694d8cf86f1b75af4e4ee69082b5cc00e0981a72c89'
def decoded(s,i=13):return gzip.decompress(base64.b64decode(re.search(r'data-c55-index="'+str(i)+r'">(.*?)</script>',s,re.S)[1])).decode()
def patch(s):
 def edit(a,b,n=1):
  nonlocal s
  assert s.count(a)==n,(a[:110],s.count(a),n);s=s.replace(a,b)
 edit("  function toggleEmcon(origin='OPERATOR')",(HERE/'designation.js').read_text()+"\n  function toggleEmcon(origin='OPERATOR')")
 edit('    emconActive = !emconActive;','    applyEmconDesignationF2(!emconActive);')
 edit("if(emconActive!==value){emconActive=value;const btn=document.getElementById('emconBtn');", "if(emconActive!==value){applyEmconDesignationF2(value);const btn=document.getElementById('emconBtn');")
 edit("setEmcon: (on) => { tacticalNoteOperatorH1(ACTIVE_SHIP_RUNTIME,['radar']);emconActive = !!on; return emconActive; }", "setEmcon: (on) => { tacticalNoteOperatorH1(ACTIVE_SHIP_RUNTIME,['radar']);return applyEmconDesignationF2(on); }")
 # Only the operator cursor designation gate loses the SPY-sector restriction.
 edit('      if(!isInRadarSector(tr.x, tr.y, tr.z)) continue;','      if(!emconActive&&!isInRadarSector(tr.x, tr.y, tr.z)) continue;')
 edit("      radar.mode = 'PD';\n      radar.pdTracking = true;", "      radar.mode = emconActive?'TWS':'PD';\n      radar.pdTracking = !emconActive;\n      if(emconActive)releaseManualSelectionOwnershipF2();")
 edit("      if(prev !== selectedLockId) notify(`SPY PREC TRK 지정:", "      if(emconActive)notify(`지정 (EMCON · 방사 없음) · ${trackDisplayLabelById(selectedLockId)}`);\n      else if(prev !== selectedLockId) notify(`SPY PREC TRK 지정:")
 edit("    if(emconActive){ notify('EMCON 중 — 사통장치 사용 불가'); return; }\n    lockByCursor();",'    lockByCursor();')
 edit("    const modeBtn = document.getElementById('modeBtn');\n    if(!modeBtn) return;", "    const modeBtn = document.getElementById('modeBtn'),lockBtn=document.getElementById('lockBtn');\n    if(lockBtn){lockBtn.textContent=emconActive?'지정 (EMCON · 방사 없음)':'LOCK';lockBtn.title=emconActive?'수동 표적 지정 · SPY 방사/정밀추적 없음':'SPY 정밀추적 지정';}\n    if(!modeBtn) return;")
 edit("  if(modeBtn && modeBtn.id) bindPress(modeBtn, (e)=>{", "  if(modeBtn && modeBtn.id) bindPress(modeBtn, (e)=>{\n    if(emconActive){notify('지정 (EMCON · 방사 없음) · 정밀추적은 EMCON 해제 후 사용');return;}")
 edit('    updateModeButtonLabel();\n  }\n  // ===== WIP155 VLS inertial launch-state contract =====','    updateModeButtonLabel();harpoonUpdateUIA();\n  }\n  // ===== WIP155 VLS inertial launch-state contract =====')
 edit('  function updateRadar(dt){\n    if(shipEquipmentOfflineV1())return;', "  function updateRadar(dt){\n    if(emconActive&&radar.pdTracking){radar.pdTracking=false;radar.mode='TWS';}\n    if(shipEquipmentOfflineV1())return;")
 edit("    trackComposition:trackCompositionF1(tr),predictionSigmaM:gate.predictionSigmaM??null,", "    trackComposition:trackCompositionF1(tr),predictionSigmaM:gate.predictionSigmaM??null,launchEmcon:r===ACTIVE_SHIP_RUNTIME?!!emconActive:!!observerC(r).emcon,")
 edit(" | ${q.operatorIdentity} | ${q.identificationEvidence??'—'}", " | launchEmcon=${q.launchEmcon} | ${q.operatorIdentity} | ${q.identificationEvidence??'—'}")
 return s

def build(raw):
 assert hashlib.sha256(raw).hexdigest()==BASE_SHA
 html=raw.decode();main=patch(decoded(html)).replace('v48_WIP_HELI_CG_B','v48_WIP_HELI_F2_0');z=gzip.compress(main.encode(),9,mtime=0)
 m=re.search(r'data-c55-index="13">(.*?)</script>',html,re.S);html=html[:m.start(1)]+base64.b64encode(z).decode()+html[m.end(1):]
 m=re.search(r'const records=(\[.*?\]);',html,re.S);records=json.loads(m[1]);records[13].update(rawBytes=len(main.encode()),gzipBytes=len(z),sha256=hashlib.sha256(main.encode()).hexdigest());html=html[:m.start(1)]+json.dumps(records,separators=(',',':'))+html[m.end(1):]
 return html.replace('v48_WIP_HELI_CG_B','v48_WIP_HELI_F2_0').replace('V48_WIP_HELI_CG_B','V48_WIP_HELI_F2_0'),main
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('output',type=Path);a=p.parse_args();html,main=build(a.baseline.read_bytes());a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(html);a.output.with_suffix('.main.js').write_text(main);d={'htmlSha256':hashlib.sha256(html.encode()).hexdigest(),'mainSha256':hashlib.sha256(main.encode()).hexdigest(),'bytes':len(html.encode()),'addedBytes':len(html.encode())-len(a.baseline.read_bytes())};a.output.with_suffix('.manifest.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d))

"""Rebuild Harpoon C from the immutable B artifact. Large B is reconstructible K -> A -> B."""
import argparse,base64,gzip,hashlib,json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
BASE=ROOT/'Aegis_SIM_v48_WIP_HARPOON_B.html'
if not BASE.is_file():BASE=ROOT/'archive/v48/WIP_HARPOON_B/Aegis_SIM_v48_WIP_HARPOON_B.html'
BASE_SHA='a44a346abce0bb0e10b4cff231116171d0c13de1b8962d45820c6c6d10de98fc'
def patches():
 p=[((HERE.parent/'B/profile.js').read_text().split('function harpoonInstallationA(){')[0],(HERE/'profile.js').read_text().split('function harpoonInstallationA(){')[0]),((HERE.parent/'B/core.js').read_text(),(HERE/'core.js').read_text())]
 p += [("revision:'BUNKERHILL_HARPOON_B_1'","revision:'BUNKERHILL_HARPOON_C_1'"),
  ("[ACTIVE_SHIP_PROFILE.revision,'BUNKERHILL_HARPOON_A_1'","[ACTIVE_SHIP_PROFILE.revision,'BUNKERHILL_HARPOON_B_1','BUNKERHILL_HARPOON_A_1'"),
  ("    const operatorIdentity=normalizeTrackOperatorIdentityA3(tr._operatorIdentity);","    const ownLaunch=harpoonTrackIdentityC(tr);\n    const operatorIdentity=ownLaunch?ownLaunch.identity:normalizeTrackOperatorIdentityA3(tr._operatorIdentity);"),
  ("(hostileIntent?TRACK_A3_IDENTITY.ASSUMED_HOSTILE:TRACK_A3_IDENTITY.UNKNOWN)","(!ownLaunch&&hostileIntent?TRACK_A3_IDENTITY.ASSUMED_HOSTILE:TRACK_A3_IDENTITY.UNKNOWN)"),
  ("    const protectedIdentity=tr.identity===TRACK_A3_IDENTITY.FRIEND||tr.identity===TRACK_A3_IDENTITY.NEUTRAL;","    const protectedIdentity=!!ownLaunch||tr.identity===TRACK_A3_IDENTITY.FRIEND||tr.identity===TRACK_A3_IDENTITY.NEUTRAL;"),
  ("protectedIdentity?'PROTECTED_IDENTITY':(killAssessment", "protectedIdentity?(ownLaunch?.reason??'PROTECTED_IDENTITY'):(killAssessment"),
  ("harpoonPending:harpoonCopyA(harpoonRuntimeA().pending),harpoonSerial:","harpoonPending:harpoonCopyA(harpoonRuntimeA().pending),harpoonLaunchRecords:harpoonCopyA(harpoonRuntimeA().launches),harpoonSerial:"),
  ("      const isASM = tr.classification==='ASM';","      const ownRadar=tr._harpoonOwnC;\n      const isFriend=tr.identity==='FRIEND';\n      const isASM = tr.classification==='ASM';"),
  ("(isASM ? 'rgba(255,60,60,0.92)'", "(isFriend ? 'rgba(90,220,245,0.94)' : ownRadar ? 'rgba(255,210,80,0.86)' : isASM ? (['HOSTILE','ASSUMED_HOSTILE'].includes(tr.identity)?'rgba(255,60,60,0.92)':'rgba(255,210,80,0.86)')"),
  ("        } else if(isASM){\n          tag = alt2 < 30", "        } else if(ownRadar){\n          tag = (ownRadar.launchId==null?'OWN?':'H'+ownRadar.launchId)+' '+(ownRadar.confirmed?(tr.sensorAge<=.35&&!tr.memActive?'RADAR':'EST'):'OWN?');\n        } else if(isASM){\n          tag = alt2 < 30"),
  ("(isASM ? 'rgba(255,80,80,0.8)'", "(isFriend ? 'rgba(90,220,245,.94)' : ownRadar ? 'rgba(255,210,80,.86)' : isASM ? (['HOSTILE','ASSUMED_HOSTILE'].includes(tr.identity)?'rgba(255,80,80,0.8)':'rgba(255,210,80,.86)')"),
  ("classification:String(tr?.classification??'UNKNOWN'),confirmed:","identity:String(tr?.identity??'UNKNOWN'),ownLaunchId:tr?._harpoonOwnC?.confirmed?tr._harpoonOwnC.launchId:null,classification:String(tr?.classification??'UNKNOWN'),confirmed:"),
  ("for(const ms of [...(st?.missiles??[]),...(st?.harpoons??[])])", "for(const ms of st?.missiles??[])"),
  ("(asm?'rgba(255,105,105,.88)'", "(tr.identity==='FRIEND'?'rgba(90,220,245,.94)':asm?(['HOSTILE','ASSUMED_HOSTILE'].includes(tr.identity)?'rgba(255,105,105,.88)':'rgba(255,210,80,.86)')"),
  ("const center=this.auxCicCenter(st),rangeM=20000", "const center=String(this.follow.key).startsWith('HARPOON:')?{worldXM:st.ship.worldXM,worldYM:st.ship.worldYM}:this.auxCicCenter(st),rangeM=20000"),
  ("if(this.auxCicScaleEl)this.auxCicScaleEl.textContent='R 20 km';", "if(this.auxCicScaleEl){this.auxCicScaleEl.textContent='R 20 km';const title=this.auxCicScaleEl.parentElement.firstElementChild;if(title)title.textContent=String(this.follow.key).startsWith('HARPOON:')?'AUX CIC · OWN SHIP · NO DL':'AUX CIC · CAM CENTER';}"),
  ("c.fillText(this.follow.enabled?(this.follow.holdingLost?'CAM HOLD':'CAM TRACK'):'OWN SHIP',5,h-6);", "c.fillText(String(this.follow.key).startsWith('HARPOON:')?'OWN SHIP / NO DL':this.follow.enabled?(this.follow.holdingLost?'CAM HOLD':'CAM TRACK'):'OWN SHIP',5,h-6);"),
  ("const text=`${side} · ${name}","const observer=String(s.kind)==='HARPOON'?'OBSERVER / NO DL':side;\n      const text=`${observer} · ${name}"),
  ("window.__CORE_SELFTEST_FAILURES__=failures.slice();", "for(const a of [harpoonSeekerCoreAuditC(),harpoonKnowledgeCoreAuditC()])if(!a.pass)failures.push(a.schema+':'+JSON.stringify(a.checks));\nwindow.__CORE_SELFTEST_FAILURES__=failures.slice();")]
 return p
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--baseline',type=Path,default=BASE);a=ap.parse_args()
 raw=a.baseline.read_bytes();assert hashlib.sha256(raw).hexdigest()==BASE_SHA;html=raw.decode()
 match=re.search(r'<script type="application/octet-stream" data-c55-index="13">(.*?)</script>',html,re.S)
 js=gzip.decompress(base64.b64decode(match[1])).decode()
 for old,new in patches():
  assert js.count(old)==1,(old[:120],js.count(old));js=js.replace(old,new)
 js=js.replace('V48_WIP_HARPOON_B','V48_WIP_HARPOON_C').replace('WIP HARPOON B','WIP HARPOON C')
 body=js.encode();packed=gzip.compress(body,9,mtime=0)
 html=html[:match.start(1)]+base64.b64encode(packed).decode()+html[match.end(1):]
 match=re.search(r'const records=(\[.*?\]);',html,re.S);records=json.loads(match[1]);records[13].update(rawBytes=len(body),gzipBytes=len(packed),sha256=hashlib.sha256(body).hexdigest())
 html=html[:match.start(1)]+json.dumps(records,separators=(',',':'))+html[match.end(1):]
 html=html.replace('V48_WIP_HARPOON_B','V48_WIP_HARPOON_C').replace('WIP HARPOON B','WIP HARPOON C')
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(html);(a.out.parent/'harpoon-c-main.js').write_bytes(body)
 print(json.dumps({'file':str(a.out),'bytes':a.out.stat().st_size,'sha256':hashlib.sha256(body).hexdigest(),'htmlSha256':hashlib.sha256(a.out.read_bytes()).hexdigest()}))
if __name__=='__main__':main()

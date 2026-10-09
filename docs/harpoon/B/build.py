"""Apply B presentation and the requested booster tuning to the verified A artifact."""
import argparse,base64,gzip,hashlib,json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
BASE=ROOT/'archive/v48/WIP_HARPOON_A/Aegis_SIM_v48_WIP_HARPOON_A.html'
if not BASE.is_file():BASE=ROOT/'Aegis_SIM_v48_WIP_HARPOON_A.html'
SHA='ffd976a211c530bc4d193597751e49febbd755646b865e6ad2685cd9e06aab77'
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--baseline',type=Path,default=BASE);a=ap.parse_args()
 raw=a.baseline.read_bytes();assert hashlib.sha256(raw).hexdigest()==SHA;html=raw.decode()
 match=re.search(r'<script type="application/octet-stream" data-c55-index="13">(.*?)</script>',html,re.S)
 js=gzip.decompress(base64.b64decode(match[1])).decode();old=(HERE.parent/'A/renderer.js').read_text();assert js.count(old)==1
 js=js.replace(old,(HERE/'renderer.js').read_text())
 for module in ['profile.js','core.js']:
  old=(HERE.parent/'A'/module).read_text();assert js.count(old)==1,module
  js=js.replace(old,(HERE/module).read_text())
 assert js.count("revision:'BUNKERHILL_HARPOON_A_1'")==1
 js=js.replace("revision:'BUNKERHILL_HARPOON_A_1'","revision:'BUNKERHILL_HARPOON_B_1'")
 anchor="[ACTIVE_SHIP_PROFILE.revision,'BUNKERHILL_LATE_G_1','BUNKERHILL_LATE_D_1']";assert js.count(anchor)==1
 js=js.replace(anchor,"[ACTIVE_SHIP_PROFILE.revision,'BUNKERHILL_HARPOON_A_1','BUNKERHILL_LATE_G_1','BUNKERHILL_LATE_D_1']")
 anchor='function harpoonInstallationA(){';assert js.count(anchor)==1
 js=js.replace(anchor,(HERE/'visual-profile.js').read_text()+'\n'+anchor)
 anchor='min:view._c5Focus?8:18';assert js.count(anchor)==1
 js=js.replace(anchor,"min:view.follow.enabled&&String(view.follow.key).startsWith('HARPOON:')?4:(view._c5Focus?8:18)")
 anchor='window.__CORE_SELFTEST_FAILURES__=failures.slice();'
 assert js.count(anchor)==1
 js=js.replace(anchor,"const harpoonVisualAuditB=harpoonVisualCoreAuditB();if(!harpoonVisualAuditB.pass)failures.push('HARPOON_VISUAL_B_CORE:'+JSON.stringify(harpoonVisualAuditB.checks));\n"+anchor)
 js=js.replace('V48_WIP_HARPOON_A','V48_WIP_HARPOON_B').replace('WIP HARPOON A','WIP HARPOON B')
 body=js.encode();packed=gzip.compress(body,9,mtime=0);html=html[:match.start(1)]+base64.b64encode(packed).decode()+html[match.end(1):]
 match=re.search(r'const records=(\[.*?\]);',html,re.S);records=json.loads(match[1]);records[13].update(rawBytes=len(body),gzipBytes=len(packed),sha256=hashlib.sha256(body).hexdigest())
 html=html[:match.start(1)]+json.dumps(records,separators=(',',':'))+html[match.end(1):]
 asset=base64.b64encode(gzip.compress((HERE/'mouth-registration.json').read_bytes(),9,mtime=0)).decode()
 html=html.replace('</body>','<script id="harpoon-mouth-registration-b" type="application/octet-stream">'+asset+'</script>\n</body>')
 html=html.replace('V48_WIP_HARPOON_A','V48_WIP_HARPOON_B').replace('WIP HARPOON A','WIP HARPOON B')
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(html);(a.out.parent/'harpoon-b-main.js').write_bytes(body)
 print(json.dumps({'file':str(a.out),'bytes':a.out.stat().st_size,'sha256':hashlib.sha256(a.out.read_bytes()).hexdigest(),'mainSha256':hashlib.sha256(body).hexdigest()}))
if __name__=='__main__':main()

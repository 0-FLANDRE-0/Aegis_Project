"""Pinned HELI_F1 -> HELI_CG_A. Main packed13 only, shared source assets intact."""
import argparse,base64,gzip,hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
BASE_SHA='913d7d611c827ade8f62d5671d811404506c4f2923c9b9a37c3e7b3cf91724f2'
def decoded(s,i=13):return gzip.decompress(base64.b64decode(re.search(r'data-c55-index="'+str(i)+r'">(.*?)</script>',s,re.S)[1])).decode()
def patch(s):
 def rep(a,b,n=1):
  nonlocal s
  assert s.count(a)==n,(a[:90],s.count(a),n);s=s.replace(a,b)
 rep((ROOT/'docs/helicopter/F/runtime.js').read_text(),(HERE/'runtime.js').read_text())
 # One facility resolver for the live ground state machine and render adapter.
 rep("if(view.heloDoorsA||!view._c5Asset||!root)return;const T=view.THREE,F=HELO_FACILITY_A,wallParts=", "if(!root)return;const F=heloFacilityA(root.userData.shipProfileId);if(!F)return;if(view.heloDoorsA?.root===root)return;if(view.heloDoorsA)heloDisposeDoorsI(view);\n  if(root.userData.shipProfileId==='CG_52_LATE_TICONDEROGA'){if(view._bunkerAsset)heloBuildCgHangarI(view,root,F);return;}\n  if(!view._c5Asset)return;const T=view.THREE,wallParts=")
 a=s.index('  function split(poly,axis,bound,sign)',s.index('function heloCutDoorsA('));b=s.index('  const doorPlane=',a);s=s[:a]+'  const split=heloClipPolygonI;\n'+s[b:]
 rep('view.heloDoorsA={doors,geo,mat,changedMeshes:changed,removedPolygons:removed,relocatedStairTriangles,dummy:new T.Object3D()};','view.heloDoorsA={root,facility:F,doors,geo,mat,changedMeshes:changed,removedPolygons:removed,relocatedStairTriangles,dummy:new T.Object3D()};')
 rep('const d=view.heloDoorsA;if(!d)return;const F=HELO_FACILITY_A,height=',"const d=view.heloDoorsA;if(!d)return;if(d.facility.doorStyle==='CG_SHARED_OVERHEAD_FOLD'){heloSyncFoldingDoorI(view,values);return;}const F=d.facility,height=")
 rep('(slot===0?-1:1)*F.bayOffsetM);d.dummy.scale.set','heloDoorCenterI(slot,F));d.dummy.scale.set')
 rep("if(root.userData.shipProfileId==='DDG_119_LATE_FLIGHT_IIA'&&!this.ownerRuntime)heloCutDoorsA(this,root);", "if(heloFacilityA(root.userData.shipProfileId)&&!this.ownerRuntime)heloCutDoorsA(this,root);")
 rep('aircraft:[...world.values()].filter(h=>h.visible).map',"aircraft:[...world.values()].filter(h=>h.visible||(heloDoorCountI()===1&&h.onboard&&l.doors.some(open=>open>0))).map")
 rep("host.textContent='DDG-119 항공 운용'", "host.textContent='이 함정 항공 운용 미지원'")
 rep('function heloCutDoorsA(view,root=view.shipRoot){',(HERE/'hangar-render.js').read_text()+'\nfunction heloCutDoorsA(view,root=view.shipRoot){')
 # Existing facility contract keeps old damage geometry, with explicit operational registration.
 rep('r.aviation.facilities={hangar:profile.geometry.aft.hangar,flightDeck:profile.geometry.hardpoints.flightDeck};','r.aviation.facilities={hangar:profile.geometry.aft.hangar,flightDeck:profile.geometry.hardpoints.flightDeck,flightOperations:heloFacilityA(profile.id)};')
 rep('r.aviation.facilities={hangar:ACTIVE_SHIP_PROFILE.geometry.aft.hangar,flightDeck:ACTIVE_SHIP_PROFILE.geometry.hardpoints.flightDeck};','r.aviation.facilities={hangar:ACTIVE_SHIP_PROFILE.geometry.aft.hangar,flightDeck:ACTIVE_SHIP_PROFILE.geometry.hardpoints.flightDeck,flightOperations:heloFacilityA()};')
 return s

def build(raw):
 assert hashlib.sha256(raw).hexdigest()==BASE_SHA
 html=raw.decode();main=patch(decoded(html)).replace('v48_WIP_HELI_F1','v48_WIP_HELI_CG_A');z=gzip.compress(main.encode(),9,mtime=0)
 m=re.search(r'data-c55-index="13">(.*?)</script>',html,re.S);html=html[:m.start(1)]+base64.b64encode(z).decode()+html[m.end(1):]
 m=re.search(r'const records=(\[.*?\]);',html,re.S);records=json.loads(m[1]);records[13].update(rawBytes=len(main.encode()),gzipBytes=len(z),sha256=hashlib.sha256(main.encode()).hexdigest());html=html[:m.start(1)]+json.dumps(records,separators=(',',':'))+html[m.end(1):]
 return html.replace('v48_WIP_HELI_F1','v48_WIP_HELI_CG_A').replace('V48_WIP_HELI_F1','V48_WIP_HELI_CG_A'),main
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('output',type=Path);a=p.parse_args();html,main=build(a.baseline.read_bytes());a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(html);a.output.with_suffix('.main.js').write_text(main);d={'htmlSha256':hashlib.sha256(html.encode()).hexdigest(),'mainSha256':hashlib.sha256(main.encode()).hexdigest(),'bytes':len(html.encode()),'addedBytes':len(html.encode())-len(a.baseline.read_bytes())};a.output.with_suffix('.manifest.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d))

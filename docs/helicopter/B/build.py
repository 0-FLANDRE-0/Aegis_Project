"""Pinned PERF_F → HELI_A. New movement/UI/read-only model presentation only."""
import argparse,base64,gzip,hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
BASE_SHA='4571ed015469a48a0cc3ab96b4ee4e3d72c05257d2943a88fdd39272292583d5'
OLD='v48_WIP_PERF_F';NEW='v48_WIP_HELI_A';PATCHES=[]
def once(s,a,b,label):
 assert s.count(a)==1,(label,s.count(a));PATCHES.append(label);return s.replace(a,b,1)
def decoded(s,i=13):return gzip.decompress(base64.b64decode(re.search(r'data-c55-index="'+str(i)+r'">(.*?)</script>',s,re.S)[1])).decode()
def patch(s):
 module='\n'.join((HERE/f).read_text()for f in ['motion.js','runtime.js','ui.js'])
 s=once(s,"const canvas = document.getElementById('c');",module+"\nconst canvas = document.getElementById('c');",'helicopter point mass and owner state')
 s=s.replace("['NAV','ARM','FLEET','DEBUG']","['NAV','ARM','FLEET','AIR','DEBUG']").replace("Object.freeze(['NAV','ARM','FLEET','DEBUG'])","Object.freeze(['NAV','ARM','FLEET','AIR','DEBUG'])")
 s=s.replace("FLEET:'PAN_ONLY_NO_MAP_COMMAND',DEBUG:","FLEET:'PAN_ONLY_NO_MAP_COMMAND',AIR:'HELICOPTER_POSITION_ONLY',DEBUG:")
 s=once(s,"inputMode=next==='NAV'?'NAV':(next==='ARM'?'AIM':'DEBUG');","inputMode=next==='NAV'?'NAV':next==='AIR'?'AIR':(next==='ARM'?'AIM':'DEBUG');",'explicit AIR map input')
 s=once(s,"if(harpoonRouteEditingE()&&controlDeckActiveTabWip13C!=='FLEET'){","if(controlDeckActiveTabWip13C==='AIR'){\n      heloMapTapA(worldX,worldY);\n    } else if(harpoonRouteEditingE()&&controlDeckActiveTabWip13C!=='FLEET'){",'AIR cannot place ship or Harpoon waypoints')
 s=once(s,'_ptrMoved = harpoonRouteEditingE()&&e.isPrimary===false;','_ptrMoved = (harpoonRouteEditingE()||controlDeckActiveTabWip13C===\'AIR\')&&e.isPrimary===false;','multi touch cannot accidentally retarget aircraft')
 s=s.replace("pages.length===4&&tabs.length===4","pages.length===5&&tabs.length===5")
 s=once(s,'  mountNetworkUiG();','  mountNetworkUiG();heloMountUiA();','native AIR page')
 s=once(s,'    drawRescueRaftsCicK();drawNetworkPictureG();','    drawRescueRaftsCicK();drawNetworkPictureG();heloDrawMapA();','owned helo map overlay, independent of radar')
 s=once(s,'    updateInfoStrip();','    updateInfoStrip();heloUpdateUiA();','throttled AIR status')
 s=once(s,'    simStepCounter++;\n    // C11:','    heloFixedStepA(dt);\n    simStepCounter++;\n    // C11:','60 Hz helicopter update, unchanged existing phases')
 s=once(s,'    harpoonResetA(true);','    heloResetA();harpoonResetA(true);','session reset retires helo poses and queue')
 s=once(s,'...lightshipNodes,...fixedNodes,...liquidNodes','...lightshipNodes,...fixedNodes.map(q=>sources.fixedNodeTransform?sources.fixedNodeTransform(q):q),...liquidNodes','event driven aircraft mass ownership')
 s=once(s,'{weaponNodes:shipMassWeaponNodesV32}', '{weaponNodes:shipMassWeaponNodesV32,fixedNodeTransform:heloMassNodeA}', 'player aviation mass transform')
 s=once(s,'aviation:{inventory:jsonSafeCloneV48Wip11A(ACTIVE_SHIP_RUNTIME.aviation.inventory),facilities:jsonSafeCloneV48Wip11A(ACTIVE_SHIP_RUNTIME.aviation.facilities)}','aviation:heloExportA()','detached aircraft operational state')
 s=once(s,'    const harpoonMigrations=[];','    const harpoonMigrations=[];heloMigrateSaveA(src,harpoonMigrations);','explicit migration of legacy empty inventory')
 s=once(s,"operationalErrorV48Wip11B(errors,'AVIATION_INVENTORY');}","operationalErrorV48Wip11B(errors,'AVIATION_INVENTORY');heloValidateSaveA(aviation,errors);}",'strict helo preflight before writes')
 old='ACTIVE_SHIP_RUNTIME.aviation.inventory=Array.isArray(src.ship.aviation?.inventory)?src.ship.aviation.inventory.map(q=>({...q})):[];'
 s=once(s,old,old+'heloRestoreA(src.ship.aviation);','restore aircraft and queue after complete preflight')
 s=once(s,'      lifeRafts:rescueRenderStatesK(),','      helicopters:heloRenderStateA(),lifeRafts:rescueRenderStatesK(),','read-only render contract')
 loader=(ROOT/'docs/helicopter/A/asset_loader.js').read_text();render=(HERE/'render.js').read_text().replace('__HELO_RIG_JSON__',json.dumps(json.loads((HERE/'rig.json').read_text()),separators=(',',':')))
 s=once(s,'installPhysicalFleetRendererB(WIP148_EXTERNAL_3D);','installPhysicalFleetRendererB(WIP148_EXTERNAL_3D);\n'+loader+'\n'+render+'\ninstallHeloRendererA(WIP148_EXTERNAL_3D);','install asset display and camera adapter')
 return s
def main():
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('output',type=Path);a=p.parse_args();raw=a.baseline.read_bytes();assert hashlib.sha256(raw).hexdigest()==BASE_SHA;html=raw.decode();main=patch(decoded(html)).replace(OLD,NEW);gz=gzip.compress(main.encode(),9,mtime=0)
 m=re.search(r'data-c55-index="13">(.*?)</script>',html,re.S);html=html[:m.start(1)]+base64.b64encode(gz).decode()+html[m.end(1):]
 m=re.search(r'const records=(\[.*?\]);',html,re.S);records=json.loads(m[1]);records[13].update(rawBytes=len(main.encode()),gzipBytes=len(gz),sha256=hashlib.sha256(main.encode()).hexdigest());html=html[:m.start(1)]+json.dumps(records,separators=(',',':'))+html[m.end(1):]
 html=html.replace(OLD,NEW).replace('V48_WIP_PERF_F','V48_WIP_HELI_A');asset=(ROOT/'docs/helicopter/A/seahawk-render-a1.bin.gz').read_bytes();data='<script id="helo-render-a1" type="application/octet-stream">'+base64.b64encode(asset).decode()+'</script>\n'
 html=once(html,'</body>',data+'</body>','embed single shared helicopter data');a.output.write_text(html);a.output.with_suffix('.main.js').write_text(main);a.output.with_suffix('.manifest.json').write_text(json.dumps({'baselineSha256':BASE_SHA,'htmlSha256':hashlib.sha256(html.encode()).hexdigest(),'mainSha256':hashlib.sha256(main.encode()).hexdigest(),'changedPackedAssets':[13],'assetSha256':hashlib.sha256(asset).hexdigest(),'patches':PATCHES},indent=2)+'\n');print(json.dumps({'bytes':len(html.encode()),'sha256':hashlib.sha256(html.encode()).hexdigest(),'patches':PATCHES}))
if __name__=='__main__':main()

// SIM_TUNED: functional 24-parent flooding topology, not surveyed watertight rooms.
function sovInteriorAuthoredA(flood,geometry){
 const spaces=[],portals=[],equipmentNodes=[],decks=[{id:'L1',label:'보일러·기관층',z0:-2.5,z1:-.5,color:0x6b9fb8},{id:'MAIN',label:'거주·작업층',z0:-.3,z1:1.7,color:0x729e89},{id:'UPPER',label:'지휘·지원층',z0:1.9,z1:4.1,color:0x9d927b},{id:'S1',label:'상부구조',z0:5.2,z1:7.4,color:0xaa9d73},{id:'S2',label:'상부 운용층',z0:8.2,z1:10.4,color:0xb7a382},{id:'B1',label:'함교',z0:12,z1:14.2,color:0xc3a980}],byId=new Map();
 const freeze=deepFreezeShipProfileV48Wip09;
 function add(id,label,deck,x0,x1,y0,y1,kind,system,z0,z1,ek='HULL'){
  const d=decks.find(d=>d.id===deck);z0??=d.z0;z1??=d.z1;
  let lo=y0,hi=y1;
  for(let i=0;i<=4;i++)for(let j=0;j<=2;j++){
   const q=geometry.intervals(x0+(x1-x0)*i/4,z0+(z1-z0)*j/2,ek,.12),mid=(y0+y1)/2,r=q.find(r=>mid>=r[0]&&mid<=r[1]);if(!r)return null;lo=Math.max(lo,r[0]);hi=Math.min(hi,r[1]);
  }
  if(hi-lo<.45)return null;
  const center={x:(x0+x1)/2,y:(lo+hi)/2,z:(z0+z1)/2},parent=flood.cellAt({...center,z:Math.min(2,center.z)}),s=freeze({id:'sov.'+id,macroId:'sov.'+id,label,deck,kind,system,x0,x1,y0:lo,y1:hi,z0,z1,center,volumeM3:(x1-x0)*(hi-lo)*(z1-z0),parentFloodCellId:parent?.id??null,segmentIndex:0,segmentCount:1,routeable:true,occupiable:kind!=='PASSAGE',capacity:24,watertightClass:deck==='L1'?'WT':'WEATHERTIGHT',fireZone:deck+'.'+id,envelopeKind:ek,geometryBasis:'MODEL_REGISTRATION_CONTAINMENT__SIM_TUNED_TOPOLOGY'});
  spaces.push(s);byId.set(s.id,s);
  if(system&&kind!=='MAGAZINE')equipmentNodes.push(freeze({id:'sov.eq.'+id,spaceId:s.id,macroSpaceId:s.id,label,system,role:kind==='MACHINERY'?'PLANT':'OPERATOR_CONSOLE',criticality:'ESSENTIAL',position:center}));return s;
 }
 function link(a,b,kind='WATERTIGHT_DOOR'){
  if(!a||!b)return;
  portals.push(freeze({id:'sov.portal.'+portals.length,a:a.id,b:b.id,kind,axis:a.deck===b.deck?'X':'Z',position:{x:(a.center.x+b.center.x)/2,y:(a.center.y+b.center.y)/2,z:(a.center.z+b.center.z)/2},widthM:1,heightM:2,normallyOpen:true,automatic:true,watertight:kind==='WATERTIGHT_DOOR',fireRated:kind==='FIRE_DOOR',stretcherPassable:true,routeLengthM:Math.hypot(a.center.x-b.center.x,a.center.y-b.center.y,a.center.z-b.center.z),basis:'SIM_TUNED_FUNCTIONAL_ACCESS'}));
 }
 const rows=[['aft.mag','후방 함포·함대공 탄약고','MAGAZINE','AMMO_AFT'],['engine.aft','후방 기관실','MACHINERY','ENGINE_AFT'],['boiler.aft','후방 보일러실','MACHINERY','BOILER_2'],['engine.fwd','전방 기관실','MACHINERY','ENGINE_FWD'],['boiler.fwd','전방 보일러실','MACHINERY','BOILER_1'],['fwd.mag','전방 함포·함대공 탄약고','MAGAZINE','AMMO_FWD']];
 const bounds=[-58,-40,-22,-4,14,32,50],passages=[];
 for(const d of decks.slice(0,3))for(let i=0;i<6;i++){
  const a=bounds[i]+.15,b=bounds[i+1]-.15,pass=add(d.id+'.pass.'+i,'종통로 '+(i+1),d.id,a,b,-.55,.55,'PASSAGE',null);if(pass)passages.push(pass);
  if(i)link(byId.get('sov.'+d.id+'.pass.'+(i-1)),pass);
  for(const [side,ya,yb]of [['P',-7.2,-.75],['S',.75,7.2]]){
   let [id,label,kind,system]=d.id==='L1'?rows[i]:d.id==='MAIN'?['berth.'+i,'거주·보급구 '+(i+1),'HABITABLE','STORES']:['support.'+i,'지휘·지원구 '+(i+1),'CONTROL','CDC'];
   if(d.id==='L1'&&i===1&&side==='P'){system='BOILER_2';label='보일러실 2';id='boiler.2';}
   if(d.id==='L1'&&i===2){system=side==='P'?'BOILER_3':'BOILER_4';label='보일러실 '+(side==='P'?'3':'4');id='boiler.'+system;}
   if(d.id==='MAIN'&&[1,2,3,4].includes(i)){id='gen.'+i;label=(i<=2?'터빈':'디젤')+' 발전기실 '+i;system='GEN_'+i;kind='MACHINERY';}
   if(d.id==='MAIN'&&i===0&&side==='P'){id='medical';label='의무실';system='MEDICAL';kind='MEDICAL';}
   if(d.id==='UPPER'&&i===4){id='cic';label='전투정보·지휘소';system='CDC';}
   if(d.id==='UPPER'&&i===3){id='asm.mag';label='대함 탄약 지원구';system='AMMO_ASM';kind='MAGAZINE';}
   link(pass,add(d.id+'.'+id+'.'+side,label+' '+side,d.id,a,b,ya,yb,kind,system),'FIRE_DOOR');
  }
  if(d.id==='MAIN')link(byId.get('sov.L1.pass.'+i),pass,'STAIR');
  if(d.id==='UPPER')link(byId.get('sov.MAIN.pass.'+i),pass,'STAIR');
 }
 // Source-contained hangar and bridge; no Ka-27 or door/launch system installed.
 for(const [deck,z0,z1]of [['S1',5.6,7.8],['S2',8.2,10.4]]){
  let previous=null;
  for(let i=0;i<5;i++){const x0=-12+i*8+.12,x1=x0+7.76,pass=add(deck+'.pass.'+i,'상부 통로',deck,x0,x1,-.55,.55,'PASSAGE',null,z0,z1,'all');if(!pass)continue;link(previous,pass);previous=pass;link(passages.reduce((a,b)=>Math.abs(b.center.x-pass.center.x)<Math.abs(a.center.x-pass.center.x)?b:a),pass,'STAIR');
   for(const [side,ya,yb]of [['P',-5,-.75],['S',.75,5]])link(pass,add(deck+'.support.'+i+'.'+side,i===4?'함교 지원실':i===2?'기관제어실':'지휘·통신 지원실',deck,x0,x1,ya,yb,'CONTROL',i===2?'ENGINE_CONTROL':'CDC',z0,z1,'all'),'FIRE_DOOR');
  }
 }
 const hangar=add('hangar','격납고','S1',-26,-14,-2.5,2.5,'HANGAR_BAY','AVIATION',5.6,8.8,'all'),bridge=add('bridge','함교·조타실','B1',2,12,-2.5,2.5,'CONTROL','BRIDGE',12,14.2,'all');
 for(const s of [hangar,bridge])if(s)link(passages.reduce((a,b)=>Math.abs(b.center.x-s.center.x)<Math.abs(a.center.x-s.center.x)?b:a),s,'STAIR');
 return {decks:freeze(decks),spaces:freeze(spaces),macroSpaces:freeze(spaces.slice()),portals:freeze(portals),equipmentNodes:freeze(equipmentNodes),byId};
}
function sovCrewPostsA(topology){
 if(topology){const spaces=topology.spaces,find=(test)=>spaces.filter(test),table={ENGINEERING:find(s=>s.kind==='MACHINERY'),COMBAT:find(s=>s.system==='CDC'),OPERATIONS:find(s=>s.system==='BRIDGE'||s.kind==='CONTROL'),AVIATION:find(s=>s.kind==='HANGAR_BAY'),SUPPORT:find(s=>['HABITABLE','MEDICAL'].includes(s.kind)),COMMAND:find(s=>s.system==='BRIDGE')},out={};for(const [id,label,count]of SOVREMENNY_956_PROFILE.crew.departments){const a=table[id].length?table[id]:spaces.filter(s=>s.occupiable);out[id]=Array.from({length:count},(_,i)=>({spaceId:a[i%a.length].id,count:1,label}));}out.medicalSpaceId=spaces.find(s=>s.kind==='MEDICAL')?.id;out.abandonSpaceId=spaces.find(s=>s.deck==='UPPER')?.id;out.teamStaging=[[out.ENGINEERING[0].spaceId],[out.ENGINEERING[1].spaceId],[out.SUPPORT[0].spaceId]];return out;}
 const p=(spaceId,count,label)=>({spaceId:'sov.'+spaceId,count,label});
 return {ENGINEERING:[p('L1.engine.aft.P',30,'후방 기관 당직'),p('L1.engine.fwd.S',30,'전방 기관 당직'),p('L1.boiler.fwd.P',25,'전방 보일러 당직'),p('MAIN.gen.1.P',25,'발전 당직')],COMBAT:[p('UPPER.cic.P',40,'CIC'),p('UPPER.cic.S',40,'지휘지원')],OPERATIONS:[p('bridge',60,'함교 당직')],AVIATION:[p('hangar',10,'격납고 정비')],SUPPORT:[p('MAIN.medical.P',25,'의무'),p('MAIN.berth.5.S',30,'보급')],COMMAND:[p('bridge',5,'지휘부')],medicalSpaceId:'sov.MAIN.medical.P',abandonSpaceId:'sov.UPPER.pass.0',teamStaging:[['sov.MAIN.pass.1'],['sov.MAIN.pass.3'],['sov.MAIN.pass.4']]};
}
function sovMaterialBoxA(b){
 const shell=b.system==='HULL_SKIN',mm=shell?12:6;
 return {...b,renderClass:shell?'HULL':b.system==='STRUCTURE'?'STRUCT':'EQUIPMENT',damageVulnerability:1,blastVulnerability:.3,penetrationResistanceMJ:.25,materialProfileId:shell?'SHELL_UPPER':'EQUIPMENT_CASING',boundaryKind:shell?'EXTERNAL_SHELL':'SUPERSTRUCTURE_WALL',materialId:'GRADE_A_STEEL',thicknessMm:mm,linerThicknessMm:0,fuzeStimulusRhaeMm:mm*.62,arealDensityKgM2:mm*7.85,fragmentTransmission01:1,rearSpallTransmission01:1,watertight:shell,fireRated:false,materialLayers:[{materialId:'GRADE_A_STEEL',thicknessMm:mm,directPenetration:true}],geometryRegistration:'SOV_A_OFFLINE',provenance:'SIM_TUNED_ESTIMATED_STEEL_AND_SCANTLING_NOT_PUBLIC_ARMOR_DATA'};
}
function sovGeometryA(profile){
 const boxes=SOV_REG_A.hitboxes.map(sovMaterialBoxA),div=profile.damage.flood.sectionDivisions;
 // Functional machinery boxes share damage-system IDs consumed by the common
 // speed/power pipeline. Four boiler rooms and four generators are physical rooms.
 for(const [id,x,z]of [['BOILER_1',22,-2],['BOILER_2',-22,-2],['BOILER_3',-13,-2],['BOILER_4',-13,-2],['ENGINE_FWD',5,-2],['ENGINE_AFT',-31,-2],['GEN_1',-31,.5],['GEN_2',-13,.5],['GEN_3',5,.5],['GEN_4',23,.5],['CDC',23,3],['BRIDGE',7,13],['STEERING',-66,0],['AMMO_FWD',48,0],['AMMO_AFT',-55,0],['AMMO_ASM',0,3]])boxes.push(sovMaterialBoxA({name:id,oX:x,oY:id==='BOILER_3'?-3:id==='BOILER_4'?3:0,hL:5,hW:2.5,zMin:z-1,zMax:z+1,system:id,targetId:'SOV_'+id}));
 const layout=window.SovLayoutA;
 return {layout,boxes:deepFreezeShipProfileV48Wip09(boxes),stations:profile.geometry.hullStations,stern:-78.25,bow:78.25,targetIds:Object.fromEntries(boxes.map(b=>[b.name,b.targetId])),section:x=>layout.hullSection(x),halfBeam:(x,z)=>layout.halfBeam(x,z),bowAtZ:z=>layout.bowAtZ(z),contains:(x,y,z)=>layout.contains(x,y,z,'HULL',.015),buildHydroColumns:()=>SOV_REG_A.hydroColumns.map(c=>({...c,area:c.area*SOV_REG_A.hydroCalibration.effectiveBuoyancyScale}))};
}

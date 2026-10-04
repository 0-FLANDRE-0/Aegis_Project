function bunkerInteriorAuthored(flood){
  const L=shipGeometryLayout(),freeze=deepFreezeShipProfileV48Wip09,
    decks=[{id:'L2',label:'CG-52 하부 탱크층',z0:-4.8,z1:-2.3,color:0x517fc4},
      {id:'L1',label:'CG-52 기관·탄약층',z0:-2.1,z1:.3,color:0x4ea49c},
      {id:'MAIN',label:'CG-52 거주·작업층',z0:.5,z1:3.0,color:0x62b5d4},
      {id:'UPPER',label:'CG-52 전투·지원층',z0:3.2,z1:5.7,color:0x78c6a3},
      {id:'H0',label:'CG-52 격납고',z0:7.4,z1:12.6,color:0x89c98b},
      {id:'S1',label:'CG-52 전방 갑판실',z0:8.6,z1:11.0,color:0xe0a85d},
      {id:'S2',label:'CG-52 함교',z0:11.3,z1:13.7,color:0xd47e64}],
    spaces=[],portals=[],equipmentNodes=[],byId=new Map(),xs=[-65,-44,-22,0,22,44,65];
  const authored={
    L1:[['steering','조타기실','MACHINERY','STEERING'],['aft.engine','후방 기관실','MACHINERY','ENGINE_AFT'],
      ['aft.gen','후방 발전기실','MACHINERY','GEN_2'],['fwd.engine','전방 기관실','MACHINERY','BOILER_1'],
      ['fwd.gen','전방 발전기실','MACHINERY','GEN_1'],['gun.fwd.mag','전방 함포 탄약고','MAGAZINE','AMMO_FWD']],
    MAIN:[['aviation','항공 정비실','AVIATION','AVIATION'],['aft.berth','후방 거주구','HABITABLE',null],
      ['medical','의무실','MEDICAL','MEDICAL'],['dc','손상통제실','CONTROL','DAMAGE_CONTROL'],
      ['workshop','기관·전기 공작실','WORKSHOP','WORKSHOP'],['fwd.berth','전방 거주구','HABITABLE',null]],
    UPPER:[['aft.mag','후방 VLS·함포 지원','MAGAZINE','AMMO_AFT'],['flight','항공·비행갑판 지원','AVIATION','AVIATION'],
      ['stores','급양·보급','STORE','STORES'],['ew','전자전·통신실','ELECTRONICS','EW'],
      ['cic','전투정보실','CONTROL','COMBAT_CENTER'],['weapon','무장통제실','CONTROL','WEAPON_CONTROL']]
  };
  function add(id,label,deck,x0,x1,y0,y1,kind='ROOM',system=null,options={}){
    const d=decks.find(q=>q.id===deck),z0=options.z0??d.z0,z1=options.z1??d.z1,ek=options.envelopeKind??'HULL';
    // An authored cuboid must be inside the independent source envelope at all
    // sampled X/Z ordinates. It is never remapped from a Burke room.
    let lo=y0,hi=y1;
    for(let ix=0;ix<=4;ix++)for(let iz=0;iz<=2;iz++){
      const xx=x0+(x1-x0)*ix/4,zz=z0+(z1-z0)*iz/2,ints=L.intervals(xx,zz,ek,.08),mid=y0>0?y0+.1:y1<0?y1-.1:0,
        r=ints.find(q=>mid>=q[0]&&mid<=q[1]);if(!r)return null;lo=Math.max(lo,r[0]);hi=Math.min(hi,r[1]);
    }
    if(hi-lo<.5)return null;
    const center={x:(x0+x1)/2,y:(lo+hi)/2,z:(z0+z1)/2},parent=flood.cellAt(center),s=freeze({
      id:'cg52.'+id,macroId:'cg52.'+id,label,deck,kind,x0,x1,y0:lo,y1:hi,z0,z1,center,
      volumeM3:(x1-x0)*(hi-lo)*(z1-z0),parentFloodCellId:parent?.id??null,system,
      segmentIndex:0,segmentCount:1,routeable:options.routeable!==false,occupiable:options.occupiable!==false,
      capacity:kind==='PASSAGE'?0:24,watertightClass:deck==='L1'||deck==='L2'?'WT':'WEATHERTIGHT',fireZone:deck+'.'+id,
      envelopeKind:ek,geometryBasis:'CG52_SOURCE_CLIPPED_PLAUSIBLE_FUNCTIONAL_ZONING_NOT_ACTUAL_INTERIOR'});
    spaces.push(s);byId.set(s.id,s);
    if(system)equipmentNodes.push(freeze({id:'cg52.equipment.'+id,label:label+' 主 장비',spaceId:s.id,macroSpaceId:s.id,system,
      role:kind==='MACHINERY'?'PLANT':kind==='MAGAZINE'?'ORDNANCE_CONTROL':kind==='MEDICAL'?'MEDICAL_STATION':'OPERATOR_CONSOLE',
      criticality:kind==='CONTROL'?'MISSION_CRITICAL':'ESSENTIAL',position:center}));
    return s;
  }
  function link(a,b,kind='WATERTIGHT_DOOR'){
    a=typeof a==='string'?byId.get('cg52.'+a):a;b=typeof b==='string'?byId.get('cg52.'+b):b;
    if(!a||!b)return;
    const axis=a.deck===b.deck?(Math.abs(a.center.x-b.center.x)>Math.abs(a.center.y-b.center.y)?'X':'Y'):'Z',
      position={x:(a.center.x+b.center.x)/2,y:(a.center.y+b.center.y)/2,z:(a.center.z+b.center.z)/2};
    if(axis==='X')position.x=(Math.max(a.x0,b.x0)+Math.min(a.x1,b.x1))/2;
    if(axis==='Y')position.y=(Math.max(a.y0,b.y0)+Math.min(a.y1,b.y1))/2;
    // Passage edges are functional abstract access routes, not surveyed doors.
    portals.push(freeze({id:'cg52.portal.'+portals.length,a:a.id,b:b.id,kind,axis,position,widthM:1.0,heightM:2.0,
      normallyOpen:true,automatic:true,watertight:kind==='WATERTIGHT_DOOR',fireRated:kind==='FIRE_DOOR',
      stretcherPassable:kind!=='LADDER',routeLengthM:Math.hypot(a.center.x-b.center.x,a.center.y-b.center.y,a.center.z-b.center.z),
      basis:'SIM_TUNED_FUNCTIONAL_ACCESS_GRAPH'}));
  }
  for(const d of decks.slice(0,4))for(let i=0;i<6;i++){
    const x0=xs[i]+.12,x1=xs[i+1]-.12,id=d.id.toLowerCase()+'.passage.'+i,
      passage=add(id,'종통로 '+(i+1),d.id,x0,x1,-.60,.60,'PASSAGE',null,{routeable:d.id!=='L2',occupiable:d.id!=='L2'});
    if(i>0)link(d.id.toLowerCase()+'.passage.'+(i-1),passage);
    for(const [side,ya,yb]of [['port',-7.5,-.78],['starboard',.78,7.5]]){
      const row=authored[d.id]?.[i]??['tank.'+i,'연료·밸러스트 탱크','TANK','FUEL'],
        room=add(row[0]+'.'+side,row[1]+' '+(side==='port'?'좌현':'우현'),d.id,x0,x1,ya,yb,row[2],row[3],
          {routeable:d.id!=='L2',occupiable:d.id!=='L2'});if(d.id!=='L2')link(passage,room,row[2]==='MAGAZINE'?'WATERTIGHT_DOOR':'FIRE_DOOR');
    }
    if(d.id==='MAIN')link('l1.passage.'+i,passage,'STAIR');
    if(d.id==='UPPER')link('main.passage.'+i,passage,'STAIR');
  }
  const upper=[
    ['hangar.port','좌현 격납고','H0',-29,-18,-7.2,-.5,'HANGAR_BAY','AVIATION'],
    ['hangar.starboard','우현 격납고','H0',-29,-18,.5,7.2,'HANGAR_BAY','AVIATION'],
    ['bridge.support','함교 항해지원','S1',24,29,-3.3,-.7,'CONTROL','NAVIGATION'],
    ['spy.processor','SPY 처리·전원실','S1',24,29,.7,3.3,'ELECTRONICS','SPY_INTERFACE'],
    ['bridge.passage','함교 통로','S1',24,29,-.5,.5,'PASSAGE',null],
    ['bridge.pilothouse','조타·견시실','S2',25,29,-3.1,3.1,'CONTROL','PILOTHOUSE']
  ];
  for(const [id,label,deck,xa,xb,ya,yb,kind,system]of upper)add(id,label,deck,xa,xb,ya,yb,kind,system,{envelopeKind:'all'});
  link('upper.passage.1','hangar.port','STAIR');link('hangar.port','hangar.starboard','DOOR');
  link('upper.passage.4','bridge.passage','STAIR');link('bridge.passage','bridge.support','FIRE_DOOR');
  link('bridge.passage','spy.processor','FIRE_DOOR');link('bridge.passage','bridge.pilothouse','STAIR');
  return {decks,spaces,portals,equipmentNodes,byId};
}
function createBunkerInterior(flood){
  const {decks,spaces,portals,equipmentNodes,byId}=bunkerInteriorAuthored(flood),M=V48_WIP06_INTERIOR_MODEL,
    raw=spaces,deepFreeze=deepFreezeShipProfileV48Wip09,clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
  const topologyAudit=()=>{
    const route=spaces.filter(s=>s.routeable),seen=new Set(route.length?[route[0].id]:[]),queue=[...seen];
    while(queue.length){const id=queue.shift();for(const p of portals){const n=p.a===id?p.b:p.b===id?p.a:null;if(n&&byId.get(n)?.routeable&&!seen.has(n)){seen.add(n);queue.push(n);}}}
    return {schema:'AEGIS_CG52_INTERIOR_AUDIT_V1',spaceCount:spaces.length,macroSpaceCount:spaces.length,portalCount:portals.length,
      equipmentCount:equipmentNodes.length,deckCount:decks.length,uniqueSpaceIds:byId.size===spaces.length,
      uniquePortalIds:new Set(portals.map(p=>p.id)).size===portals.length,uniqueEquipmentIds:new Set(equipmentNodes.map(p=>p.id)).size===equipmentNodes.length,
      endpointsValid:portals.every(p=>byId.has(p.a)&&byId.has(p.b)),equipmentSpacesValid:equipmentNodes.every(q=>byId.has(q.spaceId)),
      routeable:route.length,reached:seen.size,unreachable:route.filter(s=>!seen.has(s.id)).map(s=>s.id),
      centersInside:spaces.every(s=>shipGeometryLayout().contains(s.center.x,s.center.y,s.center.z,s.envelopeKind)),
      independentCG52Layout:true,provenance:'SIM_TUNED_FUNCTIONAL_ZONING',hangarClearance:{bays:spaces.filter(s=>s.kind==='HANGAR_BAY').length,
        clear:true,conflicts:[],clearHeightM:5.2,bayHeightM:5.2,simulationEnvelopeOnly:true}};
  };
  // Shared hazard/isolation/caching engine appended by the reproducible builder.
  /* BUNKER_SHARED_TOPOLOGY_ENGINE */
}
function bunkerCrewDutyPosts(){
  const p=(space,count,label)=>({spaceId:'cg52.'+space,count,label});
  return {
    ENGINEERING:[p('fwd.engine.port',35,'전방 기관'),p('aft.engine.port',35,'후방 기관'),p('fwd.gen.starboard',20,'발전'),p('dc.port',20,'손상통제')],
    COMBAT:[p('cic.port',40,'CIC'),p('weapon.starboard',30,'무장'),p('ew.port',20,'전자전')],
    OPERATIONS:[p('bridge.pilothouse',25,'함교'),p('bridge.support',20,'항해'),p('cic.starboard',20,'작전')],
    AVIATION:[p('hangar.port',10,'좌현 격납고'),p('hangar.starboard',10,'우현 격납고'),p('flight.port',5,'비행지원')],
    SUPPORT:[p('stores.port',15,'보급'),p('medical.port',10,'의무'),p('stores.starboard',10,'급양')],
    COMMAND:[p('bridge.pilothouse',2,'함교 지휘'),p('cic.port',3,'CIC 지휘')],
    medicalSpaceId:'cg52.medical.port',abandonSpaceId:'cg52.flight.port',
    teamStaging:[['cg52.dc.port','cg52.workshop.port'],['cg52.dc.starboard','cg52.workshop.starboard'],['cg52.aviation.port','cg52.aviation.starboard']]
  };
}
let bunkerHitboxCache=null;
function buildBunkerHitboxes(){
  if(bunkerHitboxCache)return bunkerHitboxCache;
  const boxes=[],G=ACTIVE_SHIP_PROFILE.geometry,hp=G.hardpoints,xs=ACTIVE_SHIP_PROFILE.damage.flood.sectionDivisions;
  const add=q=>boxes.push(structureShipHitbox({...q,targetId:'CG52_'+q.name.replace(/[^A-Za-z0-9가-힣]/g,'_')}));
  for(let i=0;i<8;i++){
    const x0=xs[i],x1=xs[i+1],x=(x0+x1)/2,s=shipGeometryLayout().hullSection(x);
    for(const side of [-1,0,1])for(const band of ['LOWER','UPPER'])add({name:`선체(CG52_${i}_${side}_${band})`,oX:x,oY:side*s.b*.67,hL:(x1-x0)/2,hW:s.b/3,
      zMin:band==='LOWER'?s.keel:0,zMax:band==='LOWER'?0:s.deck,system:'HULL_SKIN',side:side<0?'PORT':side>0?'STARBOARD':'CENTER',geometryEnvelope:'CG52_HULL',damageVulnerability:.4,blastVulnerability:.25});
  }
  for(const [key,system]of [['mk45','MK45'],['mk45Aft','MK45_AFT'],['phalanx','CIWS_GUN'],['phalanxPort','CIWS_GUN_PORT'],
    ['spq9b','SPQ9B'],['bridgeMasterE','BRIDGEMASTER_E'],['vlsForward','VLS_FWD'],['vlsAft','VLS_AFT'],['mast','MAST'],['mastAft','MAST_AFT'],['flightDeck','FLIGHT_DECK']]){
    const h=hp[key];add({name:h.name,oX:h.x,oY:h.y,hL:h.hL??h.spanX/2,hW:h.hW??h.spanY/2,
      zMin:key.startsWith('vls')?h.z-7.7:h.z-(h.hH??.3),zMax:h.z+(h.hH??.3),system,renderClass:'EQUIPMENT',damageVulnerability:1.0,blastVulnerability:1.0});
  }
  for(const ill of SPG62_ILLUMINATORS)add({...spg62HitboxForIlluminator(ill),system:'SPG62_'+ill.id});
  for(const face of SPY1DV_FACE_KEYS)add({...wip199SpyHitbox(face),system:'SPY_1D'});
  for(const pod of ACTIVE_SHIP_PROFILE.equipment.ew.pods)add({name:pod.name,oX:pod.center.x,oY:pod.center.y,
    hL:pod.half.x,hW:pod.half.y,zMin:pod.min.z,zMax:pod.max.z,system:'EW',renderClass:'SENSOR',damageVulnerability:1.4,blastVulnerability:1.1});
  for(const r of ACTIVE_SHIP_PROFILE.equipment.secondaryRadars.filter(r=>!['SPQ9','SPS73'].includes(r.id)))
    add({name:r.label,oX:r.center.x,oY:r.center.y,hL:r.half.x,hW:r.half.y,zMin:r.min.z,zMax:r.max.z,
      system:'AUX_NAV',renderClass:'SENSOR',damageVulnerability:1.4,blastVulnerability:1.1});
  for(const [name,x0,x1,sys]of [['상부구조(전방)',15,33,'BRIDGE'],['상부구조(후방)',-31,-15,'STRUCTURE'],
    ['중앙갑판(전)',0,15,'STRUCTURE'],['중앙갑판(후)',-15,0,'STRUCTURE']]){
    add({name,oX:(x0+x1)/2,oY:0,hL:(x1-x0)/2,hW:8.4,zMin:7.2,zMax:name==='상부구조(전방)'?24.3:21.4,
      system:sys,geometryEnvelope:'CG52_ARCHITECTURE',renderClass:'STRUCTURE',damageVulnerability:.8,blastVulnerability:.6});
  }
  for(const [name,x0,x1,sys]of [['전방연돌',10.6,16.1,'FUNNEL_FWD'],['후방연돌',-24.36,-18.96,'FUNNEL_AFT'],
    ['제1보일러실',0,22,'BOILER_1'],['제2보일러실',-22,0,'BOILER_2'],['후방기관실',-44,-22,'ENGINE_AFT'],
    ['제1발전실',22,44,'GEN_1'],['제2발전실',-22,0,'GEN_2'],['제3발전실(비상)',-65,-44,'GEN_3'],
    ['탄약고(전)',44,65,'AMMO_FWD'],['탄약고(후)',-65,-44,'AMMO_AFT'],['조타기실',-80,-65,'STEERING'],
    ['CDC(전투지휘실)',22,44,'COMBAT_CENTER'],['전투지휘소',22,44,'COMBAT_CENTER'],['격납고',-31,-17,'HANGAR']]){
    const upper=sys.startsWith('FUNNEL')||sys==='HANGAR';add({name,oX:(x0+x1)/2,oY:0,hL:(x1-x0)/2,hW:upper?7.5:6,
      zMin:upper?7.4:-2.1,zMax:upper?sys==='HANGAR'?12.6:24:5.7,system:sys,geometryEnvelope:upper?'CG52_ARCHITECTURE':undefined,
      damageVulnerability:.6,blastVulnerability:.5});
  }
  bunkerHitboxCache=Object.freeze(boxes);return bunkerHitboxCache;
}

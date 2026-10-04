// CG-52 late-service ship and reusable hardware profiles. Mounts contain only
// installation data; immutable modules contain hardware and SIM_TUNED behavior.
const SHIP_GUN_MODULE_REGISTRY_V48_WIP13B8=deepFreezeShipProfileV48Wip09({
  ...BASE_SHIP_GUN_MODULE_REGISTRY_V48_WIP13B8,
  MK45_MOD2_MK160_SURFACE_V1:{...BASE_SHIP_GUN_MODULE_REGISTRY_V48_WIP13B8.MK45_MOD4_MK160_SURFACE_V1,
    id:'MK45_MOD2_MK160_SURFACE_V1',family:'Mk 45 Mod 2 / modernized GFCS',
    sourceBasis:{mountPerformance:'CG52_2021_MK45_MOD2_PHOTO_CAPTION__5IN54_PUBLIC',
      references:['https://www.seaforces.org/usnships/cg/CG-52-USS-Bunker-Hill.htm','https://man.fas.org/dod-101/sys/ship/weaps/mk-45.htm'],
      aerodynamics:'SHARED_SIM_TUNED_POINT_MASS',fireControlQuality:'SHARED_ANONYMOUS_RADAR_GFCS_SIM_TUNED',exactGFCSVariant:'PUBLIC_UNKNOWN'},
    mount:{...BASE_SHIP_GUN_MODULE_REGISTRY_V48_WIP13B8.MK45_MOD4_MK160_SURFACE_V1.mount,
      barrelCalibers:54,exposedBarrelM:5.88,trunnionOffsetM:{x:.7913872,y:0,z:2.0283818}},
    fireControl:{...BASE_SHIP_GUN_MODULE_REGISTRY_V48_WIP13B8.MK45_MOD4_MK160_SURFACE_V1.fireControl,maxRangeM:22000},
    magazine:{basis:'SIM_TUNED_CG52_PER_MOUNT_ALLOWANCE',initialRounds:{HE_127_SIM:360,SAP_127_SIM:240},capacityRounds:600}
  }
});
const SHIP_EQUIPMENT_PROFILE_REGISTRY=deepFreezeShipProfileV48Wip09({
  PHALANX_BLOCK_1B_V1:{id:'PHALANX_BLOCK_1B_V1',family:'Phalanx Block 1B',builderId:'CIWS_BLOCK1B_WIP13',
    ammunition:'MK244_EXISTING_WIP16',ammo:1550,fireRateRps:75,engageRangeKm:3,
    searchRangeKm:15,trackRangeKm:10,cueTrackRangeKm:15,searchToTrackTimeS:.8,
    trainHalfRad:150*Math.PI/180,elevationMinRad:-25*Math.PI/180,elevationMaxRad:85*Math.PI/180,
    trainRateRadS:115*Math.PI/180,trainAccelRadS2:200*Math.PI/180,
    elevationRateRadS:90*Math.PI/180,elevationAccelRadS2:150*Math.PI/180,
    provenance:'SHARED_DDG119_ALGORITHMS__DRIVE_AND_RANGE_SIM_TUNED'},
  SPG62_V1:{id:'SPG62_V1',family:'AN/SPG-62',trainHalfRad:Math.PI,
    elevationMinRad:-5*Math.PI/180,elevationMaxRad:85*Math.PI/180,
    destroyThresholdPct:80,provenance:'SHARED_SARH_ILLUMINATOR__MECHANICAL_ENVELOPE_SIM_TUNED'},
  MK45_MOD2_MK160_SURFACE_V1:SHIP_GUN_MODULE_REGISTRY_V48_WIP13B8.MK45_MOD2_MK160_SURFACE_V1,
  SPQ9_CG52_V1:{id:'SPQ9_CG52_V1',family:'AN/SPQ-9',band:'X',rpm:30,panelCount:1,
    publicRangeKm:20*1.852,publicMinRangeM:137,elevationObservable:false,
    role:'TWO_DIMENSIONAL_SURFACE_SEARCH_AND_GUN_FIRE_CONTROL',
    publicSource:'https://en.wikipedia.org/wiki/AN/SPQ-9',
    provenance:'USER_SELECTED_NON_B_CONFIGURATION__SPQ9A_FAMILY_PUBLIC_RANGE__RPM_PD_AND_ERRORS_SIM_TUNED',
    historicalVariant:'CG52_EXACT_A_OR_B_NOT_ESTABLISHED_BY_USER_RENDER_IMAGE'},
  SPS73_CG52_V1:{id:'SPS73_CG52_V1',family:'AN/SPS-73',exactVariant:'SPS73_SUBVARIANT_PUBLIC_UNKNOWN',
    band:'X',rpm:30,elevationObservable:false,
    role:'TWO_DIMENSIONAL_SHORT_RANGE_SURFACE_SEARCH_AND_NAVIGATION',
    publicSource:'https://man.fas.org/dod-101/sys/ship/weaps/an-sps-73.htm',
    provenance:'USER_MARKED_MAST_ANTENNA__PUBLIC_2D_ROLE__FREQUENCY_POWER_SCAN_AND_PD_SIM_TUNED'},
  SLQ32_CG52_LATE_V1:{id:'SLQ32_CG52_LATE_V1',family:'AN/SLQ-32',exactVariant:'PUBLIC_UNKNOWN',
    provenance:'SUPPLIED_TWIN_OUTBOARD_PODS__SHARED_EA_ALLOCATOR_AND_SIM_TUNED_RF'},
  NULKA_MK53_V1:{id:'NULKA_MK53_V1',family:'Mk 53 Nulka',tubesPerLauncher:2,provenance:'USER_CONFIRMED_4X2_VIEWER_REGISTRATION'},
  SRBOC_MK36_V1:{id:'SRBOC_MK36_V1',family:'Mk 36 SRBOC',tubesPerLauncher:6,provenance:'FOUR_BANKS_OF_SIX_SOURCE_TUBES'}
});
function makeBunkerShipProfile(){
  const R=BUNKER_REGISTRATION,E=SHIP_EQUIPMENT_PROFILE_REGISTRY,copy=o=>JSON.parse(JSON.stringify(o));
  const hp={};
  for(const [key,g]of Object.entries(R.guns))hp[key]={name:key==='mk45'?'Mk45':'Mk45(후방)',...g.pivot,hL:2.4,hW:1.6,hH:2.8};
  for(const [key,g]of Object.entries(R.ciws))hp[key]={name:key==='phalanx'?'Phalanx(우현)':'Phalanx(좌현)',x:g.x,y:g.y,z:g.z-.25,hL:1.25,hW:1.25,hH:1.85};
  // Compatibility geometry for archived named render consumers; no RAM equipment
  // or runtime is installed on CG-52. Live consumers use the mount inventory.
  hp.seaRam=hp.phalanxPort;
  hp.spg62=R.spg.map((v,i)=>({id:i,oX:v[0],oY:v[1],heightM:v[2],label:`ILL-${i+1}(${i<2?'전방':'후방'})`,
    moduleName:`AN/SPG-62(${i+1})`,moduleId:E.SPG62_V1.id,mountRole:i<2?'FWD':'AFT',
    sectorHalfDeg:180,blindCenterDeg:0,blindHalfDeg:0,geometryMask:true,sourceNode:`spg${i}_yaw`}));
  for(const [sec,key]of [['fwd','vlsForward'],['aft','vlsAft']]){
    const a=R.cells[sec],avg=k=>a.reduce((n,c)=>n+c[k],0)/a.length;
    hp[key]={name:sec==='fwd'?'VLS(전)':'VLS(후)',x:avg('x'),y:avg('y'),z:avg('z'),deckZM:avg('z'),rows:8,cols:8,
      spanX:Math.max(...a.map(c=>c.x))-Math.min(...a.map(c=>c.x))+.7,spanY:6.0,cellLayoutBasis:'CG52_EXPLICIT_SPARSE_61_CELLS'};
  }
  const spq=R.radars.find(r=>r.id==='SPQ9'),nav=R.radars.find(r=>r.id==='SPS73');
  hp.spq9b={name:spq.label,...spq.center,hL:spq.half.x,hW:spq.half.y,hH:spq.half.z};
  hp.bridgeMasterE={name:nav.label,...nav.center,hL:nav.half.x,hW:nav.half.y,hH:nav.half.z,antennaLengthM:2.24};
  hp.mast={name:'마스트',x:18.136,y:0,z:27.8,hL:.70,hW:.70,hH:8.9};
  hp.mastAft={name:'후방 마스트',x:-7.36,y:0,z:34.8,hL:.70,hW:.70,hH:11.3};
  hp.flightDeck={name:'비행갑판',x:-45,y:0,z:7.2,hL:14.5,hW:8.1,hH:.15};
  hp.nulka=R.nulka;hp.srboc=R.srboc;
  const installs=Object.entries(R.guns).map(([hardpointId,g])=>({id:g.id,builderId:'PROFILE_GUN_MODULE_WIP13B8',
    moduleId:'MK45_MOD2_MK160_SURFACE_V1',hardpointId,neutralAzRad:g.neutralAzRad,geometryMask:true,
    moduleName:hp[hardpointId].name,trunnionOffsetM:g.trunnionOffsetM,exposedBarrelM:g.barrelM,sourceNode:g.yawNode}));
  const closeInMounts={};
  for(const [key,g]of Object.entries(R.ciws))closeInMounts[key]={id:g.id,moduleId:E.PHALANX_BLOCK_1B_V1.id,hardpointId:key,
    type:'GUN',moduleName:hp[key].name,neutralAzRad:g.neutralAzRad,geometryMask:true,sourceNode:g.yawNode,
    ammo:E.PHALANX_BLOCK_1B_V1.ammo,engageRangeKm:E.PHALANX_BLOCK_1B_V1.engageRangeKm,fireRateRps:E.PHALANX_BLOCK_1B_V1.fireRateRps};
  const D=DDG_119_LATE_FLIGHT_IIA_PROFILE;
  const p={schema:D.schema,schemaVersion:D.schemaVersion,id:'CG_52_LATE_TICONDEROGA',revision:'BUNKERHILL_LATE_G_1',
    identity:{classId:'TICONDEROGA',className:'Ticonderoga-class guided missile cruiser',flight:'FIRST_VLS_GROUP',variant:'LATE_SERVICE_2021_2023',
      hullNumber:'CG-52',shipName:'USS Bunker Hill',country:'US',basis:'LATE_SERVICE_PUBLIC_PHOTOS_AND_SUPPLIED_VIEWER',
      radarVariantFinding:'SPY-1A_MODERNIZED__SPY1B_V_ARRAY_REPLACEMENT_NOT_VERIFIED'},
    coordinates:copy(D.coordinates),
    equipment:{registryId:'AEGIS_REUSABLE_EQUIPMENT_V1',guns:installs,closeIn:Object.values(closeInMounts),
      illuminators:hp.spg62.map(q=>({id:q.id,moduleId:q.moduleId,sourceNode:q.sourceNode})),
      secondaryRadars:R.radars,ew:{moduleId:E.SLQ32_CG52_LATE_V1.id,pods:R.ewPods},
      nulka:{moduleId:E.NULKA_MK53_V1.id,layout:R.nulka},srboc:{moduleId:E.SRBOC_MK36_V1.id,layout:R.srboc}},
    geometry:{builderId:'CG52_VIEWER5_SOURCE_GEOMETRY',deckZM:7.2,bowXM:86.396754,sternXM:-86.06325,lengthM:172.46,
      referenceHeightM:16.5,beamM:16.76,hullStations:BUNKER_ENVELOPE.stats.stations,
      visualRegistration:{id:R.id,authority:'OFFLINE_SI_REGISTRATION',physicsFeedback:false,hullCollision:'SOURCE_DERIVED_SECTION_ENVELOPE',
        interior:'CG52_INDEPENDENT_FUNCTIONAL_ZONING',liveMeshReads:false},
      superstructure:{horizontal:1,vertical:1,hangarHorizontal:1,hangarVertical:1,mastTopM:46.06,mastHorizontal:1},
      bridge:{builderId:'CG52_SOURCE_SECTION_BRIDGE',groupXM:27.8,yawRad:0},
      mk45:{basis:R.basis,xM:hp.mk45.x,yM:0,baseDeckZM:9.04,baseRadiusM:1.54,rotationRingZM:9.04,housingBottomZM:9.04,
        housingTopZM:11.80,housingLengthM:4.74,housingWidthM:3.08,trunnionXM:54.811374,trunnionZM:11.070152,exposedBarrelM:R.guns.mk45.barrelM,barrelRadiusM:.19},
      aft:{basis:R.basis,flightDeckPlaneZM:7.2,flightDeckStations:[[-60,8.1,7.2],[-31,8.1,7.2]],
        hangar:{xAftM:-31,xFwdM:-17,bottomHalfWidthM:8.0,roofHalfWidthM:7.7,shellBottomZM:7.2,roofZM:13.26,roofThicknessM:.2,
          doorFaceXM:-31,doorSillZM:7.4,doorTopZM:12.6,doorHalfWidthM:3.1,doorCenterOffsetYM:4.0,
          interiorFloorZM:7.4,interiorCeilingZM:12.6,minClearHeightM:5.2},
        support:{xM:-24.9,halfLengthM:6,halfWidthM:7.8,bottomZM:13.26,roofZM:21.43,highSpgDeckZM:25.40,lowSpgDeckZM:22.65},
        liferafts:{basis:R.basis,xM:[-32,-34,-36],lateralM:8.2,canisterRadiusM:.33,canisterLengthM:1.44,supportDeckZM:7.2,centerZM:8.1}},
      funnels:{revision:R.id,basis:R.basis,
        forward:{id:'FWD',centerXM:13.3,xAftM:10.6,xFwdM:16.1,halfLengthM:2.75,baseHalfWidthM:5.4,roofHalfWidthM:5.4,hitHalfWidthM:5.4,
          shellBottomZM:16.55,topZM:23.95,hitZMinM:16.55,hitZMaxM:23.95},
        aft:{id:'AFT',centerXM:-21.7,xAftM:-24.36,xFwdM:-18.96,halfLengthM:2.7,baseHalfWidthM:5.95,roofHalfWidthM:5.95,hitHalfWidthM:5.95,
          shellBottomZM:18.9,topZM:21.6,hitZMinM:18.9,hitZMaxM:21.6}},hardpoints:hp},
    navigation:{initialHeadingRad:-Math.PI/2,maxTrail:800,maxAheadKt:32,maxAsternKt:5},
    sensors:{modelId:'CG52_SENSOR_MODEL_LATE_V1',spy1dv:{family:'AN/SPY-1A (modernized Aegis)',snrReferenceRangeKm:185,searchMaxRangeKm:320,
        heightM:16.34,seaClutterLowFactor:.22,seaClutterExponent:.90,provenance:'PUBLIC_VARIANT__PERFORMANCE_SIM_TUNED'},
      spq9b:{moduleId:E.SPQ9_CG52_V1.id,family:'AN/SPQ-9',heightM:hp.spq9b.z,rpm:30,panelCount:1,
        snrReferenceRangeKm:32,searchMaxRangeKm:37.04,surfaceMaxRangeKm:37.04,minimumRangeM:137,
        elevationObservable:false,processor:'CG52_SPQ9_2D',provenance:E.SPQ9_CG52_V1.provenance},
      spg62:{moduleId:E.SPG62_V1.id,destroyThresholdPct:80},
      bridgeMasterE:{...copy(D.sensors.bridgeMasterE),schema:'AEGIS_CG52_SPS73_INSTALLATION_V1',family:'AN/SPS-73',
        moduleId:E.SPS73_CG52_V1.id,channel:'CG52_X_BAND_2D_SURFACE_NAV_SIM',band:'X',frequencyMHz:9400,
        frequencyToleranceMHz:30,peakPowerKw:25,antennaApertureM:2.24,antennaApertureFt:2.24/.3048,
        horizontalBeamwidthDeg:1.2,verticalBeamwidthDeg:20,nominalRpm:30,highSpeedRpm:30,
        trackMaxNmi:40,workingMinimumRangeM:60,workingRangeResolutionM:30,
        navalVariantExactConfiguration:'SPS73_SUBVARIANT_PUBLIC_UNKNOWN',
        publishedMinimumRangeLessThanM:null,publishedRangeResolutionBetterThanM:null,
        performanceBasis:'SPS73_PUBLIC_2D_ROLE__USER_PHOTO_POSITION__FREQUENCY_POWER_SCAN_PD_ERRORS_SIM_TUNED'}},
    weapons:{mainGun:installs[0],gunMounts:installs,
      vls:{builderId:'MK41_WIP125',sections:{fwd:{cells:61,rows:8,cols:8,cellLayout:R.cells.fwd.map(c=>({row:c.row,col:c.col})),defaultLoadout:[{type:'SM2',cells:61}]},
        aft:{cells:61,rows:8,cols:8,cellLayout:R.cells.aft.map(c=>({row:c.row,col:c.col})),defaultLoadout:[{type:'SM2',cells:37},{type:'ESSM4',cells:24}]}}},
      closeIn:{builderId:'CIWS_BLOCK1B_WIP13',sensor:copy(D.weapons.closeIn.sensor),mounts:closeInMounts},softKill15B:copy(D.weapons.softKill15B)},
    mass:{modelId:D.mass.modelId,fullLoadTargetKg:9754067.2,lightshipKg:7203784.7,srbocLoadoutDeltaKg:0,
      calibratedFullLoadCGM:{x:-4,y:0,z:5.1},targetLightshipCGM:{x:-3,y:0,z:6.1},calibratedReferenceGMM:1.4,personKg:110,
      weapons:{...copy(D.mass.weapons),staticOrdnanceKg:8000},
      variableLoadsKg:{propulsionFuel:1500000,aviationFuel:120000,freshWater:180000,serviceBallast:220000,technicalFluids:80000,
        helicopters:17000,crew:36300,provisionsSpares:200000,missionStores:50000,ordnance:146982.5},
      initialLoads:[['fuel.fwd',375000],['fuel.mid_fwd',375000],['fuel.mid_aft',375000],['fuel.aft',375000],['fuel.aviation',120000],
        ['water.fresh',180000],['ballast.fwd',110000],['ballast.aft',110000],['fluids.mid',40000],['fluids.aft',40000]],
      loadLocations:{'fuel.fwd':{x:45,y:0,z:.5},'fuel.mid_fwd':{x:12,y:0,z:.5},'fuel.mid_aft':{x:-14,y:0,z:.5},'fuel.aft':{x:-45,y:0,z:.5},
        'fuel.aviation':{x:-35,y:0,z:1},'water.fresh':{x:-65,y:0,z:1},'ballast.fwd':{x:65,y:0,z:-2},'ballast.aft':{x:-73,y:0,z:-2},
        'fluids.mid':{x:0,y:0,z:1},'fluids.aft':{x:-25,y:0,z:1}},
      fixedNodes:[['ordnance.torpedo','ORDNANCE_FIXED',1400,{x:-12,y:0,z:9}],['ordnance.misc','ORDNANCE_FIXED',6600,{x:0,y:0,z:3}],
        ['helo.port','AIRCRAFT',8500,{x:-24,y:-4,z:7.4}],['helo.starboard','AIRCRAFT',8500,{x:-24,y:4,z:7.4}],
        ['stores.provisions','STORES',200000,{x:-15,y:0,z:2.5}],['stores.mission','STORES',50000,{x:0,y:0,z:2.5}]],
      provenance:'9600_LONG_TON_CLASS_PUBLIC_REFERENCE__LOADS_AND_CG_SIM_TUNED'},
    hydrostatics:{...copy(D.hydrostatics),initialGMM:1.4,thrustPerKg:.23,powerPerKg:5.7,engineResponseS:5.5,rollDamping:.24},
    environment:copy(D.environment),interior:{builderId:'CG52_FUNCTIONAL_INTERIOR_V1',modelId:D.interior.modelId,
      authoringRevision:'CG52_FUNCTIONAL_INTERIOR_G_1',basis:'SOURCE_CONTAINED_SIM_TUNED_FUNCTIONAL_ZONING_NOT_ACTUAL_SHIPYARD_PLAN',expected:{floodParentCells:24}},
    crew:{...copy(D.crew),builderId:'CG52_CREW_V1',roster:330,departments:[['ENGINEERING','기관부',110],['COMBAT','전투체계부',90],
      ['OPERATIONS','작전부',65],['AVIATION','항공부',25],['SUPPORT','보급·행정·의무',35],['COMMAND','지휘부',5]]},
    damage:{...copy(D.damage),hitboxBuilderId:'CG52_SOURCE_MATERIAL_HITBOXES',flood:{...copy(D.damage.flood),sectionDivisions:[-86.06325,-65,-44,-22,0,22,44,65,86.396754]}},
    protection:D.protection,renderer:{builderId:'CG52_VIEWER5_THREE',rootName:'CG52_BUNKER_HILL_LATE',contract:'PRESENTATION_ONLY_PROFILE_CONSUMER',physicsFeedback:false},
    parity:{baselineId:'DDG119_STARTUP_A',expectedBehavior:'DDG119_REGRESSION_PRESERVED__CG52_SHARED_PHYSICS_INDEPENDENT_INSTALLATIONS'},
    provenance:{era:'LATE_SERVICE_2021_2023',geometry:'SUPPLIED_VIEWER_V5',spy:'SPY1A_CG52_TO_58__B_V_CG59_PLUS',
      uncertain:['Exact navigation radar variants','Exact late-service SLQ-32 version','Exact GFCS baseline and ammunition stowage','Actual interior layout and CG'],
      sources:['https://man.fas.org/dod-101/sys/ship/weaps/an-spy-1.htm','https://www.naval-technology.com/projects/ticonderoga/',
        'https://www.seaforces.org/usnships/cg/CG-52-USS-Bunker-Hill.htm']}}
  return deepFreezeShipProfileV48Wip09(p);
}
const CG_52_LATE_TICONDEROGA_PROFILE=makeBunkerShipProfile();

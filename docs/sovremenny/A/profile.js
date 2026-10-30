// LIVE_CANONICAL. SOV_A data-only hull profile, never a controllable player ship.
// Every authored coordinate is MODEL_REGISTRATION; topology/CG/hydro/material/
// dynamics/crew/RCS calibration are SIM_TUNED. PUBLIC_SPEC only below, by source.
function sovHullA(x){return typeof x==='string'?x==='SOVREMENNY_956':x?.profileId==='SOVREMENNY_956'||x?.id==='SOVREMENNY_956';}
function sovNoEquipmentA(r){return sovHullA(r);}
function makeSovProfileA(){
 const p=JSON.parse(JSON.stringify(DDG_119_LATE_FLIGHT_IIA_PROFILE)),R=SOV_REG_A,C=R.hydroCalibration;
 p.id='SOVREMENNY_956';p.revision='SOV_A_HULL_1';
 p.identity={classId:'SOVREMENNY_956',className:'Sovremenny-class destroyer',flight:'PROJECT_956',variant:'REFERENCE_VIEWER_V9_1',hullNumber:'956형',shipName:'소브레멘니급',country:'USSR',basis:'MODEL_REGISTRATION'};
 p.capabilities={npcOnly:true,allowedRoles:['ENEMY','NEUTRAL','UNASSIGNED'],sensors:false,weapons:false,electronicWarfare:false,aviation:false,scenarioNav:true};
 p.specification={source:'PUBLIC_SPEC',sources:{GlobalSecurity:'https://www.globalsecurity.org/military/world/russia/956-specs.htm',Wikipedia:'https://en.wikipedia.org/wiki/Sovremenny-class_destroyer'},lengthM:156.5,beamM:17.2,draft:{hullAdoptedM:6,sonarM:7.85,GlobalSecurityRangeM:[5.99,7.85],WikipediaM:5.2},displacement:{standardRangeT:[6300,6600],GlobalSecurityStandardRangeT:[6300,6500],WikipediaStandardT:6600,fullRangeT:[7900,7940],adoptedFullT:7940},speed:{publicRangeKt:[32,34],adoptedKt:32,GlobalSecurityRangeKt:[32.5,34]},propulsion:{kind:'STEAM_TURBINE',turbines:2,shafts:2,boilers:4,powerShp:100000,fixedPitch:true,blades:4},generators:{turbo:2,diesel:2},crew:{publicRange:[296,350],adopted:320,adoptionSource:'SIM_TUNED',reason:'Within public range; functional roster, not a verified ship-specific complement.'}};
 const absent={name:'NOT_INSTALLED',x:0,y:0,z:0,installed:false,hL:0,hW:0,hH:0};
 const hp={spg62:[],nulka:{schema:'AEGIS_NULKA_LAYOUT_WIP15B',revision:'SOV_NONE_A',launchers:[]},srboc:{schema:'AEGIS_SRBOC_LAYOUT_WIP15A',revision:'SOV_NONE_A',launchers:[]},inactive:R.inactiveHardpoints};
 // COMPAT_REQUIRED: zero-sized, disabled placeholders for shared ballistic helpers.
 // Not equipment, mounts, emission sources or ammunition inventory.
 for(const k of ['mk45','vlsForward','vlsAft','phalanx','seaRam','spq9b','bridgeMasterE'])hp[k]={...absent};
 hp.mast={name:'마스트',x:2.52,y:0,z:R.mastHeightM,hL:.8,hW:.8,hH:1};
 hp.flightDeck={name:'비활성 비행갑판',x:-30,y:0,z:4.9,hL:7,hW:7,hH:.1,installed:false};
 p.geometry={...p.geometry,builderId:'SOV_VIEWER9_1_STATIC_A',lengthM:156.5,beamM:17.2,modelHullBeamM:R.modelHullBeamM,bowXM:78.25,sternXM:-78.25,deckZM:4.9,referenceHeightM:R.mastHeightM,hullStations:R.stations,hardpoints:hp,visualRegistration:{id:R.schema,authority:'OFFLINE_SI_REGISTRATION',physicsFeedback:false,liveMeshReads:false,verticalDatum:R.verticalDatum},superstructure:{horizontal:1,vertical:1,mastTopM:R.mastHeightM,mastHorizontal:1},aft:{...p.geometry.aft,flightDeckPlaneZM:4.9,hangar:{...p.geometry.aft.hangar,xAftM:-26,xFwdM:-12,interiorFloorZM:5.1,interiorCeilingZM:9.1},liferafts:{...p.geometry.aft.liferafts,xM:[-30,-33,-36],centerZM:5.3,supportDeckZM:4.9,lateralM:8}}};
 p.signature={source:'SIM_TUNED',areaGeometrySource:'MODEL_REGISTRATION',projectedAreaLut:R.projectedAreaLut,areaToRcsScale:1.6,referenceHeightM:R.mastHeightM,provenance:'Static projected area with empirical RF scale, not measured military RCS.'};
 p.navigation={...p.navigation,maxAheadKt:32,maxAsternKt:5,propulsion:'STEAM_FIXED_PITCH',source:'SIM_TUNED',shaftResponseS:24};
 p.sensors={modelId:'SOV_NO_SENSORS_A',installed:[],source:'SIM_TUNED',spy1dv:{searchMaxRangeKm:0,snrReferenceRangeKm:0,heightM:0},spq9b:{searchMaxRangeKm:0,rpm:0,heightM:0},spg62:{destroyThresholdPct:0},bridgeMasterE:{band:'NONE',peakPowerKw:0,nominalRpm:0,searchMaxRangeKm:0}};
 p.geometry.funnels={revision:'SOV_SOURCE_A',basis:'MODEL_REGISTRATION',forward:{centerXM:8.6,halfLengthM:7.3,baseHalfWidthM:1.7,roofHalfWidthM:1.7,shellBottomZM:14.7,topZM:23.5},aft:{centerXM:-17.7,halfLengthM:1.5,baseHalfWidthM:1.9,roofHalfWidthM:1.9,shellBottomZM:15.8,topZM:21.6}};
 p.equipment={registryId:'SOV_INACTIVE_ONLY_A',guns:[],closeIn:[],illuminators:[],secondaryRadars:[],ew:{pods:[],installed:false},inactiveHardpoints:R.inactiveHardpoints,sensorRegistration:R.sensorRegistration};
 p.weapons={mainGun:{id:'NOT_INSTALLED',installed:false},gunMounts:[],vls:{sections:{fwd:{cells:0,rows:0,cols:0,defaultLoadout:[]},aft:{cells:0,rows:0,cols:0,defaultLoadout:[]}}},closeIn:{sensor:{searchRangeKm:0,trackRangeKm:0,cueTrackRangeKm:0,searchToTrackTimeS:0},mounts:{}},softKill15B:JSON.parse(JSON.stringify(p.weapons.softKill15B))};
 for(const k of ['srboc','nulka'])p.weapons.softKill15B[k]={...p.weapons.softKill15B[k],reserveRounds:0,roundMassKg:0};
 p.mass={...p.mass,fullLoadTargetKg:7940000,lightshipKg:6404800,srbocLoadoutDeltaKg:0,softKill15BLoadoutDeltaKg:0,personKg:110,calibratedFullLoadCGM:{x:C.referenceCGXM,y:0,z:3.6},targetLightshipCGM:{x:0,y:0,z:0},calibratedReferenceGMM:1.25,weapons:Object.fromEntries(Object.keys(p.mass.weapons).map(k=>[k,0])),variableLoadsKg:{propulsionFuel:1200000,freshWater:150000,serviceBallast:0,technicalFluids:50000,helicopters:0,crew:35200,provisionsSpares:100000,missionStores:0,ordnance:0},initialLoads:[['fuel.fwd',300000],['fuel.mid_fwd',300000],['fuel.mid_aft',300000],['fuel.aft',300000],['water.fresh',150000],['fluids.mid',50000]],fixedNodes:[['stores.provisions','STORES',100000,{x:-15,y:0,z:2}]],source:'SIM_TUNED',provenance:'7940t PUBLIC_SPEC target; stores/fuel/lightship split/CG are tuned, no weapons or aircraft mass.'};
 // Equilibrium: rho * sum(area * immersedHeight) * scale = 7,940,000 kg at z=0.
 // Raw mesh displaces 7,623.341 m3; scale=1.016134725. CG alone cannot correct
 // displacement. The explicit effective buoyancy area correction is SIM_TUNED.
 // First moments: lightship CG=(target M*CG - variable-load moments)/Mlight.
 const moments={x:-1500000,y:0,z:200000};let added=135200;
 for(const [id,kg]of p.mass.initialLoads){const q=p.mass.loadLocations[id];added+=kg;for(const k of ['x','y','z'])moments[k]+=kg*q[k];}
 // Crew positions are runtime-owned. Reference centroid (-8,0,2) is SIM_TUNED;
 // their subsequent movement changes actual trim/stability through common ledger.
 moments.x+=35200*(-8);moments.z+=35200*2;
 p.mass.lightshipKg=7940000-added;
 for(const k of ['x','y','z'])p.mass.targetLightshipCGM[k]=(7940000*p.mass.calibratedFullLoadCGM[k]-moments[k])/p.mass.lightshipKg;
 p.hydrostatics={...p.hydrostatics,rudderAreaM2:14,waveResponse:{source:'SIM_TUNED',heave:.55,roll:.18,pitch:.18},initialGMM:1.25,thrustPerKg:.19,powerPerKg:5.1,engineResponseS:24,rollDamping:.25,source:'SIM_TUNED',effectiveBuoyancyScale:C.effectiveBuoyancyScale};
 p.crew={...p.crew,roster:320,builderId:'SOV_FUNCTIONAL_CREW_A',departments:[['ENGINEERING','기관부',110],['COMBAT','전투부',80],['OPERATIONS','작전부',60],['AVIATION','격납고 정비',10],['SUPPORT','보급·의무',55],['COMMAND','지휘부',5]],source:'SIM_TUNED'};
 p.interior={builderId:'SOV_FUNCTIONAL_INTERIOR_A',modelId:p.interior.modelId,expected:{floodParentCells:24},provenance:'SIM_TUNED_FUNCTIONAL_GRAPH_NOT_A_SHIPYARD_PLAN'};
 p.protection={...p.protection,basis:'SIM_TUNED_ESTIMATED_STEEL_NO_CERTIFIED_ARMOR_DATA',boundaries:Object.fromEntries(Object.entries(p.protection.boundaries).map(([k,b])=>[k,{...b,layers:[{materialId:'GRADE_A_STEEL',thicknessMm:k.includes('SHELL')?12:k.includes('WATERTIGHT')?8:4}],insulationPresent:false}]))};
 p.damage={...p.damage,hitboxBuilderId:'SOV_STATIC_MATERIAL_BOXES_A',flood:{...p.damage.flood,sectionDivisions:[-78.25,-58,-38,-18,2,22,42,62,78.25]},survival:{...p.damage.survival,criticalWaterM3:1800,disableWaterM3:3400,sinkWaterM3:5400,capMinWaterM3:1600},source:'SIM_TUNED'};
 p.renderer={builderId:'SOV_VIEWER9_1_THREE_A',rootName:'SOVREMENNY_956',contract:'PRESENTATION_ONLY_PROFILE_CONSUMER',physicsFeedback:false};
 p.provenance={public:p.specification.sources,model:{source:'MODEL_REGISTRATION',file:R.sourceFile,sha256:R.sourceSha256},tuned:['effective buoyancy','CG/GM','functional compartments/access graph','plate thickness/material','RCS','steam response/turning','load split','crew assignment'],attribution:R.attribution};
 p.parity={baselineId:'DDG119_AND_CG52_HELI_F2',expectedBehavior:'EXISTING_SHIPS_UNCHANGED__SOV_NPC_HULL_ONLY'};
 return deepFreezeShipProfileV48Wip09(p);
}
function sovDisabledGunA(){const denied=()=>({ok:false,reason:'NO_WEAPONS_INSTALLED'});return {snapshot:()=>({id:'NOT_INSTALLED',enabled:false,state:'OFFLINE',magazine:{},loadedAmmoId:null,bodyAzRad:0,elevationRad:0}),requestFire:denied,command:denied,step:denied};}

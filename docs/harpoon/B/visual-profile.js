// Display settings are VISUAL_TUNED; booster duration/thrust live in the B flight profile.
const HARPOON_MOUTH_REGISTRATION_B=deepFreezeShipProfileV48Wip09(await readBunkerAsset('harpoon-mouth-registration-b'));
const HARPOON_VISUAL_PROFILE_B=deepFreezeShipProfileV48Wip09({
  schema:'HARPOON_BODY_NOZZLE_LAUNCH_FX_B1',physicsFeedback:false,
  bodyExitXM:-1.525,boosterExitXM:-2.315,bodyThroatXM:-1.33,bodyExitRadiusM:.129,
  bodyShell:[[-1.525,.129],[-1.505,.134],[-1.46,.146],[-1.39,.156],[-1.30,.164],[-1.17,.1685],[-1.035,.1685]],
  bodyBell:[[-1.525,.129],[-1.525,.116],[-1.50,.113],[-1.46,.105],[-1.39,.092],[-1.33,.078]],
  boosterShell:[[-2.315,.145],[-2.30,.153],[-2.24,.164],[-2.14,.16865],[-1.525,.16865]],
  boosterBell:[[-2.315,.145],[-2.315,.130],[-2.28,.118],[-2.22,.095],[-2.16,.075]],
  replacedBodySources:[15,30,31,57],couplingBodySources:[36,40,42,44,56],replacedBoosterSources:[29,34,37,38],
  tubeInnerRadiusM:.245,tubeOuterRadiusM:.293,tubeFrontDepthM:.102,launchCloudLifeS:1.35,
  launchHotLifeS:.42,maxLaunchEmitters:8,maxSmokeSamplesPerFrame:48,
  boosterSmoke:{class:'USER_ASSUMED_HIGH_SMOKE_SOLID_PROPELLANT__VISUAL_TUNED',
    spacingM:.60,lifeS:12,baseM:1.8,growthPerS:.18,alpha:.96,fadePower:.95,color:0xd5d2c8},
  provenance:'SOURCE_REGISTERED_TUBE_DOORS__VISUAL_TUNED_AFT_FAIRING_NOZZLES_PLUMES_SMOKE'
});
function harpoonVisualCoreAuditB(){
  const p=HARPOON_VISUAL_PROFILE_B,rows=HARPOON_MOUTH_REGISTRATION_B.rows,front=rows.flatMap(r=>r.doorFaces),rear=rows.flatMap(r=>r.rearFaces),
    finite=points=>points.every(([x,r],i)=>Number.isFinite(x)&&Number.isFinite(r)&&r>0&&(!i||x>=points[i-1][0]));
  const checks={visualProfileImmutable:Object.isFrozen(p)&&p.physicsFeedback===false,
    eightUniqueRegisteredMouths:rows.length===8&&new Set(rows.map(r=>r.tubeId)).size===8,
    completeFrontAndRearDoors:rows.every(r=>r.doorFaces.length===116&&r.rearFaces.length===58),
    noOverlappingSourceFaces:new Set([...front,...rear]).size===front.length+rear.length,
    rackBoresActuallyCut:HARPOON_MOUTH_REGISTRATION_B.supportBoreCuts.length>0&&HARPOON_MOUTH_REGISTRATION_B.supportBoreCutRadiusM===p.tubeInnerRadiusM&&
      HARPOON_MOUTH_REGISTRATION_B.supportBoreCuts.every(c=>!front.includes(c.sourceFace)&&!rear.includes(c.sourceFace)&&c.triangles.every(t=>t.every(w=>w.length===3&&w.every(Number.isFinite)&&Math.abs(w.reduce((s,q)=>s+q,0)-1)<1e-8))),
    bodyAndBoosterNozzleProfilesFinite:[p.bodyShell,p.bodyBell,p.boosterShell,p.boosterBell].every(finite),
    bodyThroatRecessed:p.bodyThroatXM>p.bodyExitXM&&p.bodyBell.at(-1)[1]<p.bodyExitRadiusM,
    noLengthInflation:p.bodyExitXM===-1.525&&p.boosterExitXM===-HARPOON_PROFILE_A.public.lengthM*.5,
    boundedLaunchAndSmokeWork:p.maxLaunchEmitters===8&&p.maxSmokeSamplesPerFrame<=48&&p.launchHotLifeS<p.launchCloudLifeS,
    smokyPropellantExplicitAssumption:p.boosterSmoke.class.startsWith('USER_ASSUMED_')&&p.boosterSmoke.alpha<1&&p.boosterSmoke.spacingM>=.45,
    tunedBurnPreservesImpulse:HARPOON_PROFILE_A.sim.boosterBurnS===3.2&&HARPOON_PROFILE_A.sim.boosterAverageThrustN>0&&
      HARPOON_PROFILE_A.sim.boosterAverageThrustN<=HARPOON_PROFILE_A.public.boosterThrustN&&
      Math.abs(HARPOON_PROFILE_A.sim.boosterAverageThrustN*HARPOON_PROFILE_A.sim.boosterBurnS/(HARPOON_PROFILE_A.public.boosterThrustN*HARPOON_PROFILE_A.public.boosterBurnS)-1)<.01};
  return {schema:'HARPOON_VISUAL_CORE_B1',checks,pass:Object.values(checks).every(Boolean)};
}

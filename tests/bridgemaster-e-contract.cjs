const fs = require('node:fs');
const assert = require('node:assert/strict');
const path = require('node:path');

const file = process.argv[2] || process.env.SIM_FILE || path.join(__dirname, '../Aegis_SIM_v48_WIP12B.html');
const html = fs.readFileSync(file, 'utf8');
let scripts = 0;
for (const m of html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/gi)) {
  if (/\bsrc\s*=|application\/json/.test(m[1])) continue;
  new Function(m[2]);
  scripts++;
}

const checks = {
  inlineJavaScript: scripts === 1,
  noLegacyRadar: !/SPS[-_ ]?73|AN\/SPS-73/i.test(html),
  correctIdentity: html.includes("schema:'AEGIS_BRIDGEMASTER_E_INSTALLATION_V48_WIP08'") &&
    html.includes("family:'Northrop Grumman Sperry Marine BridgeMaster E'") &&
    html.includes("channel:'S_BAND_NAV_SURFACE_WORKING_BASELINE'") &&
    html.includes("navalVariantExactConfiguration:'PUBLIC_UNKNOWN'"),
  sharedHardpoint: html.includes("x:15.75,y:5.15,z:31.78") &&
    html.includes('bridgeMasterEWorldOrigin()') && html.includes('...bmeOrigin'),
  photoDerivedMount: html.includes("mountBasis:'DDG119_PHOTO_DERIVED_UPPER_STARBOARD_YARDARM'") &&
    html.includes("name='BRIDGEMASTER_E_UPPER_STARBOARD_PLATFORM'") &&
    html.includes('meshAtAuthoritativeHardpoint:meshAtHardpoint'),
  mastOutfit: html.includes("mastOutfit.name='DDG119_PHOTO_DERIVED_MAST_OUTFIT'") &&
    html.includes("mastWires.name='DDG119_MAST_WHIP_AND_CABLE_BATCH'") &&
    html.includes("'LOWER_YARD_RF_HOUSING_'+(side>0?'STARBOARD':'PORT')") &&
    html.includes('duplicateFunctionalRadar:false') && html.includes('mastOutfitBounded:boundedOutfit'),
  physicalDamage: html.includes('"BridgeMaster E":"bridgemaster_e.01"') &&
    html.includes("'BridgeMaster E':'BRIDGEMASTER_E'") && html.includes("getModuleDmg('BridgeMaster E')"),
  actualMesh: html.includes("name='BRIDGEMASTER_E_12FT_OPEN_ARRAY'") &&
    html.includes("name='BRIDGEMASTER_E_AUTHORITATIVE_ROTOR'") &&
    html.includes('this.bridgeMasterERotor.rotation.y=-(Number(st?.radar?.bridgeMasterEAngleRad)||0)'),
  userInterface: html.includes('id="external3DBridgeMasterEBtn"') &&
    html.includes('toggleBridgeMasterERadar()'),
  readOnly3d: html.includes("schema:'AEGIS_3D_BRIDGEMASTER_E_AUDIT_V48_WIP08'") &&
    html.includes('presentationOnly:true,physicsFeedback:false'),
  publicSbandBaseline: html.includes('frequencyMHz:3050') && html.includes('peakPowerKw:30') &&
    html.includes('antennaApertureFt:12') && html.includes('horizontalBeamwidthDeg:2') &&
    html.includes('verticalBeamwidthDeg:30') && html.includes('antennaGainDb:26'),
  pulseModes: html.includes("pulseModes:{SHORT:{id:'SHORT',pulseWidthUs:.05,prfHz:1800") &&
    html.includes("MEDIUM:{id:'MEDIUM',pulseWidthUs:.25,prfHz:1800") &&
    html.includes("LONG:{id:'LONG',pulseWidthUs:.75,prfHz:785") &&
    html.includes('pulseModes:BRIDGEMASTER_E_PULSE_MODES,...BRIDGEMASTER_E_PROFILE_INSTALLATION}=ACTIVE_SHIP_PROFILE.sensors.bridgeMasterE;'),
  trackingLimits: html.includes('const BRIDGEMASTER_E_TRACK_CAPACITY = BRIDGEMASTER_E_INSTALLATION.maxRadarTracks;') &&
    html.includes('const BRIDGEMASTER_E_TRACK_MAX_KM = BRIDGEMASTER_E_INSTALLATION.trackMaxNmi*1.852;') &&
    html.includes('const BRIDGEMASTER_E_DISPLAY_SCALE_MAX_KM = BRIDGEMASTER_E_INSTALLATION.displayScaleMaxNmi*1.852;') &&
    html.includes('rangeM:BRIDGEMASTER_E_TRACK_MAX_KM*1000,trackRangeM:BRIDGEMASTER_E_TRACK_MAX_KM*1000') &&
    html.includes('displayScaleMaxM:BRIDGEMASTER_E_DISPLAY_SCALE_MAX_KM*1000'),
  cadence: html.includes('const BRIDGEMASTER_E_RPM = BRIDGEMASTER_E_INSTALLATION.nominalRpm;') &&
    html.includes('const BRIDGEMASTER_E_HIGH_SPEED_RPM = BRIDGEMASTER_E_INSTALLATION.highSpeedRpm;') &&
    html.includes('const BRIDGEMASTER_E_NOMINAL_REVISIT_S = 60/BRIDGEMASTER_E_RPM;')
};

assert.deepEqual(checks, Object.fromEntries(Object.keys(checks).map(key => [key, true])));
console.log(JSON.stringify({ result: 'PASS', scope: 'BRIDGEMASTER_E_WIP08_STATIC_CONTRACT', scripts, checks }, null, 2));

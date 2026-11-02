// Static function-scope comparison; no simulation or browser is run.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=path.resolve(__dirname,'../../../..');
const {load}=require(path.join(root,'docs/gun/B2/phase1a/compact_source.cjs'));
const baseline=path.join(root,'Aegis_SIM_v48_WIP_FRIENDLY_CONTACT_A.html'),candidate=path.join(root,'Aegis_SIM_v48_WIP_TRACK_A.html');
const a=load(baseline),b=load(candidate),hash=s=>crypto.createHash('sha256').update(s).digest('hex');
const hooks=JSON.parse(fs.readFileSync(path.join(__dirname,'hook-locations.json'))),allowed=new Set(hooks.map(x=>x.function).concat('createWeaponContextD'));
const changed=[...a.symbols].filter(([n,v])=>b.symbols.get(n)?.code!==v.code).map(([n])=>n),added=[...b.symbols.keys()].filter(n=>!a.symbols.has(n)),forbiddenChanged=changed.filter(n=>!allowed.has(n));
const protectedSymbols=[...a.symbols].filter(([n])=>/^(trackEkf|trackRadarAssociation|trackSurfaceRadarAssociation|trackSurfacePositionAssociation|trackCartesianAssociation|trackRadarPrediction|trackSurfaceRadarPrediction|trackApplySurfaceDomainConstraint|trackHasAirObservationFC|trackNoteAirObservationFC|trackMayAccept|updateTrackClassification|observerClassifyC|shipboardRadarEchoField|rf|SAM_|TRACK_FILTER_MODEL|SENSOR_MODEL|HELO_|APS_|ISAR_|HARPOON_|SHIP_EQUIPMENT|NETWORK_POLICY|OBSERVER_POLICY|CIWS_C55_POLICY|computeInterceptPk|applyInterceptResult|networkIntersectionG|networkNisG|updateMissile|updateHarpoon|gameFlightTermination|computeZEM|_wip79|_arh|_sarh|wip99|_wip99)/.test(n)).map(([name,v])=>({name,before:hash(v.code),after:hash(b.symbols.get(name)?.code??''),equal:v.code===b.symbols.get(name)?.code}));
const out={schema:'AEGIS_TRACK_A_SCOPE_1',baselineHtmlSha256:hash(fs.readFileSync(baseline)),candidateHtmlSha256:hash(fs.readFileSync(candidate)),pass:!forbiddenChanged.length&&protectedSymbols.every(x=>x.equal),changed,added,forbiddenChanged,protectedSymbols};
fs.writeFileSync(path.join(__dirname,'SCOPE.json'),JSON.stringify(out,null,2)+'\n');
console.log(JSON.stringify({pass:out.pass,changed,added,protected:protectedSymbols.length,forbiddenChanged}));
if(!out.pass)process.exitCode=1;

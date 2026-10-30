// HELI_F2. All receiver/ISAR values are SIM_TUNED, never certified APS-153 figures.
const ISAR_SPEC_F2=Object.freeze(Object.fromEntries(Object.entries({
 minRangeM:[9300,'APS153_MODE_TABLE_UNOFFICIAL'],maxRangeM:[296000,'APS153_MODE_TABLE_UNOFFICIAL'],rpm:[0,'APS153_MODE_TABLE_UNOFFICIAL'],
 wavelengthM:[.032,'GENERIC_RADAR_PRINCIPLE'],rangeResolutionM:[2,'GENERIC_RADAR_PRINCIPLE'],integrationS:[16,'GENERIC_RADAR_PRINCIPLE'],sampleIntervalS:[.5,'GENERIC_RADAR_PRINCIPLE'],
 featureBins:[12,'GENERIC_RADAR_PRINCIPLE'],contactMaxAgeS:[30,'GENERIC_RADAR_PRINCIPLE'],selectionGateM:[1800,'GENERIC_RADAR_PRINCIPLE'],associationSigma:[3,'GENERIC_RADAR_PRINCIPLE'],targetGateM:[1200,'GENERIC_RADAR_PRINCIPLE'],
 minSnr:[1,'GENERIC_RADAR_PRINCIPLE'],snrQualityScale:[12,'GENERIC_RADAR_PRINCIPLE'],resolutionQualityM:[8,'GENERIC_RADAR_PRINCIPLE'],angularFloorRad:[.00001,'GENERIC_RADAR_PRINCIPLE'],
 lengthSigmaFloorM:[2,'GENERIC_RADAR_PRINCIPLE'],heightSigmaFloorM:[1.2,'GENERIC_RADAR_PRINCIPLE'],mastSigmaFloor01:[.025,'GENERIC_RADAR_PRINCIPLE'],aspectLengthErrorFraction:[.16,'GENERIC_RADAR_PRINCIPLE'],poorQualityLengthFraction:[.13,'GENERIC_RADAR_PRINCIPLE'],poorQualityHeightM:[10,'GENERIC_RADAR_PRINCIPLE'],
 rfLengthSigmaM:[3,'GENERIC_RADAR_PRINCIPLE'],rfHeightSigmaM:[1.5,'GENERIC_RADAR_PRINCIPLE'],rfMastSigma01:[.025,'GENERIC_RADAR_PRINCIPLE'],
 seaRollDegPerM:[.8,'GENERIC_RADAR_PRINCIPLE'],seaPitchDegPerM:[.22,'GENERIC_RADAR_PRINCIPLE'],seaYawDegPerM:[.12,'GENERIC_RADAR_PRINCIPLE'],seaRollPeriodS:[8,'GENERIC_RADAR_PRINCIPLE'],seaPitchPeriodS:[6,'GENERIC_RADAR_PRINCIPLE'],seaYawPeriodS:[11,'GENERIC_RADAR_PRINCIPLE'],
 clutterScale:[1,'GENERIC_RADAR_PRINCIPLE'],pdSnrScale:[3,'GENERIC_RADAR_PRINCIPLE'],minimumSamples:[3,'GENERIC_RADAR_PRINCIPLE'],
 bufferCapacity:[8,'GENERIC_RADAR_PRINCIPLE'],receiverCapacity:[16,'GENERIC_RADAR_PRINCIPLE'],resultMaxAgeS:[600,'GENERIC_RADAR_PRINCIPLE'],positionSpeedPriorMps:[15,'GENERIC_RADAR_PRINCIPLE'],positionGateSigma:[4,'GENERIC_RADAR_PRINCIPLE'],positionGateMaxM:[8000,'GENERIC_RADAR_PRINCIPLE'],
 unknownWeight:[.12,'GENERIC_RADAR_PRINCIPLE'],scoreTemperature:[1.4,'GENERIC_RADAR_PRINCIPLE'],libraryLengthSigmaM:[4,'GENERIC_RADAR_PRINCIPLE'],libraryHeightSigmaM:[2,'GENERIC_RADAR_PRINCIPLE'],libraryMastSigma01:[.04,'GENERIC_RADAR_PRINCIPLE'],diagnosticSamples:[64,'GENERIC_RADAR_PRINCIPLE'],diagnosticSeed:[153202,'GENERIC_RADAR_PRINCIPLE']
}).map(([k,[value,reference]])=>[k,Object.freeze({value,source:'SIM_TUNED',reference})])));
const ISAR_F2=Object.freeze(Object.fromEntries(Object.entries(ISAR_SPEC_F2).map(([k,v])=>[k,v.value])));
/*__ISAR_LIBRARY_F2__*/
// Pure geometry extraction, shared by offline intelligence generation and RF synthesis.
// No class names, identities, entity keys or lookup of a class from a live target.
function isarShapeFromGeometryF2(g,boxes=[]){
 const rows=g.hullStations??g.stations;if(!rows?.length)return null;const lo=Math.min(...rows.map(q=>q[0])),hi=Math.max(...rows.map(q=>q[0])),lengthM=hi-lo,n=ISAR_F2.featureBins;
 const volumes=boxes.map(b=>({x0:b.x0??b.oX-b.hL,x1:b.x1??b.oX+b.hL,z:b.z1??b.zMax})).filter(b=>[b.x0,b.x1,b.z].every(Number.isFinite));
 const heightsM=Array.from({length:n},(_,i)=>{const x0=lo+lengthM*i/n,x1=lo+lengthM*(i+1)/n,deck=rows.filter(q=>q[0]>=x0&&q[0]<=x1).map(q=>q[2]);return Math.max(0,...deck,...volumes.filter(b=>b.x0<=x1&&b.x1>=x0).map(b=>b.z));});
 const top=volumes.reduce((a,b)=>!a||b.z>a.z?b:a,null),mastPosition01=top?apsClampF(((top.x0+top.x1)/2-lo)/lengthM,0,1):.5;
 return {lengthM,heightsM,mastPosition01,mastHeightM:top?.z??Math.max(...heightsM)};
}
function isarQualityF2(snr,deltaThetaRad,completion){const crossResolutionM=ISAR_F2.wavelengthM/(2*Math.max(ISAR_F2.angularFloorRad,deltaThetaRad));return {crossResolutionM,quality:apsClampF(snr/(snr+ISAR_F2.snrQualityScale)*ISAR_F2.resolutionQualityM/(ISAR_F2.resolutionQualityM+crossResolutionM)*completion,0,1)};}
// Measured features only. An intelligence library is information, never target truth.
function isarClassifyF2(f){
 const candidates=ISAR_LIBRARY_F2.map(lib=>{const scoreFor=reverse=>{const z=reverse?[...lib.heightsM].reverse():lib.heightsM,mp=reverse?1-lib.mastPosition01:lib.mastPosition01;
 const length=((f.lengthM-lib.lengthM)/Math.hypot(f.lengthSigmaM,ISAR_F2.libraryLengthSigmaM))**2,height=f.heightsM.reduce((sum,v,i)=>sum+((v-z[i])/Math.hypot(f.heightSigmaM,ISAR_F2.libraryHeightSigmaM))**2,0)/z.length,mast=((f.mastPosition01-mp)/Math.hypot(f.mastSigma01,ISAR_F2.libraryMastSigma01))**2;return (length+height+mast)/3;};
 return {classId:lib.classId,label:lib.label,score:Math.min(scoreFor(false),scoreFor(true))};});
 const weights=candidates.map(c=>Math.exp(-Math.min(100,c.score)/(2*ISAR_F2.scoreTemperature))),unknown=ISAR_F2.unknownWeight+(1-f.quality),total=weights.reduce((a,b)=>a+b,unknown);
 return candidates.map((c,i)=>({...c,confidence:weights[i]/total})).sort((a,b)=>b.confidence-a.confidence);
}
function isarFinishFeaturesF2(mean,snr,deltaThetaRad,completion,normal){
 const {quality,crossResolutionM}=isarQualityF2(snr,deltaThetaRad,completion),aspect=apsClampF(mean.aspectUncertainty01,0,1),lengthSigmaM=Math.hypot(ISAR_F2.lengthSigmaFloorM,ISAR_F2.rangeResolutionM,crossResolutionM*aspect,mean.lengthM*ISAR_F2.aspectLengthErrorFraction*aspect,mean.lengthM*ISAR_F2.poorQualityLengthFraction*(1-quality)),heightSigmaM=Math.hypot(ISAR_F2.heightSigmaFloorM,crossResolutionM,ISAR_F2.poorQualityHeightM*(1-quality)),mastSigma01=Math.hypot(ISAR_F2.mastSigmaFloor01,crossResolutionM/Math.max(1,mean.lengthM),(1-quality)*ISAR_F2.rfMastSigma01);
 const f={lengthM:Math.max(1,mean.lengthM+normal()*lengthSigmaM),lengthSigmaM,heightsM:mean.heightsM.map(v=>Math.max(0,v+normal()*heightSigmaM)),heightSigmaM,mastPosition01:apsClampF(mean.mastPosition01+normal()*mastSigma01,0,1),mastSigma01,quality,crossResolutionM,rangeResolutionM:ISAR_F2.rangeResolutionM,deltaThetaRad};
 return {...f,candidates:isarClassifyF2(f)};
}

function mapEsmReadA(id,c){
  const q=esmPresentationCopyA(c),e=q.estimate??null,origin=esmUiWorldA(e?.latestOriginM??q.bearingHistory.at(-1)?.originM),estimate=esmUiWorldA(e?.positionM),state=q.state??e?.state??'BEARING_ONLY';
  return {key:'ESM:'+id,kind:'ESM',id,label:'ESM '+id,identity:'UNKNOWN',classification:esmUiModeLabelA(state),
    bearingRad:q.bearing,bearingSigmaDeg:q.bearingSigmaDeg,band:q.band,emitterClass:q.emitterClass,type:q.type,
    confidence:q.quality,measuredAtS:e?.measuredAtS??q.measuredAtS,source:'ESM',esmState:state,estimate:e,
    originWorld:origin,estimateWorld:estimate,bearingHistory:q.bearingHistory,truthUsed:false,automaticEngagementAuthority:false};
}

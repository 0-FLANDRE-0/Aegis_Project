// Retain complete 10Hz trajectory proof; 60Hz command logs are in the A/B raw data.
module.exports = function proof(q) {
  const first = q.samples.find(x => x.shelfM != null);
  return { weapon:q.weapon,rangeKm:q.rangeKm,altM:q.altM,targetSpeedMps:q.targetSpeedMps,crossSpeedMps:q.crossSpeedMps,success:q.success,reason:q.reason,closestM:q.closestM,fuzeMissM:q.fuzeMissM,flightTimeS:q.flightTimeS,rng:q.rng,samples:q.samples,firstShelf:first?{timeS:first.timeS,shelfM:first.shelfM}:null };
};

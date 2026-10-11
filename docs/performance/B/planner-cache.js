// PERF_B LIVE_CANONICAL: synchronous, single-build anonymous-track forecasts.
// ctx is new for every wip118BuildEngagementControl, never stored on a runtime.
// Weapons only read these forecasts. Current reservation availability is NOT cached.
function wip118NezForecastPerfB(th,delayS,accel,ctx){
  const forecasts=ctx.nezForecastsPerfB??(ctx.nezForecastsPerfB=new WeakMap());
  let byDelay=forecasts.get(th);if(!byDelay){byDelay=new Map();forecasts.set(th,byDelay);}
  if(byDelay.has(delayS))return byDelay.get(delayS);
  const future=wip118FutureThreat(th,delayS,accel,true);byDelay.set(delayS,future);return future;
}
function wip118NezCandidatesPerfB(tr,ctx){
  const candidates=ctx.nezCandidatesPerfB??(ctx.nezCandidatesPerfB=new WeakMap());
  if(candidates.has(tr))return candidates.get(tr);
  const rows=spg62ReservationCandidateIlluminators(tr);candidates.set(tr,rows);return rows;
}

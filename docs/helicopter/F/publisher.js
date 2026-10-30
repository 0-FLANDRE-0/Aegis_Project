function heloPublishRadarPlotsE(h,plots){
 const r=ENGAGEMENT_RUNTIME.ships.get(h.ownerEntityId);if(!r)return;const s=heloHawklinkStateE(h),now=simStepCounter*SIM_FIXED_DT,q=heloSensorOwnerE(h)?.aviation.heloSensorsE?.get(h.id)?.radar;
 // Separate equal quotas avoid H1 starving H2. Their combined sustained rate
 // is bounded below the 64-entry / .4s transport capacity. No backlog exists.
 if(s.apsTokensF==null){s.apsTokensF=APS_F.reportBurst;s.apsTokenAtF=now;s.apsCursorF=0;}s.apsTokensF=Math.min(APS_F.reportBurst,s.apsTokensF+Math.max(0,now-s.apsTokenAtF)*APS_F.reportRatePerSecond/2);s.apsTokenAtF=now;
 const offset=plots.length?s.apsCursorF%plots.length:0;let sent=0;for(let i=0;i<plots.length;i++){const plot=plots[(i+offset)%plots.length];s.attemptedTotal++;const sequence=++s.sequence;if(!s.connected)continue;if(heloHawklinkSelfContactE(r,plot)){s.selfRejectedTotal++;continue;}
  const port=r.combatSystem.observerC.offboard;if(s.apsTokensF<1||port.queue.length>=64-APS_F.reportQueueReserve){if(q)q.stats.transportThrottled++;continue;}
  const report={schema:'AEGIS_OFFBOARD_PLOT_C_1',sourceId:'H'+(h.slot+1),sequence,measuredAtS:plot.measuredAtS,positionM:{...plot.positionM},covarianceM2:[...plot.covarianceM2],domainEvidence:{...plot.domainEvidence}},result=ingestOffboardReportC(r,report);
  if(result.ok){s.apsTokensF--;sent++;s.transmittedTotal++;s.lastTransmitS=now;s.recentTransmitS.push(now);}else s.rejectedTotal++;
 }if(plots.length)s.apsCursorF=(offset+Math.max(1,sent))%plots.length;
}

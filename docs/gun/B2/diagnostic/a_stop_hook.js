// PHASE0 diagnostic A correction only. Not shipped.
// STOP fields do not clear the native dynamics closure's impact-induced sway.
// The existing native horizontal-contact stop clears that closure while retaining
// roll/trim/heave attitude state. All non-A paths call the old wrapper unchanged.
const g2AStoppedTick=simulateFixedTick;
simulateFixedTick=function(dt){
 if(g2.active&&g2.flags.stopped)getShipDynamicsV15().haltHorizontalContact();
 return g2AStoppedTick(...arguments);
};

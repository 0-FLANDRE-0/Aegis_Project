// Shared detached presentation frame. Never evaluate a sensor/authority query here.
const f=pipChartFrameA,tracks=f.tracks,missiles=f.missiles,ramMissiles=f.ramMissiles,esmContacts=f.esm;
const ownChaffCartridges=f.cartridges,ownChaffs=f.chaff,ciws=f.ciws,ciwsBullets=f.bullets,mainGunProjectilesWip13B3=f.shells,shipNav=f.shipNav,spyScheduler=f.spy,radar=f.radar,shipHP=f.hp,lockCursor=f.cursor,selectedLockId=f.lockId;
const trackIsDisplayable=tr=>!!tr?._chartVisible,trackIsFireControlQuality=tr=>!!tr?._chartReady,trackCovarianceMetrics=tr=>tr?._chartUq??{},networkPresentationTrackG=tr=>tr,wip121BdaTrackPresentation=tr=>tr?._chartBda??{kind:'LIVE'},nulkaEntities15B=()=>f.nulka;

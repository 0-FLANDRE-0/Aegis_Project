// Presentation diagnostics; intentionally no simulation control methods.
window.__VIEWPORT_A__=Object.freeze({
 snapshot(){const v=WIP148_EXTERNAL_3D;return {schema:'AEGIS_VIEWPORT_A_1',viewport:AEGIS_VIEWPORT.snapshot(),twoD:{tacticalViewKm,mapZoom:vpUpdateMapZoomA(),pan:{...camOffset},ownship:worldToScreen(aircraft.x(),aircraft.y()),centerWorld:screenToWorld(AEGIS_VIEWPORT.twoD.cx,AEGIS_VIEWPORT.twoD.cy),bounds:tacticalViewportWorldBounds(),scaleLabel:formatTacticalScaleLabel(),scaleBarKm:pickNiceScaleBarKm(tacticalViewKm*.2)},threeD:{active:v.active,pan:{...v.c14CameraPan},orbit:{...v.orbit},fov:v.camera?.fov,shortFovDeg:v.vpShortFovDegA,viewOffset:v.camera?.view?{...v.camera.view}:null,version:v._viewportVersionA},distanceLimits:{...VP_TACTICAL_DISTANCE_A},presentationOnly:true};},
 worldToScreen,screenToWorld,
 setPan(x,y){if(Number.isFinite(x)&&Number.isFinite(y)){camOffset.x=x;camOffset.y=y;}},
 setDistance(km){if(Number.isFinite(km)){tacticalViewKm=clamp(km,VP_TACTICAL_DISTANCE_A.minKm,VP_TACTICAL_DISTANCE_A.maxKm);vpUpdateMapZoomA();updateTacticalScaleLabel();}},
 draw(){drawRadar();},
 projectShipPoint(xM=0,yM=11,zM=0){const v=WIP148_EXTERNAL_3D;if(!v.ready)return null;v.camera.updateMatrixWorld(true);const r=v.canvas.getBoundingClientRect(),p=v.shipRoot.localToWorld(new v.THREE.Vector3(xM,yM,zM)).project(v.camera);return {x:r.x+(p.x+1)*r.width/2,y:r.y+(1-p.y)*r.height/2,depth:p.z};}
});

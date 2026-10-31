const fs=require('fs'),{load}=require('../../missile/launch-handoff/A/source.cjs');
const q=load('Aegis_SIM_v48_WIP_MAP_D.html');
const names=['nulkaAuto15B','updateSoftKillDoctrine','harpoonRouteEditingE','updateNulkaUi15B','networkSetRadarG','emconDesignationSnapshotF2','toggleEmcon','updateMk36ButtonLabel','updateSoftKillAutoButtonLabel','updateSlq32EaButtonLabels','updateModeButtonLabel','updateEngagementControlButtonLabel','updateTrackIdentityButtonLabelA3','wip13b5UpdateGunButtonLabels','wip14a14Refresh3dQuickControls','wip13cUpdateMissileControlLabels','harpoonUpdateUIA','harpoonBindUIA','wip14a14UiSnapshot','bunkerRestoreGunInventory','harpoonRouteUndoMapA'];
const out={};for(const n of names){const s=q.symbols.get(n);out[n]={code:s.code,ordinal:q.source.slice(0,s.start).split(s.code).length-1};}
fs.writeFileSync('docs/map/E/base-functions.json',JSON.stringify(out,null,2));console.log(out.harpoonRouteEditingE);

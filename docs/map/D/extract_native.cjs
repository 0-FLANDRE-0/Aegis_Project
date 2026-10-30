const fs=require('fs'),crypto=require('crypto'),{load}=require('../../missile/launch-handoff/A/source.cjs');
const q=load('Aegis_SIM_v48_WIP_MAP_C.html'),names=['harpoonGateA','harpoonAutoTubeGateD','harpoonRouteGateE','surfaceMissileTrackReadinessWip13C4'];
const rows=names.map(n=>{const v=q.symbols.get(n);if(!v)throw Error(n);return{name:n,sha256:crypto.createHash('sha256').update(v.code).digest('hex'),line:v.line,code:v.code};});
fs.writeFileSync('docs/map/D/native_preview.inc.js',rows.map(r=>r.code).join('\n')+'\n');fs.writeFileSync('docs/map/D/native-preview-manifest.json',JSON.stringify({sourceHtmlSha256:q.htmlSha256,functions:rows.map(({code,...r})=>r)},null,2)+'\n');console.log(rows.map(r=>({name:r.name,line:r.line,sha256:r.sha256})));

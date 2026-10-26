// CLEAN_A audit preparation. No production function is patched here.
const fs=require('fs'),path=require('path'),zlib=require('zlib');
const H=__dirname,R=path.resolve(H,'../../..'),{load,sha}=require('../../missile/launch-handoff/A/source.cjs');
const names={KAPPA:'archive/v48/WIP_KAPPA_PIP_LOS_A/Aegis_SIM_v48_WIP_KAPPA_PIP_LOS_A.html',DZT:'archive/v48/WIP_FUZE_ZEM_A/Aegis_SIM_v48_WIP_FUZE_ZEM_A.html',HANDOFF:'Aegis_SIM_v48_WIP_LAUNCH_HANDOFF_A.html',ARH:'Aegis_SIM_v48_WIP_ARH_MEASUREMENT_FIX_A.html',VERTICAL:'Aegis_SIM_v48_WIP_NEAR_VERTICAL_PATH_FIX_A.html',LATEST:'Aegis_SIM_v48_WIP_ENV_D_REMEASURE_A.html',VP:'archive/v48/WIP_VP_A/Aegis_SIM_v48_WIP_VP_A.html'};
const versions={},loaded={};for(const[n,f]of Object.entries(names)){const q=load(path.join(R,f));loaded[n]=q;versions[n]={file:f,htmlSha256:q.htmlSha256,mainSha256:sha(q.source)};}
const comparisons=[];for(const[a,b]of [['KAPPA','DZT'],['DZT','HANDOFF'],['HANDOFF','ARH'],['ARH','VERTICAL'],['VERTICAL','LATEST']]){
 const x=loaded[a],y=loaded[b],changed=[],added=[];
 for(const[n,s]of x.symbols)if(s.type==='function'&&y.symbols.has(n)&&s.code!==y.symbols.get(n).code)changed.push({name:n,beforeSha256:sha(s.code),afterSha256:sha(y.symbols.get(n).code)});
 for(const[n,s]of y.symbols)if(s.type==='function'&&!x.symbols.has(n))added.push(n);
 comparisons.push({before:a,after:b,changed,added});
}
// Causal control only: the product keeps every launch-handoff fix. This test
// artifact restores the old launcher function without touching any coefficient.
const d=loaded.DZT.symbols.get('updateMissileBodyB3'),h=loaded.HANDOFF,s=h.symbols.get('updateMissileBodyB3');
const source=h.source.slice(0,s.start)+d.code+h.source.slice(s.end);let html=h.raw.toString();const p=html.match(/data-c55-index="13">([^<]+)<\/script>/),gz=zlib.gzipSync(source,{level:9,mtime:0});html=html.replace(p[1],gz.toString('base64'));const m=html.match(/const records=(\[.*?\]);/s),rs=JSON.parse(m[1]);Object.assign(rs[13],{rawBytes:Buffer.byteLength(source),gzipBytes:gz.length,sha256:sha(source)});html=html.replace(m[0],'const records='+JSON.stringify(rs)+';');
const temp='/tmp/aegis-clean-a/variants';fs.mkdirSync(temp,{recursive:true});const file=path.join(temp,'HANDOFF_REVERT_LAUNCH_ONLY.html');fs.writeFileSync(file,html);versions.REVERT_LAUNCH_ONLY={file,htmlSha256:sha(html),diagnosticOnly:true,revertedFunction:'updateMissileBodyB3',retainedUnusedHelper:true};
fs.mkdirSync(path.join(H,'evidence'),{recursive:true});fs.mkdirSync(path.join(H,'results'),{recursive:true});fs.writeFileSync(path.join(H,'builds.json'),JSON.stringify({baseCommit:'837539645b663e8653caa7aac037e6857efe5a2d',versions,comparisons},null,2)+'\n');console.log(JSON.stringify(comparisons,null,2));

const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {unpack,mainScope}=require('../../fuze-zem/A/source.cjs');
const H=__dirname,build=JSON.parse(fs.readFileSync(path.join(H,'build.json'))),sha=x=>crypto.createHash('sha256').update(x).digest('hex');
const deg=x=>x*Math.PI/180;
function loadFunction(file){
  const raw=fs.readFileSync(file),source=unpack(raw),sym=mainScope(source).symbols.get('_wip79KappaPipState');
  const make=new Function(`const clamp=(x,a,b)=>Math.max(a,Math.min(b,x)),deg=x=>x*Math.PI/180,window={WIP79_KAPPA_TERMINAL_POLICY:'PIP_LOS'},_samB1VecCopy=x=>({...x}),samNavB1OwnState=m=>m.own,weaponLinkB3AdvisedTgo=(m,t,x)=>x,_wip81KappaTgoLimit=x=>x,loftB4ShapeWaypoint=(m,t,q)=>({...q,shapedGammaFDeg:q.gammaF/deg(1),vectorNormMps:Math.hypot(q.vFinal.x,q.vFinal.y,q.vFinal.z)});${sym.code};return _wip79KappaPipState;`);
  return{fn:make(),functionSha256:sha(sym.code),htmlSha256:sha(raw)};
}
function scenario(name,{dx,dy,dz,mx=0,my=0,mz=0,vx=300,vy=0,vz=0}){
  const speed=Math.max(80,Math.hypot(vx,vy,vz)),m={_wip81KappaTgoRawS:0,own:{posM:{x:mx,y:my,z:mz},velMps:{x:vx,y:vy,z:vz}}};
  const targetState={isValid:true,selfStateM:m.own,posM:{x:mx+dx,y:my+dy,z:mz+dz},velMps:{x:0,y:0,z:0},rangeM:Math.hypot(dx,dy,dz)};
  return{name,m,targetState,speed,requestedGammaDeg:Math.atan2(dz,Math.hypot(dx,dy))/deg(1)};
}
const cases=[
 scenario('LEVEL_1KM',{dx:1000,dy:0,dz:0}),
 scenario('BOUNDARY_UP_59_9',{dx:1000,dy:0,dz:Math.tan(deg(59.9))*1000}),
 scenario('BOUNDARY_UP_60_1',{dx:1000,dy:0,dz:Math.tan(deg(60.1))*1000}),
 scenario('NEAR_VERTICAL_UP',{dx:100,dy:0,dz:57295}),
 scenario('NEAR_VERTICAL_DOWN',{dx:100,dy:0,dz:-60000,mz:60000}),
 scenario('TINY_HORIZONTAL_VALID',{dx:.1,dy:0,dz:0}),
 scenario('TINY_LEFT_UP',{dx:-.1,dy:0,dz:100}),
 scenario('TINY_RIGHT_UP',{dx:.1,dy:0,dz:100}),
 scenario('EXACT_VERTICAL_UP',{dx:0,dy:0,dz:20000}),
 scenario('EXACT_VERTICAL_DOWN',{dx:0,dy:0,dz:-20000,mz:20000}),
 scenario('COINCIDENT',{dx:0,dy:0,dz:0,mz:1000})
];
const rows=[];
for(const variant of ['BASE','MIN','FINAL']){
  const loaded=loadFunction(build.variants[variant].file);
  for(const c of cases){
    const q=loaded.fn(c.m,c.targetState),values=[q.gammaF,q.vFinal.x,q.vFinal.y,q.vFinal.z,q.vectorNormMps];
    rows.push({variant,name:c.name,requestedGammaDeg:c.requestedGammaDeg,actualGammaDeg:q.shapedGammaFDeg,requestedSpeedMps:c.speed,vectorNormMps:q.vectorNormMps,vector:q.vFinal,finite:values.every(Number.isFinite),speedRelativeError:Math.abs(q.vectorNormMps-c.speed)/c.speed,htmlSha256:loaded.htmlSha256,functionSha256:loaded.functionSha256});
  }
}
const by=(variant,name)=>rows.find(x=>x.variant===variant&&x.name===name),checks={};
checks.baseClampReproduced=Math.abs(by('BASE','BOUNDARY_UP_60_1').actualGammaDeg-60)<1e-9&&Math.abs(by('BASE','NEAR_VERTICAL_UP').actualGammaDeg-60)<1e-9&&Math.abs(by('BASE','NEAR_VERTICAL_DOWN').actualGammaDeg+60)<1e-9;
checks.minimumUnclamps=by('MIN','BOUNDARY_UP_60_1').actualGammaDeg>60&&by('MIN','NEAR_VERTICAL_UP').actualGammaDeg>89&&by('MIN','NEAR_VERTICAL_DOWN').actualGammaDeg<-89;
checks.minimumSmallHorizontalShrinkReproduced=by('MIN','TINY_HORIZONTAL_VALID').speedRelativeError>.8;
checks.finalAnglesNatural=['LEVEL_1KM','BOUNDARY_UP_59_9','BOUNDARY_UP_60_1','NEAR_VERTICAL_UP','NEAR_VERTICAL_DOWN','EXACT_VERTICAL_UP','EXACT_VERTICAL_DOWN'].every(n=>Math.abs(by('FINAL',n).actualGammaDeg-by('FINAL',n).requestedGammaDeg)<1e-9);
checks.finalFinite=rows.filter(x=>x.variant==='FINAL').every(x=>x.finite);
checks.finalSpeedPreserved=rows.filter(x=>x.variant==='FINAL').every(x=>x.speedRelativeError<1e-12);
checks.finalCoincidentDeterministic=JSON.stringify(by('FINAL','COINCIDENT').vector)==='{"x":300,"y":0,"z":0}';
checks.leftRightContinuous=by('FINAL','TINY_LEFT_UP').vector.x<0&&by('FINAL','TINY_RIGHT_UP').vector.x>0&&Math.abs(by('FINAL','TINY_LEFT_UP').vector.z-by('FINAL','TINY_RIGHT_UP').vector.z)<1e-12;
const out={schema:'AEGIS_NEAR_VERTICAL_PATH_FIX_A_GEOMETRY_1',pass:Object.values(checks).every(Boolean),checks,definition:{requestedGamma:'atan2(PIP vertical displacement, horizontal displacement)',coincident:'retain current horizontal heading and velocity pitch; deterministic +X only if no horizontal velocity exists'},rows};
fs.writeFileSync(path.join(H,'geometry.json'),JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify({pass:out.pass,checks},null,2));if(!out.pass)process.exitCode=1;

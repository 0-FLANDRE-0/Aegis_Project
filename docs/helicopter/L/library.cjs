// Offline only. Add one registration object to library-input.json for a new class.
const fs=require('fs'),vm=require('vm'),path=require('path'),dir=__dirname,input=JSON.parse(fs.readFileSync(path.join(dir,'library-input.json'),'utf8'));
const code=fs.readFileSync(path.join(dir,'model.js'),'utf8'),ctx=vm.createContext({Object,Math});vm.runInContext('function apsClampF(x,a,b){return Math.max(a,Math.min(b,x))}\n'+code,ctx);
const rows=input.entries.map(e=>{ctx.g=e.geometry;ctx.b=e.boxes;return {classId:e.classId,label:e.label,...JSON.parse(vm.runInContext('JSON.stringify(isarShapeFromGeometryF2(g,b))',ctx))};});
fs.writeFileSync(path.join(dir,'library.json'),JSON.stringify({basis:input.basis,source:'SIM_TUNED',reference:'GENERIC_RADAR_PRINCIPLE',entries:rows},null,2)+'\n');console.log(rows.map(r=>[r.classId,r.lengthM,r.mastPosition01]));

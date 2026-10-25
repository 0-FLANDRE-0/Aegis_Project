const fs=require('fs'),path=require('path'),H=__dirname;
const input=JSON.parse(fs.readFileSync(path.join(H,'inputs.json'))),source=fs.readFileSync(path.join(H,'native-engine.js'),'utf8')+'\n'+fs.readFileSync(path.join(H,'private.js'),'utf8');
const factory=new Function('DATA','SETTINGS','PROFILE','PRIVATE_SHIP',source);
const seeds=require('../D/engine.cjs').seeds;
function create(){return factory(structuredClone(input.data),structuredClone(input.settings),{},{entityId:'ENV_PRIVATE',navigation:{heading:0,speed:0,positionWorld:{x:0,y:0}},weapons:{}});}
module.exports={create,input,source,seeds};

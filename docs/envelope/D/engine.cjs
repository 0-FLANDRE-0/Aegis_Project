const fs=require('fs'),path=require('path');
const H=__dirname,D=path.join(H,'diagnostic');
const input=JSON.parse(fs.readFileSync(path.join(H,'inputs.json')));
const source=fs.readFileSync(path.join(D,'native-engine.js'),'utf8')+'\n'+fs.readFileSync(path.join(D,'private.js'),'utf8');
const factory=new Function('DATA','SETTINGS','PROFILE','PRIVATE_SHIP',source);
function create(){return factory(structuredClone(input.data),structuredClone(input.settings),{},{entityId:'ENV_PRIVATE',navigation:{heading:0,speed:0,positionWorld:{x:0,y:0}},weapons:{}});}
const seeds=[
 {rngSeed:1831565813,navigationSeed:2047861954},
 {rngSeed:305419896,navigationSeed:2654435769},
 {rngSeed:2271560481,navigationSeed:1013904242},
 {rngSeed:324508639,navigationSeed:2779096485},
 {rngSeed:610839776,navigationSeed:1515870810},
];
module.exports={create,source,input,seeds};

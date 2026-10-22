/** AEGIS v48 portable source-transform: Dynamic B4 all four SAMs.
 * Accepts already-unpacked JS from the PREVIOUS MR+ESSM dynamic patch.
 * Performs only exact, fail-closed string replacements. Does not inject into a running game. */
'use strict';
const fs=require('node:fs');
const oldCondition="if((p.id==='SM2MR_B4'||p.id==='ESSM_B4') && s.mode!=='DIRECT' && s.phase!=='DIVE'){";
const newCondition="if((p.id==='SM2MR_B4'||p.id==='ESSM_B4'||p.id==='SM2ER_B4'||p.id==='SM6_B4') && s.mode!=='DIRECT' && s.phase!=='DIVE'){";
const rules=[
 [oldCondition,newCondition,2],
 ["profiles:['SM2MR_B4','ESSM_B4']","profiles:['SM2MR_B4','ESSM_B4','SM2ER_B4','SM6_B4']",2],
 ['game-only smooth dynamic shelf controller for two legacy profiles','game-only smooth dynamic shelf controller for all four SAM loft profiles',2],
 ['Only two legacy game routes opt in; ER/SM-6 keep their exact baseline logic.','Four lofted SAM routes opt in; ER/SM-6 retain their existing profile limits.',2],
 ['V48_GAME_B4_DYNAMIC_TEST','V48_GAME_B4_DYNAMIC_ALL4_TEST',2]
];
function apply(source){
  if (typeof source !== 'string')throw Error('Expected JS source string');
  if(source.includes(newCondition)){if(source.split(newCondition).length-1!==2)throw Error('partial application'); return {source,status:'already applied'};}
  for(const [a,,n] of rules){const got=source.split(a).length-1;if(got!==n)throw Error(`Unsupported source: expected ${n} occurrence(s) for ${a.slice(0,58)}, found ${got}`);}
  let out=source;for(const [a,b] of rules)out=out.split(a).join(b);return {source:out,status:'patched'};
}
module.exports={apply};
if(require.main===module){
  const [,,input,output]=process.argv;
  if(!input||!output||input===output){console.error('Usage: node AEGIS_B4_ALL4_source_patch.js INPUT_UNPACKED_JS OUTPUT_UNPACKED_JS');process.exit(2);}
  if(fs.existsSync(output))throw Error('Output exists; refusing overwrite');
  const result=apply(fs.readFileSync(input,'utf8'));fs.writeFileSync(output,result.source);console.log(result.status);
}

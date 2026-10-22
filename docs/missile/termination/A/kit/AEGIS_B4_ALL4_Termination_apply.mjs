#!/usr/bin/env node
/**
 * AEGIS v48 GAME-ONLY cumulative source transplant.
 * Applies Dynamic Loft B4 to all four SAMs AND the onboard-observation-based
 * flight termination + SM-6 battery-life patch. Node 18+ built-ins only.
 * Does not run the game or use external connections.
 */
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {resolve,extname} from 'node:path';
import {createRequire} from 'node:module';
import {gzipSync,gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
const require=createRequire(import.meta.url);
const {applyAegisB4DynamicLoft}=require('./AEGIS_B4_Dynamic_Loft_v48_port.js');
const {apply:extendAll4}=require('./AEGIS_B4_ALL4_source_patch.js');
const {apply:applyTermination}=require('./AEGIS_PostMiss_Battery_source_patch.js');
const ALL4="if((p.id==='SM2MR_B4'||p.id==='ESSM_B4'||p.id==='SM2ER_B4'||p.id==='SM6_B4') && s.mode!=='DIRECT' && s.phase!=='DIVE'){";
function requireCount(s,sub,count){const n=s.split(sub).length-1;if(n!==count)throw Error('Unsupported source: '+sub.slice(0,66)+' has '+n+' expected '+count);}
function patchJs(s){
 let state=s,steps=[];
 if(state.includes(ALL4)){
  requireCount(state,ALL4,2);
  steps.push('Dynamic B4 ALL4 already applied');
 }else{
  const a=applyAegisB4DynamicLoft(state);state=a.source;steps.push('MR+ESSM loft: '+a.status);
  const b=extendAll4(state);state=b.source;steps.push('ER+SM6 loft: '+b.status);
 }
 const c=applyTermination(state);state=c.source;steps.push('post-miss+SM6 battery: '+c.status);
 return {source:state,steps};
}
function patchHtml(html){
 const re=/(<script type="application\/octet-stream" data-c55-index="13">)([^<]+)(<\/script>)/g;
 const all=[...html.matchAll(re)];if(all.length!==1)throw Error('Expected one v48 c55 game-main gzip');
 const match=all[0],old=gunzipSync(Buffer.from(match[2],'base64')).toString('utf8');
 const changed=patchJs(old);if(changed.source===old)return {source:html,steps:changed.steps};
 const raw=Buffer.from(changed.source,'utf8'),gz=gzipSync(raw,{level:9,mtime:0});
 let result=html.slice(0,match.index)+match[1]+gz.toString('base64')+match[3]+html.slice(match.index+match[0].length);
 const meta=/{"id":"c55-game-main","type":"text\/javascript","rawBytes":\d+,"gzipBytes":\d+,"sha256":"[a-f0-9]+"}/g;
 const x=[...result.matchAll(meta)];if(x.length!==1)throw Error('Expected exactly one main metadata record');
 const v=JSON.stringify({id:'c55-game-main',type:'text/javascript',rawBytes:raw.length,gzipBytes:gz.length,sha256:createHash('sha256').update(raw).digest('hex')});
 result=result.slice(0,x[0].index)+v+result.slice(x[0].index+x[0][0].length);
 return {source:result,steps:changed.steps};
}
function main(){
 let input=null,output=null,dry=false;let argv=process.argv.slice(2);
 for(let i=0;i<argv.length;i++){
  if(argv[i]==='--input')input=argv[++i];else if(argv[i]==='--output')output=argv[++i];else if(argv[i]==='--dry-run')dry=true;else throw Error('Unknown argument '+argv[i]);
 }
 if(!input||(!output&&!dry))throw Error('Usage: node AEGIS_B4_ALL4_Termination_apply.mjs --input INPUT.html|.js --output OUTPUT [--dry-run]');
 if(output&&resolve(output)===resolve(input))throw Error('Input overwriting forbidden');
 if(output&&existsSync(output))throw Error('Output exists, refusing overwrite');
 const source=readFileSync(input,'utf8');const result=/\.html?$/i.test(extname(input))?patchHtml(source):patchJs(source);
 if(!dry)writeFileSync(output,result.source);
 process.stdout.write(JSON.stringify({input,output:dry?null:output,dryRun:dry,steps:result.steps,changed:source!==result.source},null,2)+'\n');
}
try{main()}catch(e){console.error(e.stack||e);process.exit(1)}

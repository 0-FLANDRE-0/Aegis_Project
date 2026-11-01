// Parse large immutable data literals as same-length padding, then recover every
// symbol from ORIGINAL source offsets. Nothing here is executed by the game.
const fs=require('fs'),{unpack,mainScope}=require('../../../missile/fuze-zem/A/source.cjs');
function load(file){
 const raw=fs.readFileSync(file),source=unpack(raw),literals=[];
 const chunks=[];let offset=0;
 for(const line of source.split('\n')){
  const match=line.length>100000?line.match(/^([ \t]*const\s+([\w$]+)\s*=)/):null;
  if(match){const prefix=match[1],name=match[2],stub=prefix+'0;',end=line.lastIndexOf(';'),cr=line.endsWith('\r')?'\r':'';if(end<0)throw Error('UNTERMINATED_DATA:'+name);literals.push({name,start:offset+line.indexOf(name),end:offset+end});chunks.push(stub+' '.repeat(line.length-stub.length-cr.length)+cr);}
  else chunks.push(line);
  offset+=line.length+1;
 }
 const masked=chunks.join('\n');
 if(masked.length!==source.length)throw Error('SOURCE_OFFSETS_CHANGED');
 const q=mainScope(masked);for(const value of q.symbols.values())value.code=source.slice(value.start,value.end);
 for(const literal of literals){const symbol=q.symbols.get(literal.name);if(symbol?.start===literal.start){symbol.end=literal.end;symbol.code=source.slice(literal.start,literal.end);}}
 return {file,raw,source,...q,maskedDataLiterals:literals.map(r=>r.name)};
}
module.exports={load};

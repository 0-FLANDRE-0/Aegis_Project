"""Pinned TRACK-B packer and reversible patch manifest support.

This scaffold does not implement association behavior. A nonempty, reviewed
patch manifest is required before a TRACK-B product can be generated.

Manifest: {schema, patches:[...], allowedChangedSymbols:[...],
           allowedAddedSymbols:[...], allowedProtectedAssociationChanges:[...]}
Patch operations:
  replace: label, before, after, count(default1), optional scope
  module:  label, path(relative to this folder), anchor, placement(before/after)
Scope: {function, occurrence(default0)} or {start, end, occurrence(default0)}.
"""
from pathlib import Path
import argparse,base64,difflib,gzip,hashlib,json,re

P=Path(__file__).resolve().parent;R=P.parents[3]
BASE=R/'Aegis_SIM_v48_WIP_TRACK_A.html'
OUT=R/'Aegis_SIM_v48_WIP_TRACK_B.html'
BASE_COMMIT='ee960dbb7c796e3c91cbe4b6d3d5f59948a0e561'
PIN='e2c1976a8a21eae6a494bf6caf0ec5b702663bd97721763ef7e92c6d6096d67a'
MAIN_PIN='8d2de4f64cb18e3248156e36fa454daee91b5603e03fee5a8f7bd372e0d5780e'
sha=lambda b:hashlib.sha256(b).hexdigest()

def unpack(raw):
 m=re.search(rb'data-c55-index="13">([^<]+)',raw)
 if not m:raise ValueError('Missing existing packed main script index13')
 return gzip.decompress(base64.b64decode(m[1])).decode()

def pack(raw,source):
 m=re.search(rb'data-c55-index="13">([^<]+)',raw)
 encoded_source=source.encode();compressed=gzip.compress(encoded_source,9,mtime=0);encoded=base64.b64encode(compressed)
 out=raw[:m.start(1)]+encoded+raw[m.end(1):]
 meta=re.search(rb'const records=(\[.*?\]);',out,re.S)
 if not meta:raise ValueError('Missing existing packed-script metadata')
 records=json.loads(meta[1]);records[13].update(rawBytes=len(encoded_source),gzipBytes=len(compressed),sha256=sha(encoded_source))
 if'encodedBytes'in records[13]:records[13]['encodedBytes']=len(encoded)
 return out[:meta.start(1)]+json.dumps(records,separators=(',',':')).encode()+out[meta.end(1):]

def scope_span(source,scope):
 if not scope:return 0,len(source)
 occurrence=scope.get('occurrence',0)
 if not isinstance(occurrence,int)or occurrence<0:raise ValueError('scope occurrence must be a nonnegative integer')
 if'function'in scope:
  matches=list(re.finditer(r'^( *)function '+re.escape(scope['function'])+r'\(',source,re.M))
  if len(matches)<=occurrence:raise ValueError('Missing scoped function '+scope['function'])
  m=matches[occurrence];n=re.search(r'^'+re.escape(m[1])+r'function [A-Za-z_$]',source[m.end():],re.M)
  if not n:raise ValueError('Function scope needs a following same-indent declaration; use explicit scope anchors')
  return m.start(),m.end()+n.start()
 start,end=scope.get('start'),scope.get('end')
 if not isinstance(start,str)or not start or not isinstance(end,str)or not end:raise ValueError('Explicit scope needs nonempty start/end anchors')
 starts=[m.start()for m in re.finditer(re.escape(start),source)]
 if len(starts)<=occurrence:raise ValueError('Missing explicit scope start')
 a=starts[occurrence];b=source.find(end,a+len(start))
 if b<0:raise ValueError('Missing explicit scope end')
 return a,b

def read_manifest(path):
 data=json.loads(path.read_text())
 if isinstance(data,list):data={'schema':'AEGIS_TRACK_B_PATCH_MANIFEST_1','patches':data}
 if not isinstance(data,dict)or not isinstance(data.get('patches'),list):raise ValueError('Patch manifest requires a patches list')
 if data.get('schema')!='AEGIS_TRACK_B_PATCH_MANIFEST_1':raise ValueError('Unknown patch-manifest schema')
 if not data['patches']:raise ValueError('No association implementation patches: refusing to generate a no-op TRACK-B HTML')
 for key in ['allowedChangedSymbols','allowedAddedSymbols','allowedProtectedAssociationChanges']:
  if key not in data:data[key]=[]
  if not isinstance(data[key],list)or any(not isinstance(x,str)for x in data[key]):raise ValueError(key+' must be a string list')
 return data

def aggregate_manifest():
 """Materialize reviewed component files; this does not generate a game HTML."""
 module=P/'association.js';text=module.read_text()
 patches=[{'op':'module','label':'TRACK_B_ASSOCIATION_CORE','path':'association.js','sha256':sha(text.encode()),'anchor':'// TRACK_A_DIAGNOSTICS_END','placement':'after'}]
 added=set(re.findall(r'^function ([A-Za-z_$][\w$]*)\(',text,re.M));added.update(re.findall(r'^(?:const|let|var) ([A-Za-z_$][\w$]*)\s*=',text,re.M))
 changed=set();exceptions=set();components=[]
 for filename in ['patch-own.json','patches-offboard.json','patches-npc.json','patches-spq.json','patches-c55.json']:
  path=P/filename;raw=path.read_bytes();component=json.loads(raw)
  if isinstance(component,list):
   entries=component
   # This component explicitly scopes every change to the two SPQ functions;
   # its list form carries those function names as its change allowlist.
   changed.update(p['scope']['function']for p in entries if p.get('scope',{}).get('function'))
  else:
   if component.get('schema')!='AEGIS_TRACK_B_PATCH_MANIFEST_1':raise ValueError('Unknown component manifest: '+path.name)
   if component.get('baselineMainSha256',MAIN_PIN)!=MAIN_PIN:raise ValueError('Component baseline differs: '+path.name)
   entries=component['patches'];changed.update(component.get('allowedChangedSymbols',[]));added.update(component.get('allowedAddedSymbols',[]));exceptions.update(component.get('allowedProtectedAssociationChanges',[]))
  patches.extend(entries);components.append({'path':path.name,'sha256':sha(raw),'patches':len(entries)})
 # Pin every module, not just the shared core. A concurrent helper/comment
 # edit must fail before producing a mixed ACTIVE/SHADOW pair.
 for patch in patches:
  if patch.get('op')=='module':patch['sha256']=sha((P/patch['path']).read_bytes())
 manifest={'schema':'AEGIS_TRACK_B_PATCH_MANIFEST_1','baselineMainSha256':MAIN_PIN,'componentManifests':components,'patches':patches,'allowedChangedSymbols':sorted(changed),'allowedAddedSymbols':sorted(added),'allowedProtectedAssociationChanges':sorted(exceptions),'status':'TEST_CANDIDATE_REQUIRES_ROOT_REVIEW_AND_RUNTIME_VALIDATION','releaseApproved':False}
 (P/'patches.json').write_text(json.dumps(manifest,indent=2)+'\n');return manifest

def transform(source,manifest,mode='ACTIVE'):
 if mode not in ['ACTIVE','SHADOW']:raise ValueError('Unknown implementation mode')
 before=source;changes=[];modules=[]
 if not manifest.get('patches'):raise ValueError('A reviewed, nonempty patch list is required')
 for index,patch in enumerate(manifest['patches']):
  if not isinstance(patch,dict):raise ValueError('Patch must be an object')
  op=patch.get('op','replace');label=patch.get('label',f'patch-{index+1}');count=patch.get('count',1)
  if not isinstance(count,int)or count<1:raise ValueError('Patch count must be positive')
  if op=='module':
   relative=patch.get('path');module=(P/relative).resolve()if isinstance(relative,str)else None
   if module is None or not module.is_relative_to(P.resolve()):raise ValueError('Module path must stay inside this stage directory')
   original_text=module.read_text();text=original_text;old=patch.get('anchor');placement=patch.get('placement','after')
   if patch.get('sha256')and sha(original_text.encode())!=patch['sha256']:raise ValueError('Module differs from reviewed manifest: '+relative)
   if module.name=='association.js':
    token="const TRACK_B_IMPLEMENTATION_MODE='ACTIVE';"
    if text.count(token)!=1:raise ValueError('Association module must contain one explicit ACTIVE implementation token')
    text=text.replace(token,"const TRACK_B_IMPLEMENTATION_MODE='"+mode+"';",1)
   if placement not in ['before','after']:raise ValueError('Module placement must be before or after')
   new=text+'\n'+old if placement=='before'else old+'\n'+text
   modules.append({'path':relative,'sourceSha256':sha(original_text.encode()),'renderedSha256':sha(text.encode()),'sha256':sha(text.encode()),'bytes':len(text.encode()),'implementationMode':mode if module.name=='association.js'else None})
  elif op=='replace':old,new=patch.get('before'),patch.get('after')
  else:raise ValueError('Unknown patch operation '+str(op))
  if not isinstance(old,str)or not old or not isinstance(new,str)or new==old:raise ValueError('Every patch must have nonempty distinct before/after text')
  a,b=scope_span(source,patch.get('scope'));section=source[a:b]
  if section.count(old)!=count:raise AssertionError((label,'replacement count',section.count(old),count))
  next_section=section.replace(old,new);source=source[:a]+next_section+source[b:]
  change={'label':label,'op':op,'scope':patch.get('scope'),'before':old,'after':new,'count':count,'sourceLineBefore':before.count('\n',0,before.find(old))+1 if old in before else None}
  # A global unique snippet/module insertion must not duplicate the whole
  # 40MB packed main script in BUILD.json for every small patch.
  if patch.get('scope'):change.update(scopeBefore=section,scopeAfter=next_section)
  changes.append(change)
 restored=source
 for change in reversed(changes):
  # Reverse the exact scoped span, so identical snippets in two NPC/player
  # contexts cannot silently restore the wrong copy.
  if change['scope']:
   a,b=scope_span(restored,change['scope'])
   if restored[a:b]!=change['scopeAfter']:raise AssertionError((change['label'],'inverse scope content changed'))
   restored=restored[:a]+change['scopeBefore']+restored[b:]
  else:
   if restored.count(change['after'])!=change['count']:raise AssertionError((change['label'],'ambiguous inverse snippet',restored.count(change['after'])))
   restored=restored.replace(change['after'],change['before'])
 if restored!=before:raise AssertionError('Unlisted main-script bytes changed')
 return source,changes,modules

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--manifest',type=Path,default=P/'patches.json');parser.add_argument('--mode',choices=['ACTIVE','SHADOW'],default='ACTIVE');parser.add_argument('--check-base',action='store_true');parser.add_argument('--aggregate',action='store_true');args=parser.parse_args()
 raw=BASE.read_bytes();assert sha(raw)==PIN,'TRACK-A artifact differs from pinned input';before=unpack(raw);assert sha(before.encode())==MAIN_PIN,'TRACK-A main script differs from pinned input'
 if args.check_base:
  print(json.dumps({'baseBranch':'track-a-contract-trace','baseCommit':BASE_COMMIT,'baselineHtmlSha256':PIN,'baselineMainSha256':MAIN_PIN,'verified':True,'candidateGenerated':False}));return
 if args.aggregate:
  manifest=aggregate_manifest();print(json.dumps({'manifest':str((P/'patches.json').relative_to(R)),'patches':len(manifest['patches']),'components':len(manifest['componentManifests']),'candidateGenerated':False,'releaseApproved':False}));return
 manifest=read_manifest(args.manifest)
 for component in manifest.get('componentManifests',[]):
  path=(P/component['path']).resolve()
  if not path.is_relative_to(P.resolve())or sha(path.read_bytes())!=component['sha256']:raise ValueError('Component manifest differs from reviewed aggregate: '+component['path'])
 source,changes,modules=transform(before,manifest,args.mode)
 if source.count("const TRACK_B_IMPLEMENTATION_MODE='"+args.mode+"';")!=1:raise ValueError('Implemented association mode is missing or ambiguous')
 output=OUT if args.mode=='ACTIVE'else R/'Aegis_SIM_v48_WIP_TRACK_B_SHADOW.html';build_name='BUILD.json'if args.mode=='ACTIVE'else'BUILD_SHADOW.json';diff_name='changes.diff'if args.mode=='ACTIVE'else'changes-shadow.diff'
 out=pack(raw,source);assert unpack(out)==source;output.write_bytes(out)
 report={'schema':'AEGIS_TRACK_B_BUILD_1','baseBranch':'track-a-contract-trace','baseCommit':BASE_COMMIT,'baselineSha256':PIN,'baselineMainSha256':MAIN_PIN,'manifest':str(args.manifest.resolve().relative_to(R)),'manifestSha256':sha(args.manifest.read_bytes()),'output':output.name,'implementationMode':args.mode,'testCandidate':True,'releaseApproved':False,'htmlSha256':sha(out),'mainSha256':sha(source.encode()),'inverseByteExact':True,'modules':modules,'allowedChangedSymbols':manifest['allowedChangedSymbols'],'allowedAddedSymbols':manifest['allowedAddedSymbols'],'allowedProtectedAssociationChanges':manifest['allowedProtectedAssociationChanges'],'changes':changes}
 (P/build_name).write_text(json.dumps(report,indent=2)+'\n');(P/diff_name).write_text(''.join(difflib.unified_diff(before.splitlines(True),source.splitlines(True),fromfile=BASE.name+'::main',tofile=output.name+'::main')));print(json.dumps({'output':output.name,'mode':args.mode,'sha256':sha(out),'patches':len(changes),'inverseByteExact':True,'testCandidate':True,'releaseApproved':False}))

if __name__=='__main__':main()

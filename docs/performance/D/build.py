"""Pinned PERF_C to PERF_D: equivalent sectional hulls and earlier mesh publication."""
import argparse,base64,gzip,hashlib,json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent
BASE_SHA='5f8fb9ed69a960c4eef4c15ab22271c82c9b59a095a9ec8a959689ecba9acffd'
OLD='v48_WIP_PERF_C';NEW='v48_WIP_PERF_D';PATCHES=[]
def once(s,a,b,label):
 assert s.count(a)==1,(label,s.count(a));PATCHES.append(label);return s.replace(a,b,1)
def decoded(html,index=13):return gzip.decompress(base64.b64decode(re.search(r'data-c55-index="'+str(index)+r'">(.*?)</script>',html,re.S)[1])).decode()
def envelope(s):
 return once(s,"const p=[...new Map(points.map(a=>[a.map(v=>Math.round(v*1e5)).join(','),a])).values()].sort((a,b)=>a[0]-b[0]||a[1]-b[1]);", "// PERF_D: preserve rounded-key last-value/first-insertion order without per-point temporary arrays.\n const unique=new Map();for(const a of points)unique.set(Math.round(a[0]*1e5)+','+Math.round(a[1]*1e5),a);\n const p=[...unique.values()].sort((a,b)=>a[0]-b[0]||a[1]-b[1]);",'section hull equivalent deduplication')
def build(s):
 s=envelope(s)
 s=once(s,"const u=contour[i],v=contour[(i+1)%contour.length],e=v.clone().sub(u),den=d.x*e.y-d.y*e.x;if(Math.abs(den)<1e-9)continue;const r=(u.x*e.y-u.y*e.x)/den,t=(u.x*d.y-u.y*d.x)/den;", "const u=contour[i],v=contour[(i+1)%contour.length],ex=v.x-u.x,ey=v.y-u.y,den=d.x*ey-d.y*ex;if(Math.abs(den)<1e-9)continue;const r=(u.x*ey-u.y*ex)/den,t=(u.x*d.y-u.y*d.x)/den;",'fold contour scalar edges; identical arithmetic')
 s=once(s,"const start=performance.now(),c12Limit=Number.isFinite(this._c12DamageShareMs)?Math.max(.25,this._c12DamageShareMs):(this._damageQuickV11?5:3);", "// PERF_D: ownship opening borrows only the unused part of the existing 6ms frame allowance.\n      // Other owners keep their shares; optional detail keeps its existing slice.\n      const start=performance.now(),baseLimit=Number.isFinite(this._c12DamageShareMs)?Math.max(.25,this._c12DamageShareMs):(this._damageQuickV11?5:3),work=this._c12BudgetOwner?.c12FrameWork,c12Limit=this._damageQuickV11&&this._c12BudgetOwner===this&&Number.isFinite(this._c12DamageShareMs)&&work?Math.max(baseLimit,Math.min(work.allowanceMs,work.allowanceMs-work.usedMs)):baseLimit;",'opening borrows unused frame allowance; detail and total unchanged')
 s=once(s,"let committed=false,unmatched=0;", "let committed=false,published=false,unmatched=0;",'separate geometry publication from decoration completion')
 a='''        this.restoreDamageSurfacesV2();for(const v of this.damageScarVisuals?.values()??[])this.disposeDamageScarV1(v);
        for(const [mesh,geo] of geometries)mesh.geometry=geo;for(const rows of edges.values())for(const e of rows)e.line.geometry=e.geometry;
        for(const [line,geo] of lineGeosV10){line.geometry=geo;this.damageDetachedLinesV10.set(line,lineOriginalsV10.get(line));}
        for(const v of visuals.values())v.binding.mesh.add(v.group);
        const used=new Set([...bindings.values()].map(b=>b.mesh));for(const mesh of geometries.keys())used.add(mesh);for(const mesh of originals.keys())if(!used.has(mesh))originals.delete(mesh);
        this.damageDetachedBoxesV10=[...geometries.values()].flatMap(g=>g.userData.detachedBoundsV10??[]);this.damageOriginalMeshesV2=originals;this.damageSurfaceBindingsV2=bindings;this.damageScarVisuals=visuals;this.damageUnmatchedCountV2=unmatched;committed=true;'''
 publish='''      // PERF_D: a complete opening/fold snapshot can be displayed before its
      // scorch and outline decoration. Never expose an individual half-cut mesh.
      // Ownership transfers once; cancelled decoration must not dispose live surfaces.
      const publish=()=>{
        this.restoreDamageSurfacesV2();for(const v of this.damageScarVisuals?.values()??[])this.disposeDamageScarV1(v);
        for(const [mesh,geo] of geometries)mesh.geometry=geo;
        for(const v of visuals.values())v.binding.mesh.add(v.group);
        const used=new Set([...bindings.values()].map(b=>b.mesh));for(const mesh of geometries.keys())used.add(mesh);for(const mesh of originals.keys())if(!used.has(mesh))originals.delete(mesh);
        this.damageDetachedBoxesV10=[...geometries.values()].flatMap(g=>g.userData.detachedBoundsV10??[]);this.damageOriginalMeshesV2=originals;this.damageSurfaceBindingsV2=bindings;this.damageScarVisuals=visuals;this.damageUnmatchedCountV2=unmatched;published=true;
        if(quick)this._damageOpeningRevisionPerfD=(this._damageOpeningRevisionPerfD||0)+1;
      };
'''
 marker='''      const remember=mesh=>{''';assert s.count(marker)==1
 start=s.index(marker);end=s.index('      try{',start);s=s[:end]+publish+s[end:]
 s=once(s,"        for(const v of visuals.values()){const b=v.binding,s=v.scar;", "        if(quick){publish();yield;}\n        for(const v of visuals.values()){const b=v.binding,s=v.scar;",'atomic visible quick snapshot before scorch and edges')
 s=once(s,a,"        if(!published)publish();\n        for(const rows of edges.values())for(const e of rows)e.line.geometry=e.geometry;\n        for(const [line,geo] of lineGeosV10){line.geometry=geo;this.damageDetachedLinesV10.set(line,lineOriginalsV10.get(line));}\n        committed=true;",'final decorations retain native shape and completion revision')
 s=once(s,"for(const v of visuals.values())this.disposeDamageScarV1(v);for(const geo of geometries.values())geo.dispose();for(const rows of edges.values())", "if(!published){for(const v of visuals.values())this.disposeDamageScarV1(v);for(const geo of geometries.values())geo.dispose();}for(const rows of edges.values())",'cancel unpublished work only; retain attached opening ownership')
 return s
def main():
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('output',type=Path);a=p.parse_args();raw=a.baseline.read_bytes();assert hashlib.sha256(raw).hexdigest()==BASE_SHA
 html=raw.decode();changes={2:envelope(decoded(html,2)),13:build(decoded(html)).replace(OLD,NEW)};records=json.loads(re.search(r'const records=(\[.*?\]);',html,re.S)[1])
 for i,candidate in changes.items():
  gz=gzip.compress(candidate.encode(),mtime=0);m=re.search(r'data-c55-index="'+str(i)+r'">(.*?)</script>',html,re.S);html=html[:m.start(1)]+base64.b64encode(gz).decode()+html[m.end(1):]
  records[i].update(rawBytes=len(candidate.encode()),gzipBytes=len(gz),sha256=hashlib.sha256(candidate.encode()).hexdigest())
 row=re.search(r'const records=(\[.*?\]);',html,re.S);html=html[:row.start(1)]+json.dumps(records,separators=(',',':'))+html[row.end(1):];html=html.replace(OLD,NEW).replace('V48_WIP_PERF_C','V48_WIP_PERF_D');a.output.write_text(html);a.output.with_suffix('.main.js').write_text(changes[13])
 manifest={'baselineSha256':BASE_SHA,'htmlSha256':hashlib.sha256(html.encode()).hexdigest(),'mainSha256':hashlib.sha256(changes[13].encode()).hexdigest(),'changedPackedRecords':[2,13],'patches':PATCHES};a.output.with_suffix('.manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({'bytes':len(html.encode()),'sha256':manifest['htmlSha256'],'patches':PATCHES}))
if __name__=='__main__':main()

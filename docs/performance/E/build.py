"""Pinned PERF_D to PERF_E; renderer-only scheduling and exact buffer updates."""
import argparse,base64,gzip,hashlib,json,re
from pathlib import Path
BASE_SHA='bd3bc97089cd0085c1990b5460fd4b8d6f5c9bcf794e1f520a42bc9c2aa95c2e'
OLD='v48_WIP_PERF_D';NEW='v48_WIP_PERF_E';PATCHES=[]
def once(s,a,b,label):
 assert s.count(a)==1,(label,s.count(a));PATCHES.append(label);return s.replace(a,b,1)
def decoded(html,index=13):return gzip.decompress(base64.b64decode(re.search(r'data-c55-index="'+str(index)+r'">(.*?)</script>',html,re.S)[1])).decode()
def build(s):
 s=once(s,'for(let i=0;i<poly.length;i++){const a=poly[i],b=poly[(i+1)%poly.length],da=plane.n.dot(a.p)-plane.d,db=plane.n.dot(b.p)-plane.d,ia=da<=1e-7,ib=db<=1e-7;', '''// PERF_E: each immutable polygon vertex has the same signed distance in both adjacent edges.
    const first=plane.n.dot(poly[0].p)-plane.d;let da=first;
    for(let i=0;i<poly.length;i++){const a=poly[i],b=poly[(i+1)%poly.length],db=i+1===poly.length?first:plane.n.dot(b.p)-plane.d,ia=da<=1e-7,ib=db<=1e-7;''','same polygon arithmetic; reuse adjacent signed distance')
 s=once(s,'inside.push(q);outside.push(q);}}\n    return {inside,outside};','inside.push(q);outside.push(q);}da=db;}\n    return {inside,outside};','advance distance without changing output order')
 s=once(s,"      const xs=poly.map(v=>v.p.x),ys=poly.map(v=>v.p.y),zs=poly.map(v=>v.p.z);\n      if(Math.min(...xs)>bound||Math.max(...xs)<-bound||Math.min(...ys)>bound||Math.max(...ys)<-bound||Math.min(...zs)>b.slab||Math.max(...zs)<-b.slab){rows.push(row);continue;}","      const a=poly[0].p,c=poly[1].p,d=poly[2].p;\n      if(Math.min(a.x,c.x,d.x)>bound||Math.max(a.x,c.x,d.x)<-bound||Math.min(a.y,c.y,d.y)>bound||Math.max(a.y,c.y,d.y)<-bound||Math.min(a.z,c.z,d.z)>b.slab||Math.max(a.z,c.z,d.z)<-b.slab){rows.push(row);continue;}",'triangle bound without three temporary arrays')
 s=once(s,'      const publish=()=>{\n        this.restoreDamageSurfacesV2();for(const v of this.damageScarVisuals?.values()??[])this.disposeDamageScarV1(v);', '''      const publish=(complete=true)=>{
        // PERF_E: keep already attached completed anchor geometry alive when the
        // surrounding meshes finish. A cancelled job may free only unpublished buffers.
        this.restoreDetachedLinesV10();
        for(const [mesh,v] of this.damageOriginalMeshesV2??[]){
          if(!complete&&!geometries.has(mesh))continue;
          const next=geometries.get(mesh)??v.geometry;
          if(mesh.geometry!==v.geometry&&mesh.geometry!==next)mesh.geometry.dispose();
          mesh.geometry=next;
          for(const e of v.edges)if(e.line.geometry!==e.geometry){e.line.geometry.dispose();e.line.geometry=e.geometry;}
        }
        for(const [id,v] of this.damageScarVisuals??[])if(visuals.get(id)!==v)this.disposeDamageScarV1(v);''','multiple complete-mesh publications preserve live ownership')
 s=once(s,'for(const mesh of originals.keys())if(!used.has(mesh))originals.delete(mesh);\n        this.damageDetachedBoxesV10=', 'if(complete)for(const mesh of originals.keys())if(!used.has(mesh))originals.delete(mesh);\n        this.damageDetachedBoxesV10=','retain original records for not-yet-published adjacent meshes')
 s=once(s,'        for(const [mesh,holes] of cuts){const key=JSON.stringify(holes.map(b=>b.damageKeyV14));', '''        // PERF_E: finish every scar's anchor mesh before the larger adjacent meshes.
        // Every mesh still consumes its original ordered holes and final cutter.
        const anchors=new Set([...visuals.values()].filter(v=>v.group.userData.actualHole).map(v=>v.binding.mesh));
        const staged=quick&&anchors.size>0&&(this._bunkerAsset||this._c5Asset)&&[...cuts.keys()].some(m=>!anchors.has(m));
        const batches=staged?[[...cuts].filter(([m])=>anchors.has(m)),[...cuts].filter(([m])=>!anchors.has(m))]:[[...cuts]];
        for(let phase=0;phase<batches.length;phase++){
        for(const [mesh,holes] of batches[phase]){const key=JSON.stringify(holes.map(b=>b.damageKeyV14));''','prioritize complete anchor meshes while retaining hole order')
 s=once(s,'        if(reuse)for(const [mesh,record] of originals){', '''        if(staged&&phase===0){publish(false);yield;}
        }
        if(reuse)for(const [mesh,record] of originals){''','publish both completed anchors before adjacent cutting')
 s=once(s,'for(const geo of geometries.values())geo.dispose();}for(const rows of edges.values())', 'for(const geo of geometries.values())geo.dispose();}else{for(const [mesh,geo] of geometries)if(mesh.geometry!==geo)geo.dispose();}for(const rows of edges.values())','cancellation releases staged adjacent buffers and retains attached anchors')
 s=once(s,"revision=String(state.damageRevision)+':'+String(v.damagePresenter?._damageGeometryRevisionV11??0);", "revision=String(state.damageRevision)+':'+String(v.damagePresenter?._damageGeometryRevisionV11??0)+':'+String(v.damagePresenter?._damageOpeningRevisionPerfD??0);",'target proxy follows every opening publication')
 s=once(s,'revision=this._damageGeometryRevisionV11??0;if(r.revision!==revision)', "revision=(this._damageGeometryRevisionV11??0)+':'+(this._damageOpeningRevisionPerfD??0);if(r.revision!==revision)",'ownship proxy follows every opening publication')
 s=once(s,'    if(!r.root?.parent)continue;view.c11LodCounts[r.level??0]++;', '''    if(!r.root?.parent)continue;
    const opening=(r.target?.damagePresenter??view)._damageOpeningRevisionPerfD??0;
    if(r._perfEOpening!==opening){c11DisposeProxy(r);r._perfEOpening=opening;}
    view.c11LodCounts[r.level??0]++;''','invalidate distant proxies before the same draw of a new opening')
 s=once(s,'  for(const b of store.batches.values())b.count=0;let culled=0,cells=0,ribbons=0;', '''  for(const b of store.batches.values()){
    b.count=0;
    // Bundled r140 invokes onUpload only on initial buffer creation. After a
    // partial upload WebGLAttributes resets the queued single range to -1.
    // Consume that native acknowledgement before accumulating new writes.
    for(const a of Object.values(b.mesh.geometry.attributes))if(a.isInstancedBufferAttribute&&a._perfEQueuedVersion===a.version&&a.updateRange?.count===-1){
      a._perfEStart=Infinity;a._perfEEnd=-1;a._perfEQueuedVersion=null;
    }
  }let culled=0,cells=0,ribbons=0;''','acknowledge consumed legacy ranges as well as native onUpload callbacks')
 marker='function c13CreateSmokeBatch(view,mode,capacity){'
 helper='''// PERF_E: compare the exact Float32 values sent to the GPU. Dirty ranges persist
// until Three uploads them, including multiple flushes and hidden/reappearing tails.
function c13SetSmokeAttributePerfE(a,j,x,y,z,w){
  const off=j*a.itemSize;
  for(let k=0;k<a.itemSize;k++){
    const value=Math.fround(k===0?x:(k===1?y:(k===2?z:w))),i=off+k;
    if(Object.is(a.array[i],value)&&!Number.isNaN(value))continue;
    a.array[i]=value;a._perfEStart=Math.min(a._perfEStart??Infinity,i);a._perfEEnd=Math.max(a._perfEEnd??-1,i);
  }
}
'''
 s=once(s,marker,helper+marker,'exact smoke attribute writer')
 s=once(s,'g.setAttribute(name,new T.InstancedBufferAttribute(new Float32Array(capacity*size),size).setUsage(T.DynamicDrawUsage));', '''{
    const attr=new T.InstancedBufferAttribute(new Float32Array(capacity*size),size).setUsage(T.DynamicDrawUsage);
    attr.onUpload(()=>{attr._perfEStart=Infinity;attr._perfEEnd=-1;});g.setAttribute(name,attr);
  }''','clear pending ranges only after actual native GPU upload')
 # Each old setter writes one tightly packed Float32 instance; preserve all source expressions.
 start=s.index('function c13FlushSmoke(view){');end=s.index('function c13DisposeSmokeGPU(view)',start);block=s[start:end]
 block,n=re.subn(r'a\.(i\w+)\.set(?:XYZW|XYZ|XY|X)\(j,',r'c13SetSmokeAttributePerfE(a.\1,j,',block);assert n==7,n;PATCHES.append('all seven native smoke attributes retain exact Float32 output')
 old="    for(const a of Object.values(g.attributes)){if(!a.isInstancedBufferAttribute)continue;const count=b.count*a.itemSize;if(a.clearUpdateRanges){a.clearUpdateRanges();a.addUpdateRange(0,count);}else{a.updateRange.offset=0;a.updateRange.count=count;}a.needsUpdate=true;}"
 new="""    for(const a of Object.values(g.attributes)){if(!a.isInstancedBufferAttribute)continue;
      const first=a._perfEStart??Infinity,last=a._perfEEnd??-1;if(last<first)continue;
      const count=last-first+1;if(a.clearUpdateRanges&&a.addUpdateRange){a.clearUpdateRanges();a.addUpdateRange(first,count);}else{a.updateRange.offset=first;a.updateRange.count=count;}a.needsUpdate=true;a._perfEQueuedVersion=a.version;
    }"""
 block=once(block,old,new,'upload changed ranges only; retain untouched tails');s=s[:start]+block+s[end:]
 return s

def main():
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('output',type=Path);a=p.parse_args();raw=a.baseline.read_bytes();assert hashlib.sha256(raw).hexdigest()==BASE_SHA
 html=raw.decode();candidate=build(decoded(html)).replace(OLD,NEW);i=13;gz=gzip.compress(candidate.encode(),mtime=0);m=re.search(r'data-c55-index="13">(.*?)</script>',html,re.S);html=html[:m.start(1)]+base64.b64encode(gz).decode()+html[m.end(1):]
 row=re.search(r'const records=(\[.*?\]);',html,re.S);records=json.loads(row[1]);records[i].update(rawBytes=len(candidate.encode()),gzipBytes=len(gz),sha256=hashlib.sha256(candidate.encode()).hexdigest());html=html[:row.start(1)]+json.dumps(records,separators=(',',':'))+html[row.end(1):];html=html.replace(OLD,NEW).replace('V48_WIP_PERF_D','V48_WIP_PERF_E');a.output.write_text(html);a.output.with_suffix('.main.js').write_text(candidate)
 a.output.with_suffix('.manifest.json').write_text(json.dumps({'baselineSha256':BASE_SHA,'htmlSha256':hashlib.sha256(html.encode()).hexdigest(),'mainSha256':hashlib.sha256(candidate.encode()).hexdigest(),'changedPackedAssets':[13],'patches':PATCHES},indent=2)+'\n');print(json.dumps({'bytes':len(html.encode()),'sha256':hashlib.sha256(html.encode()).hexdigest(),'patches':PATCHES}))
if __name__=='__main__':main()

"""CG_TURRET_A: exact, bounded render/origin rollback over merged B2B."""
from pathlib import Path
import base64,difflib,gzip,hashlib,json,re,subprocess
P=Path(__file__).resolve().parent;R=P.parents[3]
BASE=R/'Aegis_SIM_v48_WIP_GUN_B2.html';OUT=R/'Aegis_SIM_v48_WIP_CG_TURRET_A.html'
EXPECTED='d2ae791e38221ec660283989728ea50e0eeb9075c2501cdbef9086e6c61cbc26'
sha=lambda b:hashlib.sha256(b).hexdigest()
def unpack(raw):return gzip.decompress(base64.b64decode(re.search(rb'data-c55-index="13">([^<]+)',raw)[1])).decode()
def pack(raw,s):
 m=re.search(rb'data-c55-index="13">([^<]+)',raw);z=gzip.compress(s.encode(),9,mtime=0);encoded=base64.b64encode(z);out=raw[:m.start(1)]+encoded+raw[m.end(1):]
 m=re.search(rb'const records=(\[.*?\]);',out,re.S);records=json.loads(m[1]);records[13].update(rawBytes=len(s.encode()),gzipBytes=len(z),sha256=sha(s.encode()))
 if 'encodedBytes'in records[13]:records[13]['encodedBytes']=len(encoded)
 return out[:m.start(1)]+json.dumps(records,separators=(',',':')).encode()+out[m.end(1):]
def transform(s,origin=True):
 changes=[]
 def replace(a,b):
  nonlocal s
  assert s.count(a)==1,(a[:80],s.count(a));s=s.replace(a,b,1);changes.append({'before':a,'after':b})
 if origin:replace('moduleName:hp[hardpointId].name,trunnionOffsetM:{x:.91,y:0,z:2.87},exposedBarrelM:6.206,sourceNode:g.yawNode',
  'moduleName:hp[hardpointId].name,trunnionOffsetM:g.trunnionOffsetM,exposedBarrelM:g.barrelM,sourceNode:g.yawNode')
 start=s.index('    // GUN_B1: reuse the existing DDG Mod4 generator, hide authored round turrets.')
 end=s.index('    this.phalanxYawGroup=',start)
 replace(s[start:end],"    // CG_TURRET_A: authored 54-calibre round visual; installed Mod 4 performance stays in the module profile.\n    this.mk45TraverseGroup=parts.get('mk45f_yaw');this.mk45ElevationGroup=parts.get('mk45f_pitch');\n")
 replace('    for(const q of st.mountInventory?.guns??[]){const g=this._gunB1Visuals?.get(q.hardpointId);if(g){g.yaw.rotation.y=-q.bodyAzRad;g.pitch.rotation.z=q.elevationRad;}}',
  '    for(const q of st.mountInventory?.guns??[]){const g=BUNKER_REGISTRATION.guns[q.hardpointId];\n      rotate(g.yawNode,-(q.bodyAzRad-g.neutralAzRad));rotate(g.pitchNode,q.elevationRad-g.restElevationRad);}')
 return s,changes
if __name__=='__main__':
 raw=BASE.read_bytes();assert sha(raw)==EXPECTED,'BASELINE_MISMATCH_STOP'
 old=unpack(raw);s,changes=transform(old);OUT.write_bytes(pack(raw,s))
 restored=s
 for c in reversed(changes):assert restored.count(c['after'])==1;restored=restored.replace(c['after'],c['before'],1)
 assert restored==old
 (P/'changes.diff').write_text('\n'.join(l.rstrip() for l in difflib.unified_diff(old.splitlines(),s.splitlines(),fromfile='B2B::main',tofile='CG_TURRET_A::main',lineterm=''))+'\n')
 (P/'build.json').write_text(json.dumps({'baselineMainCommit':subprocess.check_output(['git','rev-parse','origin/main'],cwd=R,text=True).strip(),'baselineSha256':sha(raw),'htmlSha256':sha(OUT.read_bytes()),'mainSha256':sha(s.encode()),'inverseByteExact':True,'changes':changes},indent=2)+'\n')
 print(sha(OUT.read_bytes()))

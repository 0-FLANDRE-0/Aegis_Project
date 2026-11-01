"""Build GUN_B2B from the immutable B2A product with an exact inverse scope proof."""
from pathlib import Path
import argparse, base64, difflib, gzip, hashlib, json, re

P = Path(__file__).resolve().parent
R = P.parents[3]
BASE = Path('/tmp/aegis-gun-b2/b2b-baseline.html')
OUT = R / 'Aegis_SIM_v48_WIP_GUN_B2.html'
BASE_SHA = '9515e70cb88f7caac8dd9c0b618a104a878882a5a1c06f0967059150e2b7d516'
sha = lambda b: hashlib.sha256(b).hexdigest()
parser=argparse.ArgumentParser();parser.add_argument('--embed',action='store_true');args=parser.parse_args()

raw = BASE.read_bytes()
assert sha(raw) == BASE_SHA
params = json.loads((P / 'model-parameters.json').read_text())
assert params['fuzeMatching']['within20to80']

match = re.search(rb'data-c55-index="13">([^<]+)</script>', raw)
old = gzip.decompress(base64.b64decode(match[1])).decode()
s = old
changes = []

old_frag = "fragments:{id:'127_HE_MFP_FICTIONAL_GAME',provenance:'SIM_TUNED_GAME_ONLY',explosiveMassKg:3.7,caseMassKg:9,gurneyDrivenMassKg:9,fragmentCount:1200,avgFragmentMassKg:.0075,gurneyMps:2200,effectiveFragmentFraction:1,annularBandHalfAngleDeg:55,coneHalfAngleDeg:55}"
mott = params['mott']; inp = params['input']
edges = '[' + ','.join('Infinity' if x is None else repr(x) for x in mott['massBinEdgesKg']) + ']'
new_frag = (
    "fragments:{id:'127_HE_MOTT_GAME',provenance:'PUBLIC_REF_PLUS_SIM_TUNED_EQUIVALENT_CYLINDER',"
    f"explosiveMassKg:{inp['explosiveMassKg']!r},caseMassKg:{inp['caseMassKg']!r},"
    f"gurneyDrivenMassKg:{inp['caseMassKg']!r},fragmentCount:{mott['n0']!r},"
    f"avgFragmentMassKg:{(inp['caseMassKg']/mott['n0'])!r},gurneyMps:{inp['gurneyMps']!r},"
    "effectiveFragmentFraction:1,annularBandHalfAngleDeg:20,coneHalfAngleDeg:20,"
    "mott:{enabled:true,reference:'SAND94_2255_TABLES_5_6_PLUS_SIM_TUNED_EQUIVALENT_CYLINDER',"
    f"mottB:{inp['mottB']!r},muKg:{mott['muKg']!r},n0:{mott['n0']!r},"
    f"referenceFragmentMassKg:{inp['referenceFragmentMassKg']!r},massBinEdgesKg:{edges}}}}}"
)
assert s.count(old_frag) == 1
s = s.replace(old_frag, new_frag, 1)
changes.append({'symbol':'GUN_B1_SPEC.fragments','old':old_frag,'new':new_frag})

old_center = 'fuze:{polarCenterDeg:45.943755735305814'
new_center = 'fuze:{polarCenterDeg:' + repr(params['fuzeMatching']['fixedPolarCenterDeg'])
assert s.count(old_center) == 1
s = s.replace(old_center, new_center, 1)
changes.append({'symbol':'GUN_B2_SPEC.fuze.polarCenterDeg','old':old_center,'new':new_center})

helper = r'''function gunB15inMottFragmentationPk(missDistM,weaponType,targetLabel,kin={},field=null){
    const w=GUN_B1_SPEC.fragments,tp=INTERCEPT_FRAGMENT_TARGETS[targetLabel]??INTERCEPT_FRAGMENT_TARGETS['Kh-35U'];
    if(!w?.mott?.enabled||!tp)return {pk:0,reason:'NO_5IN_MOTT_PROFILE'};
    const r=Math.max(.75,Number(field?.radiusM??missDistM)||.75),vm=Math.max(0,Number(kin.missileSpeedMps)||0),rel=Math.max(0,Number(kin.relativeSpeedMps)||0),vf=_wip88GurneyFragmentSpeed(w),M=Math.max(1e-6,Number(w.gurneyDrivenMassKg??w.caseMassKg));
    const half=deg(Number(w.annularBandHalfAngleDeg??w.coneHalfAngleDeg)),bodySolidAngleSr=Number(field?.bodySolidAngleSr)||(4*Math.PI*Math.sin(half)),bandAreaM2=r*r*bodySolidAngleSr,mu=Math.max(1e-12,Number(w.mott.muKg)),N0=M/(2*mu),edges=w.mott.massBinEdgesKg;
    const fragmentImpactSpeedMps=Math.hypot(vf,rel),tailCount=x=>N0*Math.exp(-x),tailMass=x=>Number.isFinite(x)?N0*mu*(x*x+2*x+2)*Math.exp(-x):0,bins=[];
    let expectedLethalHits=0,penetratingExpectedCount=0,massCheckKg=0,countCheck=0;
    for(let i=0;i<edges.length-1;i++){
      const lo=Math.max(0,Number(edges[i])||0),hi=Number(edges[i+1]),a=Math.sqrt(lo/mu),b=Number.isFinite(hi)?Math.sqrt(hi/mu):Infinity,count=tailCount(a)-(Number.isFinite(b)?tailCount(b):0),massKg=tailMass(a)-tailMass(b),representativeMassKg=massKg/Math.max(1e-12,count),v50Mps=tp.fragPenV50Mps*Math.cbrt(w.mott.referenceFragmentMassKg/representativeMassKg),penetrationProbability=1/(1+Math.exp(-(fragmentImpactSpeedMps-v50Mps)/Math.max(1,tp.fragPenWidthMps))),surfaceDensityM2=count/bandAreaM2,lethal=surfaceDensityM2*tp.vitalAreaM2*penetrationProbability;
      countCheck+=count;massCheckKg+=massKg;penetratingExpectedCount+=count*penetrationProbability;expectedLethalHits+=lethal;bins.push({index:i+1,loKg:lo,hiKg:Number.isFinite(hi)?hi:null,count,massKg,representativeMassKg,v50Mps,penetrationProbability,surfaceDensityM2,expectedLethalHits:lethal});
    }
    const penetrationProbability=penetratingExpectedCount/Math.max(1e-12,N0),expectedCoverageIntersections=(N0/bandAreaM2)*tp.vitalAreaM2,pk=clamp(-Math.expm1(-Math.max(0,expectedLethalHits)),0,1),delta=Math.atan2(vm,Math.max(1e-6,vf)),bandHalfAngleDeg=rad2deg(half);
    return {pk,gunB2Field:field,weaponType,warheadId:w.id,targetLabel,missDistM:r,explosiveMassKg:w.explosiveMassKg,gurneyDrivenMassKg:M,fragmentSpeedMps:vf,fragmentCount:N0,coverageFragmentCount:N0,effectiveFragmentCount:N0,effectiveCoverageFragmentCount:N0,fragmentClusterMultiplicity:1,fragmentFieldEfficiency:1,fragmentCountSource:'MOTT_MASS_BINS',coneTiltDeg:rad2deg(delta),coneCenterDeg:rad2deg(Math.PI/2-delta),coneHalfAngleDeg:bandHalfAngleDeg,annularBandHalfAngleDeg:bandHalfAngleDeg,coneAspectFactor:1,bandAreaM2,fragmentSurfaceDensityM2:N0/bandAreaM2,terminalFragmentSurfaceDensityM2:N0/bandAreaM2,vitalAreaM2:tp.vitalAreaM2,relativeSpeedMps:rel,missileSpeedMps:vm,targetSpeedMps:Number(kin.targetSpeedMps)||0,encounterAngleDeg:rad2deg(clamp(Number(kin.encounterAngleRad)||0,0,Math.PI)),fragmentImpactSpeedMps,penetrationProbability,clusterKillProbability:penetrationProbability,expectedCoverageIntersections,expectedLethalHits,mottMuKg:mu,mottN0:N0,mottMassCheckKg:massCheckKg,mottCountCheck:countCheck,massBins:bins};
  }
'''

new_b2 = r'''function gunB2FragmentationPk(missDistM,weaponType,targetLabel,kin={}){
    const w=GUN_B1_SPEC.fragments;
    if(!w)return {pk:0,reason:'NO_FRAGMENT_PROFILE'};
    const field=gunB2FragmentField(kin,_wip88GurneyFragmentSpeed(w));
    if(!field.ok)return {pk:0,reason:field.reason,gunB2Field:field};
    return gunB15inMottFragmentationPk(missDistM,weaponType,targetLabel,kin,field);
  }'''
new_b1 = r'''function gunB1FragmentationPk(missDistM,weaponType,targetLabel,kin={}){
    return gunB15inMottFragmentationPk(missDistM,weaponType,targetLabel,kin,null);
  }'''

def function(name: str, source: str) -> str:
    found = re.search(r'^function ' + re.escape(name) + r'\([\s\S]*?\n  }', source, re.M)
    assert found, name
    return found[0]

old_b2 = function('gunB2FragmentationPk', s)
old_b1 = function('gunB1FragmentationPk', s)
s = s.replace(old_b2, helper + new_b2, 1)
s = s.replace(old_b1, new_b1, 1)
changes.extend([
    {'symbol':'gunB15inMottFragmentationPk','old':None,'newSha256':sha(helper.encode())},
    {'symbol':'gunB2FragmentationPk','oldSha256':sha(old_b2.encode()),'newSha256':sha(new_b2.encode())},
    {'symbol':'gunB1FragmentationPk','oldSha256':sha(old_b1.encode()),'newSha256':sha(new_b1.encode())},
])

old_table=re.search(r'const GUN_B2_RANGE_TABLE=deepFreezeShipProfileV48Wip09\([^\n]+\);',s)[0]
new_table=old_table
if args.embed:
    table=json.loads((P/'range-table.json').read_text())
    assert table['measurementModelFingerprints']['nativeSourceHashes']
    new_table='const GUN_B2_RANGE_TABLE=deepFreezeShipProfileV48Wip09('+json.dumps(table,separators=(',',':'))+');'
    s=s.replace(old_table,new_table,1)
    changes.append({'symbol':'GUN_B2_RANGE_TABLE','oldSha256':sha(old_table.encode()),'newSha256':sha(new_table.encode()),'presentationOnly':True})

# Exact inverse proof: remove every permitted B2B edit and recover B2A byte-for-byte.
reconstructed = s.replace(new_table,old_table,1) if args.embed else s
reconstructed = reconstructed.replace(helper + new_b2, old_b2, 1).replace(new_b1, old_b1, 1)
reconstructed = reconstructed.replace(new_center, old_center, 1).replace(new_frag, old_frag, 1)
assert reconstructed == old, 'UNAUTHORIZED_SOURCE_CHANGE'

packed = base64.b64encode(gzip.compress(s.encode(), mtime=0))
out = raw[:match.start(1)] + packed + raw[match.end(1):]
record_match = re.search(rb'const records=(\[.*?\]);', out, re.S)
records = json.loads(record_match[1])
records[13]['sha256'] = sha(s.encode())
records[13]['rawBytes'] = len(s.encode())
records[13]['encodedBytes'] = len(packed)
out = out[:record_match.start(1)] + json.dumps(records,separators=(',',':')).encode() + out[record_match.end(1):]
OUT.write_bytes(out)
Path('/tmp/aegis-gun-b2/b2b-current.js').write_text(s)

manifest = {
    'schema':'AEGIS_GUN_B2B_BUILD_1','baselineCommit':'fa0fdde96dfcc7c0655f8ba8bc3e7a903b4591f4',
    'baselineHtmlSha256':BASE_SHA,'htmlSha256':sha(out),'mainSha256':sha(s.encode()),
    'onlyApprovedChangesInverseExact':True,'embeddedMeasuredDisplayTable':args.embed,'changes':changes,
}
(P/'build.json').write_text(json.dumps(manifest,indent=2)+'\n')
diff_text=''.join(difflib.unified_diff(old.splitlines(True),s.splitlines(True),fromfile='GUN_B2A::main',tofile='GUN_B2B::main'))
(P/'GUN_B2B.diff').write_text('\n'.join(line.rstrip() for line in diff_text.splitlines())+'\n')
print(json.dumps(manifest,indent=2))

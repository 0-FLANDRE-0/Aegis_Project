"""Build two test-only ablations of frozen87da; never write shipping products."""
from pathlib import Path
import argparse,difflib,hashlib,importlib.util,json,sys
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;R=P.parents[3]
PIN='87da98bf8f6d8bd68ef87a3d2ac75ce9c355db9e95bd192ab060d01e5bdede18'
sha=lambda b:hashlib.sha256(b).hexdigest()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,default=Path('/dev/shm/track-b-stabilization-variants'))
    args=parser.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    spec=importlib.util.spec_from_file_location('frozen_b_packer',P.parent/'B/build.py')
    packer=importlib.util.module_from_spec(spec);spec.loader.exec_module(packer)
    source=R/'Aegis_SIM_v48_WIP_TRACK_B_STABLE_A.html';raw=source.read_bytes();assert sha(raw)==PIN
    before=packer.unpack(raw)
    start=before.index('function trackBSolveB(input,assigner){')
    end=before.index('function trackBTraceB(event){',start)
    fn=before[start:end]
    large_start=fn.index('    if(rr.length>TRACK_B_POLICY.maxComponentSize||cc.length>TRACK_B_POLICY.maxComponentSize){')
    large_end=fn.index('    for(const q of base.out){\n      const matrix=',large_start)
    original_large=fn[large_start:large_end]
    old_hold="""    if(rr.length>TRACK_B_POLICY.maxComponentSize||cc.length>TRACK_B_POLICY.maxComponentSize){
      c.ambiguous=true;c.reason='DIAGNOSTIC_ABLATION_OLD_COMPONENT_HOLD';
      for(const i of rr)heldPlots.add(i);for(const id of cc)heldTracks.add(id);
      components.push(c);continue;
    }
"""
    call='&&trackBEvidenceCertificateStableB(edges,rr,cc,base,assigner,delta,gate)'
    assert fn.count(call)==1
    variants=[('s-only',original_large,old_hold),('large-only',call,'&&false'+call)]
    records=[];evidence=P/'evidence/ablation';evidence.mkdir(parents=True,exist_ok=True)
    for label,old,new in variants:
        assert fn.count(old)==1
        changed=fn.replace(old,new,1);after=before[:start]+changed+before[end:]
        assert after[:start]==before[:start] and after[start+len(changed):]==before[end:]
        assert changed.replace(new,old,1)==fn
        result=packer.pack(raw,after);assert packer.unpack(result)==after
        target=args.out/('Aegis_TRACK_B_DIAGNOSTIC_'+label.upper().replace('-','_')+'.html');target.write_bytes(result)
        diff=''.join(difflib.unified_diff(fn.splitlines(True),changed.splitlines(True),fromfile='frozen87da::trackBSolveB',tofile='DIAGNOSTIC_'+label+'::trackBSolveB'))
        (evidence/(label+'.diff')).write_text(diff)
        records.append({'label':label,'path':str(target),'htmlSha256':sha(result),'mainSha256':sha(after.encode()),
                        'changedExistingFunction':'trackBSolveB','onlyFunctionChanged':True,'inverseMainByteExact':True,
                        'diff':str((evidence/(label+'.diff')).relative_to(P)),
                        'interpretation':'Secondary covariance HOLD release only; >12 retains old wholeHOLD' if label=='s-only' else 'Large-component certificates only; secondary covariance HOLD release disabled'})
    report={'schema':'AEGIS_TRACK_B_DIAGNOSTIC_ABLATIONS_1','parentHtmlSha256':PIN,
            'parentMainSha256':sha(before.encode()),'builderSha256':sha(Path(__file__).read_bytes()),
            'variants':records,'diagnosticOnly':True,'notShipping':True,'fullRegressionTested':False,
            'physicalSensorEkfIffRoeWeaponDamageAiAndSaveBytesChanged':False,
            'existingThresholdsOrCoefficientsChanged':False,'releaseApproved':False}
    (evidence/'VARIANTS.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))

if __name__=='__main__':main()

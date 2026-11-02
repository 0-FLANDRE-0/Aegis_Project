"""Seven conditional approvals only; offline exact comparison, never game code.

No approval exists until RESULTS.json meets the user's preregistered condition.
This reader is also usable on a fresh original paired/D1 report for the same
reviewed HTML. It cannot approve another build, seed or tolerance change.
"""
from pathlib import Path
import argparse,base64,gzip,hashlib,importlib.util,json,re

P=Path(__file__).resolve().parent
R=P.parents[3]
SHIPS=('DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA')
CHECKS=('samePhysicalState','sameExistingObserverState','raidInventoryDeltaBounded')
IDS={f'{s}:raid:{c}'for s in SHIPS for c in CHECKS}|{'D1:419012:signatureSha256'}
sha=lambda b:hashlib.sha256(b).hexdigest()
value_hash=lambda v:sha(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())
_spec=importlib.util.spec_from_file_location('original_air_origin_projection',R/'docs/radar/air-origin/A/approved_expectations.py')
_projection=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_projection)


def pair_value(row,check):
    if check=='raidInventoryDeltaBounded':
        return sum(c['type']!='EMPTY'for cells in row['state']['inventory']['vls'].values()for c in cells)
    return _projection.pair_value(row,check)


def load_approval(path,html):
    q=json.loads(Path(path).read_text())
    assert q['schema']=='AEGIS_TRACK_B_R4_USER_APPROVED_EXPECTATIONS_1'
    assert len(q['entries'])==7 and {e['id']for e in q['entries']}==IDS
    assert sha(html)==q['reviewedHtmlSha256'],'EXACT_REVIEWED_HTML_REQUIRED'
    main=gzip.decompress(base64.b64decode(re.search(rb'data-c55-index="13">([^<]+)',html)[1]))
    assert sha(main)==q['reviewedMainSha256'],'EXACT_REVIEWED_CORE_REQUIRED'
    result_path=P/'RESULTS.json';result=json.loads(result_path.read_text())
    assert result['decision']=='USER_CONDITIONAL_APPROVAL_CRITERION_MET'
    assert sha(result_path.read_bytes())==q['statisticalResultSha256']
    assert sha((R/'docs/radar/air-origin/A/approved_expectations.py').read_bytes())==q['originalProjectionSha256']
    assert q['otherExpectationsChanged']==q['tolerancesChanged']==0
    for e in q['entries']:
        assert e['oldExpected']!=e['newExpected'] and e['reason'] and e['causePath']
        assert value_hash(e['oldExpected'])==e['oldValueSha256']
        assert value_hash(e['newExpected'])==e['newValueSha256']
    return q


def evaluate(q,pair_report,d1_report):
    assert pair_report['candidateSha256']==d1_report['candidateSha256']==q['reviewedHtmlSha256']
    assert pair_report['baselineSha256']==q['oldReferenceHtmlSha256']
    assert not pair_report['errors'] and all(d1_report['checks'].values())
    entries={e['id']:e for e in q['entries']};changed=[];pair_rows=[]
    for row in pair_report['cases']:
        checks=dict(row['checks']);original=dict(checks)
        if row['scenario']=='raid':
            for c in CHECKS:
                key=f"{row['ship']}:raid:{c}";e=entries[key]
                assert pair_value(row['pair']['baseline'],c)==e['oldExpected'],'OLD_EXPECTATION_DRIFT'
                actual=pair_value(row['pair']['candidate'],c)
                checks[c]=actual==e['newExpected']
                changed.append({'id':key,'originalPass':original[c],'approvedExactPass':checks[c],
                                'actualSha256':value_hash(actual),'expectedSha256':e['newValueSha256']})
        assert all(checks[c]==v for c,v in original.items()if row['scenario']!='raid'or c not in CHECKS)
        pair_rows.append({'ship':row['ship'],'scenario':row['scenario'],'originalChecks':original,'approvedChecks':checks})
    assert len(pair_rows)==6 and sum(len(r['approvedChecks'])for r in pair_rows)==42
    d1=[]
    ref=d1_report['references']['track-a']
    assert ref['cases']==len(ref['rows'])==30
    for row in ref['rows']:
        ok=row['sameOriginalSignature']
        if row['seed']==419012:
            e=entries['D1:419012:signatureSha256']
            assert row['referenceSignature']==e['oldExpected']
            ok=row['candidateSignature']==e['newExpected']
            changed.append({'id':e['id'],'originalPass':row['sameOriginalSignature'],'approvedExactPass':ok,
                            'actualSha256':value_hash(row['candidateSignature']),'expectedSha256':e['newValueSha256']})
        d1.append({'seed':row['seed'],'originalPass':row['sameOriginalSignature'],'approvedExactPass':ok})
    assert len(changed)==7 and {r['id']for r in changed}==IDS
    return {'schema':'AEGIS_TRACK_B_R4_APPROVED_EXACT_COMPARISONS_1',
            'status':'PASS'if all(r['approvedExactPass']for r in changed)and all(all(r['approvedChecks'].values())for r in pair_rows)and all(r['approvedExactPass']for r in d1)else'FAIL',
            'pairedPassed':sum(sum(r['approvedChecks'].values())for r in pair_rows),'pairedCount':42,
            'd1Passed':sum(r['approvedExactPass']for r in d1),'d1Count':30,
            'expectationsChanged':7,'tolerancesChanged':0,'otherChecksChanged':0,
            'sourceResultsPreserved':True,'actualNewBrowserRuns':0,
            'meaning':'Exact re-evaluation of original native outputs under only the seven conditionally approved expectations. Not another game execution.',
            'changes':changed,'paired':pair_rows,'d1':d1,
            'notApproved':['CIWS419025','ORIGINAL_FRIENDLY_OBSERVER_TWO','LEGACY_EMCON_UI14']}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--approval',type=Path,default=P/'APPROVED_EXPECTATIONS.json')
    ap.add_argument('--html',type=Path,default=R/'Aegis_SIM_v48_WIP_TRACK_B_STABLE_D.html')
    ap.add_argument('--pair',type=Path,default=P.with_name('B_stabilization_r4')/'evidence/regression/paired-track-a/baseline-comparison.json')
    ap.add_argument('--d1',type=Path,default=P.with_name('B_stabilization_r4')/'evidence/regression/d1/COMPARISON.json')
    ap.add_argument('--out',type=Path,default=P/'APPROVED_COMPARISONS.json');a=ap.parse_args()
    q=load_approval(a.approval,a.html.read_bytes())
    result=evaluate(q,json.loads(a.pair.read_text()),json.loads(a.d1.read_text()))
    result['inputs']={str(p):sha(p.read_bytes())for p in [a.approval,a.html,a.pair,a.d1]}
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:result[k]for k in ['status','pairedPassed','d1Passed','expectationsChanged']}))
    return 0 if result['status']=='PASS'else 1


if __name__=='__main__':raise SystemExit(main())

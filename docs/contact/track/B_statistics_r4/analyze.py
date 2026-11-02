"""Preregistered paired seed-block analysis. Never changes game/expectations."""
from pathlib import Path
import collections,csv,hashlib,json
import numpy as np
from trial_data import load as load_trial
from run import verify as verify_frozen_sources

P=Path(__file__).resolve().parent
METRICS=['leakers','damagingHitRounds','kills','floodM3','hpReferenceOnly']


def exact_worse_p(d):
    d=np.asarray(d,dtype=np.float64)
    # Enumerate every sign assignment exactly, sharing the sign within seed.
    sums=np.zeros(1<<len(d),dtype=np.float64)
    numbers=np.arange(len(sums),dtype=np.uint32)
    for i,value in enumerate(d):sums+=np.where((numbers>>i)&1,value,-value)
    return float(np.count_nonzero(sums>=float(d.sum()))/len(sums))


def intervals(blocks,draws,seed,strata):
    rng=np.random.default_rng(seed);total=np.zeros((draws,blocks.shape[1]))
    for indices in strata:
        values=blocks[indices]
        chosen=rng.integers(0,len(values),size=(draws,len(values)))
        total+=values[chosen].sum(axis=1)
    return np.quantile(total,[.025,.975],axis=0).T.tolist()


def verdict(delta,p,ci):
    if len(ci)!=2 or not np.isfinite([delta,p,*ci]).all() or ci[0]>ci[1]:return 'INCONCLUSIVE'
    if (delta>0 and p<=.05)or ci[0]>0:return 'CLEARLY_WORSE'
    if ci[0]<=0<=ci[1] or ci[1]<=0:return 'WITHIN_USER_SAMPLING_VARIATION_OR_BETTER'
    return 'INCONCLUSIVE'


def main():
    plan=json.loads((P/'PLAN.json').read_text())
    freeze=json.loads((P/'evidence/CONTROLLER_SOURCE.json').read_text())
    assert hashlib.sha256((P/'PLAN.json').read_bytes()).hexdigest()==freeze['planSha256']
    assert hashlib.sha256((P/'run.py').read_bytes()).hexdigest()==freeze['sourceSha256']
    verify_frozen_sources(plan)
    analysis_pin=json.loads((P/'ANALYSIS_SOURCE.json').read_text())
    assert hashlib.sha256(Path(__file__).read_bytes()).hexdigest()==analysis_pin['analysisSha256']
    assert hashlib.sha256((P/'trial_data.py').read_bytes()).hexdigest()==analysis_pin['trialDataSha256']
    rows=[]
    for path in sorted((P/'evidence/runs').glob('*/attempt1/JOB.json')):
        q=load_trial(path.parent);rows.append(q)
        (path.parent/'METRICS_STATISTICAL.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
    assert len(rows)==120 and len({q['id']for q in rows})==120,'ALL120_FROZEN_TRIALS_REQUIRED'
    assert all(sum(q['initialCount']for q in rows if q['product']==name)==320 for name in ['B','R4'])
    for q in rows:
        assert all(q['nativeChecks'].values()) and q['noGameObjectsRetiredByTest']
        assert hashlib.sha256((P/q['rawPath']).read_bytes()).hexdigest()==q['rawSha256']
    lookup={(q['scenario'],q['seed'],q['product']):q for q in rows}
    pairs=[]
    for case,cfg in plan['scenarios'].items():
        for seed in plan['seeds20'][:cfg['nSeeds']]:
            a,z=lookup[(case,seed,'B')],lookup[(case,seed,'R4')]
            assert a['initialCount']==z['initialCount']
            pairs.append({'scenario':case,'seed':seed,'B':{k:a[k]for k in METRICS},
                          'R4':{k:z[k]for k in METRICS},
                          'difference':{k:z[k]-a[k]for k in METRICS},
                          'BEndS':a['end']['timeS'],'R4EndS':z['end']['timeS']})
    blocks=np.array([[sum(q['difference'][k]for q in pairs if q['seed']==seed)for k in METRICS]for seed in plan['seeds20']])
    cis=intervals(blocks,200000,20261102,[list(range(10)),list(range(10,20))])
    primary={}
    for i,k in enumerate(METRICS[:2]):
        delta=float(blocks[:,i].sum());p=exact_worse_p(blocks[:,i])
        primary[k]={'BTotal':sum(q['B'][k]for q in pairs),'R4Total':sum(q['R4'][k]for q in pairs),
                    'differenceR4MinusB':delta,'seedBlockDifferences':blocks[:,i].tolist(),
                    'oneSidedExactWorseP':p,'paired95PercentIntervalForTotalDifference':cis[i],
                    'decision':verdict(delta,p,cis[i])}
    order=sorted(primary,key=lambda k:primary[k]['oneSidedExactWorseP'])
    adjusted=0
    for rank,k in enumerate(order):
        adjusted=max(adjusted,min(1,(2-rank)*primary[k]['oneSidedExactWorseP']))
        primary[k]['holmAdjustedPInformational']=adjusted
    decision='CLEARLY_WORSE'if any(q['decision']=='CLEARLY_WORSE'for q in primary.values())else'USER_CONDITIONAL_APPROVAL_CRITERION_MET'if all(q['decision']=='WITHIN_USER_SAMPLING_VARIATION_OR_BETTER'for q in primary.values())else'INCONCLUSIVE'
    scenarios={}
    for n,case in enumerate(plan['scenarios']):
        pp=[q for q in pairs if q['scenario']==case]
        dd=np.array([[q['difference'][k]for k in METRICS]for q in pp])
        cc=intervals(dd,100000,20261102+n+1,[list(range(len(dd)))])
        scenarios[case]={'seedPairs':len(pp),'B':{k:sum(q['B'][k]for q in pp)for k in METRICS},
                         'R4':{k:sum(q['R4'][k]for q in pp)for k in METRICS},
                         'difference':{k:float(dd[:,i].sum())for i,k in enumerate(METRICS)},
                         'primary':{k:{'exactWorseP':exact_worse_p(dd[:,i]),'paired95PercentInterval':cc[i]}for i,k in enumerate(METRICS[:2])},
                         'pairs':pp}
    anchors=json.loads((P/'ANCHOR_CONTROLS.json').read_text())
    assert all(q['status']=='PASS'for q in anchors['rows'])
    execution=json.loads((P/'evidence/PROGRESS.json').read_text())
    assert execution['completed']==120 and all(q['status']=='VALID'for q in rows)
    assert execution['elapsedS']<=plan['execution']['maxWallSeconds']
    result={'schema':'AEGIS_TRACK_B_R4_PAIRED_STATISTICAL_RESULT_1','decision':decision,
            'planSha256':freeze['planSha256'],'pairedBattles':60,'actualBattles':120,
            'initialAsmsPerProduct':320,'primary':primary,'scenarioResults':scenarios,
            'secondaryOverall':{k:{'B':sum(q['B'][k]for q in pairs),'R4':sum(q['R4'][k]for q in pairs),
                                   'paired95PercentDifference':cis[i]}for i,k in enumerate(METRICS)if i>=2},
            'analysisMeaning':'User-specified between-seed sampling-variation decision, not formal noninferiority with an unspecified margin.',
            'floodMeaning':'Native water at each preregistered terminal+5 endpoint; differing end times are reported, not normalized with a new physical model.',
            'hpUsedForApproval':False,'statisticalRngSeparateFromGame':True,
            'allAnchorChecksPass':True,'allOriginalGameBytesUnchanged':True,
            'gameExpectationsUpdatedByAnalysis':False,'mergeExecutedByAnalysis':False}
    dest=P/'RESULTS.json';dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    with(P/'PAIRED_RESULTS.csv').open('w',newline='')as f:
        names=['scenario','seed','BEndS','R4EndS']+[f'{v}_{k}'for k in METRICS for v in ['B','R4','difference']]
        w=csv.DictWriter(f,fieldnames=names);w.writeheader()
        for q in pairs:w.writerow({**{k:q[k]for k in ['scenario','seed','BEndS','R4EndS']},**{f'{v}_{k}':q[v][k]for k in METRICS for v in ['B','R4','difference']}})
    print(json.dumps({'decision':decision,'primary':primary,'elapsedS':execution['elapsedS']},ensure_ascii=False))


if __name__=='__main__':main()

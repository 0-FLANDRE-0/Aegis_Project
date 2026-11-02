"""Outcome-independent statistical validity; native negative outcomes are data."""
from pathlib import Path
import collections,gzip,hashlib,importlib.util,json
P=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('frozen_battle_decode_only',P.with_name('B_stabilization')/'battle.py')
codec=importlib.util.module_from_spec(sp);sp.loader.exec_module(codec)
KILLS={'INTERCEPT_KILL','INTERCEPT_STRUCTURAL_FAILURE','PHALANX_KILL','DELAYED_STRUCTURAL_FAILURE','WARHEAD_AIRBURST'}
HITS={'NORMAL_HIT','DUD_PENETRATION','DAMAGED_HIT','DEGRADED_HIT','WARHEAD_DUD_HIT'}


def load(out):
    out=Path(out).resolve()
    job=json.loads((out/'JOB.json').read_text())
    tag=('old-active' if job['product']=='B' else'candidate-active')+'-'+job['case']['id']
    path=out/(tag+'.json.gz')
    result=codec.decode_capture(json.loads(gzip.decompress(path.read_bytes())))
    summary=json.loads((out/(tag+'-SUMMARY.json')).read_text())
    execution=json.loads((out/'SUMMARY.json').read_text())
    assert not execution['errors'],(job['id'],execution['errors'])
    plan=json.loads((P/'PLAN.json').read_text())
    assert summary['productSha256']==plan['products'][job['product']]['sha256']
    assert summary['fixtureSha256']==plan['sourcePins']['derivedHelper']
    assert result['case']==job['case'] and len(result['targets'])==len(job['case']['asms'])
    assert summary['setupSha256']==hashlib.sha256(json.dumps(job['case'],sort_keys=True,separators=(',',':')).encode()).hexdigest()
    checks=codec.post_validation(result)
    assert all(checks.values()),(job['id'],checks)
    assert result['startsWithZeroTracks'] and result['mode']=='AUTO'
    assert result['end']['reason']=='ALL_INITIAL_NATIVE_TERMINAL_OR_EGRESS_PLUS_5S'
    assert all(t['statisticalResolved']for t in result['targets'])
    kinds=collections.Counter();outcomes=[]
    for t in result['targets']:
        native=t['retirement'].get('cause')or t.get('_deathReason')or t.get('_wip113Outcome')or t.get('retiredReason')
        if t['alive']:
            assert t['statisticalEgress']['qualified'];kind='EGRESS'
        elif native in KILLS:kind='KILL'
        elif native in HITS:kind='LEAKER'
        elif native and ('SEA'in native or'WATER'in native or native in ['GUIDANCE_CONTROL_LOSS_MISS','FUEL_EXHAUSTED','LIFETIME_EXCEEDED','LIFE_EXPIRED','TERRAIN_IMPACT','GROUND_IMPACT','SELF_DESTRUCT']):kind='OTHER_NATIVE_TERMINAL'
        else:raise AssertionError(('NATIVE_OUTCOME_NEEDS_SOURCE_CLASSIFICATION',job['id'],native))
        kinds[kind]+=1;outcomes.append({'initialId':t['id'],'category':kind,'nativeCause':native,'egress':t['statisticalEgress']})
    hits=[e for e in result['events']if e['kind']=='NATIVE_SHIP_HIT_RECORD']
    damaging=[e for e in hits if(e['hit'].get('dmg')or 0)>0 and not e['hit'].get('miss')]
    ship=result['final']['ship']
    return {'id':job['id'],'scenario':job['scenario'],'seed':job['seed'],'product':job['product'],
        'status':'VALID','functionalFixtureStatusPreserved':result['status'],
        'behaviorQualificationsNotSamplingGates':{k:result['qualification'][k]for k in ['nativeSensorUpdates','nativeAutoWeaponRelease']},
        'initialCount':len(outcomes),'kills':kinds['KILL'],'leakers':kinds['LEAKER'],'egress':kinds['EGRESS'],
        'otherNativeTerminal':kinds['OTHER_NATIVE_TERMINAL'],'damagingHitRounds':len(damaging),
        'allHitRecordCount':len(hits),'wreckDamagingCallbacks':sum(bool(e['hit'].get('wip11cWreck'))for e in damaging),
        'floodM3':sum(c['waterM3']for c in ship['damage']['flooding']['cells']),'hpReferenceOnly':ship['shipHP'],
        'initialOutcomes':outcomes,'end':result['end'],'nativeChecks':checks,
        'rawPath':str(path.relative_to(P)),'rawSha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'noGameObjectsRetiredByTest':result['statisticalEndpoint']['gameObjectsRetiredByTest']==0,
        'productSha256':summary['productSha256'],'fixtureSha256':summary['fixtureSha256']}

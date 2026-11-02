"""Frozen B/R4 paired statistics. Test endpoint only; no game code edits."""
from pathlib import Path
import argparse, collections, concurrent.futures, gzip, hashlib, importlib.util
import json, os, signal, subprocess, sys, time, traceback

sys.dont_write_bytecode = True
P = Path(__file__).resolve().parent
R = P.parents[3]
E = P / 'evidence'
FROZEN = P.with_name('B_stabilization')
sha = lambda b: hashlib.sha256(b).hexdigest()


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    tmp.replace(path)


def memory():
    cg = Path('/sys/fs/cgroup')
    return {'current': int((cg/'memory.current').read_text()),
            'max': int((cg/'memory.max').read_text()),
            'events': {s[0]: int(s[1]) for line in (cg/'memory.events').read_text().splitlines() if (s := line.split())}}


def verify(plan):
    for product in plan['products'].values():
        assert sha((R/product['file']).read_bytes()) == product['sha256']
    paths = {'baseHelper': FROZEN/'battle.js', 'derivedHelper': P/'test_support/statistical_battle.js',
             'frozenRunner': FROZEN/'battle.py', 'instrumentAndBrowser': R/'docs/missile/fuze-zem/A/browser_tools.py',
             'loader': R/'docs/gun/B2/phase1b/fast_http.py', 'server': R/'docs/gun/B2/diagnostic/http_browser.py'}
    for key, path in paths.items():
        assert sha(path.read_bytes()) == plan['sourcePins'][key], key


def jobs(plan):
    rows = []
    b = module('frozen_case_specs_only', FROZEN/'battle.py')
    for scenario, definition in plan['scenarios'].items():
        for seed in plan['seeds20'][:definition['nSeeds']]:
            case = json.loads(json.dumps(b.CASES[definition['base']]))
            case.update(id=f'{scenario}_{seed}', seed=seed, maxSeconds=600,
                        egressKm=30, egressOutwardS=10,
                        checkpointSeconds=[90] if scenario == 'S13' and seed == 419027 else [])
            if 'firstAsms' in definition:
                case['asms'] = case['asms'][:definition['firstAsms']]
            # Paired products share all setup bytes. Alternate execution order.
            for product in (['B','R4'] if seed % 2 == 0 else ['R4','B']):
                rows.append({'id':f'{scenario}-{seed}-{product}', 'scenario':scenario,
                             'seed':seed, 'product':product, 'case':case})
    anchors = {'S6-419027-R4':0, 'S6-419027-B':1, 'S13-419027-R4':2, 'S13-419027-B':3}
    return sorted(rows, key=lambda x:(anchors.get(x['id'],4), list(plan['scenarios']).index(x['scenario']), x['seed']))


def worker(job_file):
    plan = json.loads((P/'PLAN.json').read_text())
    verify(plan)
    job = json.loads(Path(job_file).read_text())
    out = Path(job['out'])
    os.environ.pop('B2_PHASE1_REGRESSION', None)
    b = module('frozen_statistical_battle_native_runner', FROZEN/'battle.py')
    b.P = P
    b.HELPER = P/'test_support/statistical_battle.js'
    b.CASES = {job['case']['id']: job['case']}
    label = 'old-active' if job['product']=='B' else 'candidate-active'
    product = plan['products']['R4']
    sys.argv = [str(FROZEN/'battle.py'), '--run', '--versions', label,
                '--cases', job['case']['id'], '--candidate',str(R/product['file']),
                '--sha',product['sha256'], '--out',str(out)]
    return b.main()


def metrics(job, out):
    b = module('frozen_lossless_statistics_decoder', FROZEN/'battle.py')
    tag = ('old-active' if job['product']=='B' else 'candidate-active')+'-'+job['case']['id']
    path = out/(tag+'.json.gz')
    result = b.decode_capture(json.loads(gzip.decompress(path.read_bytes())))
    check = b.post_validation(result)
    assert all(check.values()), check
    assert result['status']=='QUALIFYING_COMPLETED_BATTLE', result['end']
    assert all(t['statisticalResolved'] for t in result['targets'])
    kinds = collections.Counter()
    rows = []
    for t in result['targets']:
        native = t['retirement'].get('cause') or t.get('_deathReason') or t.get('_wip113Outcome') or t.get('retiredReason')
        if t['alive']:
            assert t['statisticalEgress']['qualified']
            category = 'EGRESS'
        elif native in ['INTERCEPT_KILL','INTERCEPT_STRUCTURAL_FAILURE','PHALANX_KILL','DELAYED_STRUCTURAL_FAILURE','WARHEAD_AIRBURST']:
            category = 'KILL'
        elif native in ['NORMAL_HIT','DUD_PENETRATION','DAMAGED_HIT','DEGRADED_HIT','WARHEAD_DUD_HIT']:
            category = 'LEAKER'
        elif native and ('SEA' in native or 'WATER' in native or native in ['GUIDANCE_CONTROL_LOSS_MISS','FUEL_EXHAUSTED','LIFETIME_EXCEEDED','LIFE_EXPIRED','TERRAIN_IMPACT','GROUND_IMPACT','SELF_DESTRUCT']):
            category = 'OTHER_NATIVE_TERMINAL'
        else:
            category = 'UNCLASSIFIED_NATIVE_TERMINAL'
        kinds[category] += 1
        rows.append({'initialId':t['id'], 'category':category, 'nativeCause':native,
                     'nativeAlive':t['alive'], 'egress':t['statisticalEgress']})
    hits = [e for e in result['events'] if e['kind']=='NATIVE_SHIP_HIT_RECORD']
    damaging = [e for e in hits if (e['hit'].get('dmg') or 0)>0 and not e['hit'].get('miss')]
    ship = result['final']['ship']
    passive = out/(tag+'-PASSIVE.json.gz')
    value = {'id':job['id'], 'scenario':job['scenario'], 'seed':job['seed'], 'product':job['product'],
             'status':'VALID' if kinds['UNCLASSIFIED_NATIVE_TERMINAL']==0 else 'NEEDS_NATIVE_OUTCOME_CLASSIFICATION',
             'initialCount':len(rows), 'kills':kinds['KILL'], 'leakers':kinds['LEAKER'],
             'egress':kinds['EGRESS'], 'otherNativeTerminal':kinds['OTHER_NATIVE_TERMINAL'],
             'damagingHitRounds':len(damaging), 'allHitRecordCount':len(hits),
             'wreckDamagingCallbacks':sum(bool(e['hit'].get('wip11cWreck')) for e in damaging),
             'floodM3':sum(c['waterM3'] for c in ship['damage']['flooding']['cells']),
             'hpReferenceOnly':ship['shipHP'], 'nativeOutcomeCounts':dict(collections.Counter(x['nativeCause'] or 'EGRESS' for x in rows)),
             'initialOutcomes':rows, 'nativeHitRecords':hits, 'end':result['end'],
             'globalRng':result['final']['globalRng'], 'inventory':result['final']['inventory'],
             'moduleDamage':ship['damage']['moduleDamage'], 'counts':result['counts'],
             'rawPath':str(path.relative_to(P)), 'rawSha256':sha(path.read_bytes()),
             'passiveFinalSha256':sha(gzip.decompress(passive.read_bytes())),
             'nativeChecks':check, 'checkpoints':result['statisticalEndpoint']['checkpoints'],
             'noGameObjectsRetiredByTest':result['statisticalEndpoint']['gameObjectsRetiredByTest']==0}
    save(out/'METRICS.json',value)
    return value


def kill_tree(proc):
    try:
        import psutil
        descendants = psutil.Process(proc.pid).children(recursive=True)
    except Exception:
        descendants = []
    try: os.killpg(proc.pid,signal.SIGTERM)
    except ProcessLookupError: pass
    try: proc.wait(timeout=8)
    except subprocess.TimeoutExpired:
        try: os.killpg(proc.pid,signal.SIGKILL)
        except ProcessLookupError: pass
    for child in descendants:
        try: child.kill()
        except Exception: pass


def execute(job, deadline):
    out = E/'runs'/job['id']/'attempt1'
    out.mkdir(parents=True,exist_ok=True)
    job = {**job, 'out':str(out)}
    job_file = out/'JOB.json';save(job_file,job)
    # Preserve enough launch headroom for one fresh renderer. Other live
    # workers can finish while this one waits; hard wall deadline still holds.
    while memory()['max']-memory()['current'] < 2_000_000_000:
        if time.monotonic()>=deadline: return {'id':job['id'],'status':'BUDGET_EXPIRED_BEFORE_START'}
        time.sleep(1)
    before=memory();at=time.monotonic();limit=min(900,max(1,deadline-at))
    cmd=[sys.executable,'-u',str(Path(__file__).resolve()),'--worker',str(job_file)]
    with (out/'worker.log').open('w') as log:
        proc=subprocess.Popen(cmd,cwd=R,stdout=log,stderr=subprocess.STDOUT,
                              env={**os.environ,'TMPDIR':'/dev/shm','PYTHONDONTWRITEBYTECODE':'1'},start_new_session=True)
        try: code=proc.wait(timeout=limit)
        except subprocess.TimeoutExpired:
            kill_tree(proc);code=124
    after=memory()
    receipt={'id':job['id'],'command':cmd,'exitCode':code,'wallS':time.monotonic()-at,
             'memoryBefore':before,'memoryAfter':after,'gameCodeChanged':False}
    try:
        if code!=0: raise RuntimeError('WORKER_EXIT_'+str(code))
        value=metrics(job,out)
        receipt.update(status=value['status'],metricsPath=str((out/'METRICS.json').relative_to(P)),
                       leakers=value['leakers'],damagingHitRounds=value['damagingHitRounds'])
    except Exception as exc:
        receipt.update(status='INCOMPLETE',error=str(exc),traceback=traceback.format_exc())
    save(out/'EXECUTION.json',receipt)
    return receipt


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--worker');ap.add_argument('--run',action='store_true')
    ap.add_argument('--pilot',action='store_true');ap.add_argument('--resume',action='store_true')
    args=ap.parse_args()
    if args.worker:return worker(args.worker)
    plan=json.loads((P/'PLAN.json').read_text());verify(plan);all_jobs=jobs(plan)
    assert len(all_jobs)==120
    assert sha((P/'test_support/statistical_battle.js').read_bytes())==plan['sourcePins']['derivedHelper']
    if not args.run:
        save(P/'JOBS.json',all_jobs);print(json.dumps({'jobs':len(all_jobs),'run':False}));return 0
    timing_path=E/'BUDGET.json'
    if timing_path.exists():
        timing=json.loads(timing_path.read_text());deadline=timing['deadlineMonotonic']
    else:
        now=time.monotonic();timing={'startMonotonic':now,'deadlineMonotonic':now+10800,
                                    'startUtc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'maxWallS':10800}
        save(timing_path,timing);deadline=timing['deadlineMonotonic']
    existing={}
    for job in all_jobs:
        f=E/'runs'/job['id']/'attempt1/EXECUTION.json'
        if f.exists():existing[job['id']]=json.loads(f.read_text())
    todo=all_jobs[:2] if args.pilot else all_jobs
    todo=[j for j in todo if j['id'] not in existing]
    print(json.dumps({'startingJobs':len(todo),'closed':len(existing),'remainingBudgetS':deadline-time.monotonic(),'maxBrowsers':2}),flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        pending={pool.submit(execute,j,deadline):j for j in todo}
        for future in concurrent.futures.as_completed(pending):
            result=future.result();existing[result['id']]=result
            save(E/'PROGRESS.json',{'completed':len(existing),'planned':120,'rows':list(existing.values()),
                  'elapsedS':time.monotonic()-timing['startMonotonic'],'budgetRemainingS':deadline-time.monotonic()})
            print(json.dumps({k:result.get(k) for k in ['id','status','wallS','leakers','damagingHitRounds']},ensure_ascii=False),flush=True)
    verify(plan)
    return 0 if all(r['status']=='VALID' for r in existing.values()) else 2


if __name__=='__main__':
    raise SystemExit(main())

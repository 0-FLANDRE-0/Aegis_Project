"""Only the requested 14 scenarios, same native path in current/patched game pages."""
from pathlib import Path
import base64, gzip, hashlib, json, re, sys, time
from playwright.sync_api import sync_playwright

H = Path(__file__).resolve().parent
R = H.parents[3]
C = H / 'diagnostic'
E = H / 'evidence'
E.mkdir(exist_ok=True)
sys.path.insert(0, str(R / 'docs/pip/B'))
import browser_backend
browser_backend.install()
sys.path.insert(0, str(R / 'docs/helicopter/H'))
from browser import launch, load_fleet

used = {q['name'] for q in json.loads((C / 'dependencies.json').read_text())['rows']}
boundary = {k: v for k, v in json.loads((C / 'boundaries.json').read_text()).items() if k in used}
overrides = [k + '=(' + v['code'] + ');' for k, v in boundary.items() if v['code'].startswith('function ')]
names = [k for k, v in boundary.items() if v['code'].startswith('function ')]
helper = (C / 'private.js').read_text().split('return {runCase,profiles:')[0] + "\nwindow.__RECOVERY_NATIVE__={runCase(c){const saved={" + ','.join(names) + "};try{" + '\n'.join(overrides) + "selectedLockId=1;emconActive=false;engagementControlMode='MANUAL';shipNav.positionWorld.x=0;shipNav.positionWorld.y=0;shipNav.vx=shipNav.vy=shipNav.speed=0;return runCase(c);}finally{" + ';'.join(n + '=saved.' + n for n in names) + "}}};\n"
reduce_source = (H / 'proof.cjs').read_text().split('module.exports = ', 1)[1].strip().removesuffix(';')
state = "()=>JSON.stringify({tick:__NAVAL_SIM_DIAG__.snapshot(),operation:__NAVAL_SIM_DIAG__.exportOperationalStateV48Wip11A(),mutation:__NAVAL_SIM_DIAG__.operationalImportMutationFingerprintV48Wip11B(),helicopters:__HELO__.snapshot(),world:__AEGIS_ENGAGEMENT_RUNTIME__.world,tracks:[...__AEGIS_ACTIVE_SHIP_RUNTIME__.combatSystem.trackManager.tracks],links:__AEGIS_ACTIVE_SHIP_RUNTIME__.combatSystem.weaponLinksB3},(k,v)=>v instanceof Map?[...v]:v instanceof Set?[...v]:v)"
cases = json.loads((H / 'cases.json').read_text())['cases']
pages = {'CURRENT': Path('/tmp/aegis-kappa/CURRENT.html'), 'PATCHED': R / 'Aegis_SIM_v48_WIP_KAPPA_PIP_LOS_A.html'}
errors, checks, records, capture_records = [], {}, [], []
started = time.perf_counter()
with sync_playwright() as pw:
    browser = launch(pw)
    for version, file in pages.items():
        if not file.exists():
            file = R / 'archive/v48/WIP_RANGE_RECOVERY_A/Aegis_SIM_v48_WIP_RANGE_RECOVERY_A.html'
        source = (C / ('current-native-engine.js' if version == 'CURRENT' else 'native-engine.js')).read_text() + '\n' + (C / 'private.js').read_text()
        raw = file.read_bytes()
        p = load_fleet(browser, raw, own='DDG_119_LATE_FLIGHT_IIA', errors=errors)
        captured = p.evaluate('__ENV_A__.capture()')
        expected = json.loads((H / 'inputs.json').read_text())
        checks[version + '.liveInputsMatchOffline'] = captured['data'] == expected['data'] and captured['settings'] == expected['settings']
        status = p.evaluate('__ENV_A__.status()')
        checks[version + '.nativeAudit'] = not status['changedNativeFunctions']
        checks[version + '.envelopeStalenessHonest'] = status['recalculationRequired']
        if version == 'PATCHED':
            table = p.evaluate('__ENV_KAPPA_A__.table()')
            checks['PATCHED.noOldTablePresentedAsNew'] = len(table['rows']) == 0 and table['profileHash'] is None and len(table['historicalResults']) == 2 and status['envelopeMeasured'] is False
            checks['PATCHED.regeneratedCapsuleSynchronized'] = status['nativeCapsuleSynchronized'] is True
            (E / 'patched-capture.json').write_text(json.dumps(captured,separators=(',',':')))
        capture_records.append({'version': version, 'htmlSha256': hashlib.sha256(raw).hexdigest(), 'status': status})
        p.evaluate('(x)=>{const f=new Function("DATA","SETTINGS","PROFILE","PRIVATE_SHIP",x.source),q=__ENV_A__.capture();window.__RECOVERY_PRIVATE__=f(q.data,q.settings,{}, {entityId:"ENV_PRIVATE",navigation:{heading:0,speed:0,positionWorld:{x:0,y:0}},weapons:{}});window.__RECOVERY_REDUCE__=eval("("+x.reduce+")");}', {'source': source, 'reduce': reduce_source})
        private = []
        for c in cases:
            before = p.evaluate(state)
            q = p.evaluate('c=>__RECOVERY_REDUCE__(__RECOVERY_PRIVATE__.runCase(c))', c)
            checks[version + '.' + c['caseId'] + '.worldRngTickUnchanged'] = before == p.evaluate(state)
            private.append(q)
        p.close()
        html = raw.decode()
        m = re.search(r'data-c55-index="13">([^<]+)</script>', html)
        s = gzip.decompress(base64.b64decode(m[1])).decode()
        s = s.replace('\n  completeShipStartup();', '\n' + helper + '\n  completeShipStartup();', 1)
        z = gzip.compress(s.encode(), 9, mtime=0)
        html = html[:m.start(1)] + base64.b64encode(z).decode() + html[m.end(1):]
        m = re.search(r'const records=(\[.*?\]);', html, re.S)
        rs = json.loads(m[1]); rs[13].update(rawBytes=len(s.encode()), gzipBytes=len(z), sha256=hashlib.sha256(s.encode()).hexdigest())
        html = html[:m.start(1)] + json.dumps(rs, separators=(',', ':')) + html[m.end(1):]
        p = load_fleet(browser, html.encode(), own='DDG_119_LATE_FLIGHT_IIA', errors=errors)
        p.evaluate('s=>{window.__RECOVERY_REDUCE__=eval("("+s+")")}', reduce_source)
        details = []
        for c, q in zip(cases, private):
            native = p.evaluate('c=>__RECOVERY_REDUCE__(__RECOVERY_NATIVE__.runCase(c))', c)
            keys = ['timeS', 'xM', 'yM', 'altitudeM', 'speedMps', 'mach']
            delta = {k: max(abs(x[k] - y[k]) for x, y in zip(q['samples'], native['samples'])) for k in keys}
            prefix = version + '.' + c['caseId']
            checks[prefix + '.sampleCount'] = len(q['samples']) == len(native['samples'])
            checks[prefix + '.trajectoryExact'] = all(v == 0 for v in delta.values())
            checks[prefix + '.nativeFuze'] = q['success'] == native['success'] and q['reason'] == native['reason'] and q['fuzeMissM'] == native['fuzeMissM']
            checks[prefix + '.firstShelf'] = q['firstShelf'] == native['firstShelf']
            records.append({'version': version, 'caseId': c['caseId'], 'samples': len(q['samples']), 'maxError': delta, 'reason': native['reason'], 'success': native['success']})
            details.append({'caseId': c['caseId'], 'private': q, 'native': native})
            print(version, c['caseId'], native['reason'], delta, flush=True)
        (E / f'browser-{version}.json.gz').write_bytes(gzip.compress(json.dumps(details, separators=(',', ':')).encode(), 9, mtime=0))
        p.close()
    browser.close()
checks['pageErrors'] = not errors
result = {'pass': all(checks.values()), 'checks': checks, 'records': records, 'captures': capture_records, 'errors': errors, 'elapsedS': time.perf_counter() - started, 'method': 'native VLS release/update in disposable whole-game world with ideal information boundaries; detached copy of identical native code; no full envelope sweep or natural-sensor certification'}
(E / 'browser.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'pass': result['pass'], 'checks': len(checks), 'failed': [k for k, v in checks.items() if not v], 'errors': errors}))
raise SystemExit(0 if result['pass'] else 1)

"""C/D combat comparison and equal fixed ticks at 1/8/16/64x.

The six cold-aircraft cases use the existing full-simulation fixture, comparing
all existing combat/EW/network/team state and global/private RF RNG. The exact
new aviation/radio metadata and host profiler observations are excluded; existing
port queues, counters, sources and tracks are retained.
"""
import argparse
import base64
import gzip
import hashlib
import json
import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'docs/multiship/G'))
from browser_g import launch, load_fleet


def baseline(a):
    approved = None
    approved_path = getattr(a, 'approved_raid_baseline', None)
    if approved_path:
        approved = json.loads(approved_path.read_text())
        assert approved['schema'] == 'AEGIS_CLEAN_A_APPROVED_RAID_BASELINES_1'
        main = gzip.decompress(base64.b64decode(re.search(rb'data-c55-index="13">([^<]+)', a.html.read_bytes())[1]))
        main = re.sub(rb'// ENV_D_DATA_BEGIN[\s\S]*?// ENV_D_DATA_END', b'', main)
        assert hashlib.sha256(main).hexdigest() == approved['gameCoreWithoutEnvelopeSha256'], 'CLEAN_A baseline requires its explicitly reviewed game core'
        assert all(v['classification'] == 'a' for v in approved['entries'].values())
    source_path = ROOT / 'docs/multiship/H4/regression_baseline.py'
    source = source_path.read_text()
    normalizer = r'''def physical(value):
    if isinstance(value,dict):
        result={k:physical(v)for k,v in value.items()if k not in ['performance','aviation']}
        if value.get('schema')=='AEGIS_OFFBOARD_PORT_C_1':
            # HELI_D owns only these new radios. Existing port queues, counters,
            # unrelated sources, all tracks and every RNG stay in the comparison.
            result.pop('helicopterImplemented',None)
            result['sources']=[s for s in result.get('sources',[])if s.get('sourceId')not in ['H1','H2']]
        if value.get('schema')=='AEGIS_SHIP_OBSERVER_C_1'and'deferred'in result:
            result['deferred']=[s for s in result['deferred']if s!='helicopterFlightAndSensors']
        return result
    if isinstance(value,list):return [physical(v)for v in value]
    return value
'''
    start,end=source.index('def physical('),source.index('def main(')
    source=source[:start]+normalizer+source[end:]
    needle='dynamics:d.shipDynamics(),rng:'
    assert source.count(needle)==1
    source=source.replace(needle,'dynamics:d.shipDynamics(),observers:d.observerSnapshotC(),offboard:d.offboardSnapshotC(),rng:',1)
    needle="'bothFaultFree':"
    assert source.count(needle)==1
    source=source.replace(needle,"'sameExistingObserverState':physical(pair['baseline']['observers'])==physical(pair['candidate']['observers']),'sameExistingOffboardPorts':physical(pair['baseline']['offboard'])==physical(pair['candidate']['offboard']),'bothFaultFree':",1)
    source = source.replace('AEGIS_MULTI_SHIP_H4_BASELINE_COMPARISON', 'AEGIS_HELO_D_BASELINE_COMPARISON').replace('H3/H4', 'HELI_C/HELI_D')
    source = source.replace("abs(count_vls(pair['baseline'])-count_vls(pair['candidate']))<=1", "count_vls(pair['baseline'])==count_vls(pair['candidate'])")
    source = source.replace('exclude existing EW/network/tactical metadata, new attack settings and profiler', 'exclude only profiler, changed aviation schema, new H1/H2 radio configs and the exact completed-helicopter metadata labels; include full existing observer tracks/private RF RNG/queues/counters/unrelated ports and EW/network/tactical/maneuver/attack/team')
    source = source.replace('Ownship defense/maneuver utility is OFF by default. No allied peers or Harpoon launch in this paired regression; H3-on maneuver and native defense are verified separately.', 'Cold helicopters, defense/maneuver utility OFF. No allied peers or Harpoon launch in these six paired cases. Active aircraft are tested by the separate fixed-clock, altitude and native suites.')
    if approved:
        # Update only explicitly reviewed category-(a) raid expectations.
        # CLEAN_A approves DDG; CLEAN_B also approves CG under the user's
        # outcome-only policy. Every assertion remains an exact comparison.
        needle = "                rows.append({'ship':ship"
        assert source.count(needle) == 1
        update = '''                if scenario=='raid' and ship in CLEAN_A_APPROVED['entries']:
                    ref=CLEAN_A_APPROVED['entries'][ship]
                    assert physical_signature(pair['baseline'])==ref['old']['physical']
                    assert physical(pair['baseline']['observers'])==ref['old']['observer']
                    assert count_vls(pair['baseline'])==ref['old']['loadedVlsCells']
                    observations['cleanABaselineUpdate']={'assertions':ref['assertions'],'oldHash':ref['oldHash'],'newHash':ref['newHash'],'reason':ref['reason'],'originalChecks':dict(checks)}
                    checks['samePhysicalState']=physical_signature(pair['candidate'])==ref['expected']['physical']
                    checks['raidInventoryDeltaBounded']=count_vls(pair['candidate'])==ref['expected']['loadedVlsCells']
                    checks['sameExistingObserverState']=physical(pair['candidate']['observers'])==ref['expected']['observer']
'''
        source = source.replace(needle, update + needle, 1)
    scope = {'__file__': str(source_path), '__name__': '_helo_d_baseline', 'CLEAN_A_APPROVED': approved}
    exec(compile(source, str(source_path), 'exec'), scope)
    previous_argv = sys.argv
    sys.argv = [str(source_path), str(a.baseline), str(a.html), str(a.out)]
    try:
        scope['main']()
    except SystemExit:
        pass  # Collect its report alongside the independent clock fixture.
    finally:
        sys.argv = previous_argv
    report = json.loads((a.out / 'baseline-comparison.json').read_text())
    # Progress is useful while running, but duplicates the complete final case
    # report and is not part of the published evidence set.
    (a.out / 'baseline-comparison-progress.json').unlink(missing_ok=True)
    return report


def clock(a):
    errors, rows = [], []
    with sync_playwright() as pw:
        browser = launch(pw)

        # Only prevent background RAF before boot. The served production HTML
        # is unmodified; runFramesToTicks uses the actual frame accumulator and
        # complete fixed-step simulation at each selected time multiplier.
        class ControlledBrowser:
            def new_page(self, **options):
                page = browser.new_page(**options)
                page.add_init_script('window.requestAnimationFrame=()=>0;')
                return page

        controlled = ControlledBrowser()
        for scale in [1, 8, 16, 64]:
            page = load_fleet(controlled, a.html.read_bytes(), own='DDG_119_LATE_FLIGHT_IIA', ally='CG_52_LATE_TICONDEROGA', enemy=None, errors=errors)
            row = page.evaluate('''scale=>{
                const d=__NAVAL_SIM_DIAG__,api=__HELO__;
                __WIP125_DIAG__.forcePreSail();document.getElementById('wip125DepartBtn').click();d.setTerrainDiagBypass(true);
                const before=api.snapshot(),commands=[];
                for(const h of before.aircraft){
                    commands.push(api.command(h.id,'SET_ALTITUDE',{altitudeM:h.slot===0?1200:200}));
                    commands.push(api.command(h.id,'SET_IFF',{enabled:true}));
                    commands.push(api.command(h.id,'SET_RADAR',{enabled:true}));
                    commands.push(api.command(h.id,'LAUNCH'));
                    commands.push(api.command(h.id,'WAYPOINT',{x:2000+h.slot*1000,y:1500}));
                    commands.push(api.command(h.id,'ROUTE_APPEND',{x:1000,y:2200}));
                }
                commands.push(api.command(before.aircraft[0].id,'FOLLOW_SHIP'));
                d.setShipRudderTest(6);d.setEmcon(false);
                const run=d.runFramesToTicks(60,scale,8000);d.setEmcon(true);
                const emconRun=d.runFramesToTicks(60,scale,8000),after=api.snapshot();
                return {scale,commands,run,emconRun,after,radar:__APS153__.snapshot(),iff:__HELO_SENSOR_STAGE_A_E__.snapshot(),ownIffRng:JSON.parse(JSON.stringify(__AEGIS_ACTIVE_SHIP_RUNTIME__.combatSystem.observerC.heloIffE?.rng??null)),offboard:d.offboardSnapshotC(),observers:d.observerSnapshotC(),rng:__HARPOON_DIAG_A__.snapshot().rng,
                    contract:d.simulationUpdateContractV48Wip11A(),core:__CORE_SELFTEST_FAILURES__};
            }''', scale)
            rows.append(row)
            page.close()
        browser.close()
    signature = lambda r: json.dumps({'after': r['after'], 'rng': r['rng'], 'offboard': r['offboard'], 'observers': r['observers'], 'radar': r['radar'], 'iff': r['iff'], 'ownIffRng': r['ownIffRng']}, sort_keys=True)
    checks = {str(r['scale']) + '.exact': signature(r) == signature(rows[0]) for r in rows}
    checks['allCommandsAccepted'] = all(c['ok'] for r in rows for c in r['commands'])
    checks['differentAltitudesPreserved'] = all([h['targetAltitudeM'] for h in r['after']['aircraft']] == [1200, 200] for r in rows)
    checks['sensorsEnabled'] = all(all(h['iffOn'] and h['radarOn'] for h in r['after']['aircraft']) for r in rows)
    checks['hawklinkSourcesRegistered'] = all({s['sourceId'] for s in r['offboard']['sources']} >= {'H1','H2'} for r in rows)
    checks['radarEmconDoesNotBlockLinks'] = all(all(s['connected'] for s in r['offboard']['sources'] if s['sourceId'] in ['H1','H2']) for r in rows)
    checks['privateRadarStreamsActuallyAdvanced'] = all(all(h['statistics'] is not None and h['statistics']['rngState'] != 0 and h['radar']['turn'] > 0 for h in r['radar']['aircraft']) for r in rows)
    checks['hawklinkActuallyDelivered'] = all(r['offboard']['accepted'] > 0 and any(h['sensorsE']['link']['transmittedTotal'] > 0 for h in r['after']['aircraft']) for r in rows)
    checks['iffStreamActuallyRan'] = all(r['ownIffRng'] is not None and r['after']['aircraft'][0]['sensorsE']['iffRepliesReceived'] > 0 for r in rows)
    checks['fixed60Hz'] = all(r['contract']['fixedTickHz'] == 60 for r in rows)
    checks['corePass'] = all(not r['core'] for r in rows)
    report = {'pass': all(checks.values()) and not errors, 'checks': checks, 'rows': rows, 'errors': errors,
              'htmlSha256': hashlib.sha256(a.html.read_bytes()).hexdigest()}
    (a.out / 'clock.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


def main():
    p = argparse.ArgumentParser()
    p.add_argument('baseline', type=Path)
    p.add_argument('html', type=Path)
    p.add_argument('out', type=Path)
    p.add_argument('--clock-only', action='store_true')
    p.add_argument('--baseline-only', action='store_true')
    p.add_argument('--approved-raid-baseline', type=Path, help='Explicit CLEAN_A category-(a) reference; guarded by reviewed game-core hash')
    a = p.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    if a.clock_only:
        fixed = clock(a)
        print(json.dumps({'pass': fixed['pass'], 'checks': len(fixed['checks']), 'failed': [k for k,v in fixed['checks'].items() if not v], 'errors': fixed['errors']}))
        raise SystemExit(0 if fixed['pass'] else 1)
    if a.baseline_only:
        paired = baseline(a)
        raise SystemExit(0 if paired['pass'] else 1)
    paired, fixed = baseline(a), clock(a)
    checks = {r['ship'] + ':' + r['scenario'] + ':' + k: v for r in paired['cases'] for k,v in r['checks'].items()}
    checks.update({'clock:' + k: v for k,v in fixed['checks'].items()})
    report = {'pass': paired['pass'] and fixed['pass'], 'checks': checks,
              'baselineSha256': hashlib.sha256(a.baseline.read_bytes()).hexdigest(),
              'htmlSha256': hashlib.sha256(a.html.read_bytes()).hexdigest(),
              'errors': paired['errors'] + fixed['errors'],
              'reports': ['baseline-comparison.json', 'clock.json']}
    (a.out / 'regression.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'pass': report['pass'], 'checks': len(checks), 'failed': [k for k,v in checks.items() if not v], 'errors': report['errors']}))
    raise SystemExit(0 if report['pass'] else 1)


if __name__ == '__main__':
    main()

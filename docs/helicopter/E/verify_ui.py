"""Desktop/touch AIR controls in the frozen HTML, with native DOM input events."""
import argparse
import base64
import gzip
import re
import hashlib
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'docs/multiship/G'))
from browser_g import launch, load_fleet


def main():
    p = argparse.ArgumentParser()
    p.add_argument('html', type=Path)
    p.add_argument('out', type=Path)
    a = p.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    source = gzip.decompress(base64.b64decode(re.search(r'data-c55-index="13">(.*?)</script>', a.html.read_text(), re.S)[1])).decode()
    world_per_m = float(re.search(r'const WORLD_UNITS_PER_KM_FIXED = ([0-9.]+)', source)[1]) / 1000
    errors, rows = [], []
    with sync_playwright() as pw:
        browser = launch(pw)
        for width, height in [(1000, 760), (390, 844)]:
            page = load_fleet(browser, a.html.read_bytes(), own='DDG_119_LATE_FLIGHT_IIA', ally=None, enemy=None,
                              width=width, height=height, touch=width < 500, errors=errors)
            checks = {}
            initial = page.evaluate('JSON.stringify(__HELO__.snapshot())')
            page.locator('#modeAirBtn').click()
            checks['sensorMenuEntryPresent'] = page.locator('#c15SensorsFlyout #external3DHeloRadarE').count() == 1
            checks['fiveTabs'] = page.locator('.control-deck-tab[data-tab]').count() == 5
            checks['tabReadOnly'] = initial == page.evaluate('JSON.stringify(__HELO__.snapshot())')
            checks['oldAirViewAndSeparateCancelRemoved'] = all(page.locator('#' + i).count() == 0 for i in ['airViewA', 'airShipViewA', 'airCancelA'])
            checks['cameraTrackingEntriesRetained'] = all(page.locator('#c15CameraFlyout #external3DHeloB' + str(i)).count() == 1 for i in [0, 1])
            page.locator('#airHeloA0').click()
            checks['initialSensorFlags'] = page.evaluate('__HELO__.snapshot().aircraft.every(h=>h.iffOn===true&&h.radarOn===false)')
            checks['initialSensorLabels'] = page.locator('#airIffE').inner_text() == 'IFF ON' and page.locator('#airRadarE').inner_text() == '레이더 OFF'
            page.locator('#airIffE').click()
            checks['iffToggleSelectedOnly'] = page.evaluate('__HELO__.snapshot().aircraft[0].iffOn===false&&__HELO__.snapshot().aircraft[1].iffOn===true') and page.locator('#airIffE').get_attribute('aria-pressed') == 'false'
            page.locator('#airRadarE').click()
            checks['radarToggleSelectedOnly'] = page.evaluate('__HELO__.snapshot().aircraft[0].radarOn===true&&__HELO__.snapshot().aircraft[1].radarOn===false') and page.locator('#airRadarE').get_attribute('aria-pressed') == 'true'
            page.locator('#airHeloA1').click()
            checks['selectionUsesPerAircraftSensorFlags'] = page.locator('#airIffE').inner_text() == 'IFF ON' and page.locator('#airRadarE').inner_text() == '레이더 OFF'
            page.locator('#airHeloA0').click()
            page.wait_for_timeout(300)
            page.locator('#airIffE').click()
            page.locator('#airRadarE').click()
            checks['flagsRestoredThroughControls'] = page.evaluate('__HELO__.snapshot().aircraft.every(h=>h.iffOn===true&&h.radarOn===false)')
            checks['rosterIncludesLinkAndRecentPlotCount'] = 'plots/10s' in page.locator('#airHeloA0').inner_text()
            checks['launchInitialLabel'] = page.locator('#airLaunchA').inner_text() == '출격 요청'
            checks['controlsLeftListRight'] = page.evaluate('document.getElementById("airControlsB").getBoundingClientRect().right<=document.getElementById("airListB").getBoundingClientRect().left')
            layout = page.evaluate('''()=>{const p=document.getElementById('controlDeckAirPage'),l=document.getElementById('airAircraftA');return {
                pageHeight:p.getBoundingClientRect().height,pageTop:p.getBoundingClientRect().top,
                listHeight:l.clientHeight,rowHeight:[...l.children].reduce((s,r)=>s+r.getBoundingClientRect().height,0),
                listOverflow:getComputedStyle(l).overflowY,documentWidth:document.documentElement.scrollWidth,viewportWidth:innerWidth};}''')
            checks['compactPageHeight'] = layout['pageHeight'] <= (280 if width < 500 else 270) + 1
            checks['listHasEmptySpace'] = layout['listHeight'] > layout['rowHeight'] + 12
            checks['listScrollEnabled'] = layout['listOverflow'] in ['auto', 'scroll']
            checks['noHorizontalOverflow'] = layout['documentWidth'] <= width

            # Opening and editing the modal must not alter simulation state until apply.
            before = page.evaluate('JSON.stringify(__HELO__.snapshot())')
            page.locator('#airAltitudeC').click()
            checks['altitudeDialogOpened'] = page.locator('#airAltitudeDialogC').is_visible()
            checks['dialogReadOnlyUntilApply'] = before == page.evaluate('JSON.stringify(__HELO__.snapshot())')
            presets = page.locator('#airAltitudePresetsC [data-altitude-m]').evaluate_all('es=>es.map(e=>Number(e.dataset.altitudeM))')
            maximum = page.evaluate('__HELO__.snapshot().constants.maxAltitudeM.value')
            checks['representativePresetsAndPublicMaximum'] = all(v in presets for v in [25, 50, 100, 200, 500, 800, 1000, 1200, 2000, 3000, maximum])
            checks['altitudeInputRangeCorrect'] = page.locator('#airAltitudeInputC').evaluate('(e,max)=>Number(e.min)===25&&Number(e.max)===max', maximum)
            checks['altitudeDialogWithinViewport'] = page.locator('#airAltitudeDialogC').evaluate('e=>{const r=e.getBoundingClientRect();return r.left>=0&&r.top>=0&&r.right<=innerWidth&&r.bottom<=innerHeight;}')
            page.locator('#airAltitudePresetsC [data-altitude-m="200"]').click()
            checks['presetEditsInputWithoutMutation'] = float(page.locator('#airAltitudeInputC').input_value()) == 200 and before == page.evaluate('JSON.stringify(__HELO__.snapshot())')
            page.screenshot(path=str(a.out / f'altitude-{width}.png'))
            page.locator('#airAltitudeApplyC').click()
            checks['presetApplySelectedOnly'] = page.evaluate('__HELO__.snapshot().aircraft[0].targetAltitudeM===200&&__HELO__.snapshot().aircraft[1].targetAltitudeM===50')
            page.wait_for_timeout(300)
            page.locator('#airAltitudeC').click()
            page.locator('#airAltitudeInputC').fill('1200')
            page.locator('#airAltitudeApplyC').click()
            checks['directNumericAltitude'] = page.evaluate('__HELO__.snapshot().aircraft[0].targetAltitudeM===1200')
            page.wait_for_timeout(300)
            page.locator('#airAltitudeC').click()
            before_bad = page.evaluate('JSON.stringify(__HELO__.snapshot())')
            page.locator('#airAltitudeInputC').fill(str(maximum + 1))
            page.locator('#airAltitudeApplyC').click()
            checks['overMaximumRejectedWithoutWrites'] = before_bad == page.evaluate('JSON.stringify(__HELO__.snapshot())') and page.locator('#airAltitudeDialogC').is_visible()
            page.wait_for_timeout(300)
            page.locator('#airAltitudeInputC').fill('24')
            page.locator('#airAltitudeApplyC').click()
            checks['underMinimumRejectedWithoutWrites'] = before_bad == page.evaluate('JSON.stringify(__HELO__.snapshot())')
            page.wait_for_timeout(300)
            page.locator('#airAltitudeInputC').fill('50')
            page.locator('#airAltitudeApplyC').click()
            checks['defaultRestored'] = page.evaluate('__HELO__.snapshot().aircraft[0].targetAltitudeM===50')

            old_cursors = page.evaluate('JSON.stringify(__NAVAL_SIM_DIAG__.wip13cControlDeckSnapshot().state)')
            for x in [.4, .55, .7]:
                page.locator('#c').click(position={'x': width*x, 'y': height*.18})
                page.wait_for_timeout(100)
            checks['threeMapWaypoints'] = page.evaluate('__HELO__.snapshot().aircraft[0].route.length===3')
            checks['shipWeaponCursorsUntouched'] = old_cursors == page.evaluate('JSON.stringify(__NAVAL_SIM_DIAG__.wip13cControlDeckSnapshot().state)')
            page.locator('#airUndoB').click()
            checks['undoLastWaypoint'] = page.evaluate('__HELO__.snapshot().aircraft[0].route.length===2')
            page.locator('#airFollowB').click()
            checks['followButton'] = page.evaluate('__HELO__.snapshot().aircraft[0].navigationMode==="FOLLOW_SHIP"&&__HELO__.snapshot().aircraft[0].route.length===0')
            page.locator('#c').click(position={'x': width*.62, 'y': height*.16})
            checks['mapReturnsToRoute'] = page.evaluate('__HELO__.snapshot().aircraft[0].navigationMode==="ROUTE"&&__HELO__.snapshot().aircraft[0].route.length===1')

            page.locator('#airLaunchA').click()
            checks['queuedLabelIsCancel'] = page.locator('#airLaunchA').inner_text() == '출격 대기 취소'
            page.wait_for_timeout(300)
            page.locator('#airLaunchA').click()
            checks['sameButtonCancelsQueue'] = page.evaluate('__HELO__.snapshot().queue.length===0&&__HELO__.snapshot().aircraft[0].state==="HANGARED"')
            checks['cancelRestoresLaunchLabel'] = page.locator('#airLaunchA').inner_text() == '출격 요청'
            page.wait_for_timeout(300)
            page.locator('#airLaunchA').click()
            page.locator('#airHeloA1').click()
            page.wait_for_timeout(300)
            page.locator('#airLaunchA').click()
            checks['twoLaunchesQueued'] = page.evaluate('__HELO__.snapshot().queue.length===2')
            page.wait_for_timeout(300)
            page.locator('#airLaunchA').click()
            checks['secondQueueCancelOnly'] = page.evaluate('__HELO__.snapshot().queue.length===1&&__HELO__.snapshot().aircraft[0].state==="QUEUED"&&__HELO__.snapshot().aircraft[1].state==="HANGARED"')
            page.evaluate('__NAVAL_SIM_DIAG__.stepTicks(1500)')
            page.locator('#airHeloA0').click()
            checks['activeLaunchDisabled'] = page.locator('#airLaunchA').is_disabled()
            checks['livePhaseStatus'] = '갑판 이동' in page.locator('#airHeloA0').inner_text()
            checks['cameraVisibleAircraftEnabled'] = not page.locator('#external3DHeloB0').is_disabled()
            page.evaluate('__NAVAL_SIM_DIAG__.stepTicks(8500)')
            page.wait_for_timeout(300)
            capture = r"""()=>new Promise(resolve=>{const context=document.getElementById('c').getContext('2d'),calls=[],old=context.arc;context.arc=function(...a){calls.push({radius:a[2],dash:this.getLineDash(),alpha:this.globalAlpha});return old.apply(this,a);};requestAnimationFrame(()=>requestAnimationFrame(()=>{context.arc=old;resolve(calls);}));})"""
            circle_before = page.evaluate('JSON.stringify(__HELO__.snapshot())')
            circle = page.evaluate(capture)
            h = page.evaluate('__HELO__.snapshot().aircraft[0]')
            expected_radius = h['sensorsE']['radar']['horizonM'] * world_per_m
            checks['selectedAirborneHorizonCircle'] = not h['onboard'] and any(abs(c['radius']-expected_radius) < 1e-6 and c['dash'] for c in circle)
            checks['mapDrawReadOnly'] = circle_before == page.evaluate('JSON.stringify(__HELO__.snapshot())')
            page.locator('#airHeloA1').click()
            no_circle = page.evaluate(capture)
            checks['noDeckAircraftHorizonCircle'] = not any(abs(c['radius']-expected_radius) < 1e-6 for c in no_circle)
            checks['corePass'] = page.evaluate('__CORE_SELFTEST_FAILURES__.length===0')
            page.screenshot(path=str(a.out / f'air-{width}.png'))
            rows.append({'viewport': [width, height], 'layout': layout, 'checks': checks})
            page.close()
        browser.close()
    out = {'pass': not errors and all(all(r['checks'].values()) for r in rows), 'cases': rows,
           'errors': errors, 'htmlSha256': hashlib.sha256(a.html.read_bytes()).hexdigest()}
    (a.out / 'ui.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'pass': out['pass'], 'checks': sum(len(r['checks']) for r in rows),
                      'failed': [str(r['viewport'][0])+':'+k for r in rows for k,v in r['checks'].items() if not v], 'errors': errors}))
    raise SystemExit(0 if out['pass'] else 1)


if __name__ == '__main__':
    main()

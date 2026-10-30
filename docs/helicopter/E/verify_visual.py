"""Native Three/SwiftShader proof of the read-only helicopter radar overlay.

The overlay receives detached production render snapshots. Synthetic phase/range
samples never write authoritative flight, radar, IFF, link, or track state.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'docs/multiship/G'))
from browser_g import launch, load_fleet

SYNC = '''()=>{const v=__WIP148_3D_VIEW__;v.syncShipFittings(get3DRenderState());v.syncCamera();v.renderer.render(v.scene,v.camera);}'''
PROBE = r'''()=>{
 const view=__WIP148_3D_VIEW__,r=view.heloRadarResourcesE,state=get3DRenderState().helicopters,T=view.THREE;
 return {flag:view.heloRadarVisibleE,geometryCount:r.geometries.length,materialCount:r.materials.length,
 rows:state.aircraft.map(h=>{const v=r.visuals.get(h.id),end=new T.Vector3(1,0,0).multiply(v.axis.scale).applyEuler(v.axis.rotation).add(v.root.position);return {id:h.id,onboard:h.onboard,emitting:h.radar.emitting,visible:v.root.visible,position:v.root.position.toArray(),hposition:h.positionM,range:Math.min(h.radar.horizonM,h.radar.maxRangeM),scale:v.ring.scale.x,azimuthRad:h.radar.azimuthRad,rotation:v.axis.rotation.y,end:end.toArray(),shared:v.ring.geometry===r.geometries[0]&&v.axis.geometry===r.geometries[1],readonly:v.root.userData.presentationOnly===true&&v.root.userData.physicsFeedback===false};})};
}'''


def main():
    p = argparse.ArgumentParser()
    p.add_argument('html', type=Path)
    p.add_argument('out', type=Path)
    a = p.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    checks, records, errors = {}, {}, []
    with sync_playwright() as pw:
        browser = launch(pw, True)
        page = load_fleet(browser, a.html.read_bytes(), own='DDG_119_LATE_FLIGHT_IIA', ally=None, enemy=None,
                          width=1100, height=760, errors=errors)
        # Complete actual preparation with radars OFF; this renderer suite only
        # needs live emission after departure. RF endurance belongs to B/C gates.
        page.evaluate("()=>{for(const h of __HELO__.snapshot().aircraft)__HELO__.command(h.id,'LAUNCH');__NAVAL_SIM_DIAG__.stepTicks(16000);for(const h of __HELO__.snapshot().aircraft)__HELO__.command(h.id,'SET_RADAR',{enabled:true});__NAVAL_SIM_DIAG__.stepTicks(1);}")
        page.evaluate("async()=>{const v=__WIP148_3D_VIEW__;await v.open();v.c12ApplyPreset('LOW');}")
        page.wait_for_function('__WIP148_3D_VIEW__.heloVisualsA.size===2', timeout=90000)
        page.evaluate(SYNC)
        checks['defaultVisualizationOff'] = page.evaluate('__WIP148_3D_VIEW__.heloRadarVisibleE===false&&__WIP148_3D_VIEW__.heloRadarResourcesE===null')
        page.locator('#c14ControlsToggle').click()
        page.locator('#c15SensorsCategory').click()
        before = page.evaluate('JSON.stringify(__HELO__.snapshot())')
        page.locator('#external3DHeloRadarE').click()
        page.evaluate(SYNC)
        checks['sensorsMenuToggleReadOnly'] = before == page.evaluate('JSON.stringify(__HELO__.snapshot())')
        checks['sensorsMenuPressed'] = page.locator('#external3DHeloRadarE').get_attribute('aria-pressed') == 'true'
        records['production'] = probe = page.evaluate(PROBE)
        checks['bothAirborneEmittingRadarsVisible'] = len(probe['rows']) == 2 and all(not r['onboard'] and r['emitting'] and r['visible'] for r in probe['rows'])
        checks['twoSharedGeometriesFourReusedMaterials'] = probe['geometryCount'] == 2 and probe['materialCount'] == 4 and all(r['shared'] for r in probe['rows'])
        checks['overlayCarriesPresentationOnlyFlags'] = all(r['readonly'] for r in probe['rows'])
        checks['horizonRangeAndAuthoritativeBearing'] = all(abs(r['range']-r['scale']) < 1e-6 and abs(r['rotation']+r['azimuthRad']) < 1e-9 for r in probe['rows'])
        checks['overlayUsesWorldPositionAndSeaPlane'] = all(abs(r['position'][0]-r['hposition']['x']) < 1e-8 and abs(r['position'][2]-r['hposition']['y']) < 1e-8 and abs(r['position'][1]-1) < 1e-9 and abs(r['end'][1]-1) < 1e-9 for r in probe['rows'])
        page.evaluate('''()=>{const v=__WIP148_3D_VIEW__;v._heloRadarGeoReferencesE=[...v.heloRadarResourcesE.geometries];v._heloRadarMaterialReferencesE=[...v.heloRadarResourcesE.materials];}''')
        before = page.evaluate('JSON.stringify(__HELO__.snapshot())')
        records['detachedPhases'] = page.evaluate('''()=>{const v=__WIP148_3D_VIEW__,s=get3DRenderState(),rows=[];for(const angle of [0,Math.PI/2,Math.PI,Math.PI*1.5]){const st=structuredClone(s);for(const h of st.helicopters.aircraft){h.radar.azimuthRad=angle;h.radar.horizonM=20000;h.radar.maxRangeM=10000;}v.syncShipFittings(st);rows.push([...v.heloRadarResourcesE.visuals.values()].every(r=>Math.abs(r.axis.rotation.y+angle)<1e-9&&r.ring.scale.x===10000));}v.syncShipFittings(s);return rows;}''')
        checks['detachedPhaseAndRangeSamplesReadOnly'] = all(records['detachedPhases']) and before == page.evaluate('JSON.stringify(__HELO__.snapshot())')
        checks['frameUpdatesReuseSameResources'] = page.evaluate('''()=>{const v=__WIP148_3D_VIEW__,r=v.heloRadarResourcesE;return r.geometries.every((g,i)=>g===v._heloRadarGeoReferencesE[i])&&r.materials.every((m,i)=>m===v._heloRadarMaterialReferencesE[i]);}''')
        page.wait_for_timeout(300)
        page.locator('#external3DHeloRadarE').click()
        page.evaluate(SYNC)
        checks['toggleOffHidesBothWithoutDisposal'] = page.evaluate('''()=>{const v=__WIP148_3D_VIEW__,r=v.heloRadarResourcesE;return [...r.visuals.values()].every(r=>!r.root.visible)&&r.geometries.every((g,i)=>g===v._heloRadarGeoReferencesE[i]);}''')
        checks['toggleOffReadOnly'] = before == page.evaluate('JSON.stringify(__HELO__.snapshot())')
        page.wait_for_timeout(300)
        page.locator('#external3DHeloRadarE').click()
        page.evaluate(SYNC)
        page.evaluate("()=>{const h=__HELO__.snapshot().aircraft[0];__HELO__.command(h.id,'SET_RADAR',{enabled:false});__NAVAL_SIM_DIAG__.stepTicks(1);}")
        page.evaluate(SYNC)
        records['oneOff'] = page.evaluate(PROBE)
        checks['radarOffHidesOnlySelectedEmitter'] = not records['oneOff']['rows'][0]['visible'] and records['oneOff']['rows'][1]['visible']
        page.evaluate("()=>{const h=__HELO__.snapshot().aircraft[0];__HELO__.command(h.id,'SET_RADAR',{enabled:true});__NAVAL_SIM_DIAG__.stepTicks(1);}")
        page.evaluate(SYNC)
        page.evaluate('''()=>{const v=__WIP148_3D_VIEW__;v.heloFocusA=__HELO__.snapshot().aircraft[0].id;v.orbit.yaw=.5;v.orbit.pitch=.9;v.orbit.distance=80000;v.syncCamera();v.renderer.render(v.scene,v.camera);}''')
        page.screenshot(path=str(a.out / 'radar-horizons.png'))
        checks['webglNoError'] = page.evaluate('__WIP148_3D_VIEW__.renderer.getContext().getError()===0')
        page.evaluate('''()=>{const v=__WIP148_3D_VIEW__;window.__heloRadarDisposedE={geometry:0,material:0};for(const g of v.heloRadarResourcesE.geometries)g.addEventListener('dispose',()=>__heloRadarDisposedE.geometry++);for(const m of v.heloRadarResourcesE.materials)m.addEventListener('dispose',()=>__heloRadarDisposedE.material++);__NAVAL_SIM_DIAG__.resetEntireSessionV48Wip11A();const s=get3DRenderState();v.syncWorldEpochWip14A(s);v.syncShipFittings(s);}''')
        checks['resetDisposesSharedResourcesOnce'] = page.evaluate('__WIP148_3D_VIEW__.heloRadarResourcesE===null&&__heloRadarDisposedE.geometry===2&&__heloRadarDisposedE.material===4')
        checks['corePass'] = page.evaluate('__CORE_SELFTEST_FAILURES__.length===0')
        browser.close()
    out = {'pass': all(checks.values()) and not errors, 'checks': checks, 'records': records, 'errors': errors,
           'htmlSha256': hashlib.sha256(a.html.read_bytes()).hexdigest(),
           'limits': 'Native Three/SwiftShader; actual UI events and fixed ticks. Does not measure hardware FPS.'}
    (a.out / 'visual.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'pass': out['pass'], 'checks': len(checks), 'failed': [k for k,v in checks.items() if not v], 'errors': errors}))
    raise SystemExit(0 if out['pass'] else 1)


if __name__ == '__main__':
    main()

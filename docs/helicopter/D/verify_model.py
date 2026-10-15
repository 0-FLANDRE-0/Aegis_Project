"""Native renderer proof for the aft-wheel fix, ground pose, rotors and CAMERA.

All synthetic angle/phase probes change detached render snapshots only. The
actual preparation/departure cases use the production fixed-step simulation.
"""
import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'docs/multiship/G'))
from browser_g import launch, load_fleet

_spec = importlib.util.spec_from_file_location('historical_helo_b_native', ROOT / 'docs/helicopter/C/verify_native.py')
_historical = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_historical)
RIG_FIXTURE, DOORS = _historical.RIG_FIXTURE, _historical.DOORS

SYNC = '''()=>{const v=__WIP148_3D_VIEW__;v.syncShipFittings(get3DRenderState());v.syncCamera();v.renderer.render(v.scene,v.camera);}'''
GEAR = r'''()=>{
 const v=__WIP148_3D_VIEW__,h=get3DRenderState().helicopters.aircraft[0],row=v.heloVisualsA.get(h.id),visible=o=>{for(let p=o;p;p=p.parent)if(!p.visible)return false;return true;},rubber={extended:0,alternate:0};
 row.root.traverse(m=>{if(!m.isMesh||!visible(m))return;if(m.geometry===v.heloLeaseA.geometries[20][0])rubber.extended++;if(m.geometry===v.heloLeaseA.geometries[22][0])rubber.alternate++;});
 return {rubber,parts:Object.fromEntries([12684,12689,12704,12708,12712,12715,12719,12722,12727].map(id=>[id,row.instance.parts.get(id).visible])),state:h.state,onboard:h.onboard};
}'''
GEAR_PHASES = r'''()=>{
 const v=__WIP148_3D_VIEW__,s=get3DRenderState(),before=JSON.stringify(__HELO__.snapshot()),records=[];
 for(const state of ['HANGAR_OPEN','TRAVERSE','SPREAD','START','PRE_LAUNCH_CHECK','LIFT_HOVER','DEPART','TRANSIT','ARRIVED_HOVER','FOLLOW_SHIP']){
  const st=structuredClone(s),h=st.helicopters.aircraft[0];h.state=state;h.onboard=!['DEPART','TRANSIT','ARRIVED_HOVER','FOLLOW_SHIP'].includes(state);v.syncShipFittings(st);
  const row=v.heloVisualsA.get(h.id),visible=o=>{for(let p=o;p;p=p.parent)if(!p.visible)return false;return true;},rubber={extended:0,alternate:0};
  row.root.traverse(m=>{if(!m.isMesh||!visible(m))return;if(m.geometry===v.heloLeaseA.geometries[20][0])rubber.extended++;if(m.geometry===v.heloLeaseA.geometries[22][0])rubber.alternate++;});
  records.push({state,moving:state==='LIFT_HOVER'||!h.onboard,rubber,parts:Object.fromEntries([12684,12689,12704,12708,12712,12715,12719,12722,12727].map(id=>[id,row.instance.parts.get(id).visible]))});
 }
 v.syncShipFittings(s);return {records,noSimWrites:before===JSON.stringify(__HELO__.snapshot())};
}'''
GROUND_POSE = r'''()=>{
 const v=__WIP148_3D_VIEW__,T=v.THREE,h=get3DRenderState().helicopters.aircraft[0],row=v.heloVisualsA.get(h.id),expected=v.shipRoot.matrix.clone().multiply(new T.Matrix4().makeTranslation(h.localM.x,h.localM.z,h.localM.y)).multiply(new T.Matrix4().makeRotationY(-h.localYawRad)).multiply(new T.Matrix4().makeRotationZ(-h.pitchRad)).multiply(new T.Matrix4().makeRotationX(-h.bankRad));
 return {state:h.state,localM:h.localM,pitchRad:h.pitchRad,bankRad:h.bankRad,localYawRad:h.localYawRad,maximumMatrixError:Math.max(...expected.elements.map((x,i)=>Math.abs(x-row.root.matrix.elements[i]))),matrixAutoUpdate:row.root.matrixAutoUpdate};
}'''


def open_native(page):
    page.evaluate('''async()=>{const v=__WIP148_3D_VIEW__;await v.open();v.c12ApplyPreset('LOW');}''')
    page.wait_for_function('__WIP148_3D_VIEW__.heloVisualsA.size>=1', timeout=90000)
    page.evaluate(SYNC)


def camera_track(page, slot):
    button = page.locator('#external3DHeloB' + str(slot))
    if not button.is_visible():
        if not page.locator('#c15CameraCategory').is_visible():
            page.locator('#c14ControlsToggle').click()
        page.locator('#c15CameraCategory').click()
    button.click()
    page.wait_for_function('slot=>__WIP148_3D_VIEW__.heloFocusA===__HELO__.snapshot().aircraft[slot].id', arg=slot)
    page.evaluate(SYNC)


def side_view(page):
    page.evaluate('''()=>{const v=__WIP148_3D_VIEW__;v.orbit.yaw=0;v.orbit.pitch=0;v.orbit.distance=15;v.syncCamera();v.renderer.render(v.scene,v.camera);}''')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('html', type=Path)
    p.add_argument('out', type=Path)
    p.add_argument('--baseline', type=Path, default=ROOT / 'archive/v48/WIP_HELI_B/Aegis_SIM_v48_WIP_HELI_B.html')
    a = p.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    errors, checks, records = [], {}, {}
    with sync_playwright() as pw:
        browser = launch(pw, True)
        page = load_fleet(browser, a.baseline.read_bytes(), own='DDG_119_LATE_FLIGHT_IIA', ally=None, enemy=None,
                          width=900, height=650, errors=errors)
        page.evaluate("()=>{__HELO__.command(__HELO__.snapshot().aircraft[0].id,'LAUNCH');__NAVAL_SIM_DIAG__.stepTicks(7800);}")
        open_native(page)
        camera_track(page, 0)
        records['baselineAirborneGear'] = page.evaluate(GEAR)
        checks['baselineReproducesTwoRearRubberWheels'] = records['baselineAirborneGear']['rubber'] == {'extended': 1, 'alternate': 1}
        side_view(page)
        page.screenshot(path=str(a.out / 'rear-wheel-before.png'))
        page.close()

        page = load_fleet(browser, a.html.read_bytes(), own='DDG_119_LATE_FLIGHT_IIA', ally=None, enemy=None,
                          width=900, height=650, errors=errors)
        page.evaluate("()=>{for(const h of __HELO__.snapshot().aircraft)__HELO__.command(h.id,'LAUNCH');__NAVAL_SIM_DIAG__.stepTicks(600);}")
        open_native(page)
        before_camera = page.evaluate('JSON.stringify(__HELO__.snapshot())')
        camera_track(page, 0)
        checks['cameraMenuTracksFirstWithoutSimWrites'] = before_camera == page.evaluate('JSON.stringify(__HELO__.snapshot())')
        checks['cameraInitialDistance42m'] = page.evaluate('__WIP148_3D_VIEW__.orbit.distance===42')
        checks['airViewButtonsRemovedCameraEntriesRetained'] = all(page.locator('#' + key).count() == 0 for key in ['airViewA', 'airShipViewA']) and all(page.locator('#external3DHeloB' + str(i)).count() == 1 for i in [0, 1])
        records['portDoor'] = page.evaluate(DOORS, 0)
        checks['portPortalHasNoSolidWall'] = not records['portDoor']['blockers']
        records['gearPhases'] = page.evaluate(GEAR_PHASES)
        checks['oneRearRubberWheelAcrossTenRenderPhases'] = all(r['rubber'] == {'extended': 1, 'alternate': 0} for r in records['gearPhases']['records'])
        checks['completeGroundAirGearExclusivity'] = all(
            all(r['parts'][str(i)] == (not r['moving']) for i in [12684, 12689, 12712])
            and all(r['parts'][str(i)] == r['moving'] for i in [12722, 12727, 12719])
            and r['parts']['12704'] and not r['parts']['12708'] and not r['parts']['12715']
            for r in records['gearPhases']['records'])
        checks['phaseVisibilityProbesReadOnly'] = records['gearPhases']['noSimWrites']
        page.evaluate('''()=>{const v=__WIP148_3D_VIEW__;v.orbit.yaw=Math.PI/2;v.orbit.pitch=.1;v.orbit.distance=32;v.syncCamera();v.renderer.render(v.scene,v.camera);}''')
        page.screenshot(path=str(a.out / 'port-open.png'))
        page.evaluate('__NAVAL_SIM_DIAG__.stepTicks(960)')
        page.evaluate(SYNC)
        records['traverseGroundPose'] = page.evaluate(GROUND_POSE)
        gp = records['traverseGroundPose']
        checks['actualTraverseUsesDeckHeightAndTilt'] = gp['state'] == 'TRAVERSE' and gp['localM']['z'] > 3.3 and abs(gp['pitchRad']) > .01 and gp['maximumMatrixError'] < 1e-10 and not gp['matrixAutoUpdate']
        page.screenshot(path=str(a.out / 'exit-turn.png'))
        page.evaluate('__NAVAL_SIM_DIAG__.stepTicks(2040)')
        page.evaluate(SYNC)
        records['rig'] = page.evaluate(RIG_FIXTURE)
        checks.update(records['rig']['checks'])
        page.evaluate('__NAVAL_SIM_DIAG__.stepTicks(3450)')
        page.evaluate(SYNC)
        records['actualLiftGear'] = page.evaluate(GEAR)
        records['actualLiftPose'] = page.evaluate(GROUND_POSE)
        checks['actualLiftHasOneRearWheel'] = records['actualLiftGear']['state'] == 'LIFT_HOVER' and records['actualLiftGear']['rubber'] == {'extended': 1, 'alternate': 0}
        checks['liftRetainsReadOnlyShipAttachmentAndAttitude'] = records['actualLiftPose']['maximumMatrixError'] < 1e-10 and not records['actualLiftPose']['matrixAutoUpdate']
        page.evaluate('__NAVAL_SIM_DIAG__.stepTicks(750)')
        page.evaluate(SYNC)
        records['actualAirborneGear'] = page.evaluate(GEAR)
        checks['actualAirborneHasOneRearWheel'] = not records['actualAirborneGear']['onboard'] and records['actualAirborneGear']['rubber'] == {'extended': 1, 'alternate': 0}
        side_view(page)
        page.screenshot(path=str(a.out / 'rear-wheel-after.png'))
        page.evaluate('__NAVAL_SIM_DIAG__.stepTicks(1000)')
        page.wait_for_function('__WIP148_3D_VIEW__.heloVisualsA.size===2', timeout=90000)
        page.evaluate(SYNC)
        before_camera = page.evaluate('JSON.stringify(__HELO__.snapshot())')
        camera_track(page, 1)
        checks['cameraMenuTracksSecondWithoutSimWrites'] = before_camera == page.evaluate('JSON.stringify(__HELO__.snapshot())')
        checks['cameraSecondDistance42m'] = page.evaluate('__WIP148_3D_VIEW__.orbit.distance===42')
        checks['bothAircraftShareOriginal77Geometries'] = page.evaluate('__WIP148_3D_VIEW__.heloVisualsA.size===2&&__WIP148_3D_VIEW__.heloLeaseA.geometries.length===77&&[...__WIP148_3D_VIEW__.heloVisualsA.values()].every(v=>v.instance.parts.get(12704).children[0].geometry===__WIP148_3D_VIEW__.heloLeaseA.geometries[18][0])')
        records['starboardDoor'] = page.evaluate(DOORS, 1)
        checks['starboardPortalHasNoSolidWall'] = not records['starboardDoor']['blockers']
        records['doorModification'] = page.evaluate('''()=>{const d=__WIP148_3D_VIEW__.heloDoorsA;return {changedMeshes:d.changedMeshes,removedPolygons:d.removedPolygons,relocatedStairTriangles:d.relocatedStairTriangles};}''')
        # The whole assembly has 48 triangles. The prototype regional capture
        # omitted four bottom faces entirely below its 2.5 m height filter.
        checks['sourceStairMovedAsComplete48TriangleAssembly'] = records['doorModification']['relocatedStairTriangles'] == 48
        page.screenshot(path=str(a.out / 'camera-second.png'))
        checks['geometryAttributesMatricesAndGlValid'] = page.evaluate('''()=>{const v=__WIP148_3D_VIEW__;let bad=0;v.shipRoot.traverse(o=>{if(!o.isMesh)return;const a=o.geometry.attributes;if(a.normal&&a.normal.count!==a.position.count)bad++;if(a.color&&a.color.count<a.position.count)bad++;});for(const m of v.heloVisualsA.values())m.root.traverse(o=>{if(!o.matrix.elements.every(Number.isFinite))bad++;});return !bad&&v.renderer.getContext().getError()===0;}''')
        page.evaluate('''()=>{__NAVAL_SIM_DIAG__.resetEntireSessionV48Wip11A();const v=__WIP148_3D_VIEW__,s=get3DRenderState();v.syncWorldEpochWip14A(s);v.syncShipFittings(s);}''')
        checks['resetRetiresAllAircraftLeaseAndRotorGeometry'] = page.evaluate('__WIP148_3D_VIEW__.heloVisualsA.size===0&&__WIP148_3D_VIEW__.heloLeaseA===null&&__WIP148_3D_VIEW__.heloRotorGeosB===null&&__WIP148_3D_VIEW__.heloFocusA===null')
        checks['corePass'] = page.evaluate('__CORE_SELFTEST_FAILURES__.length===0')
        page.close()
        browser.close()
    report = {'pass': all(checks.values()) and not errors, 'checks': checks, 'records': records, 'errors': errors,
              'htmlSha256': hashlib.sha256(a.html.read_bytes()).hexdigest(),
              'baselineSha256': hashlib.sha256(a.baseline.read_bytes()).hexdigest(),
              'testExpectationCorrected': {'prototypeCount': 44, 'completeAssemblyCount': 48,
                  'reason': 'The prototype regional capture excluded four bottom faces with all vertices below 2.5 m; the final complete-assembly selector includes them. Gameplay bytes were unchanged.'},
              'limits': 'Actual Chromium/Three.js/SwiftShader, not hardware FPS or a combat collision model. Detached render-only probes preserve simulation. Full source-triangle path clearance is a separate suite.'}
    (a.out / 'model.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'pass': report['pass'], 'checks': len(checks), 'failed': [k for k,v in checks.items() if not v], 'errors': errors}))
    raise SystemExit(0 if report['pass'] else 1)


if __name__ == '__main__':
    main()

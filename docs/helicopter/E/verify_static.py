"""Pinned packing/scope and anonymous-sensor boundaries, separately gateable A/B/C."""
import argparse
import base64
import gzip
import hashlib
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

from build import BASE_SHA, NEW, OLD, decoded, patch

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
# Only integration points may change. All other pre-existing function bodies,
# including complete physical damage, dynamics, missile guidance and releases,
# remain byte identical to the frozen HELI_C baseline.
INTEGRATION = {
    'observerClassifyC', 'navalCiwsSourcesD', 'createWeaponContextD',
    'c55SensorSweep', 'updateTrackOperationalStateA3',
    'physicalRfReflectorRegistryWip13A2', 'simulateFixedTick',
}
B_INTEGRATION = {'shipboardRadarEchoFieldWip13B13', 'surfaceTargetRcsM2Wip13A', 'installHeloRendererA'}
C_INTEGRATION = {'harpoonGateA', 'offboardSnapshotC', 'observerSnapshotC', 'observerAcceptPlotsC'}
AST_AUDIT = r'''
const fs=require('node:fs'),acorn=require('acorn');
function inspect(file){const s=fs.readFileSync(file,'utf8'),out={};
 function walk(n){if(!n||typeof n!=='object')return;
  if(n.type==='FunctionDeclaration')(out[n.id.name]??=[]).push(s.slice(n.start,n.end));
  for(const [k,v]of Object.entries(n)){if(['start','end'].includes(k))continue;
   if(Array.isArray(v))v.forEach(walk);else if(v&&typeof v==='object')walk(v);}}
 walk(acorn.parse(s,{ecmaVersion:2022}));return out;}
const b=inspect(process.argv[1]),c=inspect(process.argv[2]);
console.log(JSON.stringify({existingCount:Object.keys(b).length,
 changed:Object.keys(b).filter(n=>JSON.stringify(b[n])!==JSON.stringify(c[n])),
 removed:Object.keys(b).filter(n=>!(n in c)),
 added:Object.keys(c).filter(n=>!(n in b)),
 processors:Object.fromEntries(['heloIffStepE','heloRadarSurfaceMeasurementE','heloPublishRadarPlotsE'].filter(n=>c[n]).map(n=>[n,c[n]]))}));
'''


def main():
    p = argparse.ArgumentParser()
    p.add_argument('baseline', type=Path)
    p.add_argument('html', type=Path)
    p.add_argument('out', type=Path)
    p.add_argument('--phase', choices=['A', 'B', 'C'], default='C')
    a = p.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    b, c = a.baseline.read_text(), a.html.read_text()
    bm, cm = decoded(b), decoded(c)
    checks = {
        'baselinePinned': hashlib.sha256(b.encode()).hexdigest() == BASE_SHA,
        'mainRebuildExact': patch(bm, a.phase).replace(OLD, NEW) == cm,
    }
    records = lambda h: json.loads(re.search(r'const records=(\[.*?\]);', h, re.S)[1])
    checks['other13PackedAssetsExact'] = records(b)[:13] == records(c)[:13]
    env = os.environ.copy()
    env.setdefault('NODE_PATH', str(ROOT / 'docs/performance/F/node_modules'))
    with tempfile.TemporaryDirectory() as tmp:
        for i, row in enumerate(records(c)):
            z = base64.b64decode(re.search(r'data-c55-index="' + str(i) + r'">(.*?)</script>', c, re.S)[1])
            raw = gzip.decompress(z)
            checks[f'record{i}'] = len(raw) == row['rawBytes'] and len(z) == row['gzipBytes'] and hashlib.sha256(raw).hexdigest() == row['sha256']
            f = Path(tmp) / f'{i}.js'
            f.write_bytes(raw)
            checks[f'syntax{i}'] = subprocess.run(['node', '--check', str(f)], capture_output=True).returncode == 0
        for i, m in enumerate(re.finditer(r'<script\b([^>]*)>(.*?)</script>', c, re.S)):
            if 'application/octet-stream' in m[1] or not m[2].strip():
                continue
            f = Path(tmp) / f'loader{i}.js'
            f.write_text(m[2])
            checks[f'loader{i}'] = subprocess.run(['node', '--check', str(f)], capture_output=True).returncode == 0
        bf, cf = Path(tmp) / 'base.js', Path(tmp) / 'candidate.js'
        bf.write_text(bm)
        cf.write_text(cm)
        q = subprocess.run(['node', str(ROOT / 'docs/performance/F/verify_scope.cjs'), str(bf), str(cf)], capture_output=True, text=True, env=env)
        scope = json.loads(q.stdout)
        checks['scopeNoNewUnresolved'] = not scope['added']
        audit = json.loads(subprocess.check_output(['node', '-e', AST_AUDIT, str(bf), str(cf)], env=env))
        allowed = INTEGRATION | (B_INTEGRATION if a.phase != 'A' else set()) | (C_INTEGRATION if a.phase == 'C' else set())
        unexpected = [n for n in audit['changed'] if not n.startswith('helo') and n not in allowed]
        checks['allOtherExistingFunctionsUnchanged'] = not unexpected
        checks['noExistingFunctionsRemoved'] = not audit['removed']
        audit['unexpectedChanged'] = unexpected
    # Front ends may access physical truth. The receiver/track processors may
    # consume only anonymous measured reports and authenticated response bits.
    stage_a = (HERE / 'stage_a.js').read_text()
    receiver = '\n'.join(audit['processors']['heloIffStepE'])
    checks['iffAssociatesMeasurementsNotTruth'] = not re.search(r'\b(?:_truthObject|ownerEntityId|h\.id|rfId|_debugSourceId)\b', receiver)
    checks['physicalTruthStopsAtRfFrontEnd'] = '_truthObject:h' in stage_a and 'heloPhysicalReflectorsE' in stage_a
    checks['noAircraftAiPoolRegistration'] = not re.search(r'\btargetPool\s*\.\s*(?:push|unshift|splice)\s*\(', stage_a)
    modules = '\n'.join((HERE / f).read_text() for f in ['motion.js', 'runtime.js', 'ui.js'])
    code = re.sub(r'//[^\n]*', '', modules)
    checks['flightRuntimeNoTruthRegistrationOrWeaponRelease'] = not re.search(r'\b(?:targetPool|navalReflectorsC|weaponCommandD|fireSM2|simRandom)\b', code)
    render = (HERE / 'render.js').read_text()
    checks['renderReadOnly'] = not any(x in render for x in ['heloCommandA(', 'heloFixedStepA(', 'heloMoveA(', 'heloIffStepE(', 'heloRadarFixedStepE(', 'heloHawklinkBeforeObserversE(', 'heloSensorStateE(', 'heloRadarStateE(', 'configureOffboardSourceC(', 'ingestOffboardReportC('])
    checks['singleHeloPayload'] = c.count('id="helo-render-a1"') == 1
    ui = (HERE / 'ui.js').read_text()
    checks['airOldViewButtonsRemoved'] = not any(x in ui for x in ['airViewA', 'airShipViewA', 'airCancelA'])
    checks['cameraTrackingRetained'] = all(x in ui for x in ['external3DHeloB', 'heloFocusViewB'])
    checks['altitudeCommandRetained'] = 'SET_ALTITUDE' in ui and 'altitudeM' in ui
    if a.phase != 'A':
        stage_b = (HERE / 'stage_b.js').read_text()
        checks['surfaceRadarReusesUnifiedRfKernel'] = 'shipboardRadarEchoFieldWip13B13(' in stage_b
        checks['legacyShipAdapterNotCalledForHelicopter'] = 'spq9bSurfaceAttemptWip13B1(' not in stage_b
        processor='\n'.join(audit['processors'].get('heloRadarSurfaceMeasurementE', []))
        checks['surfaceProcessorUsesAnonymousEchoes'] = bool(processor) and not re.search(r'\b(?:_truthObject|rfId|_debugSourceId|targetId)\b', processor)
        checks['radarOnDefaultOff'] = 'iffOn:true,radarOn:false' in (HERE / 'runtime.js').read_text()
        checks['noAirDetectionMode'] = not re.search(r'domainEvidence\s*:\s*\{\s*air\s*:\s*(?:1|\.[5-9])', stage_b)
    if a.phase == 'C':
        stage_c = (HERE / 'stage_c.js').read_text()
        checks['nativeOffboardPortUsed'] = all(x in stage_c for x in ['configureOffboardSourceC(', 'ingestOffboardReportC(', 'AEGIS_OFFBOARD_PLOT_C_1'])
        checks['noTruthKeysInLinkModule'] = not re.search(r'\b(?:_truthObject|_truth|targetId|rfId|_debugSourceId)\b', re.sub(r'//[^\n]*', '', stage_c))
        checks['noLink16Export'] = not re.search(r'\b(?:ingestNetwork|networkPublish|sendLink16|exportNetwork)\w*\s*\(', stage_c)
    oldassets = {m[1]: m[2] for m in re.finditer(r'<script id="([^"]+)" type="application/octet-stream">(.*?)</script>', b, re.S)}
    newassets = {m[1]: m[2] for m in re.finditer(r'<script id="([^"]+)" type="application/octet-stream">(.*?)</script>', c, re.S)}
    checks['existingEmbeddedModelsExact'] = all(newassets.get(k) == v for k, v in oldassets.items())
    report = {'pass': all(checks.values()), 'phase': a.phase, 'checks': checks, 'scope': scope, 'functionAudit': audit,
              'htmlSha256': hashlib.sha256(c.encode()).hexdigest(), 'mainSha256': hashlib.sha256(cm.encode()).hexdigest()}
    (a.out / 'static.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'pass': report['pass'], 'phase': a.phase, 'checks': len(checks), 'failed': [k for k, v in checks.items() if not v], 'unexpectedChanged': unexpected}))
    raise SystemExit(0 if report['pass'] else 1)


if __name__ == '__main__':
    main()

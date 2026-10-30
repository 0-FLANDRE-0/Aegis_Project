"""Rebuild the one-block game patch and its detached native diagnostic copy."""
from pathlib import Path
import base64, difflib, gzip, hashlib, json, os, re, shutil, subprocess, tempfile

H = Path(__file__).resolve().parent
R = H.parents[3]
C = R / 'docs/envelope/C'
D = H / 'diagnostic'
D.mkdir(exist_ok=True)
NAME = 'Aegis_SIM_v48_WIP_KAPPA_PIP_LOS_A.html'
base = R / 'Aegis_SIM_v48_WIP_RANGE_RECOVERY_A.html'
if not base.exists():
    base = R / 'archive/v48/WIP_RANGE_RECOVERY_A' / base.name
raw = base.read_bytes()
assert hashlib.sha256(raw).hexdigest() == '9ee346084b0c1a32cf303127aae74517f11fed79305ce84678d85385a25bc826'
html = raw.decode()
main = gzip.decompress(base64.b64decode(re.search(r'data-c55-index="13">([^<]+)</script>', html)[1])).decode()
tag = '// ENV_C: RANGE_A aligned diagnostic-only source capsule.'
def live(s):
    a = s.index(tag); b = s.index('\n  completeShipStartup();', a)
    return s[:a] + s[b:]
before = live(main)
tool = H / 'kit/AEGIS_KAPPA_PIP_LOS_Source_Patch.mjs'
with tempfile.TemporaryDirectory(prefix='kappa-build-') as t:
    t = Path(t)
    patched = t / 'patched.js'
    receipt = json.loads(subprocess.check_output(['node', str(tool), str(base), str(patched)], text=True))
    assert receipt['changedBlocks'] == 2
    after = live(patched.read_text())
    (t / 'live.js').write_text(after)
    for name in ['extract.cjs', 'boundaries.json', 'suite.js']:
        shutil.copyfile(C / name, D / name)
    subprocess.run(['node', str(D / 'extract.cjs'), str(t / 'live.js')], check=True)
    # Independently prove that re-extraction equals the kit's one-function patch.
    old_copy = t / 'patched-copy.js'
    copy_receipt = json.loads(subprocess.check_output(['node', str(tool), str(C / 'native-engine.js'), str(old_copy)], text=True))
    assert copy_receipt['changedBlocks'] == 1 and old_copy.read_bytes() == (D / 'native-engine.js').read_bytes()
(D / 'current-native-engine.js').write_bytes((C / 'native-engine.js').read_bytes())
private = (C / 'private.js').read_text()
needle = 'syncIdealRf(m);updateMissile(m,SIM_FIXED_DT);'
assert private.count(needle) == 1
private = private.replace(needle, 'const previousKappaDebug=m._wip79Kappa;'+needle)
needle = 'kappaAz:k.az??null,'
assert private.count(needle) == 1
private = private.replace(needle, needle + "kappaFresh:m._wip79Kappa!==previousKappaDebug,configuredPolicy:String(m._wip79KappaTerminalPolicy??window.WIP79_KAPPA_TERMINAL_POLICY??'PIP_LOS'),kappaPolicy:k.policy??null,kappaTgoS:k.tgo??null,kappaTgoCapS:k.tgoCapS??null,kappaPipM:structuredClone(k.pip??null),kappaTargetPipM:structuredClone(k.targetPip??k.pip??null),kappaVFinalMps:structuredClone(k.vFinal??null),waypointB4:!!k.waypointB4,targetEstimateAltitudeM:st.posM?.z??null,heightAboveTargetEstimateM:st.posM?.z!=null?m.z-st.posM.z:null,")
(D / 'private.js').write_text(private)
old_table = json.loads((C / 'ENVELOPE_TABLE_C.json').read_text())
table = {'schema': 'AEGIS_KAPPA_A_UNMEASURED_ENVELOPE_1', 'provenance': 'UNMEASURED_CURRENT_GUIDANCE', 'profileHash': None, 'rows': [], 'measurementStatus': 'NO_NEW_RANGE_SWEEP', 'notice': '기존 ENV_C와 RECOVERY_A는 이전 종말 수평방향 계산의 결과이며 새 유도 코드의 사거리 측정값이 아니다.', 'historicalResults': [{'path': 'docs/envelope/C/ENVELOPE_TABLE_C.json', 'profileHash': old_table['profileHash'], 'status': 'HISTORICAL_PRE_KAPPA_PIP_LOS'}, {'path': 'docs/missile/range/RECOVERY_A/REPORT.md', 'htmlSha256': hashlib.sha256(raw).hexdigest(), 'status': 'HISTORICAL_PRE_KAPPA_PIP_LOS'}]}
(D / 'UNMEASURED_ENVELOPE.json').write_text(json.dumps(table, ensure_ascii=False, indent=2)+'\n')
generator = (C / 'generate.py').read_text().replace("'ENVELOPE_TABLE_C.json'", "'UNMEASURED_ENVELOPE.json'")
generator = generator.replace('// ENV_C: RANGE_A aligned diagnostic-only source capsule.', '// ENV_KAPPA_A: regenerated Kappa PIP-LOS native diagnostic capsule.')
needle = "return {provenance:'GAME_ENGINE_COMPUTED',currentProfileHash:current,"
assert generator.count(needle) == 1
generator = generator.replace(needle, "return {guidanceRevision:'KAPPA_PIP_LOS_A',envelopeMeasured:false,historicalResults:table.historicalResults,measurementNotice:table.notice,nativeCapsuleSynchronized:changedNativeFunctions.length===0,provenance:'GAME_ENGINE_COMPUTED',currentProfileHash:current,")
generator = generator.replace("\\nwindow.__ENV_C__=window.__ENV_A__;\\n'", "\\nwindow.__ENV_C__=window.__ENV_A__;\\nwindow.__ENV_KAPPA_A__=window.__ENV_A__;\\n'")
(D / 'generate.py').write_text(generator.rstrip()+'\n')
subprocess.run(['python', str(D / 'generate.py')], check=True)
source = after.replace('\n  completeShipStartup();', '\n'+(D / 'adapter.js').read_text()+'\n  completeShipStartup();', 1)
z = gzip.compress(source.encode(), 9, mtime=0)
m = re.search(r'data-c55-index="13">([^<]+)</script>', html)
html = html[:m.start(1)]+base64.b64encode(z).decode()+html[m.end(1):]
m = re.search(r'const records=(\[.*?\]);', html, re.S)
records = json.loads(m[1]); records[13].update(rawBytes=len(source.encode()), gzipBytes=len(z), sha256=hashlib.sha256(source.encode()).hexdigest())
html = html[:m.start(1)]+json.dumps(records, separators=(',', ':'))+html[m.end(1):]
html = html.replace('v48_WIP_RANGE_RECOVERY_A','v48_WIP_KAPPA_PIP_LOS_A').replace('V48_WIP_RANGE_RECOVERY_A','V48_WIP_KAPPA_PIP_LOS_A')
(R / NAME).write_text(html)
input_data = json.loads((R / 'docs/missile/range/RECOVERY_A/inputs-RECOVERY.json').read_text())
assert input_data['settings']['WIP81_KAPPA_TGO_CAP_S'] == 90 and input_data['settings']['WIP79_KAPPA_TERMINAL_POLICY'] == 'PIP_LOS'
(H / 'inputs.json').write_text(json.dumps({k:input_data[k] for k in ['data','settings']}, separators=(',', ':')))
(H / 'game-change.diff').write_text(''.join(difflib.unified_diff(before.splitlines(True), after.splitlines(True), fromfile='CURRENT/live-game.js', tofile='PATCHED/live-game.js', n=6)))
(H / 'diagnostic-telemetry.diff').write_text(''.join(difflib.unified_diff((C / 'private.js').read_text().splitlines(True), private.splitlines(True), fromfile='ENV_C/private.js', tofile='KAPPA_A/diagnostic/private.js', n=3)))
manifest = {'baselineCommit': subprocess.check_output(['git','rev-parse','origin/range-loft-recovery-a'], cwd=R, text=True).strip(), 'baselineHtmlSha256': hashlib.sha256(raw).hexdigest(), 'html': NAME, 'bytes': len(html.encode()), 'sha256': hashlib.sha256(html.encode()).hexdigest(), 'nativeChangedBlocks': 2, 'regeneratedNativeCopyExactKitPatch': True, 'newEnvelopeRows': 0, 'oldResultsHistorical': table['historicalResults'], 'sourcePatchReceipt': receipt, 'diagnosticPatchReceipt': copy_receipt}
(H / 'build.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
print(json.dumps(manifest))

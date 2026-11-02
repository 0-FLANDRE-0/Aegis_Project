"""Read final packed HTML and pin actual solver/finalizer bodies; no browser."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json

P = Path(__file__).resolve().parent
R = P.parents[3]
ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('--sha', required=True)
ap.add_argument('--shadow-sha', required=True)
args = ap.parse_args()
spec = importlib.util.spec_from_file_location('r4_native_original_unpacker', P.parent / 'B/build.py')
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)
sha = lambda raw: hashlib.sha256(raw).hexdigest()
module = (P / 'association.js').read_text()
manifest = json.loads((P / 'patches.json').read_text())
finalizer_patch = next(row for row in manifest['patches'] if row['label'] == 'STABLE_REACQUIRE_TASK_OWNERSHIP')['after']
assert sha(module.encode()) == '1abcb0863af7908931aa8a3f7c28cda37c10077f086eb903f387cefa7f1f86d7'
rows = []
for mode, name, pin in [('ACTIVE', 'Aegis_SIM_v48_WIP_TRACK_B_STABLE_D.html', args.sha),
                        ('SHADOW', 'Aegis_SIM_v48_WIP_TRACK_B_STABLE_D_SHADOW.html', args.shadow_sha)]:
    raw = (R / name).read_bytes()
    assert sha(raw) == pin
    main = build.unpack(raw)
    variant = module if mode == 'ACTIVE' else module.replace("const TRACK_B_STABILIZATION_MODE='ACTIVE';", "const TRACK_B_STABILIZATION_MODE='SHADOW';", 1)
    assert main.count(variant) == 1
    assert main.count(finalizer_patch) == 1
    begin, end = build.scope_span(main, {'function': 'spyFinalizeAcceptedTrackV31'})
    fragment = main[begin:end]
    assert finalizer_patch in fragment
    rows.append({'file': name, 'htmlSha256': pin, 'actualMainSha256': sha(main.encode()),
                 'actualModuleSha256': sha(variant.encode()), 'moduleOccurrences': 1, 'mode': mode,
                 'actualFinalizerScopedSha256': sha(fragment.encode()),
                 'finalizerScopeIncludesFollowingSameIndentStatements': True,
                 'finalizerPatchOccurrences': 1, 'actualFinalizerStartLine': main[:begin].count('\n') + 1})
value = {'schema': 'AEGIS_TRACK_B_R4_NATIVE_PRODUCT_RECEIPT_1', 'status': 'PASS',
         'moduleSha256': sha(module.encode()), 'finalizerPatchSha256': sha(finalizer_patch.encode()),
         'products': rows, 'browserRuns': 0, 'sourceChanged': False,
         'claim': 'Actual packed bodies only; separate build proofs cover mode inversion/scope. Fresh native execution is separate evidence.'}
(P / 'evidence').mkdir(exist_ok=True)
(P / 'evidence/RUNTIME_PRODUCT_RECEIPT.json').write_text(json.dumps(value, indent=2) + '\n')
print(json.dumps(value, indent=2))

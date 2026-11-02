"""Build a reversible R4 stabilization candidate on frozen TRACK-B ACTIVE.

--check-base and --aggregate never generate a game HTML. Root owns association.js
and patches.json (integration patches in the existing TRACK-B manifest schema).
This tool owns the materialized build-manifest.json and build/source proofs.
SHADOW preserves TRACK-B ACTIVE policy while evaluating the new solver in
diagnostics; it is not the original TRACK-B SHADOW implementation mode.
"""
from pathlib import Path
import argparse
import difflib
import hashlib
import importlib.util
import json
import re
import subprocess
import sys

sys.dont_write_bytecode = True
P = Path(__file__).resolve().parent
R = P.parents[3]
ORIGINAL = P.parent / 'B'
R1 = P.parent / 'B_stabilization'
R2 = P.parent / 'B_stabilization_r2'
R3 = P.parent / 'B_stabilization_r3'
STAGE_NAME = 'TRACK_B_STABILIZATION_R4'
BASE = R / 'Aegis_SIM_v48_WIP_TRACK_B.html'
PINS_SHA = '24041e9981762a68813c23ec9643e0cefe0bf01d0b7056cf19069d97e1b43db6'
R1_PINS_SHA = '7b2f5bac06edd6dc13573c3aa6706874b7124a8b8e35614bd8ea93b66c312a17'
R2_PINS_SHA = 'fa08577af50afe68dcac2302d2fb27f75c6a3952840fd9b75f81dbcca6296c1f'
R3_PINS_SHA = '1f126bac4a81fce9929f0233db6f3c4be16e45e963dbff7a3220c852867992d8'
CONTRACT_SHA = 'c04c1379bbe38c0ca15f00de914a4159784d2f48320de5a32ba735338cedc0c2'
MANIFEST_SCHEMA = 'AEGIS_TRACK_B_STABILIZATION_R4_BUILD_MANIFEST_1'
MODE_TOKEN = "const TRACK_B_STABILIZATION_MODE='ACTIVE';"
LEGACY_TOKEN = "const TRACK_B_IMPLEMENTATION_MODE='ACTIVE';"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def original_util():
    spec = importlib.util.spec_from_file_location('track_b_r4_frozen_build_util', ORIGINAL / 'build.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_r1():
    raw = (P / 'R1_SOURCE_PINS.json').read_bytes()
    if sha(raw) != R1_PINS_SHA:
        raise ValueError('R1_SOURCE_PIN_MANIFEST_CHANGED')
    pins = json.loads(raw)
    for relative, expected in pins['files'].items():
        if sha((R / relative).read_bytes()) != expected:
            raise ValueError('FROZEN_R1_IMPLEMENTATION_OR_PRODUCT_CHANGED: ' + relative)
    if sha((P / 'CHANGE_CONTRACT.json').read_bytes()) != CONTRACT_SHA:
        raise ValueError('R4_CHANGE_CONTRACT_CHANGED')
    return pins


def change_contract():
    verify_r1()
    return json.loads((P / 'CHANGE_CONTRACT.json').read_text())


def verify_r2():
    raw = (P / 'R2_SOURCE_PINS.json').read_bytes()
    if sha(raw) != R2_PINS_SHA:
        raise ValueError('R2_SOURCE_PIN_MANIFEST_CHANGED')
    pins = json.loads(raw)
    for relative, expected in pins['files'].items():
        if sha((R / relative).read_bytes()) != expected:
            raise ValueError('FROZEN_R2_IMPLEMENTATION_OR_PRODUCT_CHANGED: ' + relative)
    return pins


def verify_r3():
    raw = (P / 'R3_SOURCE_PINS.json').read_bytes()
    if sha(raw) != R3_PINS_SHA:
        raise ValueError('R3_SOURCE_PIN_MANIFEST_CHANGED')
    pins = json.loads(raw)
    for relative, expected in pins['files'].items():
        if sha((R / relative).read_bytes()) != expected:
            raise ValueError('FROZEN_R3_IMPLEMENTATION_OR_PRODUCT_CHANGED: ' + relative)
    return pins


def verify_baseline(write_proof=False):
    r1_pins = verify_r1()
    verify_r2()
    verify_r3()
    pins_raw = (P / 'BASELINE_PINS.json').read_bytes()
    if sha(pins_raw) != PINS_SHA:
        raise ValueError('BASELINE_PINS_CHANGED')
    pins = json.loads(pins_raw)
    for relative, expected in pins['files'].items():
        if sha((R / relative).read_bytes()) != expected:
            raise ValueError('FROZEN_ORIGINAL_CHANGED: ' + relative)
    util = original_util()
    raw = BASE.read_bytes()
    source = util.unpack(raw)
    if sha(source.encode()) != pins['baselineMainSha256']:
        raise ValueError('FROZEN_BASELINE_MAIN_CHANGED')
    old_module = (ORIGINAL / 'association.js').read_text()
    if source.count(old_module) != 1:
        raise ValueError('BASELINE_MODULE_NOT_UNIQUE_OR_NOT_SOURCE_EXACT')
    # This also pins gzip/packed metadata representation before deriving a file.
    if util.pack(raw, source) != raw:
        raise ValueError('BASELINE_PACK_ROUNDTRIP_NOT_BYTE_EXACT')
    proof = {**pins, 'stageName': STAGE_NAME, 'pinsFileSha256': PINS_SHA, 'verified': True,
             'r1SourcePinsSha256': R1_PINS_SHA, 'r1SourceCommit': r1_pins['sourceCommit'],
             'r2SourcePinsSha256': R2_PINS_SHA, 'r2ImplementationAndProductsByteExact': True,
             'r3SourcePinsSha256': R3_PINS_SHA, 'r3ImplementationAndProductsByteExact': True,
             'r1ImplementationAndProductsByteExact': True, 'r1EvidenceTreeFrozen': False,
             'originalAssociationOccurrenceCount': 1,
             'packedRoundTripByteExact': True, 'candidateGenerated': False}
    if write_proof:
        write_json(P / 'BASELINE_PROVENANCE.json', proof)
    return pins, util, raw, source


def names(source):
    return set(re.findall(r'^function ([A-Za-z_$][\w$]*)\(', source, re.M)) | set(
        re.findall(r'^(?:const|let|var) ([A-Za-z_$][\w$]*)\s*=', source, re.M))


def local_file(relative):
    path = (P / relative).resolve()
    if not path.is_relative_to(P.resolve()):
        raise ValueError('STAGE_INPUT_OUTSIDE_DIRECTORY: ' + str(relative))
    return path


def aggregate():
    pins, _, _, _ = verify_baseline()
    contract = change_contract()
    prior_build = json.loads((R3 / 'BUILD.json').read_text())
    integration_path = P / 'patches.json'
    integration_raw = integration_path.read_bytes()
    if sha(integration_raw) != contract['integrationPatchSha256']:
        raise ValueError('R4_INTEGRATION_CONTRACT_MISMATCH')
    integration = json.loads(integration_raw)
    if integration.get('schema') != 'AEGIS_TRACK_B_PATCH_MANIFEST_1' or not isinstance(integration.get('patches'), list):
        raise ValueError('Integration patches must use the original TRACK-B manifest schema')
    old_integration_raw = (R3 / 'patches.json').read_bytes()
    old_integration = json.loads(old_integration_raw)
    if sha(old_integration_raw) != contract['priorIntegrationPatchSha256'] or integration['patches'][:-1] != old_integration['patches']:
        raise ValueError('FROZEN_R3_INTEGRATION_ENTRIES_CHANGED')
    if integration['patches'][-1].get('scope', {}).get('function') != contract['additionalIntegrationFunction']:
        raise ValueError('UNAPPROVED_ADDITIONAL_INTEGRATION_FUNCTION')
    original = (ORIGINAL / 'association.js').read_text()
    module_raw = (P / 'association.js').read_bytes()
    module = module_raw.decode()
    if module.count(MODE_TOKEN) != 1 or module.count(LEGACY_TOKEN) != 1:
        raise ValueError('Expected one stabilization ACTIVE token and one unchanged legacy ACTIVE token')
    entries = [{'op': 'replace', 'label': 'TRACK_B_STABILIZATION_R4_ASSOCIATION_MODULE',
                'before': original, 'after': module, 'count': 1}]
    dependencies = [{'path': 'patches.json', 'sha256': sha(integration_raw)},
                    {'path': 'association.js', 'sha256': sha(module_raw)}]
    for entry in integration['patches']:
        item = dict(entry)
        if item.get('op') == 'module':
            relative = item['path']
            item['sha256'] = sha(local_file(relative).read_bytes())
            dependencies.append({'path': relative, 'sha256': item['sha256']})
        elif item.get('op', 'replace') != 'replace':
            raise ValueError('Only exact replace and module insert patches are supported')
        entries.append(item)
    allowed = {}
    for key in ('allowedChangedSymbols', 'allowedAddedSymbols', 'allowedProtectedAssociationChanges'):
        value = integration.get(key, [])
        if not isinstance(value, list) or any(not isinstance(v, str) for v in value):
            raise ValueError(key + ' must be a string list')
        allowed[key] = sorted(set(value))
    allowed['allowedChangedSymbols'] = sorted(set(allowed['allowedChangedSymbols']) | names(original))
    allowed['allowedAddedSymbols'] = sorted(set(allowed['allowedAddedSymbols']) | (names(module) - names(original)))
    module_audit = subprocess.run(['node', str(P / 'module_scope.cjs')], text=True, capture_output=True)
    if module_audit.returncode:
        raise ValueError('R3_TO_R4_MODULE_SCOPE_FAILED\n' + module_audit.stdout + module_audit.stderr)
    manifest = {'schema': MANIFEST_SCHEMA, 'stageName': STAGE_NAME,
                'baselineHtmlSha256': pins['files'][BASE.name],
                'baselineMainSha256': pins['baselineMainSha256'], 'legacyPolicy': 'TRACK_B_ACTIVE',
                'dependencies': dependencies, 'patches': entries, **allowed,
                'r1SourcePinsSha256': R1_PINS_SHA, 'changeContractSha256': CONTRACT_SHA,
                'r2SourcePinsSha256': R2_PINS_SHA,
                'r3SourcePinsSha256': R3_PINS_SHA,
                'r1AllowedChangedSymbols': sorted(set(prior_build['r1AllowedChangedSymbols']) | set(contract['allowedChangedSymbols'])),
                'r1AllowedAddedSymbols': prior_build['r1AllowedAddedSymbols'],
                'r2AllowedChangedSymbols': sorted(set(prior_build['r2AllowedChangedSymbols']) | set(contract['allowedChangedSymbols'])),
                'r2AllowedAddedSymbols': prior_build['r2AllowedAddedSymbols'],
                'r3AllowedChangedSymbols': contract['allowedChangedSymbols'],
                'r3AllowedAddedSymbols': contract['allowedAddedSymbols'],
                'testCandidate': True, 'releaseApproved': False}
    write_json(P / 'build-manifest.json', manifest)
    return manifest


def dependency_check(manifest):
    for record in manifest['dependencies']:
        if sha(local_file(record['path']).read_bytes()) != record['sha256']:
            raise ValueError('REVIEWED_STAGE_INPUT_CHANGED: ' + record['path'])


def packed_envelope(raw):
    """Retain every outer HTML/asset byte except main payload/record metadata."""
    match = re.search(rb'data-c55-index="13">([^<]+)', raw)
    masked = raw[:match.start(1)] + b'PACKED_MAIN_PAYLOAD' + raw[match.end(1):]
    metadata = re.search(rb'const records=(\[.*?\]);', masked, re.S)
    records = json.loads(metadata[1])
    records[13] = {'mainRecordOnly': True}
    return masked[:metadata.start(1)] + json.dumps(records, separators=(',', ':')).encode() + masked[metadata.end(1):]


def transform(source, manifest, mode, util):
    original = source
    changes, modules = [], []
    for index, patch in enumerate(manifest['patches']):
        old, new = patch.get('before'), patch.get('after')
        label = patch.get('label', 'patch-' + str(index + 1))
        if patch.get('op') == 'module':
            raw = local_file(patch['path']).read_bytes()
            if sha(raw) != patch['sha256']:
                raise ValueError('MODULE_CHANGED: ' + patch['path'])
            text = raw.decode()
            old = patch['anchor']
            placement = patch.get('placement', 'after')
            if placement not in ('before', 'after'):
                raise ValueError('Invalid module insertion placement')
            new = text + '\n' + old if placement == 'before' else old + '\n' + text
            modules.append({'path': patch['path'], 'sourceSha256': sha(raw), 'renderedSha256': sha(text.encode())})
        if index == 0:
            if label != 'TRACK_B_STABILIZATION_R4_ASSOCIATION_MODULE' or new.count(MODE_TOKEN) != 1:
                raise ValueError('FIRST_PATCH_MUST_REPLACE_PINNED_ASSOCIATION_MODULE')
            new = new.replace(MODE_TOKEN, f"const TRACK_B_STABILIZATION_MODE='{mode}';", 1)
            modules.append({'path': 'association.js', 'sourceSha256': sha(patch['after'].encode()),
                            'renderedSha256': sha(new.encode()), 'stabilizationMode': mode,
                            'legacyImplementationMode': 'ACTIVE'})
        count = patch.get('count', 1)
        if not isinstance(old, str) or not old or not isinstance(new, str) or new == old or not isinstance(count, int) or count < 1:
            raise ValueError('Every patch needs nonempty distinct before/after text and a positive count')
        scope = patch.get('scope')
        a, b = util.scope_span(source, scope)
        section = source[a:b]
        if section.count(old) != count:
            raise AssertionError((label, 'replacement count', section.count(old), count))
        updated = section.replace(old, new)
        source = source[:a] + updated + source[b:]
        change = {'label': label, 'op': patch.get('op', 'replace'), 'scope': scope,
                  'before': old, 'after': new, 'count': count}
        if scope:
            change.update(scopeBefore=section, scopeAfter=updated)
        changes.append(change)
    restored = source
    for change in reversed(changes):
        if change['scope']:
            a, b = util.scope_span(restored, change['scope'])
            if restored[a:b] != change['scopeAfter']:
                raise AssertionError((change['label'], 'inverse scope mismatch'))
            restored = restored[:a] + change['scopeBefore'] + restored[b:]
        else:
            if restored.count(change['after']) != change['count']:
                raise AssertionError((change['label'], 'inverse patch not unique'))
            restored = restored.replace(change['after'], change['before'])
    if restored != original:
        raise AssertionError('UNLISTED_MAIN_BYTES_CHANGED')
    return source, changes, modules


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-base', action='store_true')
    parser.add_argument('--aggregate', action='store_true')
    parser.add_argument('--mode', choices=['ACTIVE', 'SHADOW'], default='ACTIVE')
    args = parser.parse_args()
    pins, util, raw, before = verify_baseline(write_proof=True)
    if args.check_base:
        print(json.dumps({'verified': True, 'frozenFiles': len(pins['files']),
                          'baselineHtmlSha256': pins['files'][BASE.name], 'candidateGenerated': False}))
        return
    if args.aggregate:
        manifest = aggregate()
        print(json.dumps({'patches': len(manifest['patches']), 'manifest': 'build-manifest.json', 'candidateGenerated': False}))
        return
    manifest_raw = (P / 'build-manifest.json').read_bytes()
    manifest = json.loads(manifest_raw)
    if manifest.get('schema') != MANIFEST_SCHEMA or manifest.get('baselineMainSha256') != pins['baselineMainSha256']:
        raise ValueError('WRONG_REVIEWED_BUILD_MANIFEST')
    dependency_check(manifest)
    source, changes, modules = transform(before, manifest, args.mode, util)
    if source.count(LEGACY_TOKEN) != 1 or source.count(f"const TRACK_B_STABILIZATION_MODE='{args.mode}';") != 1:
        raise ValueError('AMBIGUOUS_OR_CHANGED_POLICY_MODE')
    out = util.pack(raw, source)
    if util.unpack(out) != source or util.pack(out, before) != raw:
        raise AssertionError('PACKED_HTML_INVERSE_NOT_BYTE_EXACT')
    if packed_envelope(out) != packed_envelope(raw):
        raise AssertionError('NON_MAIN_ASSET_OR_HTML_ENVELOPE_CHANGED')
    # Detect changes during compilation before writing either product or report.
    dependency_check(manifest)
    verify_baseline()
    output = R / ('Aegis_SIM_v48_WIP_TRACK_B_STABLE_D' + ('_SHADOW' if args.mode == 'SHADOW' else '') + '.html')
    suffix = '_SHADOW' if args.mode == 'SHADOW' else ''
    report = {'schema': 'AEGIS_TRACK_B_STABILIZATION_R4_BUILD_1', 'baselineCommit': pins['baselineCommit'],
              'stageName': STAGE_NAME, 'r1SourcePinsSha256': R1_PINS_SHA, 'changeContractSha256': CONTRACT_SHA,
              'r2SourcePinsSha256': R2_PINS_SHA,
              'r3SourcePinsSha256': R3_PINS_SHA,
              'baselineSha256': pins['files'][BASE.name], 'baselineMainSha256': pins['baselineMainSha256'],
              'manifestSha256': sha(manifest_raw), 'output': output.name,
              'implementationMode': args.mode, 'stabilizationMode': args.mode,
              'legacyImplementationMode': 'ACTIVE', 'legacyPolicy': 'TRACK_B_ACTIVE',
              'htmlSha256': sha(out), 'mainSha256': sha(source.encode()),
              'inverseByteExact': True, 'packedHtmlInverseByteExact': True,
              'frozenOriginalFiles': pins['files'], 'modules': modules, 'changes': changes,
              **{key: manifest[key] for key in ('allowedChangedSymbols', 'allowedAddedSymbols', 'allowedProtectedAssociationChanges')},
              'r1AllowedChangedSymbols': manifest['r1AllowedChangedSymbols'],
              'r1AllowedAddedSymbols': manifest['r1AllowedAddedSymbols'],
              'r2AllowedChangedSymbols': manifest['r2AllowedChangedSymbols'],
              'r2AllowedAddedSymbols': manifest['r2AllowedAddedSymbols'],
              'r3AllowedChangedSymbols': manifest['r3AllowedChangedSymbols'],
              'r3AllowedAddedSymbols': manifest['r3AllowedAddedSymbols'],
              'testCandidate': True, 'releaseApproved': False}
    output.write_bytes(out)
    write_json(P / ('BUILD' + suffix + '.json'), report)
    write_json(P / ('SOURCE_PROOF' + suffix + '.json'), {
        'schema': 'AEGIS_TRACK_B_STABILIZATION_R4_SOURCE_PROOF_1',
        'stageName': STAGE_NAME, 'r1SourcePinsSha256': R1_PINS_SHA,
        'r2SourcePinsSha256': R2_PINS_SHA,
        'r3SourcePinsSha256': R3_PINS_SHA,
        'baselineHtmlSha256': pins['files'][BASE.name], 'candidateHtmlSha256': sha(out),
        'baselineMainSha256': pins['baselineMainSha256'], 'candidateMainSha256': sha(source.encode()),
        'stabilizationMode': args.mode, 'legacyImplementationMode': 'ACTIVE',
        'manifestSha256': sha(manifest_raw), 'dependencies': manifest['dependencies'],
        'inverseMainBytesExact': True, 'inversePackedHtmlBytesExact': True,
        'nonMainEnvelopeByteExact': True, 'nonMainEnvelopeSha256': sha(packed_envelope(raw)),
        'packedScriptRecordChanged': 13,
        'patches': [{'label': change['label'], 'scope': change['scope'], 'count': change['count'],
                     'beforeSha256': sha(change['before'].encode()), 'afterSha256': sha(change['after'].encode())}
                    for change in changes],
        'originalInputsStillPinned': True, 'gameCodeExecuted': False, 'releaseApproved': False})
    (P / ('changes-shadow.diff' if suffix else 'changes.diff')).write_text(''.join(difflib.unified_diff(
        before.splitlines(True), source.splitlines(True), fromfile=BASE.name + '::main', tofile=output.name + '::main')))
    print(json.dumps({'output': output.name, 'stabilizationMode': args.mode, 'sha256': sha(out),
                      'patches': len(changes), 'inverseByteExact': True, 'packedHtmlInverseByteExact': True,
                      'testCandidate': True, 'releaseApproved': False}))


if __name__ == '__main__':
    main()

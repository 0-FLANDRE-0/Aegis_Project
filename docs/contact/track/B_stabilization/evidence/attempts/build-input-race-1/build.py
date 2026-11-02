"""Build a reversible stabilization candidate on frozen TRACK-B ACTIVE.

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
import sys

sys.dont_write_bytecode = True
P = Path(__file__).resolve().parent
R = P.parents[3]
ORIGINAL = P.parent / 'B'
BASE = R / 'Aegis_SIM_v48_WIP_TRACK_B.html'
PINS_SHA = '24041e9981762a68813c23ec9643e0cefe0bf01d0b7056cf19069d97e1b43db6'
MANIFEST_SCHEMA = 'AEGIS_TRACK_B_STABILIZATION_BUILD_MANIFEST_1'
MODE_TOKEN = "const TRACK_B_STABILIZATION_MODE='ACTIVE';"
LEGACY_TOKEN = "const TRACK_B_IMPLEMENTATION_MODE='ACTIVE';"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def original_util():
    spec = importlib.util.spec_from_file_location('track_b_frozen_build_util', ORIGINAL / 'build.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_baseline(write_proof=False):
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
    proof = {**pins, 'pinsFileSha256': PINS_SHA, 'verified': True,
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
    integration_path = P / 'patches.json'
    integration_raw = integration_path.read_bytes()
    integration = json.loads(integration_raw)
    if integration.get('schema') != 'AEGIS_TRACK_B_PATCH_MANIFEST_1' or not isinstance(integration.get('patches'), list):
        raise ValueError('Integration patches must use the original TRACK-B manifest schema')
    original = (ORIGINAL / 'association.js').read_text()
    module_raw = (P / 'association.js').read_bytes()
    module = module_raw.decode()
    if module.count(MODE_TOKEN) != 1 or module.count(LEGACY_TOKEN) != 1:
        raise ValueError('Expected one stabilization ACTIVE token and one unchanged legacy ACTIVE token')
    entries = [{'op': 'replace', 'label': 'TRACK_B_STABILIZATION_ASSOCIATION_MODULE',
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
    manifest = {'schema': MANIFEST_SCHEMA, 'baselineHtmlSha256': pins['files'][BASE.name],
                'baselineMainSha256': pins['baselineMainSha256'], 'legacyPolicy': 'TRACK_B_ACTIVE',
                'dependencies': dependencies, 'patches': entries, **allowed,
                'testCandidate': True, 'releaseApproved': False}
    write_json(P / 'build-manifest.json', manifest)
    return manifest


def dependency_check(manifest):
    for record in manifest['dependencies']:
        if sha(local_file(record['path']).read_bytes()) != record['sha256']:
            raise ValueError('REVIEWED_STAGE_INPUT_CHANGED: ' + record['path'])


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
            if label != 'TRACK_B_STABILIZATION_ASSOCIATION_MODULE' or new.count(MODE_TOKEN) != 1:
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
    # Detect changes during compilation before writing either product or report.
    dependency_check(manifest)
    verify_baseline()
    output = R / ('Aegis_SIM_v48_WIP_TRACK_B_STABLE_A' + ('_SHADOW' if args.mode == 'SHADOW' else '') + '.html')
    suffix = '_SHADOW' if args.mode == 'SHADOW' else ''
    report = {'schema': 'AEGIS_TRACK_B_STABILIZATION_BUILD_1', 'baselineCommit': pins['baselineCommit'],
              'baselineSha256': pins['files'][BASE.name], 'baselineMainSha256': pins['baselineMainSha256'],
              'manifestSha256': sha(manifest_raw), 'output': output.name,
              'implementationMode': args.mode, 'stabilizationMode': args.mode,
              'legacyImplementationMode': 'ACTIVE', 'legacyPolicy': 'TRACK_B_ACTIVE',
              'htmlSha256': sha(out), 'mainSha256': sha(source.encode()),
              'inverseByteExact': True, 'packedHtmlInverseByteExact': True,
              'frozenOriginalFiles': pins['files'], 'modules': modules, 'changes': changes,
              **{key: manifest[key] for key in ('allowedChangedSymbols', 'allowedAddedSymbols', 'allowedProtectedAssociationChanges')},
              'testCandidate': True, 'releaseApproved': False}
    output.write_bytes(out)
    write_json(P / ('BUILD' + suffix + '.json'), report)
    (P / ('changes-shadow.diff' if suffix else 'changes.diff')).write_text(''.join(difflib.unified_diff(
        before.splitlines(True), source.splitlines(True), fromfile=BASE.name + '::main', tofile=output.name + '::main')))
    print(json.dumps({'output': output.name, 'stabilizationMode': args.mode, 'sha256': sha(out),
                      'patches': len(changes), 'inverseByteExact': True, 'packedHtmlInverseByteExact': True,
                      'testCandidate': True, 'releaseApproved': False}))


if __name__ == '__main__':
    main()

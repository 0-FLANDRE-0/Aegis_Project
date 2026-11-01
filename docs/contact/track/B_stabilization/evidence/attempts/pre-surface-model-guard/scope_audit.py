"""Run the frozen TRACK-B AST scope gate with explicit stabilization paths.

No game code executes. Only IO/configuration lines in the original checker are
redirected; its symbol comparison and recursive kernel traversal are unchanged.
Each candidate is checked against both original B ACTIVE and TRACK-A. Detailed
proofs remain separate so a previously permitted B association change cannot
silently become permission to edit an RF/EKF or weapon kernel now.
"""
from pathlib import Path
import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
P = Path(__file__).resolve().parent
R = P.parents[3]


def build_util():
    spec = importlib.util.spec_from_file_location('track_b_stabilization_build', P / 'build.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def one_line(source, prefix, replacement):
    matches = [line for line in source.splitlines() if line.startswith(prefix)]
    if len(matches) != 1:
        raise ValueError('FROZEN_AUDIT_REDIRECTION_NOT_UNIQUE: ' + prefix)
    return source.replace(matches[0], replacement, 1)


def redirected_checker(source, root, mode, base, candidate, build_path, inherited, output, baseline_sha):
    quote = lambda value: json.dumps(str(value))
    redirects = [
        ('const root=', 'const root=' + quote(root) + ",hash=x=>crypto.createHash('sha256').update(x).digest('hex');"),
        ('const modeIndex=', 'const mode=' + quote(mode) + ';'),
        ('const base=', 'const base=' + quote(base) + ',candidate=' + quote(candidate) + ';'),
        ('const buildPath=', 'const buildPath=' + quote(build_path) + ';'),
        ("if(hash(fs.readFileSync(base))!==", "if(hash(fs.readFileSync(base))!==" + quote(baseline_sha) + ")throw Error('PINNED_AUDIT_BASE_CHANGED');"),
        ('const a=load(base)', 'const a=load(base),b=load(candidate),inherited=JSON.parse(fs.readFileSync(' + quote(inherited) + '));'),
        ('fs.writeFileSync(path.join(__dirname,', 'fs.writeFileSync(' + quote(output) + ",JSON.stringify(out,null,2)+'\\n');console.log(JSON.stringify({pass,mode,changed,added,protected:protectedSymbols.length,nestedProtected:nestedProtectedSymbols.length,forbiddenChanged,forbiddenAdded,invalidExceptions,addedNestedKernels}));if(!pass)process.exitCode=1;"),
    ]
    for prefix, replacement in redirects:
        source = one_line(source, prefix, replacement)
    return source


def run_audit(util, pins, report, mode, stage, node_path, prefix=''):
    original_checker = (util.ORIGINAL / 'check_scope.cjs').read_bytes()
    candidate = R / report['output']
    suffix = '_SHADOW' if mode == 'SHADOW' else ''
    output = P / (prefix + 'SCOPE_VS_' + stage + suffix + '.json')
    supplied = {key: report[key] for key in ('implementationMode', 'htmlSha256', 'inverseByteExact',
                'allowedChangedSymbols', 'allowedAddedSymbols', 'allowedProtectedAssociationChanges')}
    if stage == 'A':
        previous = json.loads((util.ORIGINAL / 'BUILD.json').read_text())
        for key in ('allowedChangedSymbols', 'allowedAddedSymbols', 'allowedProtectedAssociationChanges'):
            supplied[key] = sorted(set(supplied[key]) | set(previous[key]))
        baseline = R / 'Aegis_SIM_v48_WIP_TRACK_A.html'
    else:
        baseline = util.BASE
    report_file = P / (prefix + 'AUDIT_INPUT_VS_' + stage + suffix + '.json')
    util.write_json(report_file, supplied)
    code = redirected_checker(original_checker.decode(), R, mode, baseline, candidate,
                              report_file, P.parent / 'A/SCOPE.json', output,
                              pins['files'][baseline.name])
    checker_file = P / (prefix + 'AUDIT_VS_' + stage + suffix + '.cjs')
    checker_file.write_text(code)
    environment = os.environ.copy()
    if node_path:
        environment['NODE_PATH'] = node_path
    result = subprocess.run(['node', str(checker_file)], cwd=R, env=environment,
                            text=True, capture_output=True, timeout=240)
    if result.returncode or not output.is_file():
        raise RuntimeError('SCOPE_VS_' + stage + ' failed\n' + result.stdout + result.stderr)
    scope = json.loads(output.read_text())
    if not scope['pass'] or len(scope['protectedSymbols']) != 189 or len(scope['nestedProtectedSymbols']) != 161:
        raise AssertionError('PROTECTED_SCOPE_ROSTER_OR_RESULT_CHANGED: ' + stage)
    return output, scope, {
        'sourceCheckerSha256': util.sha(original_checker),
        'redirectedCheckerSha256': util.sha(code.encode()),
        'redirectedCheckerPath': checker_file.name,
        'auditInputPath': report_file.name,
        'auditInputSha256': util.sha(report_file.read_bytes()),
        'redirectsOnly': ['root', 'mode', 'base/candidate paths', 'build report path',
                         'baseline checksum', 'inherited roster path', 'output path'],
        'kernelTraversalAndSymbolComparisonUnchanged': True,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=['ACTIVE', 'SHADOW'], default='ACTIVE')
    parser.add_argument('--preflight', action='store_true', help='Audit original B as a tool check; no candidate is generated')
    parser.add_argument('--node-path', help='Explicit existing node_modules search path; no packages are installed')
    args = parser.parse_args()
    util = build_util()
    pins, _, _, _ = util.verify_baseline()
    suffix = '_SHADOW' if args.mode == 'SHADOW' else ''
    report_path = util.ORIGINAL / 'BUILD.json' if args.preflight else P / ('BUILD' + suffix + '.json')
    report = json.loads(report_path.read_text())
    if args.preflight and args.mode != 'ACTIVE':
        raise ValueError('Preflight uses original B ACTIVE only')
    if not args.preflight and (report['stabilizationMode'] != args.mode or report['legacyImplementationMode'] != 'ACTIVE'):
        raise ValueError('STABILIZATION_MODE_OR_LEGACY_POLICY_MISMATCH')
    if util.sha((R / report['output']).read_bytes()) != report['htmlSha256']:
        raise ValueError('CANDIDATE_BUILD_CHECKSUM_MISMATCH')
    if not args.preflight and util.sha((P / 'build-manifest.json').read_bytes()) != report['manifestSha256']:
        raise ValueError('CANDIDATE_MANIFEST_CHANGED')
    if not shutil.which('node'):
        raise RuntimeError('Node is required for the existing AST audit')
    node_path = args.node_path or os.environ.get('NODE_PATH')
    fallback = Path('/workspace/aegis-performance-c/docs/performance/C/node_modules')
    if not args.node_path and (fallback / 'acorn/package.json').is_file():
        node_path = os.pathsep.join(dict.fromkeys(filter(None, [node_path, str(fallback)])))
    details = {}
    for stage in ('B', 'A'):
        path, scope, proof = run_audit(util, pins, report, args.mode, stage, node_path,
                                     prefix='TOOL_PREFLIGHT_' if args.preflight else '')
        details['againstTrack' + stage] = {
            'path': path.name, 'sha256': util.sha(path.read_bytes()),
            'pass': scope['pass'], 'changed': scope['changed'], 'added': scope['added'],
            'protectedSymbols': len(scope['protectedSymbols']),
            'nestedProtectedSymbols': len(scope['nestedProtectedSymbols']), **proof,
        }
    util.verify_baseline()
    result = {'schema': 'AEGIS_TRACK_B_STABILIZATION_SCOPE_1', 'pass': True,
              'stabilizationMode': args.mode, 'legacyPolicy': 'TRACK_B_ACTIVE',
              'candidateHtmlSha256': report['htmlSha256'],
              'candidateMainSha256': report['mainSha256'],
              'baselineHtmlSha256': pins['files'][util.BASE.name],
              'originalInputsStillPinned': True, 'inverseByteExact': report['inverseByteExact'],
              'packedHtmlInverseByteExact': report.get('packedHtmlInverseByteExact', None),
              'toolPreflightOnly': args.preflight,
              'nodePath': node_path, 'gameCodeExecuted': False, **details}
    util.write_json(P / ('SCOPE_TOOL_PREFLIGHT.json' if args.preflight else 'SCOPE' + suffix + '.json'), result)
    print(json.dumps({key: result[key] for key in ['pass', 'stabilizationMode',
          'candidateHtmlSha256', 'originalInputsStillPinned', 'gameCodeExecuted']}))


if __name__ == '__main__':
    main()

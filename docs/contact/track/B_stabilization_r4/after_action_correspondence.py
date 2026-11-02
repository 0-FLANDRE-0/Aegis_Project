"""Offline descriptive correspondence audit; never a game input or identity oracle.

Read existing lossless battle captures only. No browser, RNG, simulation step,
product import, trajectory interpolation, assignment solver or tuned gate is used.
The nearest recorded initial-ASM reference is a geometric descriptor, NOT a
physical match. Physical ID swaps/duplicates/false merges remain UNKNOWN.
"""
from pathlib import Path
import argparse
import collections
import csv
import gzip
import hashlib
import importlib.util
import inspect
import json
import math

HERE = Path(__file__).resolve().parent
CODEC_PATH = HERE.parent / 'B_stabilization' / 'battle.py'
sha = lambda b: hashlib.sha256(b).hexdigest()


def finite(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def vector(v, size):
    return isinstance(v, list) and len(v) == size and all(finite(x) for x in v)


def xyz(v):
    return [v.get(k) for k in ('x', 'y', 'z')] if isinstance(v, dict) else [None]*3


def norm(v):
    return math.sqrt(sum(x*x for x in v))


def distribution(values):
    values = sorted(x for x in values if finite(x))
    if not values:
        return {'count': 0, 'minimum': None, 'median': None, 'maximum': None}
    n = len(values)
    return {'count': n, 'minimum': values[0],
            'median': (values[(n-1)//2]+values[n//2])/2, 'maximum': values[-1]}


def load_capture(path):
    raw = path.read_bytes()
    value = json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)
    spec = importlib.util.spec_from_file_location('existing_battle_export_codec', CODEC_PATH)
    codec = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(codec)  # main/browser imports are guarded in this module.
    envelope = {k: v for k, v in value.items() if k != 'jsonGzipBase64'} if value.get('captureTransport') else None
    capture = codec.decode_capture(value)
    receipt = capture.get('transportReceipt')
    if receipt:
        assert receipt['jsonStringifyExact'] is True
        assert receipt['originalJsonSha256'] == receipt['decodedJsonSha256']
        assert receipt['omittedRecords'] == receipt['omittedFields'] == 0
        assert receipt['nativeAssociationRecordCount'] == len(capture['associationReturns'])
        assert receipt['lineageRecordCount'] == len(capture['observedPlotLineage'])
    assert sha(path.read_bytes()) == sha(raw), 'Input changed during read-only audit'
    return capture, {'path': str(path), 'sha256': sha(raw), 'storedEnvelope': envelope,
                     'storedBrowserRoundTripReceipt': receipt,
                     'codecPath': str(CODEC_PATH), 'codecFileSha256': sha(CODEC_PATH.read_bytes()),
                     'decodeFunctionSha256': sha(inspect.getsource(codec.decode_capture).encode()),
                     'independentJavascriptStringifyReexecution': False}


def csv_write(path, rows, columns):
    with path.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=columns)
        w.writeheader()
        w.writerows(rows)


def analyze(capture, provenance):
    samples = capture['samples']
    assert all(a['step'] < b['step'] and a['timeS'] < b['timeS'] for a, b in zip(samples, samples[1:]))
    pairs, tracks, collisions, switches = [], [], [], []
    duplicate_ids = []
    previous, seen_ids, numbers = {}, set(), collections.defaultdict(set)
    no_state, no_truth, invalid_cov, unknown_alive = 0, 0, 0, 0
    separation, live_counts, per_sample = [], [], []
    for sample in samples:
        step, time_s = sample['step'], sample['timeS']
        ids_here = collections.Counter(t.get('trackId') for t in sample['tracks'])
        if any(n > 1 for n in ids_here.values()):
            duplicate_ids.append({'step': step, 'trackIds': [k for k,n in ids_here.items() if n > 1]})
        truth = [t for t in sample['truthAfterAction'] if t.get('alive') is True and vector(xyz(t.get('positionM')), 3)]
        unknown_alive += sum(t.get('alive') not in (True, False) for t in sample['truthAfterAction'])
        live_ids = sorted(t['id'] for t in truth)
        live_counts.append(len(truth))
        for i, a in enumerate(truth):
            for b in truth[i+1:]:
                separation.append(norm([x-y for x, y in zip(xyz(a['positionM']), xyz(b['positionM']))]))
        groups = collections.defaultdict(list)
        sample_nearest = []
        for tr in sample['tracks']:
            tid = tr.get('trackId')
            if tid is not None:
                seen_ids.add(tid)
                numbers[str(tid)].add(tr.get('trackNumber'))
            state, diag = tr.get('kf6'), tr.get('Pdiag')
            if not vector(state, 6):
                no_state += 1
                continue
            covariance_valid = vector(diag, 6) and all(x > 0 for x in diag)
            invalid_cov += not covariance_valid
            candidates = []
            for physical in truth:
                pos = xyz(physical['positionM'])
                vel = xyz(physical.get('velocityMps'))
                dx = [state[i]-pos[i] for i in range(3)]
                dv = [state[i+3]-vel[i] for i in range(3)] if vector(vel, 3) else None
                d = norm(dx)
                candidates.append((d, str(physical['id']), physical['id'], dx, dv))
                row = {'step': step, 'timeS': time_s, 'trackId': tid,
                       'initialAsmReferenceId': physical['id'], 'distance3dM': d,
                       'horizontalDistanceM': math.hypot(dx[0], dx[1]),
                       'dxM': dx[0], 'dyM': dx[1], 'dzM': dx[2],
                       'velocityResidualMps': norm(dv) if dv is not None else None,
                       'dvxMps': dv[0] if dv is not None else None,
                       'dvyMps': dv[1] if dv is not None else None,
                       'dvzMps': dv[2] if dv is not None else None}
                # Per-axis standardized residual only. No cross-covariance,
                # diagonal-NIS surrogate, probability or pass/fail gate.
                for i, name in enumerate(('x', 'y', 'z')):
                    row[name+'MarginalSigmaUnits'] = dx[i]/math.sqrt(diag[i]) if covariance_valid else None
                pairs.append(row)
            candidates.sort(key=lambda q: (q[0], q[1]))
            base = {k: tr.get(k) for k in ('trackId', 'trackNumber', 'confirmed', 'classification', 'identity', 'engagementAuthority', 'sensorSource', 'sensorAge', '_lastMeasurementStep')}
            base.update({'step': step, 'timeS': time_s, 'estimateEpochS': None,
                         'liveInitialAsmReferences': len(truth), 'covarianceDiagonalValid': covariance_valid,
                         'nearestInitialAsmReferenceId': candidates[0][2] if candidates else None,
                         'nearestDistance3dM': candidates[0][0] if candidates else None,
                         'runnerUpDistance3dM': candidates[1][0] if len(candidates) > 1 else None,
                         'nearestDistanceMarginM': candidates[1][0]-candidates[0][0] if len(candidates) > 1 else None,
                         'exactNearestTieCount': sum(c[0] == candidates[0][0] for c in candidates) if candidates else 0})
            tracks.append(base)
            if not candidates:
                no_truth += 1
                continue
            nearest = candidates[0][2]
            groups[nearest].append(base)
            sample_nearest.append(base)
            old = previous.get(tid)
            if old and old['nearestReferenceId'] != nearest:
                switches.append({'trackId': tid, 'fromSampleStep': old['step'], 'toSampleStep': step,
                                 'sampleGapS': time_s-old['timeS'], 'fromReferenceId': old['nearestReferenceId'],
                                 'toReferenceId': nearest, 'sameLiveReferenceSet': old['liveIds'] == live_ids,
                                 'oldReferenceStillAlive': old['nearestReferenceId'] in live_ids,
                                 'previousDistanceM': old['distanceM'], 'currentDistanceM': candidates[0][0],
                                 'interpretation': 'NEAREST_REFERENCE_CHANGE_NOT_PROVEN_ID_SWAP'})
            previous[tid] = {'step': step, 'timeS': time_s, 'nearestReferenceId': nearest,
                             'distanceM': candidates[0][0], 'liveIds': live_ids}
        for rid, group in groups.items():
            if len(group) > 1:
                collisions.append({'step': step, 'timeS': time_s, 'initialAsmReferenceId': rid,
                                   'trackIds': [t['trackId'] for t in group],
                                   'distancesM': [t['nearestDistance3dM'] for t in group],
                                   'interpretation': 'SHARED_NEAREST_REFERENCE_NOT_PROVEN_DUPLICATE'})
        per_sample.append({'step': step, 'timeS': time_s, 'recordedTracks': len(sample['tracks']),
                           'validEstimatedStates': len(sample_nearest), 'liveInitialAsmReferences': len(truth),
                           'sharedNearestReferenceGroups': sum(len(g)>1 for g in groups.values())})
    logical_bad = []
    for index, record in enumerate(capture.get('associationReturns', [])):
        selected = record.get('actualSelectedPairs', [])
        pp, tt = [p.get('i') for p in selected], [p.get('id') for p in selected]
        if len(pp) != len(set(pp)) or len(tt) != len(set(tt)):
            logical_bad.append({'recordIndex': index, 'step': record.get('step'), 'route': record.get('route'),
                                'duplicatePlotIndices': [x for x, n in collections.Counter(pp).items() if n > 1],
                                'duplicateTrackIds': [x for x, n in collections.Counter(tt).items() if n > 1]})
    receipt = capture.get('transportReceipt')
    summary = {
        'schema': 'AEGIS_AFTER_ACTION_GEOMETRIC_REFERENCE_AUDIT_1',
        'classification': 'AFTER_ACTION_TEST_ONLY_NO_GAME_CONSUMER',
        'source': provenance, 'case': capture.get('case'), 'traceMode': capture.get('traceMode'),
        'captureStatus': capture.get('status'), 'end': capture.get('end'),
        'samplerTag': 'OBSERVED_TRACKS_AND_AFTER_ACTION_TRUTH_SEPARATE',
        'sampleCount': len(samples), 'sampleGapS': distribution([b['timeS']-a['timeS'] for a,b in zip(samples,samples[1:])]),
        'trackSnapshotCount': sum(len(s['tracks']) for s in samples), 'distinctLogicalTrackIds': len(seen_ids),
        'finiteEstimatedStateRows': len(tracks), 'missingEstimatedStateRows': no_state,
        'invalidOrMissingCovarianceDiagonals': invalid_cov, 'unknownTruthAliveFlags': unknown_alive,
        'recordedTruthCoverage': 'INITIAL_ASMS_ONLY_NOT_ALL_WORLD_ENTITIES',
        'liveInitialAsmReferencesPerSnapshot': distribution(live_counts),
        'pairwiseLiveInitialAsmSeparationM': distribution(separation),
        'pairResidualRows': len(pairs), 'rowsWithoutLiveInitialAsmReference': no_truth,
        'nearestReferenceDistanceM': distribution([t['nearestDistance3dM'] for t in tracks]),
        'nearestReferenceDistanceMarginM': distribution([t['nearestDistanceMarginM'] for t in tracks]),
        'nearestReferenceChanges': len(switches),
        'nearestReferenceChangesWithSameLiveReferenceSet': sum(q['sameLiveReferenceSet'] for q in switches),
        'sharedNearestReferenceGroupAppearances': len(collisions),
        'logicalAssociationRecordsAudited': len(capture.get('associationReturns', [])),
        'logicalWithinReturnAuditStatus': 'OBSERVED_LOGGED_RETURNS_ONLY' if capture.get('associationReturns') else 'NOT_INSTRUMENTED_NO_RETURN_RECORDS',
        'logicalWithinReturnOneToOneViolations': len(logical_bad),
        'logicalWithinReturnOneToOneViolationRecords': logical_bad,
        'duplicateLogicalTrackIdSnapshotCount': len(duplicate_ids),
        'duplicateLogicalTrackIdSnapshots': duplicate_ids,
        'logicalTrackIdWithChangingTrackNumber': {k:sorted(v, key=str) for k,v in numbers.items() if len(v)>1},
        'nativeSourceFunctionSha256': {k:sha(v.encode()) for k,v in capture.get('nativeSources', {}).items() if isinstance(v,str)},
        'plotLineageCount': len(capture.get('observedPlotLineage', [])),
        'plotLineageTimeS': distribution([q.get('timeS') for q in capture.get('observedPlotLineage', [])]),
        'captureDropCounters': {k:v for k,v in capture.get('counts', {}).items() if 'Dropped' in k},
        'fullPhysicalCorrespondence': {'status': 'UNKNOWN_NO_PHYSICAL_MEASUREMENT_LINEAGE',
                                       'provenIdSwapCount': None, 'provenFalseMergeCount': None,
                                       'provenDuplicatePhysicalTrackCount': None},
        'limitations': [
            'Nearest-reference changes are geometric descriptors, not proven physical ID switches.',
            'Shared nearest reference is not proof of a duplicate; all pair residuals remain available.',
            'Initial ASM truth omits other possible world reflectors, weapons and clutter.',
            'KF prediction/state epoch is not serialized; no offset or extrapolation is applied.',
            'Pdiag omits correlations; marginal sigma units are neither native NIS nor calibrated probabilities.',
            'One-Hz snapshots cannot rule out within-interval switches or reconstruct per-plot physical lineage.',
            'Native physical measurements may be unresolved/composite before association.',
            'No threshold, physical assignment, trajectory model or truth feedback is introduced.'
        ],
        'storedTransportReceiptPresent': receipt is not None,
        'productCodeChanged': False, 'rawInputsChanged': False, 'browsersLaunched': 0,
    }
    return summary, tracks, pairs, collisions, switches, per_sample


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--capture', action='append', required=True, metavar='LABEL=PATH')
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    index = {'schema': 'AEGIS_AFTER_ACTION_REFERENCE_AUDIT_INDEX_1',
             'scriptSha256': sha(Path(__file__).read_bytes()), 'captures': {}}
    for arg in a.capture:
        label, name = arg.split('=', 1)
        assert label and all(c.isalnum() or c in '-_' for c in label)
        path = Path(name)
        capture, provenance = load_capture(path)
        result, tracks, pairs, groups, changes, snapshots = analyze(capture, provenance)
        folder = a.out / label
        folder.mkdir(exist_ok=True)
        result['auditScriptSha256'] = index['scriptSha256']
        for filename, data in [('SUMMARY.json', result), ('nearest-reference-changes.json', changes),
                               ('shared-nearest-reference-groups.json', groups)]:
            (folder/filename).write_text(json.dumps(data, indent=2, allow_nan=False)+'\n')
        for filename, rows in [('track-snapshots.csv', tracks), ('all-reference-pair-residuals.csv', pairs), ('sample-coverage.csv', snapshots)]:
            columns = list(rows[0]) if rows else ['noRows']
            csv_write(folder/filename, rows, columns)
        index['captures'][label] = {'path': name, 'sha256': provenance['sha256'],
                                    'summaryPath': str(folder/'SUMMARY.json'),
                                    'summarySha256': sha((folder/'SUMMARY.json').read_bytes()),
                                    'physicalCorrespondenceStatus': result['fullPhysicalCorrespondence']['status']}
    (a.out/'INDEX.json').write_text(json.dumps(index, indent=2, allow_nan=False)+'\n')
    print(json.dumps(index, indent=2))


if __name__ == '__main__':
    main()

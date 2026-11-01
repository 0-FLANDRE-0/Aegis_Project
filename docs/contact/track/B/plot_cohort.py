"""Plot saved native cohort fixtures; never execute a game, solver or RF model.

Inputs are only cohort-supplement/{baseline,shadow,active,SUMMARY}.json.
All coordinates are anonymous measurements/reports or receiver filter states.
The plots do not establish physical-target truth or natural-RF performance.
"""
from pathlib import Path
import csv
import hashlib
import json

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap


ROOT = Path(__file__).resolve().parent
INPUT = ROOT / 'evidence/cohort-supplement'
OUTPUT = ROOT / 'evidence/figures'
CLASSIFICATION = 'DIRECT_NATIVE_ANONYMOUS_INGRESS_NOT_NATURAL_RF'
CASES = ('npcActualGreedyTrap', 'hawklinkActualSequentialFalseReplay')
MODES = ('baseline', 'shadow', 'active')
COLORS = ('#777777', '#b7a580', '#007e87')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


def read_inputs():
    data, provenance = {}, {}
    for mode in (*MODES, 'SUMMARY'):
        name = mode + '.json'
        raw = (INPUT / name).read_bytes()
        item = json.loads(raw)
        assert item['classification'] == CLASSIFICATION
        data[mode] = item
        provenance[mode] = {
            'path': 'cohort-supplement/' + name,
            'sha256': sha(raw),
        }
        if mode != 'SUMMARY':
            assert not item['fixturePreconditionOrRuntimeFailures']
            assert item['nativeResult']['naturalRfOrWeaponEvidence'] is False
            provenance[mode].update({
                'productSha256': item['productSha256'],
                'testCopySha256': item['testCopySha256'],
                'helpers': item['helpers'],
            })
            for case in CASES:
                record = item['nativeResult']['records'][case]
                assert record['physicalTruthUsed'] is False
                assert all(record['fixturePreconditions'].values())
    summary = data['SUMMARY']
    assert summary['status'] == 'PASS'
    assert summary['naturalRfOrWeaponEvidence'] is False
    assert summary['shadowActualNativeRecordsExact'] is True
    assert all(summary['baselineDefectsActuallyReproduced'].values())
    assert summary['activeChecks'] == {'count': 14, 'passed': 14}
    assert data['baseline']['nativeResult']['records'] == data['shadow']['nativeResult']['records']
    for mode, key in [('baseline', 'baselineSha256'), ('shadow', 'shadowSha256'), ('active', 'candidateSha256')]:
        assert data[mode]['productSha256'] == summary[key]
    assert all(data[m]['helpers'] == data['baseline']['helpers'] for m in MODES)
    records = {m: data[m]['nativeResult']['records'] for m in MODES}
    for case in CASES:
        for mode in MODES:
            assert records[mode][case]['nativeCostMatrix'] == records['baseline'][case]['nativeCostMatrix']
            assert records[mode][case]['nativeGate'] == records['baseline'][case]['nativeGate']
    npc = [records[m][CASES[0]] for m in MODES]
    hawk = [records[m][CASES[1]] for m in MODES]
    assert [r['fileCount'] for r in npc] == [3, 3, 2]
    assert [r['associatedDelta'] for r in npc] == [1, 1, 2]
    assert [r['birthDelta'] for r in npc] == [1, 1, 0]
    assert [r['acceptedDelta'] for r in hawk] == [1, 1, 2]
    assert [r['rejectedDelta'] for r in hawk] == [1, 1, 0]
    for mode in MODES:
        for case in CASES:
            assert all(t['identity'] == 'UNKNOWN' and t['authority'] == 'WITHHELD'
                       for t in records[mode][case]['after'])
        h = records[mode][CASES[1]]
        increments = [next(t for t in h['after'] if t['id'] == old['id'])['hits'] - old['hits']
                      for old in h['before']]
        assert increments == ([1, 1] if mode == 'active' else [1, 0])
        assert h['initialSurfaceRangeSigmaM'] == 15 and h['reportedHorizontalSigmaM'] == 20
    assert hawk[0]['reports'][0]['positionM']['x'] == 4029
    assert hawk[0]['midpointMeasurementBiasM'] == -1
    assert '4030m' in hawk[0]['priorMidpointAttempt'] and 'did not reproduce' in hawk[0]['priorMidpointAttempt']
    return data, records, provenance


def write_csv(data, records, sources):
    rows = []

    def add(mode, case, metric, value, pointer, unit='', detail=None):
        source = sources[mode]
        rows.append({
            'classification': CLASSIFICATION,
            'variant': mode,
            'case': case,
            'metric': metric,
            'value_json': encoded(value),
            'unit': unit,
            'source_json': source['path'],
            'source_json_sha256': source['sha256'],
            'summary_json_sha256': sources['SUMMARY']['sha256'],
            'product_sha256': source['productSha256'],
            'test_copy_sha256': source['testCopySha256'],
            'helper_source_shas_json': encoded(source['helpers']),
            'source_pointer': pointer,
            'details_json': encoded(detail),
        })

    for mode in MODES:
        for case in CASES:
            record = records[mode][case]
            base = '/nativeResult/records/' + case
            add(mode, case, 'native_gate', record['nativeGate'], base + '/nativeGate', 'NIS')
            for i, costs in enumerate(record['nativeCostMatrix']):
                for j, value in enumerate(costs):
                    add(mode, case, 'native_candidate_cost', value,
                        f'{base}/nativeCostMatrix/{i}/{j}', 'NIS',
                        {'inputIndex': i, 'filterFileId': record['before'][j]['id']})
            for i, measurement in enumerate(record['initial']):
                add(mode, case, 'initial_anonymous_measurement', measurement,
                    f'{base}/initial/{i}', 'mixed_explicit_fields',
                    {'interpretation': 'receiver initial-condition measurement, not physical-target truth'})
            input_key = 'plots' if case == CASES[0] else 'reports'
            for i, measurement in enumerate(record[input_key]):
                add(mode, case, 'anonymous_' + input_key[:-1], measurement,
                    f'{base}/{input_key}/{i}', 'mixed_explicit_fields')
            for phase in ('before', 'after'):
                for i, state in enumerate(record[phase]):
                    for key, unit in [('x', 'filter_state_SI'), ('P', 'filter_covariance_SI'), ('hits', 'native_hits')]:
                        add(mode, case, phase + '_filter_' + key, state[key],
                            f'{base}/{phase}/{i}/{key}', unit,
                            {'operationalFileId': state['id'], 'physicalTruth': False})
            for key in ('associatedDelta', 'birthDelta', 'fileCount', 'acceptedDelta', 'rejectedDelta', 'sequences', 'legacyDefectObserved', 'fixturePreconditions'):
                if key in record:
                    add(mode, case, key, record[key], base + '/' + key)
            if case == CASES[1]:
                for key in ('midpointMeasurementBiasM', 'initialSurfaceRangeSigmaM', 'reportedHorizontalSigmaM', 'priorMidpointAttempt'):
                    add(mode, case, key, record[key], base + '/' + key)
            for key, value in data[mode]['nativeResult']['checks'].items():
                if key.startswith('npcCohort.' if case == CASES[0] else 'hawkCohort.'):
                    add(mode, case, 'native_check_' + key, value, '/nativeResult/checks/' + key)
        diagnostics = data[mode]['diagnostics']['b']
        if diagnostics is not None:
            for i, event in enumerate(diagnostics['records']):
                if event.get('route', '').startswith('HAWKLINK'):
                    add(mode, CASES[1], 'recorded_association_event', event,
                        f'/diagnostics/b/records/{i}')
    path = OUTPUT / 'cohort-proof.csv'
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    return path, len(rows)


def draw_matrix(ax, record, labels, title, assignment_events=()):
    matrix, gate = record['nativeCostMatrix'], record['nativeGate']
    file_columns = {item['id']: i for i, item in enumerate(record['before'])}
    selected = {(event['plotIndex'], file_columns[event['proposedTrackId']])
                for event in assignment_events}
    # Presentation of recorded gate relationships only: no NIS, filter or solver execution.
    ax.imshow([[int(value <= gate) for value in row] for row in matrix],
              cmap=ListedColormap(['#edd6d1', '#d1e9e6']), vmin=0, vmax=1)
    for i, row in enumerate(matrix):
        for j, value in enumerate(row):
            suffix = '\nACTIVE recorded pair' if (i, j) in selected else ''
            ax.text(j, i, f'{value:.6g}\n' + ('within recorded gate' if value <= gate else 'outside recorded gate') + suffix,
                    ha='center', va='center', fontsize=9)
    ax.set_xticks([0, 1], [f"T{t['id']}: filter x {t['x'][0]:g} m" for t in record['before']])
    ax.set_yticks([0, 1], labels)
    ax.set_title(title + f'\nRecorded native NIS; gate {gate:g}', fontsize=11)
    ax.set_xlabel('Receiver filter estimates before either update')
    ax.set_xticks([-.5, .5, 1.5], minor=True)
    ax.set_yticks([-.5, .5, 1.5], minor=True)
    ax.grid(which='minor', color='white', linewidth=2)
    ax.tick_params(which='minor', bottom=False, left=False)
    ax.set_aspect('auto')


def draw_counts(ax, records, case, metrics, labels, title):
    width = .23
    for i, (mode, color) in enumerate(zip(MODES, COLORS)):
        values = [records[mode][case][metric] for metric in metrics]
        positions = [j + (i - 1) * width for j in range(len(metrics))]
        bars = ax.bar(positions, values, width=width, color=color, label=mode)
        for bar, value in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2, value + .07, str(value), ha='center', fontsize=9)
    ax.set_xticks(range(len(metrics)), labels)
    ax.set_ylim(0, 3.7 if len(metrics) == 3 else 2.7)
    ax.set_yticks(range(4 if len(metrics) == 3 else 3))
    ax.set_title(title, fontsize=11)
    ax.set_ylabel('Recorded native count')
    ax.grid(axis='y', alpha=.2)
    ax.legend(loc='upper right', frameon=False, fontsize=8)


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    data, records, sources = read_inputs()
    csv_path, row_count = write_csv(data, records, sources)
    plt.rcParams.update({'font.size': 9, 'svg.fonttype': 'none',
                         'svg.hashsalt': 'AEGIS_TRACK_B_SAVED_NATIVE_COHORT_1'})
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.subplots_adjust(left=.16, right=.97, top=.81, bottom=.22, wspace=.38, hspace=.60)
    npc = records['active'][CASES[0]]
    draw_matrix(axes[0, 0], npc,
                [f"plot {i}: measured range {p['rangeM']:g} m" for i, p in enumerate(npc['plots'])],
                'NPC: recorded gated candidate graph')
    draw_counts(axes[0, 1], records, CASES[0],
                ['fileCount', 'associatedDelta', 'birthDelta'], ['Files after', 'Corrections', 'New files'],
                'NPC greedy trap: 3 files to 2; no extra birth')
    hawk = records['active'][CASES[1]]
    assignments = [event for event in data['active']['diagnostics']['b']['records']
                   if event['route'] == 'HAWKLINK_COHORT' and event['decision'] == 'ASSIGN']
    assert len(assignments) == 2
    draw_matrix(axes[1, 0], hawk,
                [f"report {i}: reported x {p['positionM']['x']:g} m" for i, p in enumerate(hawk['reports'])],
                'Hawklink: 4029 m strict first-row preference', assignments)
    draw_counts(axes[1, 1], records, CASES[1],
                ['acceptedDelta', 'rejectedDelta'], ['Accepted reports', 'Rejected reports'],
                'Hawklink: old false replay; both reports accepted in ACTIVE')
    axes[1, 1].text(.5, -.22,
        'Original-file hit increments: baseline/shadow [1, 0]; ACTIVE [1, 1].\n'
        'All variants retain UNKNOWN identity and WITHHELD authority.',
        transform=axes[1, 1].transAxes, ha='center', fontsize=8)
    fig.suptitle('TRACK-B recorded cohort defect reproduction and correction', fontsize=15, y=.975)
    fig.text(.5, .935, CLASSIFICATION, ha='center', family='monospace', fontsize=9)
    fig.text(.5, .907,
        'Anonymous ingress and native methods only. Observed/reported coordinates and filter states; no physical-target truth.',
        ha='center', fontsize=9)
    fig.text(.5, .879,
        'Native matrix entries, counts and saved checks are evidence of measured-gate behavior; no natural-RF or weapon-performance claim.',
        ha='center', fontsize=8.5)
    fig.text(.07, .123,
        'Prior 4030 m midpoint attempt: NONREPRO, retained in source priorMidpointAttempt (not silently discarded).\n'
        'Final Hawklink input: 4029 m (-1 m fixture-only bias); initial range sigma 15 m, report horizontal sigma 20 m.\n'
        'No product comparator/coefficient change. SHADOW native records equal baseline; ACTIVE checks 14/14.', fontsize=9)
    fig.text(.07, .06,
        'Input SHA-256 baseline: ' + sources['baseline']['sha256'] + '\n'
        'Input SHA-256 active:   ' + sources['active']['sha256'], family='monospace', fontsize=6.8)
    fig.text(.07, .023,
        'All four input hashes, product/test-copy/helper hashes, raw measurement covariance and exact JSON pointers: companion CSV + SVG metadata.',
        fontsize=8)
    metadata = {'classification': CLASSIFICATION, 'dataSources': sources,
                'plotScriptSha256': sha(Path(__file__).read_bytes()),
                'csvSha256': sha(csv_path.read_bytes()),
                'kernelsExecuted': False, 'physicalTruthUsed': False,
                'naturalRfPerformanceClaimed': False,
                'prior4030mAttempt': hawk['priorMidpointAttempt']}
    svg = OUTPUT / 'cohort-proof.svg'
    fig.savefig(svg, metadata={'Date': None, 'Creator': 'AEGIS TRACK-B plot_cohort.py',
                              'Title': CLASSIFICATION, 'Description': encoded(metadata)})
    plt.close(fig)
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines()) + '\n')
    print(json.dumps({'classification': CLASSIFICATION,
                      'svg': str(svg.relative_to(ROOT)), 'svgSha256': sha(svg.read_bytes()),
                      'csv': str(csv_path.relative_to(ROOT)), 'csvSha256': sha(csv_path.read_bytes()),
                      'csvRows': row_count,
                      'sourceSha256': {key: value['sha256'] for key, value in sources.items()},
                      'kernelsExecuted': False}))


if __name__ == '__main__':
    main()

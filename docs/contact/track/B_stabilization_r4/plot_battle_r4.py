"""Offline static figures from closed battle records; no game/browser execution."""
from pathlib import Path
import csv
import hashlib
import json
import os

os.environ.setdefault('MPLCONFIGDIR', '/dev/shm/aegis-r4-matplotlib')
os.environ.setdefault('TMPDIR', '/dev/shm')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

P = Path(__file__).resolve().parent
REPO = P.parents[3]
OUT = P / 'evidence' / 'figures'
BATTLE = P / 'BATTLE_RESULTS.json'
CAUSE = P / 'evidence/battle-six-cause/RESULTS.json'
R3 = P.parent / 'B_stabilization_r3/evidence/battle-active-six/SUMMARY.json'
sha = lambda b: hashlib.sha256(b).hexdigest()
sources = {}


def read(path):
    raw = path.read_bytes()
    sources[str(path.relative_to(REPO))] = sha(raw)
    return json.loads(raw)


def ref(path, pointer):
    return {'sourceJsonPath': str(path.relative_to(REPO)),
            'sourceJsonSha256': sources[str(path.relative_to(REPO))],
            'jsonPointers': json.dumps(pointer if isinstance(pointer, list) else [pointer])}


def write_csv(name, rows):
    with (OUT/name).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def save(fig, name):
    fig.savefig(OUT/(name+'.svg'), metadata={'Date': None})
    fig.savefig(OUT/(name+'.png'), dpi=160, metadata={'Software': 'Matplotlib offline, no browser'})
    plt.close(fig)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({'font.size': 10, 'axes.spines.top': False,
                         'axes.spines.right': False, 'svg.hashsalt': 'AEGIS_R4_FACTUAL_PLOTS_1'})
    b, c, r3 = read(BATTLE), read(CAUSE), read(R3)
    rows = b['historicalReferences']+b['freshRows']

    def battle_row(variant, case):
        found = [(section, i, v) for section in ('historicalReferences', 'freshRows')
                 for i, v in enumerate(b[section]) if v['variant'] == variant and v['case'] == case]
        assert len(found) == 1, (variant, case)
        section, i, v = found[0]
        return v, ref(BATTLE, f'/{section}/{i}')

    moderate = []
    for variant, label in [('TRACK_A', 'TRACK-A'), ('OLD_B_ACTIVE', 'Original B ACTIVE'), ('R4_ACTIVE', 'R4 ACTIVE')]:
        row, reference = battle_row(variant, 'NATURAL_SATURATION_6')
        assert row['nativeInitialTargetTerminalKinds'] == {'INTERCEPT_KILL': 5, 'NORMAL_HIT': 1}
        moderate.append({'variant': label, 'legacyShipHP': row['hp'], 'waterM3': row['waterM3'],
                         'recordedEndS': row['nativeEnd']['timeS'], 'initialInterceptKill': 5,
                         'initialNormalHit': 1, **reference})
    r3_row = [v for v in r3['rows'] if v['case'] == 'NATURAL_SATURATION_6' and v['version'] == 'candidate-active']
    assert len(r3_row) == 1
    r3_row = r3_row[0]
    assert r3_row['hp'] == c['hp']['R3']
    targets = r3_row['targets']
    killed = sum(t.get('retirement', {}).get('cause') == 'INTERCEPT_KILL' for t in targets)
    hit = sum(t.get('_wip113Outcome') == 'NORMAL_HIT' for t in targets)
    assert (killed, hit) == (5, 1)
    moderate.insert(2, {'variant': 'R3 ACTIVE', 'legacyShipHP': c['hp']['R3'], 'waterM3': c['waterM3']['R3'],
                        'recordedEndS': c['ends']['R3']['timeS'], 'initialInterceptKill': killed,
                        'initialNormalHit': hit, **ref(CAUSE, ['/hp/R3', '/waterM3/R3', '/ends/R3'])})
    assert moderate[-1]['legacyShipHP'] == c['hp']['R4']
    assert moderate[-1]['waterM3'] == c['waterM3']['R4']
    write_csv('moderate6_ship_state.csv', moderate)
    colors = ['#566c86', '#407991', '#7c6d9c', '#b44338']
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 5.2), gridspec_kw={'width_ratios': [1.3, 1]})
    for ax, key, title in [(axes[0], 'legacyShipHP', 'Legacy shipHP (not sinking state)'),
                           (axes[1], 'waterM3', 'Recorded flooding water (m³)')]:
        values = [v[key] for v in moderate]
        ax.bar(range(4), values, color=colors, width=.58)
        ax.scatter(range(4), values, color=colors, s=32, zorder=4)
        ax.set_xticks(range(4), [v['variant'] for v in moderate], rotation=15, ha='right')
        ax.set_title(title, fontsize=11)
        ax.grid(axis='y', alpha=.18)
        ax.set_axisbelow(True)
        ax.set_ylim(-.005 if key == 'waterM3' else -.35, .29 if key == 'waterM3' else 11.5)
        for i, value in enumerate(values):
            text = f'{value:.6f}' if key == 'waterM3' and value > 0 else f'{value:.3f}'
            if key == 'waterM3' and value != 0 and abs(value) < 1e-15:
                text = '≈0*'
            ax.annotate(text, (i, value), xytext=(0, 7), textcoords='offset points', ha='center', fontsize=9)
    fig.suptitle('Moderate 6-ASM battle: equal initial-threat totals, different recorded ship state', fontsize=13)
    fig.text(.5, .885, 'All four: 5 INTERCEPT_KILL + 1 NORMAL_HIT. R4 adverse outcome remains unapproved.', ha='center', fontsize=10)
    fig.text(.05, .015, 'A / B / R3 end 45.316667s; R4 end 45.100000s.  *A water raw = −3.3881317890172014e−21m³ (numerical residue).\n'
             'Closed native captures; no sink-state inference, RNG-only attribution, or physical-identity proof.', fontsize=8)
    fig.subplots_adjust(top=.78, bottom=.25, wspace=.27)
    save(fig, 'moderate6_ship_state')

    events = []
    def event(product, stage, seconds, pointer, detail):
        events.append({'product': product, 'stage': stage, 'timeS': seconds, 'detail': detail, **ref(CAUSE, pointer)})
    event('R3/R4', 'First metadata divergence', c['metadataFirstDivergence']['timeS'], '/metadataFirstDivergence/timeS', 'Before/after kf6 and Pdiag equal at first controlled metadata divergence')
    event('R3/R4', 'First NIS-return difference', c['firstNisReturnDifference']['R3']['timeS'], '/firstNisReturnDifference', 'Different NIS; same selected file at this return')
    event('R3/R4', 'First choice/HOLD difference', c['firstChoiceOrHoldDifference']['R3']['timeS'], '/firstChoiceOrHoldDifference', 'Actual logged selected-result sets diverge')
    for product in ['R3', 'R4']:
        q = c['firstNativeEffectSequenceDifference'][product]
        assert q['weapon'] == '5in MFF' and q['result'] == 'MISS'
        event(product, '5in MFF MISS', q['timeS'], '/firstNativeEffectSequenceDifference/'+product, 'First effect-sequence mismatch; not proved to be the same gun-round ID')
        q = c['firstNativeLaunchDifference'][product]
        assert q['kind'] == 'NATIVE_WEAPON_LAUNCH' and q['type'] == 'SAM'
        event(product, 'SAM release mismatch', q['timeS'], '/firstNativeLaunchDifference/'+product, 'Actual launch id14; assigned logical track '+str(q['assignedTargetId']))
        for i, q in enumerate(c['nativeHitRecords'][product]):
            hit = q['hit']
            stage = 'Wreck hit callback' if hit.get('wip11cWreck') else 'Initial ASM hit callback'
            event(product, stage, q['timeS'], f'/nativeHitRecords/{product}/{i}', hit['part']+'; dmg='+str(hit['dmg']))
    write_csv('moderate6_event_timeline.csv', events)
    fig, (early, late) = plt.subplots(2, 1, figsize=(12, 7.7), gridspec_kw={'height_ratios': [1.0, 1.6]})
    for y, q in enumerate(events[:3]):
        early.scatter(q['timeS'], 2-y, color='#704e95', s=45)
        early.annotate(f"{q['timeS']:.6f}s", (q['timeS'], 2-y), xytext=(8, 7), textcoords='offset points', fontsize=9)
    early.set_yticks([2, 1, 0], [q['stage'] for q in events[:3]])
    early.set_xlim(31.35, 31.83)
    early.set_ylim(-.5, 2.6)
    early.set_title('First observed divergence: metadata, then numeric NIS, then selected-result set', loc='left', fontsize=11)
    positions = {'R4 MFF': 5, 'R3 MFF': 4, 'R3 SAM': 3, 'R4 SAM': 2, 'R4 hit': 1, 'R3 hit': 0, 'R4 wreck': -1}
    labels = ['R4 · 5in MFF MISS', 'R3 · 5in MFF MISS', 'R3 · SAM release', 'R4 · SAM release',
              'R4 · initial ASM hit / No.2 boiler room', 'R3 · initial ASM hit / CDC', 'R4 · wreck hit callbacks (3)']
    for q in events[3:]:
        suffix = {'5in MFF MISS': 'MFF', 'SAM release mismatch': 'SAM', 'Initial ASM hit callback': 'hit', 'Wreck hit callback': 'wreck'}[q['stage']]
        y = positions[q['product']+' '+suffix]
        color = '#b44338' if q['product'] == 'R4' else '#7c6d9c'
        late.scatter(q['timeS'], y, color=color, s=42, marker='x' if suffix == 'wreck' else 'o', zorder=4)
        if suffix != 'wreck':
            late.annotate(f"{q['timeS']:.6f}s", (q['timeS'], y), xytext=(7, 7), textcoords='offset points', fontsize=9)
    late.annotate('40.333333s + 40.350000s (2 callbacks)', (40.35, -1), xytext=(-10, 8), textcoords='offset points', ha='right', fontsize=9)
    late.set_yticks([5, 4, 3, 2, 1, 0, -1], labels)
    late.set_ylim(-1.7, 5.6)
    late.set_xlim(37.2, 40.85)
    late.set_title('Later native events (separate time scale)', loc='left', fontsize=11)
    for ax in (early, late):
        ax.set_xlabel('Simulation time (s)')
        ax.grid(axis='x', alpha=.2)
    fig.suptitle('R3 vs R4 moderate6: factual recorded sequence, not a complete causal decomposition', fontsize=12)
    fig.text(.025, .015, 'Gun events are sequence mismatches, not proved same-projectile comparisons. Wreck callbacks are not additional initial ASM leakers.\n'
             'No numeric process-noise/RF/Pk/RNG-draw decomposition was captured; no RNG-only or geometry-only attribution is made.', fontsize=8)
    fig.subplots_adjust(left=.33, right=.98, top=.9, bottom=.13, hspace=.65)
    save(fig, 'moderate6_event_timeline')

    holds = []
    for variant, case, label in [('OLD_B_ACTIVE', 'NATURAL_SATURATION_6', 'B · 6 ASM'),
                                 ('R4_ACTIVE', 'NATURAL_SATURATION_6', 'R4 · 6 ASM'),
                                 ('OLD_B_ACTIVE', 'NATURAL_SATURATION_13', 'B · 13 ASM'),
                                 ('R4_ACTIVE', 'NATURAL_SATURATION_13', 'R4 · 13 ASM')]:
        row, reference = battle_row(variant, case)
        holds.append({'label': label, 'closedEpisodes': row['actualHoldClosedEpisodes'],
                      'maxClosedToNextAcceptedUpdateS': row['maxClosedHoldToNextAcceptedNativeUpdateS'],
                      'openAtEndEpisodes': row['actualHoldOpenAtEndEpisodes'],
                      'maxRightCensoredElapsedS': row['maxCensoredOpenHoldElapsedS'],
                      'nativeEndS': row['nativeEnd']['timeS'], **reference})
    write_csv('hold_episode_scope.csv', holds)
    fig, ax = plt.subplots(figsize=(11, 4.5))
    for y, q in enumerate(holds):
        ax.scatter(q['maxClosedToNextAcceptedUpdateS'], y+.10, color='#356f88', s=45)
        if q['openAtEndEpisodes']:
            ax.scatter(q['maxRightCensoredElapsedS'], y-.10, facecolors='none', edgecolors='#bb6c2d', s=70, marker='>')
            ax.annotate(f"{q['maxRightCensoredElapsedS']:.3f}s open", (q['maxRightCensoredElapsedS'], y-.10), xytext=(7, 7), textcoords='offset points', fontsize=8)
        else:
            ax.annotate('no open episode', (0, y-.10), xytext=(7, 8), textcoords='offset points', fontsize=8, color='#805733')
        ax.annotate(f"{q['maxClosedToNextAcceptedUpdateS']:.3f}s closed", (q['maxClosedToNextAcceptedUpdateS'], y+.10), xytext=(7, -12), textcoords='offset points', fontsize=8)
    ax.set_yticks(range(4), [f"{q['label']}  (closed {q['closedEpisodes']}, open {q['openAtEndEpisodes']})" for q in holds])
    ax.invert_yaxis()
    ax.set_xlim(-.5, 63)
    ax.set_ylim(3.6, -.6)
    ax.set_xlabel('Recorded episode duration / elapsed time (s)')
    ax.set_title('Logical HOLD episode scope: closed recovery vs right-censored open elapsed', fontsize=12)
    ax.grid(axis='x', alpha=.2)
    ax.scatter([], [], color='#356f88', label='Closed → next accepted native update')
    ax.scatter([], [], facecolors='none', edgecolors='#bb6c2d', marker='>', label='Open at recorded end (right-censored)')
    ax.legend(loc='upper center', bbox_to_anchor=(.5, -.19), ncol=2, frameon=False, fontsize=9)
    fig.text(.02, .015, 'Open logical-file episodes can outlive retired physical targets or deleted files. Elapsed time is not continuous sensor outage or active-target stall.\n'
             '6-ASM end: B45.316667s / R445.100000s; 13-ASM end: both90s and unresolved. No phone-FPS or performance claim.', fontsize=8)
    fig.subplots_adjust(left=.27, right=.98, top=.86, bottom=.32)
    save(fig, 'hold_episode_scope')

    notes = '''# Offline battle figure notes

- `moderate6_ship_state`: legacy shipHP and recorded water, not a sink-state or physical identity metric. All four initial threat totals are 5 INTERCEPT_KILL + 1 NORMAL_HIT. End times differ. TRACK-A numerical water residue is preserved in CSV and shown approximately zero.
- `moderate6_event_timeline`: two explicitly different x-axis ranges. Native event chronology is not a complete causal decomposition. MFF sequence mismatches are not proved to be the same gun round. Three wreck callbacks are not three additional initial-threat hits.
- `hold_episode_scope`: closed episodes end at the next accepted native update; open elapsed is right-censored at the recorded endpoint, not continuous sensor outage. No physical-target continuity is inferred.
- No browser, simulation, source coefficient, expectation, original capture, existing report or table was changed. Figures are offline static plots, not phone FPS measurements.
- Every CSV row includes its source JSON path, SHA-256 and pointer. Figure provenance pins all source inputs, script, and outputs.
'''
    (OUT/'FIGURE_NOTES.md').write_text(notes)
    manifest = {'schema': 'AEGIS_R4_OFFLINE_FACTUAL_BATTLE_FIGURES_1',
                'scriptPath': str(Path(__file__).relative_to(REPO)), 'scriptSha256': sha(Path(__file__).read_bytes()),
                'sourceJsonSha256': sources, 'outputsSha256': {str(f.relative_to(P)): sha(f.read_bytes()) for f in sorted(OUT.iterdir()) if f.is_file() and f.name != 'FIGURE_PROVENANCE.json'},
                'browsersLaunched': 0, 'simulationRuns': 0, 'productChanges': 0,
                'originalInputsChanged': False, 'physicalIdentityProven': False, 'releaseApproved': False}
    assert all(sha((REPO/path).read_bytes()) == expected for path, expected in sources.items())
    (OUT/'FIGURE_PROVENANCE.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(json.dumps({'sources': sources, 'outputs': list(manifest['outputsSha256']), 'releaseApproved': False}, indent=2))


if __name__ == '__main__':
    main()

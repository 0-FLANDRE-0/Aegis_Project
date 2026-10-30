"""Export the limited moving-target experiment; never infer a maximum range."""
from pathlib import Path
import collections, csv, gzip, hashlib, json
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['svg.hashsalt'] = 'RANGE_RECOVERY_A'
import matplotlib.pyplot as plt

H = Path(__file__).resolve().parent
R = H.parents[3]
O = H / 'results'
V = json.loads((H / 'evidence/verification.json').read_text())
assert V['verificationPass']
S = json.loads((H / 'evidence/static.json').read_text())
B = json.loads((H / 'evidence/browser.json').read_text())
data = [json.loads(gzip.decompress((O / (k + '.json.gz')).read_bytes())) for k in ['primary', 'controls']]
rows = [{**x, 'version': v['version']} for j in data for v in j['versions'] for x in v['results']]
indexed = {(x['version'], x['caseId']): x['result'] for x in rows}
fixture = json.loads((H / 'cases.json').read_text())
controls = json.loads((H / 'control-cases.json').read_text())['cases']
versions = ['BASE', 'RANGE_A', 'RECOVERY']
motion_names = {'STATIONARY': '정지', 'INBOUND_300': '접근 300m/s', 'OUTBOUND_150': '이탈 150m/s', 'OUTBOUND_150_CONTROL_60': '60km 이탈 확인'}
summary = []
for x in rows:
    q = x['result']; first = q['firstShelf'] or {}
    summary.append({'version': x['version'], 'caseId': x['caseId'], 'motion': x['motion'], 'weapon': q['weapon'], 'altM': q['altM'], 'initialRangeKm': q['rangeKm'], 'targetClosingMps': q['targetSpeedMps'], 'success': q['success'], 'reason': q['reason'], 'firstShelfTimeS': first.get('timeS'), 'firstShelfM': first.get('shelfM'), 'apogeeM': q['apogeeM'], 'terminalSpeedMps': q['terminal']['speedMps'], 'terminalMach': q['terminal']['mach'], 'flightTimeS': q['flightTimeS'], 'closestM': q['closestM'], 'interceptPointKm': q['interceptPointKm'], 'terminationPointKm': q['terminationPointKm'], 'batteryRemainingS': q['batteryRemainingS']})
with (O / 'summary-72.csv').open('w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(summary[0])); w.writeheader(); w.writerows(summary)
columns = ['version', 'caseId', 'timeS', 'distanceKm', 'altitudeM', 'speedMps', 'mach', 'targetXM', 'phase', 'loftDemand', 'cruiseAltM', 'shelfM']
with (O / 'trajectories-10hz.csv').open('w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=columns); w.writeheader()
    for x in rows:
        for s in x['result']['samples']:
            w.writerow({'version': x['version'], 'caseId': x['caseId'], **{k: s.get(k) for k in columns[2:]}})
colors = {'BASE': '#2766a3', 'RANGE_A': '#c44b34', 'RECOVERY': '#1f8b56'}
styles = {'BASE': '--', 'RANGE_A': ':', 'RECOVERY': '-'}
plots = []
for c in fixture['conditions']:
    fig, axes = plt.subplots(2, 3, figsize=(14, 7))
    for col, motion in enumerate(fixture['motions']):
        case_id = c['id'] + '_' + motion['motion']
        for version in versions:
            q = indexed[(version, case_id)]; samples = q['samples']
            kw = {'color': colors[version], 'linestyle': styles[version], 'linewidth': 1.5, 'label': version}
            axes[0, col].plot([s['distanceKm'] for s in samples], [s['altitudeM'] / 1000 for s in samples], **kw)
            axes[1, col].plot([s['timeS'] for s in samples], [s['speedMps'] for s in samples], **kw)
            axes[0, col].scatter(q['terminal']['distanceKm'], q['terminal']['altitudeM'] / 1000, marker='o' if q['success'] else 'x', color=colors[version], s=20)
        axes[0, col].set(title=motion['motion'], xlabel='Horizontal missile distance from launch (km)', ylabel='Altitude MSL (km)')
        axes[1, col].set(xlabel='Flight time (s)', ylabel='Speed (m/s)')
        for row in range(2):
            axes[row, col].grid(alpha=.25)
            axes[row, col].legend(fontsize=8)
    fig.suptitle(f"{c['weapon']} | initial {c['rangeKm']}km | target {c['altM']/1000:g}km | game-engine experiment; circles=kill, x=miss")
    fig.tight_layout(rect=(0, 0, 1, .95))
    stem = c['id'] + '-comparison'
    fig.savefig(O / (stem + '.png'), dpi=130)
    fig.savefig(O / (stem + '.svg'), metadata={'Date': None})
    plt.close(fig); plots.append(stem)

html = R / 'Aegis_SIM_v48_WIP_RANGE_RECOVERY_A.html'
html_sha = hashlib.sha256(html.read_bytes()).hexdigest()
lines = ['# RANGE_RECOVERY_A — 정지·접근·이탈 제한 복구 시험', '', '**정지 6조건은 회복했지만, 이동 표적의 기존 성공 1건이 아직 회복되지 않았다. 전체 복구 완료로 판정하지 않는다.**', '',
         f"기준 RANGE_A `d42284ae4666914c604f77adbde25045a915e93f` 위 별도 `range-loft-recovery-a` 시험 브랜치. HTML `{html.name}` / {html.stat().st_size:,}bytes / SHA-256 `{html_sha}`.", '',
         '첨부 분석의 이전 50발 자료를 새 시험 결과로 재사용하지 않았다. 이번에 지정 6조건 × 운동 3종 × 버전 3종 =54발을 새로 계산하고, 장거리 이탈 실패를 구별하기 위한 60km 확인 6조건 ×3버전 =18발을 추가했다. 72개 조건을 독립적으로 두 번 실행했다. 같은 시드 한 조건당 결정적 반복이며 통계적 명중 확률이 아니다.', '',
         '## 1. 변경 범위', '', '| 항목 | SM-2ER | SM-6 |', '|---|---:|---:|', '| nominalRmaxKm / maxRmaxKm | 360 / 360 유지 | 450 / 450 유지 |', '| rangeGoalKm | 360 유지 | 450 유지 |', '| fullLoftKm | **360→240** | **450→260** |', '',
         '두 수치는 SIM_TUNED 복구 시험값이다. 설계 거리와 로프트 강도 포화 거리를 분리한다. 명칭 변경이나 최적값 탐색은 하지 않았다. 추진·항력·질량·연소·Kappa·신관·배터리·종료기·UI 코드는 변경하지 않았다. SM-2MR/ESSM 설정도 보존했다.', '',
         f"RANGE_A 실행 스크립트의 게임 명명 함수 {S['liveNamedFunctionCount']:,}개, 진단 포함 전체 {S['namedFunctionCount']:,}개가 byte-identical이다. 실행 스크립트 전체를 두 숫자 역치환하면 원본과 완전히 같다. wrapper는 버전명·gzip integrity 외 동일하며 내장 ENV_C와 기존 96행 결과표도 그대로다.", '',
         '**기존 ENV_C 표는 복구 후보에 유효하지 않다.** 프로파일 해시가 달라 기존 ‘재계산 필요’ 경고가 켜짐을 실제 브라우저에서 확인했다. 새 최대 사거리나 360/450km 달성을 이 제한 사격으로 주장하지 않는다.', '',
         '## 2. 시험 조건과 전체 결과', '',
         '- 정지 해면 발사함, 네이티브 수직 VLS·비행·유도·로프트·근접신관 경로, 이상 지속 관측.',
         '- 고정 1/60초, RNG seed `1831565813`. 접근은 사격선 방향으로 300m/s, 이탈은 반대 방향으로 150m/s. 표에는 기존 진단 부호 규약 +300/-150을 사용한다.',
         '- BASE는 ALL4_TERM 설정, RANGE_A는 전체 정렬판, RECOVERY는 현재 RANGE_A에서 fullLoft 두 값만 복원한 후보다.',
         '- 성공은 기존 신관·격추 판정 그대로. 미사일이 근처를 지나가거나 기폭만 했다고 성공으로 바꾸지 않았다.', '',
         '| 운동 | BASE | RANGE_A | RECOVERY |', '|---|---:|---:|---:|']
for motion, label in motion_names.items():
    lines.append('| ' + label + ' | ' + ' | '.join(f"{V['summary'][v][motion]['successes']}/{V['summary'][v][motion]['cases']}" for v in versions) + ' |')
lines += ['', '### 지정 6조건 × 세 운동', '', '| 기종 | 고도 | 발사 시 거리 | 운동 | BASE | RANGE_A | RECOVERY |', '|---|---:|---:|---|---|---|---|']
for c in fixture['cases']:
    lines.append(f"| {c['weapon']} | {c['altM']/1000:g}km | {c['rangeKm']}km | {motion_names[c['motion']]} | " + ' | '.join(indexed[(v, c['caseId'])]['reason'] for v in versions) + ' |')
lines += ['', '장거리 이탈 0/6은 세 버전 모두의 결과다. 원래 정지 표적 최대 거리 근처에 둔 표적이 계속 멀어지는 조건이며, 이 결과만으로 모든 이탈 표적에 대응 불가라고 해석하지 않는다.', '',
          '### 60km 이탈 확인 사격', '', '| 기종 | 표적고도 | BASE | RANGE_A | RECOVERY |', '|---|---:|---|---|---|']
for c in controls:
    lines.append(f"| {c['weapon']} | {c['altM']/1000:g}km | " + ' | '.join(indexed[(v, c['caseId'])]['reason'] for v in versions) + ' |')
lines += ['', 'RECOVERY는 RANGE_A 대비 새로운 성공→실패를 만들지 않았지만, BASE의 성공을 완전히 보존하지도 못했다. ER 60km/1km/이탈 150m/s가 남아 있으므로 후보의 전체 복구 승인이나 기존 브랜치 병합은 하지 않는다.', '',
          '## 3. 정지 조건의 비행 수치', '', '첫 shelf는 네이티브 10Hz 샘플에서 처음 유효한 값과 시각이다. 이번 로그를 과거의 확인되지 않은 원인 분리 자료나 통계 시험으로 취급하지 않는다.', '',
          '| 조건 | 버전 | 첫 shelf(km) / 시각(s) | 최고고도(km) | 종말속도(m/s) | 수명(s) | 결과 |', '|---|---|---:|---:|---:|---:|---|']
for c in fixture['conditions']:
    for v in versions:
        q = indexed[(v, c['id'] + '_STATIONARY')]; first = q['firstShelf']; shelf = f"{first['shelfM']/1000:.3f} / {first['timeS']:.3f}" if first else '없음'
        lines.append(f"| {c['id']} | {v} | {shelf} | {q['apogeeM']/1000:.3f} | {q['terminal']['speedMps']:.3f} | {q['flightTimeS']:.3f} | {q['reason']} |")
lines += ['', '전체 72행 수치와 원래 10Hz 궤적은 [요약 CSV](results/summary-72.csv) / [궤적 CSV](results/trajectories-10hz.csv.gz)에 있다. 실패 조건의 실제 유도 단계 변화와 마지막 10초 60Hz 명령도 원시 JSON에 보존했다.', '', '## 4. 남은 실패의 단계·종말 로그', '', '| 조건/버전 | 첫 하강 시각·고도 | 당시 상태 | 종말 시각·고도 | 종말 vz / pitch 명령 | 종료 사유 |', '|---|---|---|---|---|---|']
selected = [c for c in fixture['cases'] if c['motion'] == 'OUTBOUND_150']
for c in selected:
    q = indexed[('RECOVERY', c['caseId'])]; d = q['firstDescent']; last = q['diagnosticTicks'][-1]
    lines.append(f"| {c['caseId']}/RECOVERY | {d['timeS']:.3f}s / {d['altitudeM']:.1f}m | {d['mode']}/{d['phase']}/{d['guidance']} | {last['timeS']:.3f}s / {last['altitudeM']:.2f}m | {last['vzMps']:.3f}m/s / {last['cmdOmegaPit']:.8g}rad/s | {q['reason']} |")
remaining_id = controls[1]['caseId']
for v in versions:
    q = indexed[(v, remaining_id)]; d = q['firstDescent']; last = q['diagnosticTicks'][-1]
    lines.append(f"| ER60km/1km/{v} | {d['timeS']:.3f}s / {d['altitudeM']:.1f}m | {d['mode']}/{d['phase']}/{d['guidance']} | {last['timeS']:.3f}s / {last['altitudeM']:.2f}m | {last['vzMps']:.3f}m/s / {last['cmdOmegaPit']:.8g}rad/s | {q['reason']} |")
lines += ['', 'ER 60km 확인 조건은 세 버전 모두 LOFT/DIVE 상태에서 KAPPA_MIDCOURSE 하강이 시작된다. RECOVERY는 종말에서 이미 ENDGAME으로 전환했지만 약 -123.6m/s의 하강 속도로 수면을 관통한다. 기존 예측 해면 보호는 비활성이고 soft guard도 false다. fullLoft 복원만으로는 이 기하가 회복되지 않았다. RMAX 정규화·초기 계획·유도/자세 응답의 남은 상호작용을 분리할 후속 조건이다. 단일 원인을 확정하거나 제어 계수를 조정하지 않았다.', '',
          '기존 30m/200m 저고도 충돌 조사와 이 1km 표적의 추가 실패를 같은 재현 케이스라고 부르지 않는다. 이전 조사 자료는 수정하지 않았고 이번에도 해면 보호·고도 하한·충돌 판정은 변경하지 않았다.', '',
          '## 5. 검증과 실행 시간', '', '| 검사 | 결과 |', '|---|---|',
          f"| 정적 변경 범위 | PASS · fullLoft 두 숫자만 · 게임 {S['liveNamedFunctionCount']:,}개 명명 함수 동일 |",
          '| 독립 반복 | PASS · 본시험 54조건 ×2, 확인 18조건 ×2 원시 JSON 각각 비트 동일 |',
          f"| 실제 월드/독립 진단 | PASS · 72조건 · {V['browserSamplePairs']:,}개 샘플쌍, 시간/x/y/z/속도/Mach 최대 오차0 |",
          '| 진단 격리 | PASS · 실제 월드/RNG/틱 전후 변화0 |',
          '| 내장 계산표 상태 | PASS · BASE/RANGE_A 유효, RECOVERY는 재계산 필요 경고 · 변경된 네이티브 함수0 |',
          '| 기존 종료기 단위 fixture | PASS · 원래 6조건 |',
          '| 정지 6조건 회복 | 6/6 |',
          '| 기준판의 기존 성공 보존 | **미달 · 60km 이탈 확인 1건이 여전히 실패** |', '',
          '| 계산 | 1차 벽시계 | 2차 벽시계 | JSON SHA-256 |', '|---|---:|---:|---|']
for key, label in [('primary', '본시험54조건'), ('controls', '60km확인18조건')]:
    receipts = V['receipts'][key]
    lines.append(f"| {label} | {receipts[0]['elapsedMs']/1000:.3f}s | {receipts[1]['elapsedMs']/1000:.3f}s | `{receipts[0]['sha256']}` |")
lines += ['', f"브라우저 동일 경로 검증 벽시계 {B['elapsedS']:.3f}s. Node와 Chromium을 교차한 값은 작은 부동소수 차이가 가능하므로 독립 Node 2회 비트 동일성과 동일 Chromium 내 실제월드/사본 오차0을 구분한다. CPU quota와 다른 검사의 중첩을 포함하며 게임 프레임 성능 측정이 아니다.", '',
          '**실행하지 않은 검사:** 전체 96조합 최대 사거리 스윕, 새로운 사거리 표, 확률적 명중률, 자연 레이더/기동 AI 종합 시험, 전체 420+UI88 회귀. 이번은 첨부 요청과 추가 운동 조건의 제한 시험이며, 과거 통과 기록을 이번 재실행으로 표기하지 않는다. UI·센서·발사 권한·기존 공통 함수는 정적 byte 비교로 보존을 확인했다.', '',
          '## 6. 그래프·원시 자료·다음 경계', '']
for plot in plots:
    lines += [f'![{plot}](results/{plot}.png)', '']
lines += ['- [검증 기록](evidence/verification.json), [정적 검사](evidence/static.json), [실제 월드 비교](evidence/browser.json).',
          '- [본시험 원시 JSON](results/primary.json.gz), [확인 사격 원시 JSON](results/controls.json.gz), [요약 CSV](results/summary-72.csv), [재현](README.md).',
          '- 별도 시험 브랜치의 WIP 후보다. main, missile-b4-termination, range-a-env-c에 병합하지 않으며 Actions를 실행하지 않는다.',
          '- 복구 후보에서는 기존 설계 목표 360/450km를 유지하지만 최대 명중 사거리는 재측정하지 않았다. 정지 6조건 회복을 전체 안정성으로 확대 해석하지 않는다.',
          '- 다음 검토 대상으로 ER60km/1km/이탈150의 잔여 퇴행을 특정했다. RMAX/초기 로프트·종말 유도/자세 응답 분리는 별도 작업이며 이번에는 추가 수치를 변경하지 않는다.']
(H / 'REPORT.md').write_text('\n'.join(lines) + '\n')
status = f'''# v48 WIP RANGE_RECOVERY_A 상태

- 별도 시험 브랜치 `range-loft-recovery-a`, 기준 RANGE_A `d42284ae4666914c604f77adbde25045a915e93f`.
- HTML `{html.name}` / {html.stat().st_size:,}bytes / SHA-256 `{html_sha}`.
- fullLoftKm만 ER360→240 / SM-6 450→260. nominalRmax/maxRmax와 rangeGoal360/450 유지. 추진/항력/Kappa/신관/배터리/종료기/UI/SM-2MR/ESSM 변경0.
- 정지6조건 BASE6/6 → RANGE_A0/6 → RECOVERY6/6. 접근300m/s는 세 버전 모두6/6. 원래 장거리에서 이탈150m/s는 모두0/6.
- 60km 이탈 확인 BASE6/6 → RANGE_A5/6 → RECOVERY5/6. ER60km/1km/이탈150의 SEA_IMPACT는 남았다. 전체 복구 완료나 병합 대상으로 판정하지 않는다.
- 본시험54+확인18조건 각각2회 원시 JSON 비트 동일. 실제월드/독립 진단72조건 {V['browserSamplePairs']:,}샘플쌍 최대오차0, 진단 전후월드/RNG/틱 변화0. 정적·종료기 원래6fixture 통과.
- 기존 ENV_C 96행 표는 보존했고 후보에서는 ‘재계산 필요’ 경고가 켜진다. 전체96스윕/새최대거리/420+88전체회귀/자연센서 종합 시험은 실행하지 않았다.
- [전체 보고](docs/missile/range/RECOVERY_A/REPORT.md), [검증](docs/missile/range/RECOVERY_A/evidence/verification.json), [재현](docs/missile/range/RECOVERY_A/README.md).
- 실행HTML1개 ZIP / 보고서ZIP 분리. 이전 RANGE_A 세트는 byte-identical archive하며 기존 브랜치와 ENV_C/종료기 자료를 보존한다. 원격 전체 readback 영수증은 발행 후 추가한다.
'''
status_file = R / 'AEGIS_PLAN_STATUS_v48_WIP_RANGE_RECOVERY_A.md'
status_file.write_text(status)
(R / 'SHA256SUMS_v48_WIP_RANGE_RECOVERY_A.txt').write_text(html_sha + '  ' + html.name + '\n' + hashlib.sha256(status.encode()).hexdigest() + '  ' + status_file.name + '\n')
print('Limited experiment report generated:', len(rows), 'case/version rows; remaining baseline losses:', V['baselineSuccessesStillLost'])

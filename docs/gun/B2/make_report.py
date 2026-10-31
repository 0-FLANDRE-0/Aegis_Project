"""Render the final report from completed evidence; refuse partial data."""
from pathlib import Path
import collections,datetime,json,math,statistics
from zoneinfo import ZoneInfo
B=Path(__file__).resolve().parent;E=B/'evidence';load=lambda p:json.loads(p.read_text())
s=load(E/'summary.json');a=load(E/'acceptance.json');assert s['complete']and a['pass']
assert len(s['perCondition'])==80 and all(q['trials']==30 for q in s['perCondition'].values())
ex=['BASE','A','B','C','D'];ships=['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA'];short={ships[0]:'DDG',ships[1]:'CG'}
def fmt(q,dec=2):return f"{q['mean']:.{dec}f} ± {q['sigma']:.{dec}f}"if q['n']else'— (표본 없음)'
def pct(v):return f'{100*v:.1f}%'if v is not None else'—'
def group(e,ship,b,count=None):return(s['perCondition'][f'{e}|{ship}|{b}|{count}']if count else s['groups'][f'{e}|{ship}|{b}'])
def dist(values):
 return {'n':len(values),'mean':statistics.mean(values),'sigma':statistics.pstdev(values),'median':statistics.median(values)}if values else{'n':0,'mean':None,'sigma':None,'median':None}
def radii(directory,historical=False):
 result=collections.defaultdict(list)
 for p in directory.glob('worker*.jsonl'):
  for line in p.read_text().splitlines():
   r=json.loads(line)
   if r['ship']!=ships[1]or r['count']!=1 or(historical and not r['on'])or(not historical and r['experiment']!='BASE'):continue
   bursts=[q for q in r['result']['auto']['log']if q['kind']=='AIRBURST']if historical else[s['burst']for s in r['data']['shots']if s.get('burst')]
   for q in bursts:
    pos=q['positionM'];result[r['bearing'],q['outcome']].append(math.hypot(pos['x'],pos['y'])/1000)
 return result
lines=[]
def add(t=''):lines.append(t)
add('# GUN_B2 Phase 0 진단 보고서')
add();add(f"작성: {datetime.datetime.now(ZoneInfo('Asia/Seoul')).strftime('%Y-%m-%d %H:%M KST')} · 상태: **진단 완료, Phase 1 승인 대기**")
add();add('## 1. 결과와 범위')
add();add(f"정식 진단 **2,400회**, 80개 조건 각각 30개 고정 시드, 발사 탄 **{s['shots']:,}발**을 기록했다. 제품 HTML은 main `9719f1e8b3e574f0969eb57c6b2055f7f8d3ee4c`의 GUN_B1 그대로다. SHA-256은 `c9ec99f0b04e24127cc494833b8b1de24492a7ef0c00c2ee1432dba131f83ccc`다.")
add();add('90° 문제의 우선 원인은 **공중 plot의 안테나 원점 누락**이다. 실제 RF 측정은 안테나 기준인데 EKF 예측은 누락된 원점을 함 중심으로 대체한다. 이 때문에 고정적인 위치 편향이 생기며, 90°에서는 이 편향이 측방 오차가 된다. 잡음 없는 private 16조건과 자연 발사 로그에서 확인했다. 사격해 노후화·초기 선회·관측 잡음·표적 기동도 별도로 계측했다.')
add();add('센서 수정은 지시서 §0의 보존 범위와 충돌하므로 **제품에는 적용하지 않았다**. 새로운 B2 게임 HTML도 아직 생성하지 않았다. 이 보고서·원시 자료를 push한 뒤 §2/§12에 따라 멈춘다. 원점 계약 복구를 별도 선행 단계로 허용할지 결정해야 한다.')
add();add('## 2. 리뷰어 분석 검증')
add();add('| 항목 | 확인 결과 |');add('|---|---|')
for title,result in [
 ('산포 0','확인. 같은 해·같은 원점의 HE/SAP/MFF native 발사 반복에서 초기 위치·속도가 동일했다. 새 포구속도/각도 계수는 적용하지 않았다.'),
 ('해 갱신/나이','1초 갱신, 최대 release age 1.2초. BASE 실제 분포는 아래 표. B의 발사 탄은 모두 computedStep=launchStep.'),
 ('수상용 포인팅 창','AIR에도 fallback 20/+7.5/−5.5m가 적용된다. 실제 cross limit는 예측 불확실성을 차감하므로 1.5m floor까지 줄어든다. 항상 20m가 아니다.'),
 ('정확한 CPA 기폭','수정해서 이해해야 한다. 매 틱 swept 구간의 최소거리가 25m 안이면 그 틱의 최소점에서 터진다. 전체 비행 CPA를 기다리지 않으며, 진입 틱 끝에서 먼저 터질 수도 있다. 탐지 패턴/Pd/처리 지연은 없다.'),
 ('파편 띠','방향의 띠 안/밖 검사는 없다. 반폭은 면적 분모에만 들어가므로 폭만 줄이면 밀도/Pk가 오른다. 두 변경을 함께 해야 한다.'),
 ('함속 × 해 나이','G7는 속력을 0으로 초기화하지만 이후 native 항해 명령이 복원되어 가속한다. 실제 속도를 기록했다. A 정지 명령도 원점 누락 편향을 없애지 못한다.'),
 ('롤/파랑','DDG/CG에 SOV 파랑 외력은 없다. 다만 초기 평형·질량 분포·침수/피격에 의한 heel/trim은 존재한다. 자세가 완전히 고정이라는 뜻은 아니다.')]:add(f'| {title} | {result} |')
add();add('## 3. 시험 규약과 원시 로그')
add();add('DDG/CG × 0/90° × 침투 Kh-35U 1~4기 × 시드 419010…419039 × BASE/A/B/C/D. AutoAA ON, 자연 RF 탐지, 기존 CIWS 포함, 실제 전체 fixed tick 1/60초다. 50초 상한 및 표적 전부 종료 시 중단은 G7 그대로다. C만 명시된 직선 운동 통제이며 나머지 피해/충돌/관측 코드는 native다.')
add();add('각 조건은 새 게임 페이지에서 시작했다. 이전 페이지의 항해 일시 상태가 남는 초기 혼합 실행은 묶음 전체를 무효화하고 `evidence/development/interleaved-invalid/`에 보존했다. 실패한 사격만 제외하지 않았다. 과거 G7는 페이지 재사용 방식이므로 historical 비쌍대 비교로 구별하며, 동일 제품 회귀 증명은 native/계측 동일 입력 A/B로 한다.')
old=s['oldG7Comparison'];add();add(f"과거 G7 480회와의 비쌍대 비교에서는 {len(old['different'])}/480회가 달랐다. 이를 기존 결과와 exact equality라고 표시하지 않는다. 차이 필드는 summary.json의 oldG7Comparison.different에 전부 기록했다. 게임 제품 SHA는 동일하며, 새 초기화 규약의 native/계측 쌍대 8조건은 결과·RNG·기록 상태가 동일했다.")
add();add('A=기존 정지 명령, B=관측 기반 발사 순간 native 재계산+포인팅 재검사, C=직선 운동, D=normalizedMiss ≤0.001. D는 기존 0.25 margin 하한 때문에 진단 추가 검사로 만들었다. 모두 진단 하네스 전용이다. [상세 규약](PROTOCOL.md).')
add();add('**A 통제 보완:** 첫 2,400회 수집 뒤 strict 검수에서 A 4,927발 중 10발의 실제 횡속도가 0이 아니었다(최대 0.0118941m/s). STOP 명령이 공개 shipNav 필드만 지우고 native dynamics의 피격 후 private sway를 지우지 못한 시험 하네스 결함이다. 허용 오차 1e−6m/s는 유지했다. 진단 A만 기존 `haltHorizontalContact()`로 내부 횡속도를 지우고 **A 480회 전부** 같은 입력/시드로 재실행했다. 다른 1,920회는 보존했다. 원래 A 480회도 삭제하지 않는다. 최종 표본은 2,400회이며 두 행렬의 실제 실행 합계는 2,880회다(별도 동등성/단위 검수 제외). `evidence/a-stop-audit.json`과 최초 실패 acceptance/log를 함께 보존했다.')
add();add('A 보완 hook은 제품과 원래 계측 파일을 바꾸지 않고 추가했다. BASE/B/C/D 4조건의 전체 결과·RNG·기록 상태가 이전 계측과 동일했고, 기존 실패 A 조건은 독립 probe와 최종 재실행이 동일했다. 현재 원시 자료 선택은 원래 `trials`의 non-A 1,920회 + `a-stop-corrected` 480회이며 두 계측 SHA를 구별한다.')
aq=load(E/'a-stop-audit.json');add();add(f"A 보완 전후 {len(aq['correctedADifferences'])}/480회의 기록 상태 해시가 달라졌다. 발사 시점 위반 10건만 골라 대체하지 않고 A 전체를 다시 실행한 이유다. 각 caseId의 이전/새 해시는 a-stop-audit.json의 correctedADifferences에 있다. 보완 후 A 발사 수는 {aq['correctedShots']:,}발이다.")
add();add('원시 로그: `evidence/trials/worker0…3.jsonl`, 발별 요약 `evidence/shot-summary.csv`, 회차 요약 `evidence/case-summary.csv`, 80조건의 축별 μ/σ/분위수 `evidence/condition-metrics.csv`, 전체 통계 `evidence/summary.json`. 플래그·입력·computedStep·나이·원점·속도·포인팅·관측/truth 오차·기동·CPA·기폭·native arrival/Pk를 보존했다.')
add();add('`LIVE_AT_SCENARIO_END`는 비명중으로 세지 않는다. 아래 arrival/CPA 주 비교는 기폭 직전 배정 표적이 살아 있던 탄이다. Native arrival/Pk는 120m 물리 조회 안의 결과이고, 조회 밖 ET의 arrival 진단은 기존 native 파편 도달 함수를 별도 호출한 값이다. 진단값으로 피해/RNG를 다시 적용하지 않았다. 표본 수와 검열 수는 JSON/CSV에 있다.')
add();add('G7 원래 결과의 `shipHits`는 `shipHitHistory.length`여서 MISS 기록까지 포함할 수 있다. 실제 피격 횟수로 해석하지 않는다. `gunPreCiwsKills`도 비-ASM/id 충돌을 포함할 수 있는 기존 카운터라 Legacy로 구별했다. 이 둘을 모델의 명중·격추 성능으로 사용하지 않았다. 원본 필드와 상세 결과는 보존했다.')
add();add('## 4. 원점 계약 원인 확인')
add();add('`spyCollectUnifiedEchoPlotsWip13B13` → `shipboardRadarEchoToAirPlotWip13B13` → `trackEkfUpdateRadar` → `trackRadarPrediction` 경로에서 receiver 원점이 사라진다. NPC 어댑터에는 원점 덧붙임이 이미 있다. 표적 truth 없이 이미 알고 있는 own receiver 메타데이터를 끝까지 보존하는 것이 최소 수정 방향이다.')
add();add('잡음 없는 16조건 모두, 누락 소비자는 T−L 위치를 정확한 측정 일치점으로 본다. 원점을 명시한 private 자료는 실제 합성 입력 T에서 일치했다. F2 예에서 X lever는 DDG 31.0121m / CG 27.9179m, Z lever는 13.8398m / 16.2969m였다. 12m 입력의 KF 높이는 각각 −1.8398 / −4.2969m로 잘못 해석될 수 있고 legacy 높이는 0m로 제한된다. 고정 +30m나 임의 고도로 때우면 안 된다.')
add();add('[원인·소스 경로·범위 충돌 상세](ORIGIN_CONTRACT_FINDING.md), `evidence/origin-contract/results.json`을 참조한다.')
add();add('## 5. A–D 전체 비교')
add();add('μ±σ는 기록된 분포의 평균/표준편차다. ET 비율의 분모는 실제 폭발 탄이다. D의 낮은 발사 수는 결과이며, 숫자를 바꿔 발사를 강제하지 않았다.')
add();add('| 조건 | 함/방위 | 회차 | 발사 | 폭발/비행중 종료 | ET 비율 | arrival μ±σ(m) | release age μ±σ(s) |');add('|---|---|---:|---:|---:|---:|---:|---:|')
for e in ex:
 for ship in ships:
  for b in [0,90]:
   q=group(e,ship,b);m=q['metrics'];add(f"| {e} | {short[ship]} {b}° | {q['trials']} | {q['shots']} | {q['bursts']}/{q['liveAtEndShots']} | {pct(q['etFractionResolved'])} | {fmt(m['arrivalAllAssignedAliveM'])} | {fmt(m['solutionAgeS'],3)} |")
add();add('**B가 모든 조건을 개선하지는 않았다.** 표적 1~4기 합산에서 90° ET 비율은 DDG 18.0→32.3%, CG 28.8→39.7%로 증가했다. 아래 CG ×1에서는 35.9→18.1%로 감소했다. 발사·생존 표적·기폭 표본 수도 달라지므로 이 비율을 같은 탄의 성공률 전후 비교로 읽지 않는다. B의 효과는 조건에 따라 다르며, 원점 계약 복구 뒤 재평가하기 전 제품 개선으로 승인하지 않는다.')
add();add('### CG × 표적 1기 (리뷰어가 지목한 조건)')
add();add('| 조건 | 방위 | 발사 | ET 비율 | native ASM arrival μ±σ(m) | 배정 표적 arrival μ±σ(m) | 첫 AUTO CUE→첫 발 μ±σ(s) |');add('|---|---:|---:|---:|---:|---:|---:|')
for e in ex:
 for b in [0,90]:
  q=group(e,ships[1],b,1);m=q['metrics'];add(f"| {e} | {b}° | {q['shots']} | {pct(q['etFractionResolved'])} | {fmt(m['arrivalNativeAsmM'])} | {fmt(m['arrivalAllAssignedAliveM'])} | {fmt(m['caseFirstAutoCueToFirstReleaseS'])} |")
add();add('두 arrival 열은 모집단이 다르다. 첫 열은 실제 native 물리 조회 안의 ASM 결과, 두 번째는 배정 표적이 살아 있던 모든 폭발(조회 밖 포함)의 진단값이다. 초기 선회는 교전 개시 거리에, 위치 편향은 근접 반경을 벗어나는 측방 오차에 영향을 준다.')
add();add('### 폭발 거리 재확인 (CG ×1)')
add();add('과거 G7와 비교할 수 있도록 아래 수치는 폭발 위치의 세계 초기 원점 기준 수평거리다. 현재 함 중심까지의 거리를 새로 만들어 넣지 않았다. 별도 그림의 발사 trunnion 기준 거리와는 기준점이 다르다. 초기화 방식이 달라 전후를 제품 변경 효과로 해석하지 않는다.')
add();add('| 자료 | 방위 | PROX n / 중앙값(km) | ET n / 중앙값(km) | ET μ±σ(km) |');add('|---|---:|---:|---:|---:|')
for label,data in [('B1 historical',radii(B.parent/'B1/evidence/effects',True)),('Phase 0 fresh BASE',radii(E/'trials'))]:
 for b in [0,90]:
  p=dist(data[b,'MFF_PROXIMITY']);t=dist(data[b,'MFF_ET_BACKUP']);pm=f"{p['n']} / {p['median']:.3f}"if p['n']else'0 / —';tm=f"{t['n']} / {t['median']:.3f}"if t['n']else'0 / —';add(f'| {label} | {b}° | {pm} | {tm} | {fmt(t,3)} |')
add();add('## 6. 오차 분해와 기여도')
add();add('원시 CPA는 25m 밖도 포함해 실제 비행 전체에서 추적했다. 종료 분율 이후를 계산하지 않았다. 다음은 CG ×1의 기폭 전 표적이 살아 있던 탄에서, native CPA 수평 측방 성분의 정확한 장부 분해다. along/world Z도 summary.json에 있다.')
add();add('발사 시점 관측 오차는 이후 결과에 관계없이 기록했다. BASE CG ×1의 측방 위치 오차 μ±σ: '+', '.join(f"{b}° {fmt(group('BASE',ships[1],b,1)['metrics']['observationPosition.cross'])}m"for b in [0,90])+'.')
add();add('R = 위치관측 + 해시차 + 속도관측 + 표적운동 + 탄도위상. 각 항의 벡터 합은 native shell−target 상대위치와 일치한다. 이 항들은 상관·상쇄가 있으므로 분산을 독립 RSS로 합하거나 기여율 100%로 만들지 않는다. 탄도위상 항은 native 경로와 관측 CV 기준의 차이며 포인팅 오차만을 뜻하지 않는다. 포인팅 자체는 별도 로그에 있다.')
add();add('정의: τ는 실제 swept CPA까지의 비행 시간이다. 위치관측=발사 시 관측 P−truth P, 해시차=해의 P−발사 시 관측 P, 속도관측=(해의 V−발사 시 truth V)×τ, 표적운동=−(CPA의 truth P−발사 시 truth P−truth V×τ), 탄도위상=CPA의 탄 P−(해의 P+해의 V×τ). 해의 V가 오래됐다면 그 영향은 속도관측 항에도 포함된다. 해시차 한 열만으로 노후화의 전체 인과 효과를 주장하지 않고 B 통제도 함께 비교한다. 계산은 진단 사후 장부이며 사격통제가 읽지 않는다.')
add();add('| 조건/방위 | 위치관측 μ±σ(m) | 해시차 μ±σ(m) | 속도관측 μ±σ(m) | 표적운동 μ±σ(m) | 탄도위상 μ±σ(m) | CPA 측방 μ±σ(m) |');add('|---|---:|---:|---:|---:|---:|---:|')
for e in ex:
 for b in [0,90]:
  m=group(e,ships[1],b,1)['metrics'];cells=[fmt(m['budget.'+n+'.cross'])for n in ['position','staleness','velocity','motion','ballisticPhase']];add('| '+f'{e}/{b}°'+' | '+' | '.join(cells+[fmt(m['cpaResolvedLiveTarget.cross'])])+' |')
closure=max(q['metrics']['budget.closureErrorM']['max']or 0 for q in s['groups'].values());add();add(f'분해 벡터 합의 최대 오차: **{closure:.3g}m**. B는 발사 해 나이를 0으로 만들지만 원점 누락은 제거하지 않는다. A 정지와 C 직선 통제도 그 편향을 제거하지 않는다. D는 포신 오차를 줄이는 조건이며 센서 원점을 복구하는 조건이 아니다.')
add();add('### 표적 기동과 수직 오차 (CG ×1)')
add();add('평균 가속도는 방향이 바뀌면 상쇄되므로 횡/종/수직 RMS도 함께 기록했다. 아래 RMS는 각 탄의 유효 추적 시간 안에서 시간 가중한 값의 분포다. C에서는 직선 등속 통제로 0이어야 한다. 전파된 평균은 탄 비행 길이에 따라 달라지므로 조건이 다른 표본을 독립적인 기여율로 바꾸지 않는다.')
add();add('| 조건/방위 | 횡가속 RMS μ±σ(m/s²) | 종가속 RMS μ±σ(m/s²) | 수직가속 RMS μ±σ(m/s²) | CPA 수직 μ±σ(m) |');add('|---|---:|---:|---:|---:|')
for e in ex:
 for b in [0,90]:
  m=group(e,ships[1],b,1)['metrics'];add('| '+f'{e}/{b}°'+' | '+' | '.join(fmt(m['targetAccelerationRms.'+axis])for axis in ['cross','along','vertical'])+' | '+fmt(m['cpaResolvedLiveTarget.vertical'])+' |')
add();add('1순위 권고는 원점 계약 복구다. 그 뒤 같은 입력 정의로 다시 진단해 노후화·포인팅 변경의 남은 필요성을 확인해야 한다. 산포나 신관 수치를 현재 위치 편향을 가리도록 고르지 않는다.')
add();add('## 7. §4–§6 및 산포/파편 구현 제안')
add();add('**범위 결정:** 센서 메타데이터 복구는 기존 센서 보존 조건과 충돌한다. 자연 관측을 쓰는 SAM 결과도 달라질 수 있으므로 “기존 SAM 결과 byte 동일”을 동시에 주장할 수 없다. 별도 선행 단계로 허용받고 해당 자연 탐지 회귀를 수행하는 안을 권고한다. 현재는 센서 수정 0이다.')
add();add('발사 순간의 관측 기반 continuation solve+포인팅 재검사는 구조적으로 타당하지만 원점 오류의 대체 해결책은 아니다. 진단 B의 재계산 시도는 발사 수보다 많다. “3초 사이클당 1회”라는 비용 예상과 strict 현재-틱 해 재검사의 양립은 제품 구현 전에 정리해야 한다. 평균 진단 비용은 아래와 같으며 CPU headless 관측값이다.')
attempts=sum(q['nativeRefreshAttempts']for k,q in s['groups'].items()if k.startswith('B|'));cost=sum(q['nativeRefreshMs']for k,q in s['groups'].items()if k.startswith('B|'));add();add(f'B 재계산 {attempts:,}회, 누적 {cost:.1f}ms, 시도당 평균 {cost/max(1,attempts):.3f}ms. 실제 발사 횟수만큼만 계산한 수치가 아니다.')
add();add('수상 shadow 진단은 native 해/적분으로 5/10/15km, 관측 속도 10m/s, 1초 시차를 비교했다. 횡단은 약 10m의 추가 오차가 생겨 의미가 있다. 수상까지 정합을 적용하는 안을 검토하되 기존 식별·권한·FCQ와 수상 창은 유지해야 한다. 원시 결과는 `evidence/unit-probes/results.json`에 있다.')
add();add('공중 창은 신관 반경에 연동한 대칭 창으로 분리한다. 5인치 신관은 환형 패턴·최초 탐지+지연·통과당 한 난수/신호 누적을 제안한다. SAM의 결정론적 신관은 그대로 둔다. 파편은 띠 안 판정과 띠 축소를 함께 적용한다. 산포는 지시서의 16,459m/44~55m 앵커와 native 200발 이상으로만 보정하며, 공칭 823m/s는 유지한다.')
add();add('현재 실제 cross limit가 1.5m까지 줄기 때문에 6.25m 대칭 반폭 초안이 항상 더 엄격한 것은 아니다. 관측 불확실성 차감과 포신 정렬 예산을 어떻게 결합할지 Phase 1 전에 명시해야 한다. 현재 진단에는 이 초안을 적용하지 않았다.')
add();add('**모든 SIM_TUNED 초안 값과 근거:** [PHASE1_PROPOSAL_DRAFT.md](PHASE1_PROPOSAL_DRAFT.md). 아직 확정/적용값이 아니다. 원점 선행 수정 여부를 결정한 후 Phase 1 착수 보고에서 확정한다. 유효 링은 새 모델의 단발 Pk 측정 전에는 수치를 제안하지 않는다.')
add();add('## 8. 보존·기준값 갱신 검수')
add();add('| 검수 | 결과 |');add('|---|---|')
for title,result in [('정식 행렬','2,400/2,400 · 80조건 각각 30시드 · 중복 caseId 0'),('제품 HTML','C9 체크섬 동일 · B2 게임 HTML 미생성'),('보호 함수/ENV_D','281개 변경 0 · ENV_D 블록 byte 동일'),('native/계측 비교','동일 시드 8조건 결과·RNG·기록 최종 상태 동일'),('바이트 전달 비교','4조건 CDP/loopback HTTP 전체 진단·결과·RNG 동일'),('A–D 재실행','사전 지정 8조건 재현, host elapsed 필드만 제외'),('원점 계약','16 private 무잡음 입력 통과 · 실제 월드 트랙 삽입 0'),('발사 산포 단위 검증','native 반복 위치·속도 동일, 전역 RNG 변화 0'),('도메인','420/420: B1 378건 재사용 + 새 실행 42건. CG 승인 3건 적용'),('EW/H3','새 native EW 94 / H3 195 통과. 승인된 EW 저장 비교 2건만 갱신'),('승인값 guard','다른 HTML/코어, HP 1 변경, 추가 EW 변경 모두 거부'),('게임 계수/저장/CI/main','변경 0 · main 병합/release/tag 생성 0')]:add(f'| {title} | {result} |')
add('| A 정지 통제 보완 | 원래 A 480회 보존 + 보완 480회 전부 재실행 · 발사 시 속도 <1e−6m/s 검사 유지 · non-A 4조건 exact 격리 확인 |')
add();add('CG exact-state 3건은 사용자 §9 승인에 따라 idle/raid/damaged의 이전/새 값을 `approved-gun-baselines.json`에 기록했다. module ID·HE/MFF 질량 노드 분할 및 IEEE-754 합산 차이이며 허용 오차를 넓히지 않았다. EW 변경 경로도 같은 파일에 모두 있다. 기존 B1 원시 실패 보고서와 공통 비교 함수는 보존했다. 재사용 378건의 원래 실행 자료/해시는 `evidence/approved-reference-validation.json`과 B1 REUSE_POLICY에 따른다.')
add();add('## 9. 그림·실행 비용·인계')
for name,title in [('arrival-and-outcomes','Arrival 분포와 ET/검열 비율'),('cpa-projections','종료까지 관측한 CPA 측방/수직 분포'),('et-distance','ET 폭발 거리 분포')]:add();add(f'![{title}](plots/{name}.png)');add();add(f'[SVG](plots/{name}.svg)')
start=load(E/'execution-start.json');begin=datetime.datetime.fromisoformat(start['startUtc']);now=datetime.datetime.now(datetime.timezone.utc);wall=(now-begin).total_seconds();add();add(f'정식 실행 시작 기록부터 보고 생성까지 경과: {wall:.1f}초 ({wall/3600:.2f}시간). 초기화 격리 보강·전달 방식 전환·검증의 중첩 시간이 포함된다. 상세 worker별 시간은 acceptance.json/completion 기록에 있다. CPU 4 quota의 Chromium headless이며 폰 성능 측정값이 아니다.')
add();add('보고서 ZIP에는 이 보고서, 80조건 통계, 발별 원시 JSONL/CSV, 진단 도구, 그래프, 해시/승인값을 넣는다. 게임 HTML을 리포트 ZIP에 섞지 않는다. Phase 0에서는 게임을 바꾸지 않았으므로 새 B2 HTML ZIP을 만들지 않는다. 원격 검증 기록은 `REMOTE_READBACK.json`에서 별도로 확인한다.')
add();add('지시서 §2 및 §12: **“push 후 멈추고 사용자 승인을 기다린다.”** 이 요구에 따라 Phase 0에서 멈춘다. 결정이 필요한 핵심은 원점 계약 복구를 별도 선행 수정으로 허용할지다.')
(B/'PHASE0.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({'written':'PHASE0.md','cases':s['cases'],'shots':s['shots'],'budgetClosureMaxM':closure,'wallS':wall}))

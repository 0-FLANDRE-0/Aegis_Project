"""Assemble final diagnostic report after all bounded native cases complete."""
from pathlib import Path
from datetime import datetime,timezone
import json,statistics,collections,subprocess,hashlib,math
P=Path(__file__).resolve().parent;R=P.parents[3];A=P/'analysis';E=P/'evidence'
def load(n):return json.loads((A/n).read_text())
def table(headers,rows):return '\n'.join(['| '+' | '.join(headers)+' |','|'+'|'.join(['---']*len(headers))+'|']+['| '+' | '.join(str(v).replace('|',' / ')for v in r)+' |'for r in rows])
def fmt(x,n=3):return '—'if x is None else f'{x:.{n}f}'
c=load('c1-sensitivity.json');d=load('d1-cases.json');damage=load('damage-cases.json');control=load('controls-cases.json');eq=json.loads((E/'equivalence.json').read_text());progress=load('progress.json');assert progress['c1']==90 and progress['d1']==30 and progress['controls']==1 and eq['pass']and len(eq['pairs'])==4
base='6d306849f290f987cd39c31c901adb4478b07edd';product='Aegis_SIM_v48_WIP_CG_TURRET_A.html';body=(R/product).read_bytes();original=subprocess.check_output(['git','show',base+':'+product],cwd=R);assert body==original
assert not subprocess.check_output(['git','diff','--name-only',base],cwd=R).decode().strip()
causal=load('protection-causality.json');assert len(causal)==4 and all(x['nativeSignatureEqual']and x['rngEqual']for x in causal)
assert len(load('historical-comparison.json'))==40 and all(x['equal']for x in load('historical-comparison.json'))
hp0=[x for x in damage if x['hp']==0];assert len(hp0)==4
errors={f.name:json.loads(f.read_text())['errors']for f in E.glob('*-execution.json')};assert all(not x for x in errors.values())
now=datetime.now(timezone.utc);clock=json.loads((P/'TASK_CLOCK.json').read_text());elapsed=(now-datetime.fromisoformat(clock['startedUtc'])).total_seconds()if'startedUtc'in clock else (now-datetime.fromisoformat(clock['startUtc'])).total_seconds();assert elapsed<10800
eqtab=table(['조건','시드','ON/OFF 상태 서명','게임 RNG'],[[q['case']['ship'][:2]+f" {q['case']['bearing']}°",q['case']['seed'],'동일',str(q['runs'][0]['rng'])]for q in eq['pairs']])
ctab=table(['방위','회차','사격 회차','20mm 평균','피격','평균 HP'],[[str(q['bearing'])+'°',q['n'],q['firingCases'],fmt(q['gunRoundsMean'],1),q['shipHits'],fmt(q['hpMean'],3)]for q in sorted(c,key=lambda q:q['bearing'])])
arcs=load('arc-summary.json');atab=[]
for el in[-1,0,2,5]:
 for side,m in[('우현',1),('좌현',2)]:
  a=next(x for x in arcs if x['mountId']==m and x['elevationDeg']==el)
  for origin in['axis','muzzle']:
   spans=[v for v in a['blockedIntervals'][origin+'300']if v[0]<10 and v[1]>-10];atab.append([side,str(el)+'°',origin,'없음',', '.join(f'{lo:.1f}~{hi:.1f}°'for lo,hi in spans)])
atab=table(['마운트','고각','시작점','2m 차단','300m 전방 부근 차단 표본'],atab)
deadtab=table(['시드','피격/기폭 구획','선체 항','추진 항','발전 항','CDC 항','합계→HP','물/유폭'],[[x['seed'],x['detonationPart'],fmt(x['statusTerms']['hull']),fmt(x['statusTerms']['propulsion']),fmt(x['statusTerms']['power']),fmt(x['statusTerms']['cdc']),fmt(sum(x['statusTerms'].values()))+' → 0','0m³ / 0회']for x in hp0])
vtab=table(['시드','20mm 보호 시작','RAM 보호 시작','피격 시각','20mm/RAM','최종 HP'],[[q['seed'],fmt(q['firstGunProtectedVetoS']),fmt(q['firstRamProtectedVetoS']),fmt(q['impactS']),f"{q['gunRounds']}/{q['ramRounds']}",fmt(q['hp'])]for q in d if q['firstGunProtectedVetoS']is not None])
causaltab=table(['시드','마운트','OWN_RAM 최초 연관(s)','ASM 복귀(s)','복귀 뒤 ownFireEvidence','원 결과/RNG'],[[q['seed'],e['mount'],fmt(e['ownAssociated']['tS']),fmt(e['asmReturnsWithOwnFlag']['tS']),True,'동일']for q in causal for e in q['events']])
ordinary=next(x for x in damage if x['seed']==419011);c0=control[0]
dt=table(['시드','최초 트랙/확정(s)','Gun SEARCH/TRACK/ENGAGE(s)','첫 20mm/RAM(s)','20mm/RAM','피격/HP','분류'],[[r['seed'],fmt(r['firstTrackS'])+'/'+fmt(r['confirmedAsmS']),'/'.join(fmt(r[k])for k in['gunSearchS','gunTrackS','gunEngageS']),fmt(r['firstGunFireS'])+'/'+fmt(r['firstRamFireS']),f"{r['gunRounds']}/{r['ramRounds']}",f"{r['shipHits']}/{r['hp']:.2f}",r['category']]for r in d])
execution={f.stem:json.loads(f.read_text())for f in E.glob('*-execution.json')};etimes=table(['실행 묶음','벽시계 초','오류'],[[k,fmt(v['elapsedS'],1),len(v['errors'])]for k,v in sorted(execution.items())])
hash0=max(abs(max(0,100-min(100,sum(x['statusTerms'].values())))-x['hp'])for x in damage)
checks={'selectedBase':base,'productByteIdentical':body==original,'productSha256':hashlib.sha256(body).hexdigest(),'coefficientsChanged':False,'expectationsChanged':False,'c1Runs':90,'d1Runs':30,'equivalencePairs':4,'equivalencePass':True,'controlRuns':1,'additionalProtectionRuns':4,'totalAcceptedCombatRuns':133,'staticDirections':28800,'rawRayEvaluations':115200,'historicalComparisons':40,'historicalDifferences':0,'hpZeroRuns':4,'nativeHpFormulaMaxError':hash0,'supplementalSignatureMatches':4,'pageErrors':sum(len(x)for x in errors.values()),'elapsedSIncludingEarlierBaseWork':elapsed,'deadlineUtc':clock['deadlineUtc'],'completedUtc':now.isoformat(),'newGameHtml':False,'productImplementation':False,'mainMerged':False,'releaseOrTag':False}
(P/'VALIDATION.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
text=f'''# CIWS_DMG_A — CG 정면 사각 / DDG 단발 피해 진단

**결론: 제품 수정 없이 진단을 완료했다.** CG 정면 차단은 모델 구조물 광선 검사에서 재현됐다. DDG에는 별도의 C55 로컬 파일 연관 결함이 있다. 아군 RAM 측정이 ASM 파일에 잠시 붙은 뒤 `ownFireEvidence`가 남아 자위 사격을 막는다. HP 0 네 건의 직접 원인은 침몰·침수·유폭이 아닌 `computeShipStatus`의 가중 손상 합계 포화다. 수정은 적용하지 않았다.

## 1. 기준·방법·동등성

사용자의 추가 지시에 따라 원래 main/B2B 기준을 **미병합 cg-turret-a**로 변경했다. 기준 커밋 `{base}`, 게임 `{product}`, SHA-256 `{hashlib.sha256(body).hexdigest()}`. 게임 HTML은 기준 Git blob과 byte 동일하고, 새 게임 HTML·제품 계수·기대값 변경은 0이다. `ciws-dmg-a`는 이 커밋에서 분기했다. [기준 변경 기록](BASE_CHANGE.json), [제품 출처](source-provenance.json), [검수 기계 판독본](VALIDATION.json).

CG 9방위×10=90회, DDG 30회, 계측 ON/OFF 4조건×2=8회, CG 대조 1회, 보호 연관 인과 계측 4회로 **133회**를 실제 게임 fixed tick에서 실행했다. 정적 계산은 2문×4고각×3,600방위=28,800방향, 시작점/거리별 원시 광선 115,200회다. 게임의 RF·유도·피해 경로를 대체하지 않았다. [실행 도구/입력](README.md), [계측 코드](diagnostic.js).

{eqtab}

게임 RNG뿐 아니라 로컬 센서·조준·사격 RNG, 선체/모듈/수밀 구획/강도/생존 상태와 잔탄을 포함한 서명이 동일하다. 호스트 시각 필드만 제외했다. 새 기준의 4개 OFF 서명은 기준 변경 전 main 측정과도 동일했다. 추가 인과 계측 4회도 DDG 원 결과·RNG와 정확히 일치했다. [동등성 원본](evidence/equivalence.json), [추가 계측 비교](analysis/protection-causality.json).

이번 0° CG 10회와 DDG 30회는 과거 GUN_B2 Phase1의 **40개 동일 입력 결과·최종 RNG와 모두 일치**, 차이 0이다. 과거 CG 30회 자체는 피격30, 탄0, 평균HP 50.953이었다. 새 기준 CG 0° 10회 평균은 50.185다. 서로 다른 표본 수를 혼동하지 않는다. [과거 원본 발췌](evidence/historical-selected.json), [40회 비교](analysis/historical-comparison.json), [과거 CG30 요약](analysis/historical-c1-30.json).

## 2. C1: 사각 정량화와 방위 민감도

좌표는 함 로컬 미터(+X 선수, +Y 우현, +Z 위)다. 회전축은 `(3.14, ±6.06, 18.3721)`, 포구 전방 오프셋은 약1.64677m다. runtime 센서/하드포인트 높이는18.1221m로 회전축보다0.25m 낮다. 아래 정적 비교는 요청대로 **회전축 대 실제 등록 포구**다. 각 경계는 0.1° 격자의 첫/마지막 차단 표본이며 그보다 정밀한 실함 값이 아니다. [등록/경계](analysis/arc-summary.json), [전체 0.1° CSV](analysis/arcs-0.1deg.csv).

{atab}

모든 고각·두 시작점에서 **2m 광선 차단은 0**이다. 고각0°의 정면300m 광선은 회전축 기준 우현에서19.197m 앞(`x=22.3373m`), 좌현에서6.314m 앞(`x=9.4541m`)의 `DECKHOUSE:0`에 닿는다. 포구로 옮기면 각각17.550m/4.661m 앞에서 같은 구조물에 닿는다. 따라서 포구 시작점 변경만으로 정면 차단은 해소되지 않는다. [원시 arc-0-0](evidence/arc-0-0.json), [arc-1-0](evidence/arc-1-0.json).

사전 가설 중 “정확히0°에서만 두 문 모두 막힘”은 부정확했다. native gate의 전방 공통 차단 표본은 고각−1°에서−1.4~+1.8°, 0°에서−1.1~+1.1°, +2°에서−1.0~+0.5°다. +5°에서는 전방±15° 안의 공통 차단이 없다. 국부 마스트/연돌 차단도 포함한 결과다. [양쪽 공통 사각](analysis/both-mounts-forward.json).

![CG 전방 사각](figures/cg-forward-occlusion.png)

90회 민감도 결과:

{ctab}

피격 수는 기존 `shipHitHistory` 기준이며, CIWS에 손상된 불발탄/잔해 접촉도 포함한다. 피격했어도 HP100인 경우를 요격 실패 피해와 동일시하지 않는다. “사격 회차”는 두 팰렁스 중 한 문이라도 실제 탄을 소모한 회차다. 0°·±1°는 센서의 구조물 방향 검사에서 접촉 생성부터 막히므로 FC 상태에 들어가지 않는 회차가 반복된다. ±2°부터는 개방된 쪽의 사격이 나타나며, 이후 결과에는 실제 FC·탄도·피해도 함께 작용한다. 2기 이상 분산 스폰의 효과는 이번에 재측정하지 않았다. [90회 요약](analysis/c1-cases.csv), [전체 원시 로그](evidence/c1.jsonl.gz).

![C1 방위 민감도](figures/c1-sensitivity.png)

실함 대조: 공개 제원 전폭16.8m와 모델16.76m는 부합하고, 해군 개장 후 사진의 중앙부 양현 배치는 정성적으로 일치한다. **정확한 CIWS 좌표·해당 높이의 상부구조물 국부 폭·실함 정면 사각은 미확인**이다. 사진으로 모델을 실함 좌표라고 인증하지 않았다. [공개 자료와 원본 사진](PUBLIC_REVIEW.md), [모델 geometry](evidence/geometry-metadata.json).

## 3. 사각 개방 기동의 현황

현재 게임에는 H2 사각 개방 평가가 이미 있다. `maneuverCoverageNativeH2`가 native CIWS/SPG 사계를 평가하고 `maneuverPlanH2`가 좌/우30°·60° 및 속력 후보를 비교한다. 실제 적용은 native 속력·타각 명령이다. 자함 기본설정 OFF, NPC 기본 ON이며 H1 활성/AUTO, 수동 NAV 비점유 등 조건이 필요하다. 이번 기존 시험은 **MANUAL + 자함 H1/H2 OFF**이므로 사각을 열지 않는다. [실제 실행 함수](evidence/native-sources.json), [소스 발췌 5595~5728](source-excerpts.txt), [시험 정책 원본](evidence/d1.jsonl.gz).

PR52~55는 조사 시점 모두 open/unmerged였다. PR52는 방어 유틸리티/AUTO 전제, **PR53은 사각 개방 그 자체**, PR54는 대수상 공격 확장, PR55는 H2 방어 기동을 참조하는 팀/편대 계층이다. PR이 미병합인 사실과 누적 게임 HTML 내부 기능 존재는 별개다. 고정 head 코드까지 확인했으며 병합하거나 코드 이식하지 않았다. [PR 메타데이터](pr-context.json), [파일/함수 조사표](analysis/pr-arc-opening-audit.json), [PR52–54 코드](pr-sources.json), [PR55 코드](pr55-team-source.json).

## 4. D1: 30회 방어 타임라인과 저사용 원인

입력은 원래 Phase1과 같다: DDG-119, 방위90°, Kh-35U1기, 11km, AutoAAOFF, 시드419010~419039. **평균8.6은 20mm 6.1발 + RAM 2.5발**이었다(총183발/75발). 두 종류를 합친 기존 카운터를 팰렁스 탄 수로 해석하면 안 된다. SM/ESSM 발사0은 기존 시나리오 MANUAL 설정의 결과이며 VLS 고장으로 판정하지 않는다. [회차 CSV](analysis/d1-cases.csv), [원본30회](evidence/d1.jsonl.gz).

| 주 분류(중복 없음) | 회차 | 해석 |
|---|---:|---|
| SeaRAM이 3km 진입 전 격추, 20mm0 | 10 | 앞단 요격으로 팰렁스 실제 사격 불필요 |
| 3km 안에서 SeaRAM 격추, 20mm0 | 7 | 추적·FC/보호 관문 때문에 먼저 20mm를 내보내지 못함. 3회는 선택 파일 보호 veto도 기록 |
| 선택했던 로컬 파일의 보호 veto 후 피격 | 10 | 팰렁스 사격이 차단/종료됨. HP0 네 건 포함 |
| 간헐적인20mm 사격, 위 분류 제외 | 3 | 2회 피격, 1회 SeaRAM 격추. 지속 사격·명중을 보장하지 않음 |

보호 veto는 총13회(10회 피격, 3회 생존)에 있었고, raw 로그의 “가장 먼저 생성된 파일” 대신 **실제 선택했던 파일 ID**를 따라 셌다. 20mm183발에서 `applyPhalanxProjectileHit` 호출은0이었다. RAM75발 종료는 PASSED_CPA52, PROX_DETONATION_KILL18, SEA_IMPACT4, PROX_DETONATION_MISS1이었다. 이 진단에서 신관/Pk·FC 계수를 바꾸지 않았다. [분류표](analysis/d1-classification.json), [상태·관문 해석 방법](analysis/gate-method.json), [원시 사건](evidence/d1.jsonl.gz).

관문이 닫힌 표본은 native `phalanxFireControlGate`의 조준 중심 오차와 predicted miss 조건으로 나누었다. 중심 오차가 이미 초과하면 predicted miss도 동시에 실패했는지는 단정하지 않는다. 중심 조건을 통과했는데 native ready=false인 경우만 predicted-miss 단독 실패로 분류했다. ready=true 한 틱도 3km/품질/상태 체류/보호 조건을 대체하지 않는다. 회차별 거절 표본 수는 CSV, 탐색/추적 전환과 중단은 각 `analysis/d1-SEED-timeline.csv`에 있다.

{dt}

모든 시각은 native fixed tick 기준이다. 함수 내부 계측과 tick 종료 계측은 최대1틱(16.67ms) 차이가 날 수 있다. 거리별11/10/8/6/4/3/2/1/0.5/0.1km 통과, cue, 각 mount SEARCH/TRACK/ENGAGE/IDLE, 사계 차단과 재개, 탄 소모·결과는 회차별 타임라인과 원본에 보존했다.

![DDG 탄수/HP](figures/d1-ammunition-hp.png)

### 4.1 확인된 C55 보호 전이 결함

`c55SensorSweep`는 위치 게이트로 측정을 로컬 파일에 연관하고 `best.ownFireEvidence = best.ownFireEvidence || src.own`을 실행한다. `c55AssociateCms`는 이 값이 있으면 FRIEND 보호를 부여한다. **다른 물체의 측정으로 돌아와도 그 파일의 own-fire 근거를 해제/분리하는 계약이 없다.** 근접한 outgoing RAM과 incoming ASM이 한 파일을 번갈아 갱신하면 이 근거가 오염되어 남는다. 전역 센서 트랙의 HOSTILE이 FRIEND으로 바뀌어야만 발생하는 현상이 아니다. [원본 소스 37162~37230](source-excerpts.txt), [추가 계측 코드](protection-trace.js).

seed419018에서 RAM3은32.35s에 SeaRAM 파일, 32.433s에 팰렁스 파일에 붙었다. 32.467s에는 팰렁스 파일이 다시 ASM:2를 읽지만 ownFireEvidence=true/FRIEND가 남았다. RAM3은32.7s에 PASSED_CPA 종료, 이후에도 보호는 남아38.133s 피격까지 20mm 추가 사격을 막았다. 이 전이 자체는 결함으로 확인했지만, 수정 후 해당 발이 반드시 요격된다고 추정하지 않는다.

{causaltab}

HP0 네 시드 모두 같은 OWN_RAM→ASM 복귀 후 보호 잔류가 관찰됐고, 추가 계측4회는 원래 결과/전체 상태 서명/RNG와 일치했다. [인과 사건 발췌](analysis/protection-causality.json), [419018 원시 로그](evidence/protection.jsonl.gz), [나머지3개 원시 로그](evidence/protection-hp0.jsonl.gz).

{vtab}

![419018 타임라인](figures/d1-419018-timeline.png)

SeaRAM/팰렁스 우선순위: 공통 파일에 진행 중 RAM이 있으면 점수×2.5의 낮은 우선순위를 주는 코드가 있으나 두 mount의 로컬 파일 ID는 서로 다르다. 이것은 양 무장 사이의 강제 사격 금지가 아니다. 419018은 RAM3 비행 중32.367/32.433s에 팰렁스2발을 실제 발사했다. 보호 전이와 단순 “RAM 우선이라 대기”를 혼동하면 안 된다. [native c55ContactAudit/updateCIWS](evidence/native-sources.json), [419018 타임라인](analysis/d1-419018-timeline.csv).

## 5. D1: HP0 직접 원인과 피해 분해

네 건 모두1번의 `COMPARTMENT_BLAST_AUTHORITY` 이벤트가 승인됐고 같은 이벤트ID를 반복 적용한 기록은 없다. 적용 parts는 direct kinetic/spall과 authority blast를 합친 값이며 `damageFloodImpactV48Wip12E`의 기존×3.5 모듈 변환을 거친다. legacy blast 비교표는 기록용이며 authority blast와 다시 더하지 않는다. terminal cascade는 `mergeDamage:false / PREACCOUNTED_OBSERVATION_ONLY`, 강도 입력의 generic explosiveMassKg는0으로 blast 에너지 재적용을 피한다. [피해 경로 발췌](source-excerpts.txt), [회차별 채널/에너지/수밀/화재/강도 원본](analysis/damage-cases.json).

HP 계산은 `max(0,100-min(100,1.2*선체구조손상 + .4*추진손상 + .3*발전손상 + .1*CDC손상))`이며 survival.irreversible도 별도0 조건이다. 선체구조손상에는 skin 손상과 longitudinal strength loss가 결합된다. 네 건의 irreversible/lost는 모두false, survival은 NORMAL이었다.

{deadtab}

각 항은 이미 가중치가 곱해진 HP 계산 항이다. 전체12피격에서 이 식으로 재구성한 최종HP 오차 최대 `{hash0:.3g}`였다. 네 건 모두 물0m³, 수면 위 개구부, VLS/탄약고 유폭0이다. 화재는1~3구획에 발화했지만 피격 직후 같은 틱에 HP가0이 되었으므로 장시간 연소·침수 누적이 직접 원인은 아니다. 원래 시나리오가 피격 즉시 종료하므로 이후 침몰 시간을 측정했다고 주장하지 않는다. [피해 요약 CSV](analysis/damage-summary.csv), [전체 native 이벤트](evidence/d1.jsonl.gz).

![HP 가중 합계](figures/damage-hp-terms.png)

seed419018은 raw parts 합490.700 중 authority blast447.423, 합쳐진 kinetic/spall 잔여43.278이었다. 제1·제2 보일러와 제1발전실 등 인접/겹치는 legacy 기능 박스가 함께 포화되고, 선체/강도 항73.593에 추진26.667·발전17.049·CDC0.229가 더해117.538→HP0이 된다. 각 blast channel 숫자는 모델 응답 성분이며 단순 합이 최종 dmg/HP가 되는 것은 아니다. 공개145kg 탄두와 커널의90kg TNT-equivalent를 같은 수치로 해석하지 않는다. [개별 모듈/채널](analysis/damage-cases.json), [공개 정보 구분](PUBLIC_REVIEW.md).

에너지 ledger partition 오류는0, 관측한12피격의 closure error는 약0.0015~0.0655J로 chemical input376,560,000J에 비해 작았다. 이것은 solver 내부 에너지 장부가 닫힌다는 증거이며, HP 계수의 게임 설계 적절성을 입증하지 않는다. 같은 폭발을 두 번 적용한 계산 오류는 이번 로그/코드에서 발견하지 못했다. **HP=함 생존과 임무 수행능력을 한 수치에 묶은 기존 집계 설계가 이 현상의 직접 대상**이다.

대조: 같은419018/90°를 CG로 바꾸면 팰렁스{c0['gunRounds']}발, 피격0, HP100, PHALANX_STRUCTURAL_FAILURE로 위협이 사라졌다. 원래 조건을 유지했으므로 CG에 강제로 명중시키지 않았다. 따라서 DDG/CG 동일 폭발 피해 비교는 미성립이다. 일반 피격 DDG419011은 CDC 부근 기폭, 가중합{sum(ordinary['statusTerms'].values()):.3f}, HP{ordinary['hp']:.3f}였다. 부위별 기여 차이가 있으며 유폭/침수는 이 사례도0이다. [CG 대조](analysis/controls-cases.json), [CG 원시 로그](evidence/controls.jsonl.gz), [419011 타임라인](analysis/d1-419011-timeline.csv).

## 6. 수정 제안 비교 — 전부 미구현

| 제안 | 기대 효과/한계 | 근거·수치 구분 |
|---|---|---|
| **C55 own-fire 근거의 파일 연관 수명 계약 복구** | outgoing/incoming 측정이 교차해도 다른 물체의 영구 FRIEND로 전이되지 않게 해야 한다. 측정 연속성/별도 접촉 분리와 알려진 자함 발사 보호 근거의 귀속·만료를 검토한다. actual truth로 적만 보호 해제하는 예외나 FRIEND 관문 제거는 제안하지 않는다. 가장 우선할 결함이다. | 함수 `c55SensorSweep/c55AssociateCms`, HP0 네 시드 인과 로그. 새 임계값 제안 없음. |
| CG far ray 시작점 포구화 | 실제 발사점과의 일관성은 좋아진다. 정면 사각은 남고 다른 경계는 일부 바뀐다. near 2m 검사를 그대로 포구로 이동하면 축→포구 사이 포신 간섭을 놓칠 수 있으므로 별도 계약 필요. | 약1.64677m는 MODEL_REGISTRATION, 범위2/300m는 기존 SIM_TUNED. |
| CG 마운트/국부 구조물 좌표 보정 | 실제 오차가 검증되면 구조물 가림이 달라질 수 있다. 지금은 치수 있는 공개 근거가 부족해 이동량/폭 축소를 확정하지 않는다. | 공개 전폭만 부합. 정확한 사계·국부 폭은 미확인. |
| 사각 유지 + 자함 arc-opening 운용 | 실제 기동 한계 안에서 위협 측으로 사계를 열 수 있다. 기존 H2가 있으므로 무조건 새 AI를 붙일 사안은 아니다. 자함 활성/수동우선/AUTO 정책·UI를 별도 확인해야 한다. | 기존 H2의30/60° 후보는 SIM_TUNED, 새 수치 제안 아님. |
| 시험 방위 분산 | 정면 단일 기하와 일반 방어 성능을 구분한다. **0° 회귀를 제거/제외하지 않고** 여러 방위를 함께 유지한다. | 이번9방위는 시험 설계값이며 실함 사각 제원이 아니다. |
| HP 집계/생존 상태 계약 검토 | 기능 상실과 실제 침몰/복원성 상실을 구분하도록 HP 계산/표시·소비 경로를 검토한다. 부위 피해×3.5나 강도/화재 계수를 임의로 낮춰 결과를 맞추지 않는다. | 대상 `computeShipStatus`, `damageFloodTickV1`, impact 후 shipHP 대입. native 생존 NORMAL인데 HP0인4건. |
| 기능 박스·폭발 응답 귀속 감사 | 같은 세부 구획의 하중이 여러 legacy 기능 박스에 연결되는지 형상/시스템 매핑을 감사한다. 이번에는 중복 폭발 적용이 입증되지 않았으므로 이를 확정 버그로 고치지 않는다. | `wip12eAuthorityParts`, `wip12eRev4MergeImpactDamageParts`, `damageFloodImpactV48Wip12E`, `getShipSystemDamage`. |

## 7. 실행 비용·제약·마감

{etimes}

C1/D1은 자원 한도 내 별도 브라우저 프로세스로 병행했다. 모드 시간 합은 전체 벽시계가 아니다. 원래 시작 `{clock.get('startedUtc',clock.get('startUtc'))}`부터 이 보고서 생성까지 `{elapsed:.1f}s`(약{elapsed/60:.1f}분), 3시간 상한 이내다. 기준 변경 전 작업 시간도 제외하지 않았다. fixture 작성 오류와 재시도는 [DEVELOPMENT](DEVELOPMENT.json), 중지된 main 기준 결과는 별도 archive다. 최종 수용 측정의 page/core 오류0. 제품 byte 변경0, 기대값 갱신0. 전체420 도메인 회귀나 모바일 FPS를 이번에 새로 실행했다고 주장하지 않는다.

보고서·원시 로그·도구를 `ciws-dmg-a`에 push하고 원격 artifact readback 뒤 **중단**한다. main/원본 브랜치 병합·release/tag·결함 수정은 하지 않는다. 사용자 판단이 필요한 다음 우선순위는 C55 보호 전이 복구, 그 다음 HP/생존 집계 계약 검토다. CG 좌표 변경은 공개 근거가 먼저 필요하다.
'''
(P/'REPORT.md').write_text(text)
status=json.loads((P/'BUILD_STATUS.json').read_text());status.update({'diagnosticsComplete':True,'acceptedCombatRuns':133,'equivalencePass':True,'historicalDifferences':0,'completedUtc':now.isoformat()});(P/'BUILD_STATUS.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(checks,ensure_ascii=False))

"""Publish only verified final measurements; preserve all original receipt hashes."""
from pathlib import Path
import gzip,hashlib,json,os,re,subprocess
H=Path(__file__).resolve().parent;R=H.parents[3];C=R/'docs/envelope/C';E=H/'evidence'
def read(p):
 p=Path(p)
 if not p.exists():p=p.with_suffix(p.suffix+'.gz')
 return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
st=read(E/'static-final.json');bridge=read(E/'candidate-data-only.json');env=read(C/'evidence/verification/results-verification.json');path=read(C/'evidence/path-final/path-all4.json');bounds=read(C/'evidence/boundaries/boundaries.json');status=read(C/'evidence/status/status.json');domain=read(E/'domain-acceptance.json');ui=read(E/'ui/ui.json');live=read(E/'live-acceptance.json');obs=read(E/'observed-world/observed-world.json');truth=read(E/'truth120/truth120.json');cause=read(E/'causality120/causality120.json');follow=read(E/'causal-off-followup/causal-off-followup.json');validation=read(E/'validation60-acceptance.json');gains=read(E/'live-before-after.json');s0=read(C/'stage0/verification.json');s1=read(C/'stage1/verification.json');table=read(C/'ENVELOPE_TABLE_C.json');changes=read(H/'changes.json');archive=read(H/'archive-verification.json')
html=R/'Aegis_SIM_v48_WIP_RANGE_A.html';raw=html.read_bytes();sha=hashlib.sha256(raw).hexdigest();size=len(raw)
checks={'R1':st['pass']and len(changes['changes'])==8 and env['checks']['R1.mrEssm60NativeTracesUnchanged'],'R2':s0['pass']and s1['pass']and env['pass'],'R3':path['pass']and all(all(x==0 for x in q['maxError'].values())for q in path['records']),'R4':all(q['pass']for q in [domain,ui,live,obs,truth,cause,validation,bridge])and domain['checks']==420 and len(ui['checks'])==88 and len(live['checks'])==16 and gains['newVsBaselineOnHitLosses']==0 and follow['completed']and follow['counterfactualMiss'],'R5':env['pass']and len(table['rows'])==96}
assert all(checks.values())and status['pass']and bounds['pass']and archive['pass'],checks
assert not subprocess.check_output(['git','diff','9a6838a','--name-only','--','docs/envelope/A','docs/envelope/B','docs/missile/termination/A'],cwd=R,text=True)
accept={'schema':'AEGIS_RANGE_A_ACCEPTANCE_1','pass':True,'checks':checks,'htmlSha256':sha,'profileHash':table['profileHash'],'nativeNamedFunctionsUnchanged':st['nativeFunctionCount'],'domainChecks':420,'uiChecks':88,'terminationChecks':16,'nativePathSamples':sum(q['sampleCount']for q in path['records']),'boundaries':len(bounds['records']),'remotePublicationReceiptSeparate':'remote-publication.json'};(E/'acceptance.json').write_text(json.dumps(accept,indent=2))
def embed(src):
 t=src.read_text().split('\n',1)[1]
 def link(m):
  target=m[2]
  if target.startswith(('https:','http:','#')):return m[0]
  return m[1]+os.path.relpath((src.parent/target).resolve(),H)+m[3]
 t=re.sub(r'(!?\[[^\]]*\]\()([^\)]+)(\))',link,t)
 return re.sub(r'^(#{2,5}) ',r'\1# ',t,flags=re.M)
lines=['# RANGE_A + ENV_C — 최종 게임 엔진 보고','',f"HTML `{html.name}` · {size:,}bytes · SHA-256 `{sha}`",'','최신 ALL4_TERM `9a6838aade07c37262453e21cfe415d04d123d8c` 위 누적 작업이다. 0단계 측정·보고 뒤 지정한8개 설계 사거리 숫자만 정렬했다. 정렬 후6조건의 목표 최대 명중 거리는 달성하지 못했고 일부 정지 표적 최대 거리는 크게 줄었다. 이 결과를 보존하며 추진/항력/유도/배터리/해면 판정은 추가 조정하지 않았다. 모든 새 수치는 SIM_TUNED 게임 설계값이고 측정값은 GAME_ENGINE_COMPUTED다.','', '## 1. 변경 전500km 측정','',embed(C/'stage0/REPORT.md'),'','## 2. 변경값과 근거','','| 레지스트리 | 기종 | 필드 | 이전→새 값(km) | 기준 |','|---|---|---|---:|---|']
for q in changes['changes']:lines.append(f"| {q['registry']} | {q['weapon']} | {q['field']} | {q['old']}→{q['new']} | {q['rationale']} · SIM_TUNED/USER_DESIGN_TARGET_RANGE_A |")
lines+=['','파생 계산은 기존 `_samEstimateRmaxKm`, `_samBuildAdaptiveTrajectoryPlan`, `loftB4UpdatePlan`, `gameB4ReplanShelf`가 같은8값을 읽는다. 함수나 다른 분모/계수는 바꾸지 않았다. `rangeGoalKm`는 B4 계획·표시 메타데이터이며 인위적인 비행 종료 반경이 아니다.','',f"명명 네이티브 함수 {st['nativeFunctionCount']:,}개와 나머지 live source는8숫자 역치환으로 동일함을 확인했다. 자함/NPC 문맥이 공유 레지스트리를 읽으며 중복 패치를 적용하지 않았다. SAM_MISSILE_PROFILES, 추진/항력/질량/연소/시커/Kappa/신관/배터리/종료기와 MR/ESSM 설정은 그대로다. MR/ESSM60궤적의 기존 필드도 ENV_B와 동일하다.",'','독립적인 AI/교전계획 `effectiveRangeKmGameplay`260km는 유지했다. 이는 지정된 로프트값에서 계산되는 필드가 아니며 이번에는 발사/교전계획 관문을 변경하지 않았다.','', '## 3. 정렬 후6조건 — 목표 부족분','',embed(C/'stage1/REPORT.md'),'','## 4. ENV_C 전체 표·전후 비교·퇴행 재확인','',embed(C/'REPORT.md'),'','## 5. 저고도 해면 충돌 조사 — 수정 없음','',embed(C/'results/LOW_ALT_INVESTIGATION.md'),'','## 6. 검수 R1–R5와 실행 시간','','| 검수 | 결과 |','|---|---|',f"| R1 범위·코드 보존 | PASS ·8숫자만 변경 · {st['nativeFunctionCount']:,}명명 함수 byte 동일 · 자산0–12 동일 · MR/ESSM60기존 궤적 동일 |",f"| R2 독립 반복 | PASS · stage0 {s0['bytes']:,}bytes / stage1 {s1['bytes']:,}bytes / 전체ENV_C {env['records'][0]['bytes']:,}bytes 각각2회 동일 |",f"| R3 실제게임/진단 경로 | PASS · {accept['nativePathSamples']:,}샘플 · 시간/x/y/z/속도/Mach 최대 오차0 |",'| R4 기존 회귀 | PASS · 도메인420/420(15suites) + UI88/88 + 종료기16/16 · 자연탐지/전체월드/WebGL8발29검사 |','| R5 빈칸/원인 | PASS ·96조건/120궤적 완전 · 성공 시 실제요격점·실패 시 네이티브 사유 · 모든 궤적 유한값 |','',f"최종 Chromium 경계 {len(bounds['records'])}건의 성공/실패·사유 일치. Node/Chromium 최대 최근접 차이 {bounds['maxClosestDeltaM']:.12g}m, 속도 차이 {bounds['maxSpeedDeltaMps']:.12g}m/s. 이는 R3의 동일 Chromium 네이티브/사본 오차0과 다른 비교다.",'',f"120초/7200ticks DDG 무표적 출항의 truth/RNG 해시는 기준/후보 동일 `{truth['records'][0]['truthSha256']}`. 실제 미사일 궤적이 바뀐 조건은8개 설계값 변화에 따른 결과이며 정적 역치환과 전후 궤적으로 연결했다. 전투120초(자연 SPY/AI, SM-6 100km/5km, seed12002)에서는 기준 해시 `{cause['records'][0]['truthSha256']}`와 정렬판 `{cause['records'][1]['truthSha256']}`가 달랐으며, 버리는 시험 페이지에서8값만 복원하자 `{cause['records'][2]['truthSha256']}`로 기준판과 정확히 같았다. 이 전투 해시는 ownship 물리/재고/동역학·월드 엔티티 물리 스칼라·전역RNG의 명시된 투영이며 UI/표시/성능 캐시는 제외했다. 이 대조는 변화의 원인을 검증하며 해당 사격의 정상 명중을 주장하는 시험은 아니다. 같은 정렬판의 종료기OFF 반사실 사격도 끝까지 비격추(LOW_SPEED {follow['afterAction']['missile']['lifeS']:.6f}s)였다. ON은 POST_CROSS {cause['records'][1]['afterAction']['missile']['lifeS']:.6f}s로 먼저 정리됐다. 따라서 이 추가 실제AI 조건에서 OFF가 명중할 사격을 ON이 잘랐다고 해석하지 않는다.",'',f"정상240발은 OFF/ON 각각 {live['records']['normalNativeHitsOff']}/{live['records']['normalNativeHitsOn']}명중, 조기종료0. 기존 ALL4의83명중 보존+2명중 회복. 대체지원36발도 조기종료0. 추가60사격에서는 동일 조건 A/B22쌍을 식별해 조기종료0을 확인했다. 서로 다른 단독 고장 시나리오를 A/B쌍으로 비교하지 않았다.",'','RF 소실/재획득/미획득, 배터리8건, 정식VLS4건의 기존 판정을 유지했다. 배터리 경계 시험은 실제 비행 후 시계 체크포인트 방식이며 자연480초 비행 인증으로 부르지 않는다. ENV 목표거리 사격의 자연 배터리 소진과 구분한다. 자연 SPY 8발은 목표 AI를 유지하고 초기 채프 쿨다운만 길게 설정했다.','', '### 자연 탐지→정식 발사→전체 시뮬레이션','','| 기종 | 종료기OFF | 종료기ON | 표적 결과 |','|---|---|---|---|']
for i in range(0,len(obs['records']),2):
 x,y=obs['records'][i:i+2];a=x['final']['missile'];b=y['final']['missile'];outcome='양쪽 격추' if not x['final']['targetAlive']and not y['final']['targetAlive'] else '양쪽 비격추';lines.append(f"| {x['weapon']} | {a['reason']} {a['lifeS']:.6f}s | {b['reason']} {b['lifeS']:.6f}s | {outcome} |")
lines+=['','### 실행 시간(벽시계)','','| 계산 | 1차 | 2차 | 사격 수/회 |','|---|---:|---:|---:|']
for label,q in [('0단계',s0),('정렬 후6조건',s1)]:lines.append(f"| {label} | {q['receipts'][0]['elapsedMs']/1000:.3f}s | {q['receipts'][1]['elapsedMs']/1000:.3f}s | {q['receipts'][0]['calls']:,} |")
lines.append(f"| ENV_C96/120 | {env['records'][0]['elapsedMs']/1000:.3f}s | {env['records'][1]['elapsedMs']/1000:.3f}s | {env['records'][0]['calls']:,} |")
lines+=['','두 실행의 중첩, CPU quota4core, 브라우저 회귀 우선 중단/재개를 포함한다. 게임 프레임 성능이나 단독 진단 실행 속도로 일반화하지 않는다. 시작 시 자동 계산하지 않으며 `window.__ENV_C__.run()` 명시 호출과 오프라인 실행만 제공한다.','',f"브라우저 회귀 후보 SHA `{bridge['candidate']['htmlSha256']}`와 최종 SHA `{sha}`는 다르다. 최종에서는 계산표 JSON과 gzip/loader integrity만 바뀌었고 live source·그 외 wrapper·진단 코드의 동일성을 별도 검증했다. 후보 영수증의 SHA를 바꾸지 않았다. 최종 표/native audit/해시 변경 경고/경계/R3는 최종 HTML에서 다시 검사했다.",'','### 자료·보존·후속','','- [R1–R5 영수증](evidence/acceptance.json), [정적 대조](evidence/static-final.json), [후보/최종 차이](evidence/candidate-data-only.json), [종료기 검수](evidence/live-acceptance.json), [420회귀](evidence/domain-acceptance.json), [환경](TEST_ENVIRONMENT.md).','- [ENV_C 원본 보고](../../../envelope/C/REPORT.md), [재현](README.md), [별도 진단 재현](../../../envelope/C/README.md).','- 이전 ALL4_TERM8파일은 동일 bytes/Git blob archive했고 ENV_A/B 및 기존 종료기/kit 자료는 변경0이다.','- 실행 HTML1개 ZIP과 보고서/검증/그래프/CSV/JSON/재현 소스 ZIP을 분리한다. 보고 ZIP에는 실행 HTML이 없다. GitHub전체readback·ZIP CRC·파일 SHA·이전 heads 보존은 발행 후 `remote-publication.json`에 기록한다. Actions/PR/main·이전 브랜치 병합은 하지 않는다.','- 정렬 후6조건의 목표360/450km 미달과 정지 표적 사거리 퇴행, 저고도 해면 충돌을 숨기지 않고 WIP로 남긴다. 추가 추진·항력·유도·해면 보호 수정은 하지 않았다.']
(H/'REPORT.md').write_text('\n'.join(lines)+'\n')
summary=f'''# v48 WIP RANGE_A 상태

- 기준 ALL4_TERM `9a6838aade07c37262453e21cfe415d04d123d8c` 위 `range-a-env-c`. 원본v48 안정판은 보존한다.
- HTML `{html.name}` · {size:,}bytes · SHA-256 `{sha}`.
- 0단계500km6조건×2 완료 후 ER/SM-6 설계 사거리8값만360/450km로 정렬했다. {st['nativeFunctionCount']:,}명명 함수와 나머지live source 보존. 추진/항력/질량/연소/시커/Kappa/신관/배터리/종료기/MR/ESSM 설정 변경0.
- 정렬 후 고도1/10/20km 최대 명중 최초거리: ER136/135/241km, SM-6 135/132/286km. 목표 미달·정지 표적 사거리 퇴행을 보존하며 수치를 더 맞추지 않았다.
- ENV_C96조합+120궤적×2, 각 {env['records'][0]['calls']:,}사격/{env['records'][0]['bytes']:,}bytes 동일. 상한500km, 분해능1km, 실제요격점 거리 추가. [전표·전후 비교](docs/envelope/C/REPORT.md).
- R1–R5 통과. 기존420/420(15suites)+UI88/88+종료기16/16. 정상OFF/ON 각85명중/조기종료0, 기존83명중 보존+2회복. 자연SPY/정식VLS/전체fixed tick/WebGL8발29검사 통과.
- 게임/독립진단 {accept['nativePathSamples']:,}샘플 오차0, 무표적120초truth/RNG hash 동일, 전투120초는8값복원 시 기준판과 동일, 최종브라우저 경계 {len(bounds['records'])}건 일치. 최종 native/table 해시 및 변경 경고 검사 통과.
- SM-6 seed12002 100km/5km 접근250m/s는OFF3/ON3회 모두83.183333초 명중으로 회복. 고도15km 이탈250m/s 퇴행은 전표 참조.
- 저고도 이탈3+횡단18 조사 완료. 횡단11해면충돌, 원인 경로·유도/하한 기록. 수정0.
- [전체6항목 보고](docs/missile/range/A/REPORT.md), [검수](docs/missile/range/A/evidence/acceptance.json), [재현](docs/missile/range/A/README.md).
- ALL4_TERM8파일 동일 bytes/blob archive. ENV_A/B/기존 종료기 자료 변경0. 원본HTML/실행ZIP/리포트ZIP 분리. 원격전체bytes 대조 영수증은 발행 후 `docs/missile/range/A/remote-publication.json`에 기록한다. Actions/PR/main·이전브랜치 병합 없음.

추가 결정 전에는 추진·항력·유도·해면 보호를 수정하지 않는다. 설계 거리와 기존 정규화 로프트의 상호작용이 실제 최대 명중 거리를 낮춘 결과를 먼저 검토한다.
''';statusFile=R/'AEGIS_PLAN_STATUS_v48_WIP_RANGE_A.md';statusFile.write_text(summary);(R/'SHA256SUMS_v48_WIP_RANGE_A.txt').write_text(sha+'  '+html.name+'\n'+hashlib.sha256(summary.encode()).hexdigest()+'  '+statusFile.name+'\n')
section=f'''설계 사거리 정렬 WIP RANGE_A + ENV_C

- ALL4_TERM `9a6838a` 위 `range-a-env-c`. [실행ZIP(HTML1개)](https://github.com/0-FLANDRE-0/Aegis_Project/raw/refs/heads/range-a-env-c/Aegis_SIM_v48_WIP_RANGE_A_HTML.zip?download=1) · [리포트ZIP](https://github.com/0-FLANDRE-0/Aegis_Project/raw/refs/heads/range-a-env-c/Aegis_SIM_v48_WIP_RANGE_A_REPORT.zip?download=1).
- [HTML](Aegis_SIM_v48_WIP_RANGE_A.html), [상태](AEGIS_PLAN_STATUS_v48_WIP_RANGE_A.md), [SHA](SHA256SUMS_v48_WIP_RANGE_A.txt), [0단계/8값/목표 부족/전체검수](docs/missile/range/A/REPORT.md), [ENV_C전체표·전후 비교·120궤적](docs/envelope/C/REPORT.md).
- ER/SM-6 설계8숫자만360/450km로 정렬했다. 정지 표적 고도1/10/20km 최대는ER136/135/241, SM-6 135/132/286km로 줄었다. 목표에 억지로 맞추지 않고 WIP 결과로 남긴다. {st['nativeFunctionCount']:,}명명 함수/추진/항력/유도/신관/배터리/종료기 보존, MR/ESSM 변경0.
- 0단계/정렬후6조건/전체ENV_C 각각2회 비트 동일. 전체96조합/120궤적, 각 {env['records'][0]['calls']:,}사격. 실제요격점 거리·1km 전역상한 탐색, 계산표 해시 내장. 표를 지도/발사권한/AI에 연결하지 않았다.
- 기존420회귀+UI88+종료기16 통과. 정상240발OFF/ON 각85명중, 기존83명중 보존+2회복, 조기종료0. 자연탐지/전체월드/WebGL8발 통과. 게임/사본 {accept['nativePathSamples']:,}샘플 오차0, 무표적120초truth/RNG hash 동일, 전투는8값복원으로 인과 확인.
- SM-6 100km/5km 접근250m/s seed12002 해면 충돌은OFF3/ON3 모두명중으로 회복. 저고도 이탈3+횡단18조사는수정0이며 횡단11건도해면충돌했다. [조사](docs/envelope/C/results/LOW_ALT_INVESTIGATION.md).
- 원본 {size:,}bytes / SHA `{sha}`. ALL4_TERM8파일 동일 bytes/blob archive, ENV_A/B 및 기존 종료기 자료 변경0. 실행/리포트ZIP 분리·전체 원격readback 영수증은발행후추가한다. Actions/PR/main·이전브랜치 병합 없음.

'''
for name in ['README.md','AEGIS_PROJECT_INSTRUCTIONS.md']:
 p=R/name;s=p.read_text();m=re.search(r'^(#{2,3}) 최신 개발 기준 — 설계 사거리 정렬 WIP RANGE_A[^\n]*\n',s,re.M);assert m
 tail=re.search(r'^#{2,3} 직전 개발 기준 — 누적 Dynamic B4 ALL4',s[m.end():],re.M);assert tail
 s=s[:m.start()]+m[1]+' 최신 개발 기준 — '+section+s[m.end()+tail.start():];p.write_text(s)
print(json.dumps(accept))

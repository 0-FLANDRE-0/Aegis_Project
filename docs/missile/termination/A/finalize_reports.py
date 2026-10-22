"""Render this task's immutable receipts and version handoff (no flight changes)."""
import csv,gzip,hashlib,json,subprocess
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[3];B=R/'docs/envelope/B';E=H/'evidence'
def read(p):
 p=Path(p)
 if not p.exists():p=p.with_suffix(p.suffix+'.gz')
 return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
html=R/'Aegis_SIM_v48_WIP_ALL4_TERM.html';sha=hashlib.sha256(html.read_bytes()).hexdigest();size=html.stat().st_size
assert sha=='c6e10449c54b8b99aa2a51e2b7b1d3c020d15e36986c05f5941a172b90d15800'
live=read(E/'live-acceptance.json');st=read(E/'static-final.json');domain=read(E/'domain-acceptance.json');ui=read(E/'ui/ui.json');obs=read(E/'observed-world/observed-world.json');path=read(B/'evidence/path-all4/path-all4.json');status=read(B/'evidence/status/status.json');bounds=read(B/'evidence/boundaries/boundaries.json');results=read(B/'evidence/verification/results-verification.json');old=read(R/'docs/envelope/A/ENVELOPE_TABLE_A.json');new=read(B/'ENVELOPE_TABLE_B.json');raw=read(B/'results/results.json');assert all(q['pass']for q in[live,st,domain,ui,obs,path,status,bounds,results])
# All old ENV_A files remain their original Git blobs.
assert not subprocess.check_output(['git','diff','294bbb0','--name-only','--','docs/envelope/A'],cwd=R,text=True)
key=lambda q:(q['weapon'],q['altM'],q['targetSpeedMps']);before={key(q):q for q in old['rows']};comparison=[]
for q in new['rows']:
 p=before[key(q)];comparison.append({'weapon':q['weapon'],'altM':q['altM'],'targetSpeedMps':q['targetSpeedMps'],'oldKm':p['maxRangeKm'],'oldCap':p['upperCapReached'],'newKm':q['maxRangeKm'],'newCap':q['upperCapReached'],'deltaKm':q['maxRangeKm']-p['maxRangeKm']if not(p['upperCapReached']or q['upperCapReached'])else None})
with(B/'results/comparison.csv').open('w',newline='')as f:w=csv.DictWriter(f,fieldnames=list(comparison[0]));w.writeheader();w.writerows(comparison)
lines=['# ENV_B — 누적 ALL4_TERM 재측정','',f"프로파일 SHA-256: `{new['profileHash']}`",'','모든 값은 실제 게임 코드로 계산한 가상 모델 결과다. 실물 성능과 비교하지 않는다. 이 표는 지도/발사 관문에 연결하지 않았다.','',f"독립 2회 각각 {raw['calls']:,}사격, 96개 최대 거리 조합 + 120개 궤적. 원시 JSON {results['records'][0]['bytes']:,}bytes가 비트 단위로 동일하다.",f"원시 결과 SHA-256: `{results['records'][0]['sha256']}`",'',f"벽시계 실행 시간: {results['records'][0]['elapsedMs']/1000:.3f}s / {results['records'][1]['elapsedMs']/1000:.3f}s. 각 4 workers, 두 실행 일부 중첩 및 브라우저 검사 병행. 전용 CPU 성능으로 일반화하지 않는다.",'','| 검수 | 결과 |','|---|---|',f"| E1 독립 전체 결과 동일 | PASS · {results['records'][0]['bytes']:,} bytes |",f"| E2 분리 계산 월드/RNG/틱 불변 | PASS · 5개 게임/사본 비교 조건 |",f"| E3 동일 네이티브 경로 | PASS · {sum(x['sampleCount']for x in path['records']):,}샘플 · time/x/y/z/speed/Mach 최대 오차 0 |",f"| E4 표·궤적 빈칸 | 0 · 96조합/120사격 |",f"| 최종 Chromium 경계 재실행 | {len(bounds['records'])}개 모두 동일 성공/실패·사유 |",f"| Node/Chromium 최대 최근접 차이 | {bounds['maxClosestDeltaM']:.12g}m |",f"| Node/Chromium 최대 속도 차이 | {bounds['maxSpeedDeltaMps']:.12g}m/s |",f"| 런타임 소스·표 해시/변경 경고 | PASS · 246개 네이티브 함수, 설정 변경 시 재계산 경고 |",'','[전체 표·4종 궤적 그래프](results/REPORT_ENV_B.md) · [전후 96조합 CSV](results/comparison.csv) · [구판 ENV_A](../A/REPORT.md)','','## 전후 비교','', '정지 표적 기준. 단위 km. `≥300`은 검사 상한에서 성공한 하한이며 숫자 300을 실제 최대치로 해석하지 않는다.','', '| 기종 | 고도 | ENV_A 구판 | ENV_B 누적본 |','|---|---:|---:|---:|']
for c in comparison:
 if c['targetSpeedMps']==0:lines.append(f"| {c['weapon']} | {c['altM']}m | {'≥'if c['oldCap']else''}{c['oldKm']} | {'≥'if c['newCap']else''}{c['newKm']} |")
lines+=['','![전후 사거리 비교](results/envelope-before-after.png)','','## 관찰한 변화와 한계','','- MR/ESSM의 기존 시험용 로프트 상한 완화와 네 종류의 동적 선반 재계획을 모두 적용했다. MR/ESSM의 일부 거리 증가는 이 수정과 함께 나타난다.','- ER/SM-6도 기존 한계를 유지한 채 재계획에 참여하면서 모든 조건이 좋아지지는 않았다. 고도 15km·250m/s 이탈 표적은 ER 221→109km, SM-6 244→112km다. 요청한 ALL4 코드·수치를 바꾸어 결과를 맞추지 않았다.','- 120개 궤적 결과: 명중 94, LOW_SPEED 23, SEA_IMPACT 2, BATTERY_EXHAUSTED 1. 이상 유도 정보가 지속되므로 RF 기반 비명중 종료가 개입한 성능표가 아니다. 실제 RF 조건의 종료는 별도 게임 회귀에 있다.',f"- 거친 탐색에서 비단조 성공 구간 {results['nonMonotonicCoarseRows']}행을 관찰했다. 더 먼 모든 정수 km를 검사하여 전역 1km 격자 최대를 확인했다. 범위 안의 모든 거리에서 명중한다는 뜻은 아니다.",'- 기존 ENV_A 코드·표·원시 결과는 동일 Git blob으로 유지한다. 신판 계산의 이상 RF 관측 기록이 기존 이상 유도 비행 자체를 바꾸지 않는지도 60궤적 비교로 확인했다.','- 연소 종료, 최고 고도, 종말 속도, 최근접 거리, 로프트 단계 구간과 10Hz 샘플은 results의 CSV/JSON에 있다. 저장소의 큰 원시 파일은 gzip이고 리포트 ZIP에서는 읽을 수 있게 풀어서 수록한다.','- 자연 비행 전원 480초를 실물 수명/도달 거리로 해석하지 않는다. SM-6 480초는 사용자 지정 게임 시험값이다.']
(B/'REPORT.md').write_text('\n'.join(lines)+'\n')
normal=live['records'];report=['# ALL4_TERM — 누적 이식·실제 게임 검증','',f"최종 HTML `{html.name}` · {size:,}bytes · SHA-256 `{sha}`",'','기준은 최신 PIP_B + ENV_A다. 구형 UI_A1로 돌아가지 않았다. 첨부 ALL4 로프트를 자함/NPC 두 실행 문맥에 적용했으며 이미 적용된 중간 단계에서의 중복 적용도 검사했다.','', '## 변경','', '- MR/ER/SM-6/ESSM Block 2 모두 Dynamic B4 포함. MR 17,500→22,500m, ESSM 3,500→7,500m 선반 상한; ER/SM-6 기존 상한·첨부 helper 수치 유지.','- 새 종료기는 RF EKF 추정 트랙, 유효성/신호 나이/신뢰도, 자기 INS와 신관 결과만 사용한다. 실제 표적 좌표·truth 조회·기존 closest/missedTarget 변수를 입력으로 삼지 않는다.','- 첨부 원안은 ARH 차단·SARH 유지 시 기존 명중 16조건을 12초에 조기 종료했다. 신선한 대체 SARH와 유효한 수신 DL 상태가 있으면 보류하도록 종료기만 보완했다. DL은 validity/source만 보며 좌표는 읽지 않는다.','- 종료 전용 교차 시계의 임의 65초 상한을 제거했다. 35km/200m/s는 175초다. Kappa 유도용 90초와 유도 계산은 그대로다.','- SM-6 게임 배터리 450→480초. MR 380 / ER 430 / ESSM 185초 유지. A/B OFF에서도 배터리는 적용한다.','- 신관·추진·항력·시커·Kappa 관련 기존 함수 166개 바이트 동일, NPC 문맥의 나머지 함수도 동일. 모델 자산 0–12와 UI/저장 경로 보존.','', '## 검수','', '| 항목 | 결과 |','|---|---|',f"| 현재 기준·중복 방지·금지 truth 참조·소스 보존 | {len(st['checks'])}검사 PASS |",'| 정상 비행 ON/OFF | 240발, 120쌍 · OFF/ON 각 83명중 · 조기 종료 0 |','| ARH 차단·SARH/DL 대체 지원 | 36발, 18쌍 · 기존 16명중 모두 유지 · 조기 종료 0 |','| 실제 RF 소실→교차 후 종료 | 4종 모두 POST_CROSS · 관측 교차+2.5s 및 신호 공백 조건 일치 |','| RF 재획득 | 4종 모두 재획득·네이티브 신관 요격 |','| ARH 미획득 | SM-6/ESSM 무지원 12초 후 종료 · SARH에 규칙 오적용 0 |','| 배터리 | 4종×A/B 8건 · SM-6 450초 이후 유지, 480초 초과 종료 |','| 정식 VLS 요청 | 네 종류 모두 네이티브 release 기록·신관 요격 |',f"| 전체 월드·자연 레이더 트랙·실제 WebGL | 8발, 4 ON/OFF쌍 · {len(obs['checks'])}검사 PASS |",f"| 기존 관련 기능/함정 회귀 | {domain['checks']}검사 / {domain['suites']} suites PASS |",f"| 기존 PiP·창·입력 UI | {len(ui['checks'])}검사 PASS |",'| 기존 ENV_A 보존 | 변경 0, 동일 Git blobs |','| 사거리 재계산 | [ENV_B 별도 보고](../../../envelope/B/REPORT.md), 2회 비트 동일 |','','고도 30/5,000/15,000m × 중·장거리 × 5개 seed를 종류별로 실행했다. 일반 명중률을 추정한 무작위 표본은 아니다. 기존 PIP_B 동일 120조건은 80명중, 누적본은 83명중이며 그 중 아래 한 건의 기존 명중은 유지되지 않았다.','', '### 전체 월드 추가 검사','', '전투 트랙을 주입하지 않고 실제 SPY 관측으로 생성한 트랙을 선택·HOSTILE 지정·정밀추적한 뒤 정식 VLS 요청으로 발사했다. 타겟 조종 AI와 전체 simulateFixedTick을 유지했다. 초기 채프 쿨다운은 길게 설정했지만 이후 네이티브 AI를 교체하지 않았다. ON 실행은 실제 WebGL로 출항·발사·비행과 종료 후 렌더 진행을 확인했다.','', '| 기종 | 종료기 OFF | 종료기 ON | 표적 결과 |','|---|---|---|---|']
for i in range(0,len(obs['records']),2):
 a,b=obs['records'][i:i+2];x=a['final']['missile'];y=b['final']['missile'];report.append(f"| {a['weapon']} | {x['reason']} {x['lifeS']:.3f}s | {y['reason']} {y['lifeS']:.3f}s | {'양쪽 명중'if not a['final']['targetAlive']and not b['final']['targetAlive']else'양쪽 비명중'} |")
report+=['','SM-6/ESSM의 위 비명중은 OFF도 요격하지 못한 경우다. 새 종료기가 불필요한 비행을 먼저 끝냈으며, OFF가 명중한 사격을 조기에 끊은 것은 아니다.','', '## 남은 알려진 사격 결과 변화','', '**SM-6 / 100km / 5km / 접근 250m/s / seed 12002**: PIP_B는 78.033s에 명중한다. Dynamic B4 후 종료기 OFF도 148.517s에 SEA_IMPACT다. 별도 3회 반복에서 구판 3명중/신판 3비명중을 재현했다. 최근접은 약 131.75m다. 새 종료기의 조기 종료와 구분하며, 사용자 요청대로 B4 수치를 임의 변경하지 않았다. 모든 과거 사격 결과가 같다는 안정판 선언은 하지 않는다.','', '## 원안과 예비 시험의 실패도 보존','', '- 첨부 독립 9/9는 제공자의 기록으로, 이 작업의 통과 수에 합산하지 않았다. 실제 게임에서 발견한 원안 16개 조기 종료를 원시 로그와 함께 보존했다.','- 전체 RF 경로의 일부 첫 실행에는 0.283333s 시간 차이가 있었으며 같은 종료기 OFF끼리도 재현됐다. 원인 확정 없이 새 종료기의 힘/유도 변경으로 해석하지 않는다. 해당 함수의 바이트 보존과 명중 결과를 검증했다. 분리된 이상 진단/동일 네이티브 경로 비교는 5,894샘플 오차 0이다.','- 예비 3D 시험은 350ms 한 번의 프레임 샘플로 소프트웨어 렌더의 정지를 잘못 판정했고, 적 조종/채프가 있는 비명중에도 새 종료가 전혀 없어야 한다고 잘못 가정했다. 최종 시험은 다음 렌더 프레임을 기다리고 OFF의 실제 표적 결과와 비교한다. 예비 원본 결과와 실패 로그를 삭제하지 않았다.','- 자연 탐지 예비 배치의 정면 방향에서는 15초 안에 트랙이 생기지 않았다. 최종 자연 탐지 검사는 DDG face 중앙 45°에서 수행했다. 센서 모델은 수정하지 않았다. LOCK 하네스도 기존 MAP_A 커서 지정 절차에 맞춰 수정했다.','', '## 자료와 재현','', '[방법·명령](README.md) · [환경·검사 경계](TEST_ENVIRONMENT.md) · [소스 정적 대조](evidence/static-final.json) · [비행 검수](evidence/live-acceptance.json) · [기존 420검사](evidence/domain-acceptance.json) · [자연 탐지/3D 8발](evidence/observed-world/observed-world.json)','', '큰 원시 결과는 저장소에서는 gzip으로 보존하고 리포트 ZIP에서는 JSON/CSV로 풀어 수록한다. 최종 파일은 HTML 1개 ZIP과 실행 HTML을 뺀 리포트 ZIP으로 분리한다. 원격 전체 파일 readback/ZIP 검증은 발행 뒤 remote-publication.json에 고정 commit으로 기록한다. Actions dispatch/PR/main·기존 브랜치 병합은 하지 않는다.']
(H/'REPORT.md').write_text('\n'.join(report)+'\n')
statusText=f'''# v48 WIP ALL4_TERM 상태

최신 PIP_B 위 누적 이식이다. 원본 v48 stable과 이전 데이터는 보존한다.

- HTML: `{html.name}`, {size:,}bytes
- SHA-256: `{sha}`
- 새 브랜치: `missile-b4-termination` (기준 `294bbb066df41489e77f5f16d0ad6a84eec32f91`)
- 네 종류 Dynamic B4, 관측 기반 비행 종료, SM-6 배터리 480초를 반영했다. 신관/추진/항력/시커/Kappa 함수 166개는 동일하다.
- 원안의 대체 SARH/DL 유도 중 조기 종료 16조건과 종료 시계 65초 상한을 종료기에서만 보완했다. B4 수치·Kappa90초는 유지했다.
- 실제 게임 240발 ON/OFF 120쌍과 대체 지원 36발에서 기존 명중 99건 모두 유지, 조기 종료 0. 실제 RF 소실/재획득/미획득 및 배터리·정식 VLS 요청 검사 통과.
- 자연 SPY 트랙→LOCK→VLS→전체 fixed tick→실제 WebGL 8발 비교도 기존 명중 보존. 비명중 SM-6/ESSM은 OFF도 비명중이며 새 종료기로 먼저 정리된다.
- 기존 관련 회귀 420/420 (15 suites), UI 88/88. 실제 네이티브/독립 진단 5,894샘플 비교 오차0.
- ENV_B 96조합/120궤적을 2회 각각11,458사격으로 재측정, 원시46,068,182bytes 동일. 최종 Chromium 경계151건 모두 일치. 프로파일 해시 `{new['profileHash']}`.
- **알려진 B4 결과 변화:** SM-6 100km/5km/접근250m/s/seed12002는 구판 명중, B4 후 종료기 OFF도 SEA_IMPACT (3회 재현). B4 수치를 유지하라는 요청에 따라 임의 밸런스 수정하지 않았다. 종료기 조기 종료와 구분하며 전면 안정판으로 승격하지 않는다.
- 배터리 검증은 실제 비행 뒤 시계 체크포인트를 이용한 전원 경계 시험이다. 자연 비행480초 완주/실물 성능 보장은 아니다.
- PIP_B HTML/상태/SHA/두 ZIP/체크섬/workflow8개는 동일 bytes/blob archive, ENV_A 자료 변경0.
- [상세 보고](docs/missile/termination/A/REPORT.md), [재측정/전후표](docs/envelope/B/REPORT.md), [재현](docs/missile/termination/A/README.md).
- 실행용 HTML 1개 ZIP / 리포트 ZIP 분리, 원본 HTML 별도 업로드·전체 원격 readback. Actions 미실행, PR/병합 없음. 실제 발행 영수증은 `docs/missile/termination/A/remote-publication.json`.

후속: 알려진 B4 사격 변화 검토(수치 변경은 별도 요청), 그 뒤 기존 MAP_B 계획을 이어간다.
'''
(R/'AEGIS_PLAN_STATUS_v48_WIP_ALL4_TERM.md').write_text(statusText)
(R/'SHA256SUMS_v48_WIP_ALL4_TERM.txt').write_text(sha+'  '+html.name+'\n')
section='''### 최신 개발 기준 — 누적 Dynamic B4 ALL4 + 관측 기반 종료 WIP ALL4_TERM

- [실행 다운로드 — HTML 1개 ZIP](https://github.com/0-FLANDRE-0/Aegis_Project/raw/refs/heads/missile-b4-termination/Aegis_SIM_v48_WIP_ALL4_TERM_HTML.zip?download=1) · [리포트 ZIP](https://github.com/0-FLANDRE-0/Aegis_Project/raw/refs/heads/missile-b4-termination/Aegis_SIM_v48_WIP_ALL4_TERM_REPORT.zip?download=1).
- [HTML](Aegis_SIM_v48_WIP_ALL4_TERM.html), [상태](AEGIS_PLAN_STATUS_v48_WIP_ALL4_TERM.md), [SHA](SHA256SUMS_v48_WIP_ALL4_TERM.txt), [실제 게임·종료 검수](docs/missile/termination/A/REPORT.md), [ENV_B 전후 사거리·궤적](docs/envelope/B/REPORT.md), [재현](docs/missile/termination/A/README.md).
- 최신 PIP_B `294bbb0` 위 `missile-b4-termination`. 4종 B4를 자함/NPC에 적용, 중복 이식 방지. 원안의 SARH/DL 대체 유도 중 조기 종료와 임의 65초 교차 시계를 종료기에서 보완했다. 실제 표적 좌표를 종료 판단에 넣지 않는다. B4 코드·수치 및 기존 신관/추진/항력/시커/Kappa 계산 보존, SM-6 게임 배터리만480초.
- 240발 ON/OFF + 대체 지원36발에서 기존 명중99건/조기 종료0. 실제 RF 소실·재획득·미획득, 배터리8건/정식VLS4건 및 자연 SPY트랙/전체fixed tick/WebGL8발 검사 통과. 기존 관련 회귀420/420 + UI88/88. 세부 조건·초기 실패·한계는 보고서를 따른다.
- ENV_B는 96조합/120궤적, 독립2회 각각11,458사격·46,068,182bytes 동일. 실제 게임/분리 경로5,894샘플 오차0, Chromium 사거리경계151건 일치. ENV_A 구판 자료는 변경하지 않았다. 표는 아직 지도/교전 권한에 연결하지 않는다.
- **알려진 결과 변화:** SM-6 100km/5km/접근250m/s/seed12002는 B4 후 종료기OFF도 비명중 후 SEA_IMPACT (구판명중,3회재현). 요청한 B4 수치를 유지하며 조기 종료와 분리 기록한다. 전면 안정판 승격 없음.
- 원본18,278,162bytes, SHA `c6e10449c54b8b99aa2a51e2b7b1d3c020d15e36986c05f5941a172b90d15800`. 이전 전달세트8개 동일 bytes/blob archive. 원본/두 ZIP 직접 업로드·독립 원격 readback, Actions dispatch/PR/main·이전브랜치 병합 없음. 다음은 알려진 B4 결과 검토와 MAP_B다.

'''
for name in ['README.md','AEGIS_PROJECT_INSTRUCTIONS.md']:
 p=R/name;s=p.read_text();marker='### 최신 개발 기준 — PiP·정보 정리 WIP PIP_B + ENV_A'
 if marker in s:s=s.replace(marker,section+'### 직전 개발 기준 — PiP·정보 정리 WIP PIP_B + ENV_A',1)
 elif '누적 Dynamic B4 ALL4 + 관측 기반 종료 WIP ALL4_TERM'not in s:s=section+s
 for oldName in ['Aegis_SIM_v48_WIP_PIP_B.html','AEGIS_PLAN_STATUS_v48_WIP_PIP_B.md','SHA256SUMS_v48_WIP_PIP_B.txt']:
  s=s.replace(']('+oldName+')','](archive/v48/WIP_PIP_B/'+oldName+')')
 if name=='README.md':s=s.replace('### 최신 개발 기준 — 누적 Dynamic B4 ALL4','## 최신 개발 기준 — 누적 Dynamic B4 ALL4').replace('## 최신 개발 기준 — PiP·정보 정리 WIP PIP_B + ENV_A','## 직전 개발 기준 — PiP·정보 정리 WIP PIP_B + ENV_A')
 p.write_text(s)
print(json.dumps({'htmlBytes':size,'sha256':sha,'envelopeCalls':raw['calls'],'newProfileHash':new['profileHash'],'nativePathSamples':sum(x['sampleCount']for x in path['records'])}))

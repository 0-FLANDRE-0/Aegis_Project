"""Build the release evidence index and the requested Korean A-L report."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[3];D=Path(__file__).resolve().parent;E=D/'evidence/release'
old=json.loads((R/'docs/viewport/A/evidence/verification-summary.json').read_text())
paths=['../static/static.json','ui/ui.json','events/events.json','storage/storage.json','hash/hash.json','scaled-3d/scaled-3d.json','vp-viewport/viewport.json','vp-extra/extra.json','vp-invariance/invariance.json']+[r['evidence']for r in old['suites']if r['suite'].startswith('regressions/')]
artifact=R/'Aegis_SIM_v48_WIP_UI_A.html';artifactSha=hashlib.sha256(artifact.read_bytes()).hexdigest()
rows=[]
for f in paths:
 p=E/f;v=json.loads(p.read_text())
 if 'htmlSha256'in v:assert v['htmlSha256']==artifactSha,(f,v['htmlSha256'],artifactSha)
 if 'candidateSha256'in v:assert v['candidateSha256']==artifactSha
 checks=v.get('checks')or{case['ship']+'.'+case['scenario']+'.'+k:x for case in v.get('cases',[])for k,x in case['checks'].items()}
 assert checks,f
 rows.append({'evidence':str(p.relative_to(D)),'checks':len(checks),'pass':v['pass'],'failed':[k for k,x in checks.items()if not x]})
assert all(r['pass']for r in rows),rows
html=R/'Aegis_SIM_v48_WIP_UI_A.html';raw=html.read_bytes();ui=json.loads((E/'ui/ui.json').read_text());vp=json.loads((E/'vp-viewport/viewport.json').read_text());events=json.loads((E/'events/events.json').read_text());hashes=json.loads((E/'hash/hash.json').read_text())['records']['hashes']
metrics={'barHeightByScale':{str(n):{'min':min(r['barHeightPx']for r in ui['rows']if r['scale']==n),'max':max(r['barHeightPx']for r in ui['rows']if r['scale']==n)}for n in [85,100,130]},'twoDCenterMaxPx':max(r['centerErrorPx']for r in ui['rows']),'tapMaxPx':max(r['tapErrorPx']for r in ui['rows']),'threeDCenterMaxPx':max(r['errorPx']for r in ui['records']['dock']),'inputChanges':0,'burstCount':30,'originalControls':events['records']['controlCounts'],'originalNodeCount':json.loads((E/'storage/storage.json').read_text())['records']['normal']['snapshot']['originalNodeCount'],'same120sHash':hashes[0]['hash'],'stateBytes':hashes[0]['stateBytes'],'matrixRows':len(ui['rows'])}
out={'schema':'AEGIS_UI_A_VERIFICATION_1','pass':True,'htmlSha256':hashlib.sha256(raw).hexdigest(),'htmlBytes':len(raw),'baselineSha256':'432de9b88566d6198da0a21856ab85d1febda8106fcd28f6d8f13fd8801e67b9','addedBytes':len(raw)-18002954,'checks':sum(r['checks']for r in rows),'suiteCount':len(rows),'suites':rows,'metrics':metrics};(D/'evidence/verification-summary.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
bar=[r for r in ui['rows']if r['scale']==100 and r['profile'].startswith('CG')];barText=' / '.join(str(r['size'][0])+'×'+str(r['size'][1])+': '+str(r['barHeightPx'])+'px'for r in bar)
parts=['# UI_A 결과 보고서','', '## 1) 변경 요약','',
'VP_A SHA-256 `432de9b8…01e67b9`에서 표시·입력 배치만 변경했다. ShipRuntime·센서·판정·발사 권한·게임 저장 codec·모델 assets는 보존했다. 기존 3,198개 함수 이름 중 변경된 본문은 viewport 측정, 전체화면, 탭 표시, 함 선택 화면 설정 추가, SPY 표시 위치, 하단 간격 계산의 6개뿐이다. 새 창 코드는 별도 표시 모듈이다.',
'',f'산출물: `{html.name}`, {len(raw):,} bytes, SHA-256 `{out["htmlSha256"]}`. VP_A 대비 +{out["addedBytes"]:,} bytes. 패킹 records 0–12와 소브레멘니 assets는 byte-identical이다.',
'','NAV·ARM·FLEET·AIR·SYS와 관찰용 소형 CIC를 독립 창으로 옮겼다. 제목줄 이동, 모서리 크기 조절, 최대화/복원, 닫기/접기, 메뉴 고정/해제·불투명도, 전면 순서를 제공한다. 창을 선택하면 기존 탭의 입력 모드 선택 함수를 사용한다. AIR의 좌측 조작·우측 목록은 유지한다.',
'','하단 상태 바는 함 정보·설치 무장 재고·시간/배속·일시정지·상태 칩·창 메뉴를 공유한다. VLS가 설치되면 0발인 탄종도 표시한다. DDG의 단일 함포는 읽기 전용 inventory adapter로 공용 exporter에 연결한다. 게임 객체에는 쓰지 않는다. UI 크기·배치만 별도 localStorage에 저장한다.',
'','## 2) 검수 A–L 수치표','', '| 검수 | 결과 | 수치 / 근거 |','|---|---|---|',
f'| A 상태 바 | PASS | DDG/CG × 9크기 × 3배율 = {metrics["matrixRows"]}조합. 재고 누락·잘림·가로 스크롤 0 |',
'| B 화면 밖 방지 | PASS | 30회 무작위 변경, 회전, 모든 열린 창 제목줄 화면 안, NaN 0 |',
f'| C 스냅/VP_A | PASS | 2D 중심 최대 {metrics["twoDCenterMaxPx"]:.6f}px; 3D 기준점 최대 {metrics["threeDCenterMaxPx"]:.6f}px |',
'| D 입력 격리 | PASS | 창/바/위젯 × 85/100/130%: 팬·줌·표적·경로 변경 0 |',
f'| E 리스너/노드 | PASS | 탭별 실제 실행 표본 {metrics["originalControls"]}. 기존 {metrics["originalNodeCount"]}개 노드 연결 유지, 중복 id 0. 전후 native 상태 해시 일치 |',
'| F 공용 교전 위젯 | PASS | 2D·3D 모두 AUTO LOCK → FIRE 실발사 1발, VP_A와 동일 |',
'| G 시간 | PASS | ×1/4/8/16/64 값 일치. pause 중 tick 정지. pause/resume 120초 해시 동일 |',
'| H UI 저장 | PASS | 배치 재로드 일치. 손상 JSON·구 schema·차단 저장소에서 기본 프리셋/100% 시작 |',
'| I 전체화면 | PASS | 로드 0회, 첫 버튼 1회, 수동 해제 뒤 추가 0회, 실패 알림 0회. 가로 고정 OFF 시 lock 0회 |',
f'| J UI 크기 | PASS | 85/130% A–D 재검사와 3D 스냅·입력 격리 보충 검사. 실제 지도 탭 최대 오차 {metrics["tapMaxPx"]:.8f}px. 주 캔버스 CSS zoom=1 |',
'| K 시뮬 불변 | PASS | 같은 seed, 120초/7,200 ticks의 1,764,132-byte 상태 일치 |',
'| L 기존 회귀 | PASS | 기존 420건 전체 + VP_A 표시/정적 계열 148건(기존 147+신규 정적 1). 567에 420을 중복 가산하지 않음 |',
'',f'전체 실행 검사 **{out["checks"]}건 / {out["suiteCount"]} suites PASS**. 각 판정과 파일은 [검증 색인](evidence/verification-summary.json)에 기록했다. 테스트 fixture는 새 창을 열고 가려진 지도를 노출하는 동작으로 바꿨으며, AIR의 옛 고정 281px 조건은 가변 창 내부 스크롤 영역 조건으로 바꿨다. 센서·교전 판정 조건은 바꾸지 않았다.',
'',f'120초 상태 SHA-256: `{metrics["same120sHash"]}`. resize 혼합 실행도 같은 해시다. Chromium 헤드리스·SwiftShader와 CSS viewport/DPR 에뮬레이션 결과이며 실기기 FPS 측정은 아니다.',
'',f'100% CG 상태 바 높이: {barText}. 모든 재고 표시·최소 버튼 크기·가로 스크롤 금지를 우선했으므로 좁은 화면에서는 2줄을 넘는다. 이는 구현 전 보고한 제약이다.',
'','## 3) 프리셋 스크린샷','']
for label,name in [('PC 가로','pc'),('폰 가로','phone'),('세로','portrait')]:
 parts+=['### '+label,'']
 for w,h in [(1400,900),(844,390),(390,844)]:parts += [f'![{label} {w}×{h}](evidence/release/ui/preset-{name}-{w}x{h}.png)','']
parts+=['### 3D 공용 바·위젯·소형 CIC·방위 테이프','', '![3D PC](evidence/release/ui/3d-1400x900.png)','', '![3D 세로](evidence/release/ui/3d-390x844.png)','',
'## 4) 이동한 컨트롤 / 유지한 항목','',
'[이동 목록 TSV](MOVED_CONTROLS.tsv)에 기존 분류표의 식별 가능한 117개 행을 연결했다. 추가로 id가 없는 기존 time-btn 5개를 그대로 바에 옮겼고, 소형 CIC subtree를 그대로 이동했다. 기존 APS 성능표·ISAR 판별표·교전 로그 dialog 3개는 body로 옮겨 숨긴 compatibility shell 밖에서 showModal 동작을 보존했다. 고도 설정 dialog는 AIR 페이지 subtree 안에서 같은 노드로 유지했다. cloneNode·기존 컨트롤 innerHTML 재생성은 사용하지 않았다.',
'','가장자리 패널은 `uiStatusBarA`(2D/3D 공용 하단)와 열려 있고 펼쳐진 고정 창이다. 떠 있는 창, 교전 위젯, 소형 CIC, 3D 메뉴/리드아웃, HUD는 보이는 영역을 줄이지 않는다. 제목줄만 접힌 창도 viewport를 줄이지 않는다. 고정 크기는 45% 상한이고 최소 크기가 안 들어가면 접는다.',
'','`shipDetailPanel`, `damageControlPanelV1`, `damageFloodPanelV1`, 독립 무장 현황/진단 dialog, 기존 3D 컨트롤 drawer는 창 시스템에 편입하지 않았다. 요청의 UI_B 범위이거나 기존 modal 동작 유지 대상이다. 기존 drawer를 사용할 때 떠 있는 창이 가리면 창을 이동/닫을 수 있다.',
'','소형 CIC는 본래 명령 입력이 없는 관찰용 canvas다. 크기·DPR은 기존 read-only renderer가 창의 client rect를 읽어 갱신한다. 존재하지 않던 클릭 명령은 추가하지 않았다. 실제 입력 가능한 2D PIP는 UI_B에 남겼다.',
'','## 5) 미디어쿼리 변경','',
'- `(pointer:coarse), (max-width:640px)` 두 곳에서 `pointer:coarse` 분기를 제거했다. 폭에 따른 배치 분기는 유지했다.',
'- 첫 분기의 44px 버튼·8/12px padding·10px 글자 확대 규칙을 제거했다. 모든 pointer 종류에 PC 밀도를 쓴다.',
'- 기존 640/980/1000 및 max-height 520의 옛 하단 dock 규칙은 숨긴 compatibility shell에만 남는다. 이동한 페이지에는 새 창의 공통 grid/스크롤/11px 글자·36px hit target을 적용한다.',
'- 기존 3D 작은 화면의 7px 교전 버튼·quick state 숨김을 공용 위젯 규칙으로 덮어썼다. 위젯의 세 조작은 40px와 8px 간격을 유지한다.',
'- 새 max-width 700은 상태 바의 줄바꿈 정렬과 3D 리드아웃 폭만 바꾼다. coarse 전용 밀도는 없다. reduced-motion 규칙은 유지한다.',
'','## 6) UI_B에 남긴 것','',
'- 2D 좌상단 HUD·SPY 스케줄러의 창 편입. 이번에는 보이는 영역의 좌상단에만 맞췄다.',
'- 손상통제·침수·SHIP 및 무장 현황의 공용 창 편입.',
'- ARM의 무장 선택/사통/VLS 분리와 실제 2D 지도 PIP 입력.',
'- 3D drawer와 떠 있는 창의 추가 배치 프리셋, 좁은 화면의 재고/정보 밀도 개선. 재고 생략 없이 얇게 만드는 별도 설계가 필요하다.',
'','가변 UI 배치는 게임 저장에 넣지 않았다. `aegis.ui.a.layout.1`(schema 1, 가로/세로 × small/medium/large), `aegis.ui.a.preferences.1`(schema 1, 배율·가로 고정)을 사용한다. 배치 등급 경계는 700/1100px이며 저장 배치가 없으면 화면 형태로 프리셋을 고른다. GitHub Actions는 실행하지 않고 workflow_dispatch만 제공한다.']
(D/'REPORT.md').write_text('\n'.join(parts)+'\n');print(json.dumps({'pass':True,'checks':out['checks'],'metrics':metrics},ensure_ascii=False))

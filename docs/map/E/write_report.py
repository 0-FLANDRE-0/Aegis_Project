from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[2];j=lambda p:json.loads((H/p).read_text());a=j('evidence/acceptance.json');assert a['pass'];b=j('build.json');n=j('evidence/e-new/native-results.json');u=j('evidence/e-new/results.json');p=j('evidence/e-policy/policy.json');st=j('evidence/static.json');eq=j('evidence/presentation-equivalence.json');world=j('evidence/delivery-world120.json');term=j('evidence/release300-comparison.json');gl=j('evidence/webgl8-comparison.json');ew=j('evidence/ew-h3/summary.json');counts=a['counts']
lines=['# MAP_E 검증 보고서','',f"기준 main `{b['baseCommit']}` (MAP_D PR #57 병합본). 산출물 `{b['output']}`.",f"HTML SHA-256 `{b['sha256']}` · {b['bytes']:,} bytes.",'','## 1. 변경 요약','',
'ARM 탭·TGT/VLS/GUN/EW 페이지·AUTO TGT를 실제 DOM에서 제거했다. 기존 버튼의 native 함수/리스너는 원래 노드의 분리 참조로 보존한다. 시나리오·리셋·디버그 생성 버튼은 원래 DEBUG에 있어서 위치를 유지했다. 하푼 모델 출처 링크를 같은 노드로 DEBUG에 옮기고, ARMS STATUS 버튼은 + 창 추가 메뉴로 옮겼다. 기존 armsPanel/drawArmsPanel을 재사용하며 3D 위에서 닫기까지 동작한다.',
'하단 EMCON 칩은 레이더/ECM 팝오버를 연다. 전체 방사 OFF→ON은 직전 ECM 단계를 기억해 복원한다. 레이더만 조작할 때는 기존 toggleEmcon만 호출한다. Hawklink/Link16 정책을 바꾸지 않았다.',
'ECM 단계는 OFF / JAM / FULL. 새 단계 선택은 기존 electronicCommandF를 통해 auto·NJ·DJ 승인/자동 조준을 설정한다. 실제 EA 기법 선택·시간 배분은 기존 함수가 담당하며, 위협이 없으면 STANDBY다. 자함 채프 자동 dispatch와 자함 nulkaAuto15B에 FULL 조건만 추가했다. NPC lexical EW 커널·EA allocator·electronicCommandF는 byte 동일하다.',
'SRBOC/Nulka 칸은 기존 글자·여백·폭을 유지한 채 클릭/키보드로 수동 발사 팝업을 연다. native deployOwnChaff / nulkaFire15B를 명령 버튼 클릭에서만 호출하고, 기존 재고·쿨다운·cue·준비/손상 거부를 표시한다. 무장·표적 선택은 바꾸지 않는다. SRBOC는 원래처럼 위협이 없어도 함 침로를 사용해 발사할 수 있다.',
'지도 하푼 미리보기와 실제 큐 인자만 MANUAL로 고정했다. generic automatic surface gate·H3 권한·식별·트랙 나이·사거리·INS 바스켓·손상·쿨다운은 유지했다. [경로]는 harpoonRouteToggleE를 직접 호출하며 AIM 탭/ARM 창에 의존하지 않는다. 편집 시 메인/옛 입력/PiP 모두 HARPOON_INS가 우선한다.',
'폰 확대 UI에서 기존 바 폭이 넘치던 경우에는 축척 적용 후 가용 폭을 기준으로 기존 2줄 배치를 사용했다. 새 기만체 칸을 generic 무장 버튼으로 변환해 폭이 늘어나던 부분은 원래 span 노드/폰트를 유지하는 방식으로 보정했다. 지도 거리·캔버스 해상도·시뮬레이션에는 영향이 없다.','',
'## 2. 사용자 결정 및 후속 메모','',
'- CG의 개별 함수/함미 선택·사격 UI는 폐기하고 MAP_D 자동 2문을 유지한다. 내부 mainGun·selectedGunId·저장 경로는 남긴다.',
'- **EMCON 중 방사 없는 지정의 새 UI 위치는 후속 검토.** lockByCursor의 기존 비방사 지정 분기는 보존하고, 지도 정밀추적의 EMCON 차단도 유지한다. 이번에 임의의 새 메뉴를 만들지 않았다.',
'- 새 ECM 단계는 세이브에 필드를 추가하지 않는다. JAM 저장 후 불러오면 기존 SK AUTO ON에서 FULL로 추론한다. 레거시 수동 NJ/DJ 승인 플래그는 삭제하지 않고 읽기 전용 상태로 표시한다. 새 단계를 명시적으로 선택하면 OFF/JAM/FULL 매핑을 적용한다.','',
'## 3. 검수 결과','',
'PC 1400×900 / 폰 832×384, DDG/CG, 2D MAIN/실제 WebGL 3D+PiP의 8조합. 추가 축척은 85/100/130%. 헤드리스 기능/화면 검사이며 실제 휴대폰 FPS 측정은 아니다.','',
'| 검사 | 결과 |','|---|---|',
f"| 도메인 | {counts['domain']}/420 · 승인 DDG3+CG3 기준값 그대로 |",
f"| 기존 UI / MAP_B / 경고 / 추가 | {counts['UI88']} / {counts['MAPB91']} / {counts['warnings']} / {counts['extra']} 전부 통과 |",
f"| MAP_C | {counts['UIC135']} / {counts['motion73']} / {counts['rules45']} / {counts['rings33']} / {counts['DOM13']} 전부 통과 |",
f"| MAP_D native / UI / 경계 | {counts['Dnative84']} / {counts['Dui213']} / {counts['Dedges145']} 전부 통과 |",
f"| 종료기 | {term['shots']}발, 성공 {term['successBefore']}→{term['successAfter']}, 개별 결과 차이 {len(term['differences'])} |",
f"| 자연 탐지→LOCK→정식 VLS→실제 WebGL | {gl['flights']}발 / {gl['checks']}검사, 기존 {gl['hitCount']}명중 그대로, 궤적·결과 차이 0 |",
f"| 기존 EW·물류 / H3 | 94 / 195 검사, D/E raw 결과 동일 |",
f"| E1–E7 UI | {len(u['checks'])}/{len(u['checks'])} |",
f"| ECM native 파이프라인 | {len(n['checks'])}/{len(n['checks'])} |",
f"| 추가 저장·조회·축척 | {len(p['checks'])}/{len(p['checks'])} |",
'| 비행 지문 / 사거리표 / 저장 | native281 동일 / ENV_D120행 byte 동일 / 스키마 변경 0 |','',
'### E1–E7','',
'| 항목 | 실측·판정 |','|---|---|',
'| E1 | ARM/AUTO TGT/개별 CG selector DOM 0, DEBUG 기능 유지, ARMS STATUS + 메뉴 열림·닫힘, id 중복 0 |',
f"| E2 | 단계 복원·레이더 단독 토글·바깥 탭 닫힘 통과. 상태 전환 시 바 박스 최대 이동 {max(v for k,v in u['records'].items()if k.endswith('.barErrorPx')):.3f}px |",
'| E3 | OFF: 자동 EA·기만체 0. JAM: EA 운용, 채프/Nulka 자동 0. FULL: D의 발사 이력·EA·재고·RNG와 동일. NPC 설정 불변 |',
'| E4 | 수동 SRBOC 기본 2발 / Nulka 1발, 모든 ECM 단계에서 가능. 쿨다운·무 cue·무 재고 native 사유 유지. 선택 무장/표적 불변 |',
'| E5 | MANUAL/SEMIAUTO/AUTO 지도 하푼 실제 발사 성공. NEUTRAL 보호 거부 유지. H3 A/B 결과 동일 |',
'| E6 | 경로 시작/종료의 창 자동 열림 0, 탭/내부 모드 변경 0, 빈 바다 한 탭당 하푼 경유점 +1 / 함 항로점 +0 |',
'| E7 | 832×384 팝오버/기만체 팝업 화면 안. 일반 버튼 ≥28px, 수동 발사 ≥40px(100%). 85/130% 추가 경계 검사 통과 |','',
'### 120초 truth 해시','',
'| 실행 | SHA-256 |','|---|---|']
for r in world['records']:lines.append('| '+r['mode']+' | `'+r['truthSha256']+'` · MAP_D 동일 |')
lines+=['','## 4. 변경 범위·입력 감사','',
'새 UI는 자함 명령 주소·재고·장비 가용/쿨다운, 기존 관측 기반 softKillPrimaryThreat, DOM/viewport만 읽는다. 적 truth/엔티티 배열/RF 세계 직접 참조는 0이다. 센서/비행 코드·프로파일 계수를 바꾸지 않았다. 상세 공급원은 data-sources.json, 함수별 변화는 MAP_E.diff와 evidence/static.json을 참조한다.','',
'최상위 변경 함수:', '']+['- `'+x+'`'for x in st['differentTopLevel']]+['',
'이 중 자함 자동 기만체 2개는 FULL 진입 조건만, routeEditing/preview는 허용된 UI/권한 범위만 바꿨다. 나머지는 분리한 원래 노드로의 UI 참조를 유지한다. NPC 복사본은 바꾸지 않았다. 기존 SAM·함포·H3 명령 경로, DEBUG/콘솔 및 기존 키보드 함수는 삭제하지 않았다. AUTO TGT 버튼과 개별 CG 조작 UI, 수동 NJ/DJ 선택 UI는 제거했다.','',
'ARM 전수 표는 PRE_IMPLEMENTATION.md와 ARM_CONTROLS_BEFORE.tsv(DDG27/CG28, 하위탭·출처 링크 포함). 시나리오/리셋/디버그 버튼은 처음부터 DEBUG였다.','',
'## 5. 시험 이관·실행 출처','',
'제거된 ARM을 기다리던 ISAR/EMCON 준비는 분리된 원래 버튼의 원래 리스너를 호출하는 test-only adapter로 이관했다. 게임 DOM을 다시 만들지 않았다. 내부 passive label 문자열 검사는 유지하며, 외형 경계는 새 EMCON 칩으로 검사한다. MAP_C의 직접 EMCON 클릭 준비는 새 팝오버의 레이더 버튼으로 바꿨다. MAP_D의 generic AUTO 거부 검사는 mode를 명시해 기존 native gate를 계속 검사하고, 새 지도 MANUAL 권한은 E5에서 따로 검증한다.',
'H3 원본은 MAP_D/E 모두 오래된 currentStrictSchema=H3 기대값만 실패했다. 현재 H4로 기대 문자열만 갱신해 재실행했고 나머지 193개 검사/모든 권한·invalid-save 검사를 유지했다. 원본 결과는 ew-h3-original에 남겼다.',
'장시간 tool 실행 세션이 종료되어 일부 WebGL 묶음이 중단됐다. 중단 로그와 190개 통과 기록은 development/attempt 증거로 보존하고, 최종 D UI 213개 등 미완료 묶음 전체는 detached runner에서 다시 실행했다. 중단 결과를 최종 통과로 합치지 않았다.',
f"표시 폭 보정 전에 완료된 native 증거의 실제 제품 SHA는 `{eq['priorHtmlSha256']}`다. 최종 제품은 `{b['sha256']}`다. 해당 보정은 **MAP_E_UI 블록 안에만** 있고, 블록 밖 전체 JS 및 모든 named symbol이 byte 동일함을 검증했다. native/모듈 증거만 이 근거로 재사용하며, 최종 입력·레이아웃 UI, world120, 실제 WebGL8은 최종 제품에서 검사했다. 각 JSON의 실행 SHA를 바꾸지 않았다. 이전 UI 블록은 prior-presentation.js로 재구성 가능하다.",
'자세한 이관은 TEST_MIGRATIONS.md, 증거 적용 범위는 evidence/acceptance.json과 presentation-equivalence.json을 참조한다.','',
'## 6. 스크린샷·산출물','',
'보고서 ZIP 루트 REPORT.html에서 PC/폰, MAIN/PiP, DDG/CG의 팝오버·기만체 거부/발사·경로 편집을 볼 수 있다. 원시 검증 JSON/로그/소스 diff/상태/체크섬을 함께 포함한다. 게임 HTML은 별도 HTML ZIP의 단일 파일이다.','',
'검증 실행 시간(각 도구 실측, 병렬/대기 포함 범위가 달라 합산하지 않음):','']
for label,q in [('새 E UI',u),('ECM native 모듈',n),('저장/축척 정책',p),('EW/H3 A/B',ew),('world120',world)]:
 if 'elapsedS'in q:lines.append(f"- {label}: {q['elapsedS']:.1f}s")
for kind in ['gpu','cpu']:
 q=j('evidence/remaining-'+kind+'.json');lines.append(f"- 세션 중단 후 {kind} 잔여 묶음: {q['elapsedS']:.1f}s")
lines+=['','## 7. 남은 사항','',
'- EMCON 비방사 수동 지정의 GUI 위치는 후속 검토(사용자 결정). 이번에 내부 기능과 정밀추적 차단은 보존했다.',
'- JAM 단계는 게임 세이브에 저장되지 않고 불러오면 FULL로 추론한다. 레거시 수동 NJ/DJ 승인 상태는 읽기 전용으로 보존한다.',
'- 실제 휴대폰 FPS/터치 하드웨어 시험은 수행하지 않았다. 로컬 헤드리스 검증이며 GitHub Actions/CI 파일은 변경하지 않았다.',
'- main 병합, release/tag 생성 없음. map-e 산출물·원격 readback 이후 PR만 제출한다.','']
(H/'REPORT.md').write_text('\n'.join(lines));print('REPORT.md written')

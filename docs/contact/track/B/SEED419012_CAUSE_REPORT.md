# TRACK-B seed419012 — 실제 연관·cue 차이의 원인 계측

상태: **원인 경로 계측 완료, 기존 strict FAIL 미승인 유지**. 제품·기대값·허용 오차를 바꾸지 않았다. 이는 원래 D1 30건 전체의 재시험이나 TRACK-B 최종 승인 보고가 아니다.

## 1. 결론

이 차이는 단순한 진단 필드 추가가 아니다. 같은 SPY 관측에 기존 두 canonical 파일의 native NIS가 근접했을 때, TRACK-B가 실제로 관측 갱신을 보류했다. 그 뒤 canonical 평균/P·freshness와 focused 재방문 순서가 달라지고, 기존 C55가 읽는 CMS cue의 TTI 순서가 바뀌었다. 따라서 마지막 두 mount의 cue가 `300000002→300000001`로 달라졌다.

반면 계측한99개 프레임의 C55 로컬 파일 ID·로컬 추정/보호·실제 추적·무장 상태는 같았고, 원래 D1 종료 자료도 **두 cue 필드 외에는 동일**했다. 이 사격에서 결과가 같다는 사실은 관측 변화의 자동 승인이나 장래 전투 불변을 뜻하지 않는다. 원래 strict signature 차이는 FAIL로 남긴다.

초기 “A에서29.95초에만 두 번째 파일이 생겼다”는 가설은 이번 자료와 맞지 않았다. **29.0초 첫 프레임에서 A/B 모두 두 파일이 이미 존재하며**, 두 번째는 VISUAL source·1hit다. 포착 구간에 CREATE는 없다. 앞선 생성 이력은 이번 창 밖이므로 duplicate 제거를 입증했다고 쓰지 않는다.

## 2. 실행과 계측 무해성

- A: `Aegis_SIM_v48_WIP_TRACK_A.html`, SHA `e2c1976a8a21eae6a494bf6caf0ec5b702663bd97721763ef7e92c6d6096d67a`.
- B: `Aegis_SIM_v48_WIP_TRACK_B.html`, SHA `0b3e5ad90324f10057f2e500692f4f56b020ddc4f12db16423bf4d258a38e4c6`.
- 원래 `docs/ciws/dmg/A/diagnostic.js`와 `__CIWS_DMG_A__.run(c,true)`를 그대로 실행했다. DDG-119, bearing90°, seed419012, MANUAL, 함포 AutoAA OFF, 원래 fixed tick·원래 발사/피해/RNG 경로다.
- `trace_seed.py --run --root-go`가 **공유 heavy_browser_slot 하나**를 잡고 A/B를 각1회 실행했다. 브라우저는 각 페이지 뒤 finally에서 닫았다. 추가 자연 RF/NIS/EKF/연관 계산을 호출하지 않았다.
- test-only pass-through watcher가 native A/B trace sink에서 **이미 만들어진 레코드**와 직접 읽은 canonical/C55 추정·캐시 cue를29–30.65초에 복사했다. cache 생성기·snapshot 재계산·geometry 함수는 호출하지 않았다. 기록된 native fixed-tick wrapper source SHA는 A/B 모두 `c4f08708d5810c3838be61e8c354e5709178929007056069674a4624b8ffc1b1`다.

|검증|A|B|
|---|---:|---:|
|계측 실행의 원래 OFF signature와 완전 일치|PASS|PASS|
|진단 레코드 수|662|1117|
|진단 원시 JSON bytes|1,711,730|1,914,451|
|직접 추정/캐시 프레임|99|99|
|금지 진실 필드|0|0|
|capture fault / overflow|0 / 0|0 / 0|
|반복 query 동일·게임/private 상태 불변|PASS|PASS|
|preflight 및 원래 바인딩 복원 후 awaited ENV match|true / true|true / true|
|기존 원시 OFF 출력과 다른 leaf|elapsedMs1개|elapsedMs1개|

원래 diagnostic.js는 시험 중 `spawnEnemyMissile`·`applyInterceptResult`를 감싼다. 실행 직후 ENV가 정확히 이 두 함수를 다르다고 보고한 자료를 보존했다. 원래 run·결과·signature 수집이 끝난 뒤 **처음 보관한 두 함수 참조만 복원**, 추가 tick/명령 없이 다시 await한 ENV는 `match:true`다. 복원 전후 게임/private 상태 해시도 같다. 초기 복원 없는 ENV FAIL 시도와 fixture 시작 전 TargetClosed 환경 실패는 `evidence/seed419012-cause-attempts/`에 남겼다. 이를 제품 FAIL 또는 최종 PASS로 합산하지 않는다.

## 3. 관측 → 보류 → 추정 변화

native tick1796(29.933333초)의 SPY SEARCH_HORIZON 관측은 A/B에서 같다.

|실제 제공된 관측|값|
|---|---:|
|rangeM|2370.948928745497|
|azRad|1.5802040690556607|
|elRad|-0.003971368544857385|
|radialMps|-294.8917165211414|
|native AIR4D NIS →300000001|1.4913444179610076|
|native AIR4D NIS →300000002|1.1536789827861333|
|대안 총 NIS 차이|0.33766543517487424|

두 후보는 기존 gate64 안이며 같은 관측·기존 native NIS 계산 결과다. A는 더 작은 NIS의002를 실제 갱신한다. B는 같은 cardinality의 대안 차이가 기존 B 정책1 이하라 `OWN_SPY_GLOBAL / HOLD / AMBIGUOUS_ASSOCIATION`을 기록하고 해당 관측을 보류한다. 새 NIS를 진단에서 다시 계산한 결과가 아니다.

프레임의 step은 native 함수 내부 사건보다1 증가해 보일 수 있다. tick1796의 보류 뒤 **post-tick frame1797**에서 처음 canonical state/P와 캐시 cue 값 차이가 나타난다. CREATE 차이가 아니다. 이후 A의 focused 갱신은1799에001,1801에002로 나뉘지만 B는1799에002·001을 모두 갱신한다.1830에는 A가001에 VISUAL을 붙이고, B는002에 VISUAL·SPQ AIR를 붙인다. 평균/P·source/freshness와 실제 scheduler 경로가 변한 증거이며, metadata-only로 분류하지 않는다. 전체 native 갱신 순서는 `canonical-updates.csv`와 원 trace에 있다.

## 4. 실제 캐시 TTI와 로컬 CMS 연관

첫 cue **값** 차이는 frame1797, cue **순서**와 실제 mount cue 차이는 frame1800이다. `b.cues`는 이미 native가 만들어 정렬해 둔 배열을 그대로 읽었다. 별도 추정 TTI를 만들지 않았다.

frame1800, GUN mount1의 실제 캐시:

|제품|native 순서0|TTI(s)|순서1|TTI(s)|
|---|---|---:|---|---:|
|A|300000001|7.658188576828569|300000002|7.6590916896089345|
|B|300000002|7.629415071548134|300000001|7.655545168364699|

같은 프레임 RAM mount2의 로컬 파일 `-5500002`는 CMS 연결도 다르다. 기록된 local/CMS 추정 좌표로 기존 거리·속도 gate 수식만 **사후 재현**한 값은 다음과 같다. 이는 game 함수 재실행이나 새 연관 입력이 아니다.

|제품|기록된 cmsTrackId|후보001 거리(m)|후보002 거리(m)|native 거리 gate(m)|
|---|---:|---:|---:|---:|
|A|300000002|4.708775705997145|1.9152315728587266|105|
|B|300000001|4.603332469494452|4.763120039281293|105|

양 제품 모두 후보2개와 canonical 파일2개가 기록됐고, 두 후보의 velocity gate도 통과했다. 수치상 native의 최근접 선택과 일치한다. 전체 사후 거리 replay와 원래 선택은 `ANALYSIS.json`에 별도 등급으로 남겼다.

마지막 frame1838의 실제 캐시 TTI:

|제품·mount|native1순위|TTI(s)|native2순위|TTI(s)|
|---|---|---:|---|---:|
|A GUN|002|6.976145618993533|001|7.0423472604731465|
|B GUN|001|7.000081519721263|002|7.024040628315056|
|A RAM|002|6.989602928597308|001|7.050597368522857|
|B RAM|001|7.003378644115532|002|7.033123797618139|

고정 A 소스의 `c55CmsRows` L37288–37297 및 `c55StepSensors` L37402는 관측 CMS 후보를 native TTI 순으로 정렬하고, `updateCueing` L37965–37968은 그 첫 trackId를 `m.cuedTarget`에 쓴다. `c55AssociateCms` L37299–37315는 로컬 파일과 관측 CMS 파일을 거리로 연관한다. 실제 사격은 `c55Threats`/`c55Select`의 음수 로컬 파일을 사용한다(L37420–37426, L37955). 이번 창의 실제 로컬 추적 ID는 GUN `-5500001`, RAM `-5500002`로 A/B 동일했다. 자함탄 로컬 파일 `-5500008/-5500007`도 별개로 보호됐다.

## 5. 실제 사격 결과와 남은 판정

원래 after-action 종료 출력의 전체 leaf 차이는 정확히 `/mounts/0/cue`, `/mounts/1/cue` 두 개다. 각각 A002→B001이다. 두 제품 모두 피격0, HP100, 생존, RAM3발 사용, GUN0발,30.633333초(step1838)에 같은 결과로 끝났다. 마지막 RAM의 `PROX_DETONATION_KILL`, 최근접4.747193334345742m, 전역 RNG3594350424도 같다. 이는 **이 종료 자료의 비교**이며 모든 센서/private RF 상태·장래 전투까지 같다고 확장하지 않는다.

모든 캡처 프레임의 원시 leaf 차이5,678건과 원래 A/B 출력의 원시 차이1,345건을 gz JSONL로 남겼다. 후자는 이벤트 배열의 추가/순서 변화와 elapsedMs도 포함하며, 보고서가 보기 좋게 일부 필드를 삭제하지 않았다. 최종 after의 두 필드 차이만 따로 설명하는 것은 원시 전체 차이를 없애는 검수 대체가 아니다.

이번 계측은 **근접 비용 대안의 보류가 canonical 추정을 바꾸고, 기존 native cue 정렬·CMS 연관을 통해 최종 cue ID를 바꾼 경로**를 확인했다. 관측한 전투 결과 악화는 없지만, 원래 strict 실패를 자동 승인하거나 새로운 기대값으로 바꾸지 않는다. 앞선 파일 생성 이력, 이 두 관측 파일의 실제 물리 표적 동일성, 모든 미래 사격 영향은 이번 자료로 증명하지 않는다. duplicate 제거·완전한 TRACK-B closure·release 승인은 주장하지 않는다.

## 6. 재현과 자료

```sh
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/dev/shm python -u docs/contact/track/B/trace_seed.py --run --root-go
PYTHONDONTWRITEBYTECODE=1 python docs/contact/track/B/analyze_seed_trace.py
```

브라우저 실행은 root의 별도 GO 및 공유 lease가 필요하다. 제품·원래 시험 helper·기대값은 바꾸지 않는다.

- `evidence/seed419012-cause/PLAN.json`: 도구/helper/원래 fixture/product/OFF 근거 SHA.
- `EXECUTION.json`, `baseline-receipt.json`, `active-receipt.json`: 실제 실행·서명·ENV·순수성·lease.
- `*-diagnostics.json.gz`: 금지 진실 필드 없는 실제 관측/연관·추정·캐시 cue 자료.
- `*-original-result-after-action.json.gz`: 원래 시험의 전체 사후 결과. 센서·AI 입력과 분리.
- `*-all-reference-differences.jsonl.gz`, `all-cross-version-original-output-differences.jsonl.gz`, `all-captured-frame-differences.jsonl.gz`: 모든 원시 차이, 필드 제외0.
- `ANALYSIS.json`, `canonical-updates.csv`: 원 사건과 사후 수식 replay를 구분한 분석.
- `evidence/seed419012-cause-attempts/`: 초기 ENV wrapper guard FAIL 및 실행 전 브라우저 환경 실패 보존.

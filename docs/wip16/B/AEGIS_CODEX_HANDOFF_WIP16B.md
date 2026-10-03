# AEGIS WIP16B 코덱스 개발 인계서

작성 기준: 2026-10-03 13:35 KST 이후 조회한 원격 상태.

저장소는 `0-FLANDRE-0/Aegis_Project`다. WIP16B는 사용자 HTML 업로드, 바이트 일치 확인, 전용 브라우저 회귀와 전체 CI까지 완료했다. 기술적 통합 판정은 PASS이며 PR #41은 열려 있고 main에 병합되지 않았다. 다음 기능의 방향은 출항 전 함선 선택과 생성·초기화 공통화, 기존 DDG-119 보존, 벙커힐 모델·프로필 연결 순서다. 새 기능 번호와 브랜치는 아직 확정하지 않았다.

이 문서는 현재 상태와 이어받을 작업을 전달한다. 병합·승격·태그·릴리스·브랜치 삭제 승인으로 해석하지 않는다. 이후 사용자가 지시한 범위에서 이어서 작업한다.

## 1 원격 기준과 현재 판정

| 항목 | 확인한 값 |
| --- | --- |
| 저장소 | https://github.com/0-FLANDRE-0/Aegis_Project |
| main HEAD | `d2b840bae95267ffc53bfda847442b2211c1ab03` |
| 작업 브랜치 | `WIP16` |
| 인계서 작성 전 WIP16 HEAD | `f92c668bd5e8d6c3fa16bf0d4fd85c5184ebfc11` |
| 마지막 실행 검증 support HEAD | `05cd0ebcb7c0fb8a7bfcd2f65aa46184545585d4` |
| 사용자 WIP16B HTML 업로드 commit | `7562bb0925e2b85521d37fefd2c81898ed6de18a` |
| 기존 PR | https://github.com/0-FLANDRE-0/Aegis_Project/pull/41 |
| PR 상태 | OPEN, unmerged, base main, head WIP16 |
| 안정판 | `Aegis_SIM_v48.html` |
| 최신 검증 개발본 | `Aegis_SIM_v48_WIP16B.html` |
| main 병합·v48.1 승격 | 실행하지 않음 |
| 새 release/tag·브랜치 삭제 | 실행하지 않음 |

인계서 추가 커밋은 위 상태 기록 이후의 문서 커밋이다. 새 환경에서는 브랜치 HEAD와 PR 상태를 다시 조회한다. `f92c668`은 실행 검증 뒤의 문서·JSON 증거·체크섬 커밋이며 HTML, 빌더, 테스트, 워크플로를 바꾸지 않았다.

첨부된 `AEGIS_PROJECT_INSTRUCTIONS-1.md`의 고정 규칙은 참고하되, 그 안의 WIP11 스냅샷과 번호표는 과거 기록이다. 현재 main/WIP16의 실제 파일과 최신 상태 문서가 현재 진행 상태를 정한다. main의 안정판과 WIP16의 개발본을 혼동하지 않는다.

## 2 정확한 파일 식별

| 파일 | 바이트 | SHA-256 | Git blob |
| --- | ---: | --- | --- |
| `Aegis_SIM_v48.html` | 7,354,511 | `9e786ddb1331fcd496b6b9604cec87317667ebc501e99270cc33fd6ba1ab9e83` | `f540b68f138e3ed85614c41f6794be78602229d8` |
| `Aegis_SIM_v48_WIP16A.html` | 7,354,882 | `6fba8ad6225e83fc86c7f07d275ab58feb4b8027d83a29aabeba3f6fa2382f24` | `d0d8b3de795716cb21ba2f7ba9673b8024dc2ceb` |
| `Aegis_SIM_v48_WIP16B.html` | 7,357,036 | `7b63a62bb1cad123b7d7eb17c1fbe26452194c3ff2c637c09b4c48a2a6c8d76d` | `d47126f8296f3bde6b81af0ce1a2668a3c79f9cf` |

WIP16B decoded main JavaScript SHA-256는 B 상태 문서 및 `docs/wip16/B/edits.json`의 최종 main hash와 대조한다.

HTML은 사용자가 직접 업로드했다. 업로드 commit에는 B HTML 한 파일만 추가됐고, 원격 크기·Git blob이 로컬 SHA-256 검증본과 exact 일치한다. stable v48와 WIP16A 원본 blob도 보존됐다. 이 인계 작업에서 큰 HTML을 재작성하거나 재인코딩하지 않는다.

## 3 먼저 읽을 저장소 문서

main에서 안정 기준을 확인한 뒤 WIP16의 아래 파일을 읽는다.

| 파일 | 목적 |
| --- | --- |
| `README.md` | 안정판과 최신 개발 후보 구분 |
| `AEGIS_PROJECT_INSTRUCTIONS.md` | 현재 저장소 작업 규칙과 인계 기준 |
| `AEGIS_PLAN_STATUS_v48.md` / `SHA256SUMS_v48.txt` | 안정 v48 기준 |
| `WIP16_BRANCH_STATUS.md` | B 최종 판정과 A 역사 기록 |
| `AEGIS_PLAN_STATUS_v48_WIP16B.md` | B 변경 범위, 원인, 검증, 다음 단계 |
| `SHA256SUMS_v48_WIP16B.txt` | 현재 B HTML과 support 무결성 |
| `docs/wip16/B/README.md` | 빌더·렌더러 검사 실행 방법 |
| `docs/wip16/B/evidence/upload_closeout.json` | 업로드, 중간 실패, 최종 CI, artifact hash와 검사 행 |
| `docs/wip16/B/evidence/actions.json` | 기존 구현 검증과 전체 job 목록 |
| `docs/wip16/A/CLOSEOUT.md` | B 수리 전 A 마감의 역사 기록 |

`docs/wip16/A/CLOSEOUT.md`와 A 상태 문서의 HOLD는 당시 기록이다. 현재 통합 판정은 B 상태 문서와 upload_closeout을 따른다. 원본 A 기록을 현재 판정으로 덮어쓰지 않는다.

## 4 WIP16B에서 마친 내용

WIP16A에 사용자가 추가한 기능을 유지하면서 C5 모델의 렌더러 연결과 진단 검사를 수리했다. B 제품 변경은 3개 패치 묶음이며 전투·항법·피해 계산을 수정하지 않았다.

### 구멍 생성 지연

기존에도 진입·이탈 구멍의 표면 검색은 `HULL_3:SIM_antifoul`에 성공했다. HIGH 내부 화면의 SwiftShader GPU 제출이 느려 cooperative geometry job이 충분히 진행하지 못했고, 구멍 메시가 공개되지 않아 audit가 `meshMatched:false`를 표시했다. 따라서 표면 검색 실패나 물리 구멍 부재로 오판하면 안 된다.

B는 필수 ENTRY/EXIT geometry job이 남아 있을 때 직전 canvas를 유지하고, geometry commit 뒤 WebGL 제출을 재개한다. cut/fold 알고리즘, 구멍 면적, 작업 예산, 물리 틱은 유지했다. 선택적 detail 작업이 남는 것과 필수 입구·출구 생성이 미완료인 것은 구분한다.

실제 Chromium에서 선체 양현 구멍 2개, 원본 geometry 교체, 구멍 중심 ray 통과, 메시 복구를 확인했다. 단순히 audit 플래그만 PASS로 바꾼 수정이 아니다.

### 현재 C5 부품을 검사하는 진단

- `NAV_SCANNER`는 `MAST_UPPER` / `MAST_BASE` 아래에 있다. parent-local 위치를 ship-local SI로 환산해 실제 등록점·parent chain을 비교한다.
- 현재 등록점은 `xM=18.46, yM=0, zM=36.8`이다. 옛 야드암 좌표나 `rotor.position`만으로 검증하지 않는다.
- 마스트 drawable 수는 17개, scanner mesh는 2개, 기능 NAV rotor는 1개다. 장식 AUX scanner를 기능 센서 중복으로 세지 않는다.
- 함포는 실제 C5 gun joint를 검사하고, VLS는 등록된 96개 셀과 hinge/panel의 일대일 연결을 검사한다.
- 기존 VLS 피해 체적 중심과 실제 개별 셀 등록점은 역할이 다르다. 검사 통과를 위해 피해 체적을 셀 위치로 재튜닝하지 않았다.
- imported root에 기존 보호 스키마의 진단 binding을 연결했다.
- C5에 없는 옛 구명뗏목 6개 검사는 `applicable:false`다. 미적용 항목을 강제로 PASS 처리하지 않는다.
- legacy debug model의 기존 검사 경로는 유지한다. 이 문서의 최종 C5 PASS를 legacy 모델 전체 검증으로 확대하지 않는다.

검색할 주요 식별자: `WIP148_THREE_VERSION`, `bridgeMasterEAuditWip16B`, `contractAuditWip16B`, `damageAuditV48Wip03`, `buildDamageScarsV3`, `_wip16bOpeningDrawDeferrals`, `NAV_SCANNER`, `GUN_BASE`, `vlsLids`, `ACTIVE_SHIP_RUNTIME`, `__NAVAL_SIM_DIAG__`, `__WIP148_3D_VIEW__`.

### 보존한 범위

HTML C55는 14개 record로 구성되며 index 13이 main JavaScript다. A→B에서 압축 record 0–12가 모두 동일하고, main의 `const WIP148_THREE_VERSION=` 앞 전체 source도 동일하다. 무기·센서 계산, INS/GPS/DL/loft, 전투 RNG, 피해 solver, 구획·승조원과 모델 geometry를 바꾸지 않았다. 제품 B의 source 보존과 이후 테스트 harness 보완을 구분한다.

## 5 최종 검증과 증거

최종 실행 검증은 `05cd0ebcb7c0fb8a7bfcd2f65aa46184545585d4`에서 수행했고, 그 이후 문서 변경만 추가했다.

| 검증 | 결과 | Actions run |
| --- | --- | --- |
| B 전용 | 1/1 job PASS, package 34/34, renderer 13/13, runtime 14/14 | https://github.com/0-FLANDRE-0/Aegis_Project/actions/runs/37096259094 |
| A 원본 보존 | 4/4 job PASS, Python 3.11/3.12/3.13 exact package, A runtime 14/14 | https://github.com/0-FLANDRE-0/Aegis_Project/actions/runs/37096259099 |
| 전체 일반 smoke | 32/32 job PASS, B 실제 3D 통합 포함 | https://github.com/0-FLANDRE-0/Aegis_Project/actions/runs/37096259111 |

일반 smoke의 모든 job이 B 전용인 것은 아니다. 역사 payload를 유지하는 검사와 최신 루트 파일을 선택하는 검사가 혼재한다. B 전용 workflow와 일반 3D job은 업로드 B를 별도 임시 재구성본과 `cmp`한 뒤 검사한다. 업로드 파일이 있으면 B workflow는 그 파일을 덮어쓰지 않는다.

초기 CI 보고의 30/30은 첫 페이지 집계였다. 당시 실제 전체 결과도 32/32 PASS였고 현재 증거에 수정했다. GitHub job wrapper가 첫 페이지만 반환할 수 있으므로 `/actions/runs/<id>/jobs?per_page=100` 또는 페이지네이션으로 `total_count`와 실제 수집 수를 맞춘다. run 결론뿐 아니라 전체 job 결과도 확인한다.

최종 검사에서 실제 구멍 2개, 원본 geometry 복구, authoritative state 불변, 내부 138공간·160연결·70장비, 승조원 310명과 1개 instance batch를 확인했다. 센서를 0.25m 잘못 옮기거나 VLS 셀을 잘못된 hinge에 연결하면 FAIL이고, 정상 ship root 이동·회전 뒤 ship-local mount 검사는 PASS다. core/page errors는 0이다. 캡처는 HIGH 구멍 검사 뒤 LOW presentation preset에서 수집했다.

| 최종 artifact | ID | ZIP SHA-256 |
| --- | ---: | --- |
| B renderer/runtime | 11264402786 | `a3341ab6b347889844bca50466379ab3261064a2b71f804d39f9c5e7a29a8ed2` |
| A seeded runtime | 11265035465 | `f7a724202a04954f54867cb70686f3a3776e5c1ad5adbfd9ced27877ec4b0f8d` |
| 일반 B 3D | 11264257849 | `6dc3c52f17fb0380c561cef817dd6287e7b83272f94c07a22e50012b411e4f1a` |

artifact 보존 기간이 끝나도 `evidence/upload_closeout.json`의 출처·hash·검사 행과 재현 가능한 테스트를 사용한다. 전체 telemetry와 이미지는 artifact에서 받을 수 있을 때 받는다.

### 테스트 harness에서 추가로 고친 문제

업로드 직후 B/A/전체 CI는 통과했으나 반복 실행 중 다음 실패를 발견했다. 실패 기록은 upload_closeout에 남아 있다.

1. B 필수 geometry가 진행 중인데 65초 대기 제한이 먼저 끝났다. 65.96초에 generator 7,164 steps, commit 0, page error 0이었다. B 전용과 일반 3D 검사의 대기를 최대 180초로 맞추고 mesh/ray/상태 불변 합격 조건은 유지했다.
2. A의 기존 runtime 13조건 중 `no ship hit` 한 항목이 실패했다. case seed는 고정했지만 loader가 만드는 초기 환경 seed가 무작위였다. 기존 simulator fallback인 `0x6d2b79f5`를 loader 전에 고정하고 이전 phase context를 닫았다. seed를 검색해 합격하는 값을 고르지 않았다.
3. 전체 benchmark를 새 context에서 같은 boot/case seed로 반복하고 전체 결과 exact 일치 1조건을 추가했다. 원래 13조건·threshold는 유지해 현재 14조건이다. A와 B의 전체 benchmark 및 spotting 출력도 exact 일치한다.
4. harness 변경 직후 A support checksum 갱신이 빠진 중간 commit은 package에서 실패했고, 최종 `05cd0eb`에서 수정했다. 최종 A/B 체크섬을 함께 검사했다.

로컬 환경에는 실행 가능한 Chromium이 없어 이 세션의 실제 브라우저 검증은 Actions Chromium/SwiftShader에서 수행했다. 새 코덱스 환경에서 브라우저가 있으면 동일 검사를 실행할 수 있다. 환경이 없으면 미실행 사유를 기록하며 브라우저 PASS를 추정하지 않는다.

## 6 코덱스에서 시작하는 절차

1. 작업 디렉터리와 remote가 위 저장소인지 확인한다. `git status --short`를 보고 사용자 변경을 보존한다. `git fetch origin`으로 main/WIP16과 PR 상태를 새로 확인한다.
2. 저장소에 `AGENTS.md`가 있다면 해당 경로 규칙을 읽는다. 이번 원격 스냅샷에는 `AGENTS.md`가 없었지만 새 환경에서는 다시 확인한다.
3. main의 README·지침·stable 상태/체크섬을 읽고, WIP16의 최신 B 상태·인계서·upload_closeout을 읽는다. 디폴트 checkout이 main이면 그곳에 B 구현이 있는 것으로 가정하지 않는다.
4. HTML 작업 기준은 사용자 지시와 병합 상태로 정한다. WIP16 마감 확인은 frozen B로 한다. 아직 미병합인 상태에서 새 기능을 stable main에서 시작하면 WIP16 결과가 빠지므로 먼저 작업 계보를 정리한다. 병합을 자동 실행하지 않는다.
5. SHA-256과 Git blob을 대조하고 기존 통과 결과를 읽는다. 문서 확인만 하는 작업에서 변경 없는 전체 CI를 반복할 필요는 없다. 코드를 수정하거나 검증 불확실성이 생기면 관련 검사부터 실행한다.
6. 함수·상태 소유자·호출자·테스트를 찾은 뒤 이번 사용자 지시에 필요한 최소 범위를 구현한다. 전 파일 재작성이나 동시에 여러 시스템 재설계를 시작하지 않는다.

현재 B의 재현 명령은 저장소 루트 기준이다. Python 3.12, Node.js 및 브라우저 검사가 필요하면 `playwright==1.55.0`과 해당 Chromium을 준비한다.

```sh
sha256sum -c SHA256SUMS_v48_WIP16A.txt
sha256sum -c SHA256SUMS_v48_WIP16B.txt
python docs/wip16/B/build_wip16b.py Aegis_SIM_v48_WIP16A.html /tmp/Aegis_SIM_v48_WIP16B.html
cmp Aegis_SIM_v48_WIP16B.html /tmp/Aegis_SIM_v48_WIP16B.html
python docs/wip16/B/tests/package16b.py Aegis_SIM_v48_WIP16B.html Aegis_SIM_v48_WIP16A.html
python docs/wip16/B/tests/render16b.py Aegis_SIM_v48_WIP16B.html artifacts/wip16b/renderer
python docs/wip16/A/tests/runtime16a.py Aegis_SIM_v48_WIP16B.html
```

`build_wip16b.py`는 최종 B hash를 강제하는 동결 빌더다. 새 기능을 넣으려고 B의 FINAL_SHA guard를 제거하거나 같은 파일명으로 다른 HTML을 만들지 않는다. 새 제품 변경에는 새 버전 토큰과 대응 상태 문서를 사용한다. HTML 안의 큰 압축 문자열을 직접 편집하지 말고 C55 record를 해제해 필요한 source를 검토하고 재현 가능한 패치·패킹 절차를 사용한다.

## 7 다음 작업의 권장 범위

사용자는 새 함선의 모델링·애니메이션을 이미 별도 HTML로 만들어 놓았고, 세부 시스템과 runtime 연결을 원한다. 먼저 제한된 공통화로 기존 함선을 보존한 뒤 벙커힐을 연결하는 방향에 동의했다. 다음 기능 번호는 아직 정하지 않았다.

### 첫 단계 출항 전 함선 선택과 초기화 공통화

기존 DDG-119를 첫 기준으로 삼아 함선 선택 → profile 확정 → runtime 생성 → world 등록 → 렌더러 연결 흐름의 소유자를 정리한다. hull/model, 장비 inventory, joint/장착점, 구획/피해, 승조원과 UI binding 중 어떤 값이 profile이고 어떤 값이 가변 runtime인지 명확히 한다.

기존 singleton과 함선 이름에 박힌 경로를 찾아 꼭 필요한 생성·초기화 경계부터 정리한다. 모든 global을 한 번에 없애거나 엔진 전체를 모듈로 갈아엎는 작업은 범위 밖이다. 함선 선택을 출항 전에 확정하고 출항 후 교체는 별도 요구가 생길 때 다룬다.

첫 완료 조건은 기존 DDG-119의 출항, 재시작, UI, 장비 재고, 센서/조작 binding, 내부·승조원, 피해 표시와 기존 진단 결과가 보존되는 것이다. B에서 고친 nested mount, 96개 VLS binding, geometry queue 처리도 유지한다. 새 함선 profile을 추가해도 기존 profile의 가변 상태를 공유하지 않게 한다.

### 둘째 단계 벙커힐 연결

벙커힐은 이미 있는 viewer asset과 joint/animation을 재사용한다. viewer가 보여 주는 부품을 runtime 소유자와 연결하고, 각 무장·센서·문·추진 joint 및 UI inventory를 profile에서 생성하도록 한다. 두 함선이 독립된 상태로 초기화되는지 검사한다.

외형 부품 연결만으로 구획·재질·침수·질량·승조원 시스템이 완료된 것으로 취급하지 않는다. viewer에 없는 내부/피해 자료는 별도로 정의하고 검증해야 한다. 기존 DDG-119 내부 구조를 검토 없이 벙커힐에 복제하지 않는다.

첫 범위는 출항 전 한 척을 선택해 운용하는 기능이다. 복수 함정 동시 운용·편대·새 소나·헬기·다른 무기 체계는 후속 범위다.

## 8 벙커힐 참고 HTML의 인계

사용자 제공 파일은 `BunkerHill_Articulated_Viewer_v5.html`이다.

- 크기: `6,908,481 bytes`.
- SHA-256: `402814f3d59fcec1e656cca7c825f5dd4f16c61db42be9913e8af87dfba996cc`.
- 이전 검토의 구조: 12 assemblies, 138 nodes, 함포 2기, Phalanx 2기, SPG 4기, 추진축 2개, VLS 전후 각 61셀로 총 122셀.
- VLS는 전후 각 8×8 배치 중 3칸이 비사용이다. viewer의 실제 셀 등록을 읽어 연결하며 64셀씩으로 임의 생성하지 않는다.
- viewer Three.js는 r170, AEGIS 현재 네트워크 렌더러는 r160이다. asset/joint를 이식할 때 API·좌표·단위·material 차이를 확인하고, 시뮬레이터 전체 Three 버전을 요청 없이 함께 올리지 않는다.
- 이 파일은 모델·관절·애니메이션 viewer다. 함선 runtime·방호·구획·승조원 구현이 포함됐다고 가정하지 않는다.

이번 조회에서 GitHub WIP16 트리에 이 viewer 파일은 없었다. 이전 세션의 `upload/` 파일이나 ChatGPT Library는 새 코덱스 환경에서 자동으로 접근 가능한 저장소 파일이 아니다. 모델 연결 단계에 필요한 원본이 작업공간에 없으면 사용자가 이 파일을 제공해야 한다. 파일명만 같은 다른 버전을 원본으로 간주하지 말고 hash로 확인한다. 원본을 받기 전에도 기존 DDG-119의 생성·초기화 경계 조사와 계획은 진행할 수 있다.

새 모델을 처음부터 다시 만드는 것은 현재 요청이 아니다. 하푼·토마호크와 기타 대함미사일의 모델도 사용자가 별도로 준비했다고 했지만, 해당 모델의 현 파일·hash·runtime 구현 상태는 이번 마감에서 확인하지 않았다. 벙커힐 기본 연결 이후 별도 범위로 다룬다.

## 9 계속 지킬 작업 규칙

- 큰 단일 HTML은 로컬에서 수정·검증해 다운로드 파일과 크기·SHA-256을 제공하고 사용자가 지정 브랜치에 직접 업로드한다. 커넥터의 base64/blob 분할 업로드를 반복하지 않는다.
- 사용자 업로드 뒤 원격 크기·Git blob 또는 SHA-256을 검증본과 대조한다. 업로드된 frozen HTML을 요청 없이 재작성·재인코딩하지 않는다.
- 작은 문서·체크섬·테스트·워크플로는 에이전트가 같은 작업 브랜치에 반영한다. 기능 범위를 마친 뒤 상태·인계 문서를 갱신한다.
- main 병합은 명시 승인 뒤에만 한다. 버전 승격과 release/tag는 별도 지시다. 열린 PR·미병합 커밋·release 브랜치를 임의 삭제하지 않는다.
- 이전 HTML·상태·체크섬은 원본 바이트로 보존한다. 현재 repo 루트에는 역사 HTML과 frozen 재구성 기준이 여러 개 남아 있다. 단일 최신 파일 원칙을 적용하려고 현재 회귀/빌더가 참조하는 stable v48·WIP16A를 갑자기 삭제하거나 이동하지 않는다. 아카이브 정리 시 모든 경로·CI·체크섬을 함께 이행한다.
- 3D는 표시 전용이다. 물리, 센서, 유도, 충돌·피해 상태를 렌더 프레임에서 적분하지 않는다. fixed-step와 RNG 격리, truth/관측 트랙 경계를 유지한다.
- 검사 FAIL을 없애려고 threshold를 낮추거나 적용 불가를 PASS로 바꾸지 않는다. 제품 문제와 seed/시간 제한/외부 의존성/캡처 환경 문제를 증거로 구분한다.
- 정적 검사 → core self-test → 결정적 runtime → 실제 브라우저/3D → 관련 전체 CI 순서로 확인한다. 동일 검사가 통과한 뒤 변경 없이 불필요하게 반복하지 않는다.
- 작업 종료 보고에는 HTML 크기·SHA-256, 브랜치 HEAD, PR/CI 판정, 변경 범위, 검증 한계와 다음 진입점을 남긴다.

## 10 새 코덱스 대화에 붙일 시작 문장

> GitHub `0-FLANDRE-0/Aegis_Project`의 `WIP16` 브랜치에서 `docs/wip16/B/AEGIS_CODEX_HANDOFF_WIP16B.md`, 최신 B 상태 문서와 `evidence/upload_closeout.json`을 읽고 현재 main/WIP16 HEAD와 PR #41 상태를 다시 확인해줘. WIP16B는 업로드 exact·전용 회귀·전체 CI 32/32까지 통과했고, main 병합·v48.1 승격·release/tag는 아직 승인하지 않았음. 다음 방향은 출항 전 함선 선택·생성·초기화 공통화 → 기존 DDG-119 보존 → 벙커힐 모델/프로필 연결임. 우선 기존 초기화와 profile/runtime 소유 경계를 조사해 최소 변경 계획을 정리하고 내가 지정하는 범위로 이어가자. 새 브랜치 번호를 임의로 정하거나 큰 HTML을 커넥터로 업로드하지 마. 벙커힐 원본 viewer는 레포에 없으니 실제 모델 연결 때 필요하면 내가 제공할게.

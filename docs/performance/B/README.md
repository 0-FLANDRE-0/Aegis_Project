# 최적화 2단계 PERF_B

PERF_A final `4b42aacd4271ce790b47b981b9a58dc960e5d5c5` 위에서 교전 planner와 SPG-62의 반복 계산을 줄인다. 직전 HTML/status/SHA/workflow는 `archive/v48/WIP_PERF_A/`에 동일 bytes/blob으로 보존한다.

`wip118BuildEngagementControl`의 ctx는 호출마다 새 객체다. 같은 ctx 안에서 동일한 관측 threat/delay의 예측을 공유하며 NEZ scan에 쓰지 않는 원래 track의 metadata 복사를 생략한다. 기본 `wip118FutureThreat`와 ctx 없는 `wip118NezPoint`의 기존 반환 계약은 유지한다. 두 canonical planner는 별도 lexical scope에 있고 offset/SHA로 각각 pin한다. `wip118NezPoint`의 산술·스캔 간격·모든 NEZ 끝점은 유지한다.

동일 예측의 SPG 기하/손상/LOS 점수만 같은 판단 호출 안에서 재사용한다. 실제 채널의 현재 예약·provisional 충돌은 계속 호출할 때마다 검사한다. 판단 도중에 센서·물리·피해를 갱신하거나 await/callback을 실행하는 경로는 없다. 다음 판단은 새 ctx에서 현재 관측·owner·자세·손상·사통을 다시 읽는다. 이 자료는 runtime/snapshot에 저장하지 않고 실제 발사 경로에 전달하지 않는다.

owner별 immutable body frame 하나는 현재 heading/heel/trim/draft/origin x/y/z를 `Object.is`로 모두 대조한 경우에만 재사용한다. 매 호출의 survival snapshot/항법 읽기를 유지하고 같은 tick 안에서 변한 자세도 즉시 반영한다. 숫자 반올림·tick 단위의 추정 무효화는 없다. canonical constructor와 입력 오류의 예외를 유지한다. 캐시가 보유하는 frame의 모든 연산은 새 값과 detached snapshot을 반환한다.

실제 발사의 FRIEND/NEUTRAL·HOLD·EMCON·owner/local capability·손상·예비탄·FCS 재검사, sensor/CMS/AI/RNG, native flight/collision/damage, fixed60/120/20Hz, Harpoon INS/ARH/DL0, CG Phalanx-only와 DDG 장비를 유지한다. PERF_A의 도색·EW·손상 색인도 유지한다. 조작 방법은 기존과 같다.

`build.py`와 pinned `patch-index.json`은 exact 원본으로 재빌드한다. `verify_static.py`는 packed records/assets·전체 문법/scope·변경 경계를 검사한다. `verify_semantics.py`는 두 native planner의 96개 독립 제어 사례·ctx 수명·예약 변화·현재 입력 갱신·기본 반환 계약 및 두 실제 함종 core selftest를 확인한다. 기존 함대/방어/무장/피해/UI/clock 회귀와 원본끼리의 exact 상태/RNG 비교는 새 HTML에 직접 실행한다. raw source·script/report/capture SHA와 집계는 `evidence/verification-summary.json`, 직렬 성능 조건은 `PERFORMANCE.md`를 따른다.

GitHub Actions는 수동 workflow만 준비한다. 사용자 계정 제한으로 dispatch하지 않고 로컬 final-original gate로 검증한다. 사용자의 원본 직접 업로드 승인으로 새 branch에 full HTML과 지원 파일을 반영하고 tree/blob/raw bytes를 독립 읽어 확인한다. main/이전 PR 병합·새 PR 생성은 이번 작업에 포함하지 않는다.

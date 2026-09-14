# AEGIS v48 WIP06 R3 — 기능별 내부 배치와 개방형 격납고

## 판정

WIP06 내부구조 작업의 교체본이다. 독립 Node 계약·형상 검사와 GitHub Actions Chromium/WebGL 회귀를 통과했다.

## 변경 내용

- 138개 독립 공간, 160개 연결부, 70개 주요 장비 노드.
- 함교 관련 34공간을 5개 높이층에 배치. CIC, 무장통제실, 레이더 전자실, 냉각실, 해도실, 무선실 등의 길이와 폭을 기능에 따라 다르게 구성.
- 층별 종통로, 최상층 횡통로, 계단 전실과 넓은 전방 통합 조타·견시실 추가.
- 격납고 좌·우 베이는 각각 높이 6.3m의 단일 공간. 내부의 전체 중간 바닥을 제거하고 측면 서비스 통로·캣워크·지원실만 외곽에 배치.
- 외형 추종용 렌더 조각마다 생성되던 가짜 격벽·가짜 중간 바닥·격자선 제거.
- 공간 기능별 색상과 콘솔·전자 랙·기관 장비·작업대 형태 구분. 장비를 벽 쪽으로 배치하고 격납고 베이·복도에는 장비 노드를 배치하지 않음.
- 계단과 사다리를 공간 중심 높이가 아닌 실제 층 바닥 높이에 연결.
- 기존 `AEGIS_SHIP_INTERIOR_TOPOLOGY_V48_WIP06` schema와 진단 API 유지. buildId는 `WIP06_FUNCTIONAL_INTERIOR_CLEAR_HANGARS_R3`.
- 3D readout은 `WIP06 R3 내부 138공간/160연결`로 표시.

실제 조선소 도면을 재현한 배치는 아니며 기존 함정 외형 안에 맞춘 게임용 개연성 배치다. 특정 헬기의 실제 입고·로터 간섭 인증도 아니다.

## 검사 결과

`node tests/interior-wip06-contract.cjs`

- 인라인 JavaScript 전체 문법 파싱 통과.
- 내부 진단 13개 조건 통과.
- 이동 가능 115공간 전부 연결, 고립 공간 0.
- snapshot 20,000회 조회 중 재계산 0, 상태 reset 복구 통과.
- 격납고 clear=true. 시험 장애 바닥을 삽입하면 clear=false가 되는 음성 검사 통과.
- 실제 렌더 빌더가 138/138공간, 160/160연결, 70/70장비를 생성.
- 상부구조 envelope 밖 꼭짓점 0.
- 격납고 수평 삼각형은 베이 바닥에만 존재하며 가짜 중간 바닥 0.
- 렌더 호출 전후 권위 snapshot 동일.
- 내부 표시 데이터는 9개 배치로 구성. 이는 전체 장면 FPS 측정값은 아님.

로컬 환경에는 Chromium 실행 파일이 없어 로컬 WebGL 검사는 실행하지 않았다. 실제 Chromium/WebGL 검증은 아래 GitHub Actions 종결 결과를 기준으로 한다.

## GitHub 반영 위치

- 현재 WIP06 브랜치의 저장소 루트 `Aegis_SIM_v48_WIP06.html`을 이 파일로 교체.
- 저장소 루트 `AEGIS_PLAN_STATUS_v48_WIP06.md`를 이 문서로 교체.
- `tests/interior-wip06-contract.cjs`로 검사 파일 추가 가능.
- ZIP은 저장소에 올리지 않는다.
- WIP06이 아직 main에 병합되지 않았으므로 현재 WIP06 브랜치에서 교체한다.

파일 해시는 동봉한 `WIP06_R3_SHA256SUMS.txt`를 기준으로 한다.


## 원격 종결 결과

- PR #17 code head `3ab29c3418fc7a745effbc21f301e19e5d1356f7`의 Actions run `34835163250` (#60)에서 `static-smoke`, `webgl-render-probe`, `aegis-3d-render`, `ciws-b1-closure`, `ciws-b2-maneuver`, `ciws-b3-damage`, `ship-mass-ledger`, `ship-impact-penetration`, `ship-structural-fatigue`, `ship-stability-maneuver`, `ship-wave-flooding`, `ship-interior-topology` 12개 job이 모두 통과했다.
- 원격 WIP06 HTML SHA-256은 `6ee5d53c95001b0bee2e10eec4b4554bfe15599b8f214442974b8fdb1e70440b`, Git blob SHA는 `4affe9f6f80f6585037de5b7c8e79a8d03074c2d`로 전달본과 일치한다.
- Chromium 내부 topology artifact는 page/core selftest, R3 공간 계약, 격납고 무간섭, 연결망, 부모 침수 셀, 자동 격리, 결정성, cached read, render read-only와 UI 버튼을 모두 통과했다. 20,000회 조회는 약 0.4 ms이며 topology 재계산은 0회였다.
- 실제 3D audit은 renderer ready/WebGL2, 공간 138/138, 연결 160/160, 장비 70/70, 함교 5개 높이층, 격납고 2베이, 배기 트렁크 12개, 마스트 트렁크 3개, 상부구조 밖 꼭짓점 0, 외부 투명 재질 135개를 확인했다. 744개 외형 추종 fragment와 406개 portal primitive는 총 9개 drawable로 batch 처리되며 presentation-only/read-only 계약을 유지한다.
- 실제 3D 화면 readout은 `WIP06 R3 내부 138공간/160연결`이었다. 기존 ENTRY/EXIT 양현 파괴구도 meshMatched/actualHole/attached, 반대 현측, 면적 보존, pending 0과 render read-only를 모두 통과했다.
- 내부 topology artifact: `10343833076` / `sha256:76747d9472b957c6d4a5f741ef7336c750a164e9712651dd9e4419cd945e2135`.
- 실제 3D artifact: `10343872658` / `sha256:e43a93d2ffde32c2aae356110c9dd01917741c25b418e6a1db864a2162007e3a`. WebGL artifact: `10343813234` / `sha256:33183d4549368538e73738c144d3e589e0a02bd2e756b70dc5fc2b930bbb730b`.
- 기존 회귀 artifact: B1 `10342794716` / `sha256:d82c150a15882e7d745c1216bd0bc7cfb1b98917dcb322ca8a2e1315af57995a`; B2 `10343965206` / `sha256:28d9d05a5272d7a338102cb15164884fc9c9e93cf7a614ee1a4d7524382bc1b3`; B3 `10343409655` / `sha256:e4422548eeeb193c9cbfc2627e561d501c3bb0afe62262c877542843919c51a0`; 질량 `10343474736` / `sha256:3e532301fcebeeb5d85cbc013834050b7d8c7c9e6f306482fada51a0364ac972`; 관통 `10343872595` / `sha256:915c0d75110759b810fcebbd4993f21b9d3d269e0cdcb36de255f891d2badc47`; 구조 피로 `10343624109` / `sha256:66743053079cae50f20838e77afac34c5a9815c6f8eee46c84cccfc16f2102d3`; 안정성 `10342864570` / `sha256:ad17264297d03aba58e0e9d299e0c4588241993aa74dc86626bbd53996588b84`; 파도 침수 `10343758794` / `sha256:96e2b847a6a2df9b8dc29acedaeb42649a2a1f7223b7f3edef3d26708f96560f`.

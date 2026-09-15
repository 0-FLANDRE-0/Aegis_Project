# AEGIS v48 WIP07 — 공간 기반 승조원·폭압·인명피해 통합

## 판정

WIP06 R3의 실제 내부 공간·통로 그래프 위에 승조원 배치, 이동, 보수반 출동, 폭압·파편·관통체 인명피해, 의무후송과 3D 표시를 통합했다.

현재 판정은 **구현 완료 / 독립 결정적 런타임 계약 통과 / 실제 브라우저·WebGL·GitHub Actions 13개 job 통과**다. WIP 단계이므로 릴리스·태그는 만들지 않으며 PR 병합 전 상태다.

## 구현 내용

- `AEGIS_CREW_ROUTING_DAMAGE_V48_WIP07` 권위 상태 추가.
- 정원 310명을 하나의 추상 수치가 아니라 개인별 `spaceId`, `parentFloodCellId`, 함내 좌표, 부서, 당직 위치, 보수반, 건강·후송 상태로 보존.
- 기관부 100, 전투체계부 85, 작전부 60, 항공부 25, 보급·행정·의무 35, 지휘부 5명을 WIP06 R3의 기능별 방에 배치.
- WIP06의 138공간·160연결부를 그대로 읽는 경로 탐색 추가. 문 개폐·자동 격리, 계단·사다리·해치, 화재·연기·침수·온도를 경로 비용과 접근 차단에 반영.
- 일반 당직, 보수반, 자력후송, 들것후송, 퇴함에 서로 다른 이동속도와 통과 조건 적용.
- 보수반 20명 × 3개 반은 순간이동하지 않고 실제 경로로 이동하며 현장 도착 인원이 8명 미만이면 작업 효율 0.
- 보수반 손실 시 부서별 최소 당직 인원을 보존하는 범위에서 자동 충원. 플레이어는 구역·작업 우선순위를 지정하고 개인·문 단위 미세 조작은 요구하지 않음.
- 승인된 미사일 피해 이벤트를 승조원 모델에 한 번만 전달. 동일 impact ID 중복 평가는 차단.
- 폭발물 TNT 환산량과 케이스 질량으로 방 평균 반사압·파편 기대량을 계산하고, 문·계단 그래프를 따라 감쇠 전파.
- 개인별 폭심 거리 압력을 별도로 계산해 큰 방 전체가 근접 폭압을 동일하게 받는 현상을 방지.
- 2D 피해 계산이 정한 관통선을 공간 AABB 및 개인 위치와 교차시켜 관통체 직접 사상과 근접 부상을 계산.
- 별도 결정적 해시 스트림으로 사망/부상 판정. 전투 RNG 순서를 소비하지 않음.
- MINOR/SERIOUS/CRITICAL 분류, 이동 가능성, 미치료 중상 악화, 의무실 8명, 동시 들것조 4개, 자동 후송과 치료 복귀 구현.
- 기존 기관부 인원 가용률의 추진 성능 연동과 보수반 실제 도착 인원 기반 작업 효율을 유지.
- `PRESENTATION_ONLY_CREW_SNAPSHOT`을 3D가 읽어 승조원 310명을 단일 `InstancedMesh`로 표시. 이동 경로는 단일 동적 선 배치로 표시하며 렌더러는 권위 상태를 수정하지 않음.
- 3D 색상: 정상, 보수반, 이동 중, 부상, 사망을 구분. 내부 구조 보기 버튼과 함께 표시/숨김.

## 성능 설계

- 개인 위치 적분: 고정 5 Hz.
- 생리·의무·임무상태 평가: 고정 1 Hz.
- 문·위험 상태에 따른 경로 캐시 무효화: 내부 토폴로지 revision 변경 시, 최대 1 Hz.
- 폭압·파편 그래프 순회와 관통체 교차 검사는 승인된 피해 이벤트에서만 실행.
- 3D 프레임은 캐시된 snapshot revision만 확인. 경로 탐색·폭압·생리 계산을 수행하지 않음.
- 경로 캐시는 512개로 제한하고 피해 기록도 유한 길이로 제한.
- 승조원 310명은 3D draw call 1개, 경로는 draw call 1개로 배치.

## 결정적 fixture 결과

`node tests/crew-wip07-contract.cjs Aegis_SIM_v48_WIP07.html`

- 인라인 JavaScript 문법 파싱 통과.
- 승조원 계약 15개 조건 전부 통과.
- 초기 정원 310명, 실제 배치 공간 115개.
- 후방 기관실 → 함교 보수반 경로: 12공간, 132.870 m, ETA 174.318 s.
- 함교 → 의무실 들것 경로: 11공간, 87.372 m, ETA 184.023 s.
- `upper.cic.lower` 90 kg TNT / 45 kg 케이스 내부폭발 및 관통선 fixture:
  - 방 평균 최고압 약 327.402 kPa.
  - 압력·파편 영향 공간 6개.
  - 관통 공간 2개.
  - 노출 17명, 사망 14명, 부상 3명.
  - 부상자 3명 모두 실제 들것 경로로 `main.infirmary` 후송 시작.
- 동일 피해 event ID 두 번째 입력 무시, damage evaluation 1회.
- 20,000회 snapshot 조회 약 0.44 ms(현재 Node 환경), 조회 중 snapshot rebuild·route evaluation·damage evaluation 각 0회.
- 3D 데이터 싱크 검사: 1 instance batch, 310/310명, 시험 이동경로 17개 선분, 권위 snapshot 변경 0.

`node tests/interior-wip06-contract.cjs Aegis_SIM_v48_WIP07.html`

- WIP06 R3 토폴로지 회귀 통과.
- 138공간 / 160연결 / 70장비 유지.
- 이동 가능 115공간 전부 연결, 고립 0.
- 격납고 clear=true, 상부구조 외부 꼭짓점 0.
- 내부구조 렌더 데이터 9개 배치 유지.

## 브라우저와 Actions

- Playwright 10개 파일의 11개 테스트가 정상 수집됨.
- workflow YAML 파싱 통과.
- 기존 12개 job에 `ship-crew-damage`를 추가해 총 13개 job으로 구성.
- `aegis-3d-render`는 내부 구조 표시 상태에서 승조원 310명, instance batch 1개, presentation-only 계약, WIP07 결정적 프로브와 권위 상태 불변을 검사하도록 확장.
- 최종 검증: GitHub Actions `AEGIS smoke check` run #64, run ID `34841619976`, branch head `bf68e948bea69ef27c13f34c94ae3bce2aa8f570`.
- 13개 job 전부 success: `static-smoke`, `webgl-render-probe`, `aegis-3d-render`, `ciws-b1-closure`, `ciws-b2-maneuver`, `ciws-b3-damage`, `ship-impact-penetration`, `ship-mass-ledger`, `ship-structural-fatigue`, `ship-stability-maneuver`, `ship-wave-flooding`, `ship-interior-topology`, `ship-crew-damage`.
- 신규 브라우저 검사는 페이지 로드, 출항 오버레이 해제 후 보수반 UI 생성, 310명 정확 배치, 그래프 이동, 들것 후송, 폭압·파편·관통체 혼합 사상, 캐시 조회, presentation-only 상태를 모두 통과.
- 실제 3D Chromium/WebGL audit: renderer ready, 내부 구조 버튼 표시·눌림, 승조원 레이어 visible, `InstancedMesh` 1 batch, 310/310명 표시, `allPersonnelRepresented=true`, `physicsFeedback=false`, `PRESENTATION_ONLY_CREW_SNAPSHOT` 통과.
- 같은 3D capture에서 WIP06 내부 구조 138공간/160연결/70장비가 모두 실제 mesh에 표현되고, WIP03 ENTRY/EXIT 양현 파괴구가 `meshMatched=true`, `actualHole=true`, `attached=true`로 유지됨.
- 3D 증거 artifact: ID `10346890422`, digest `sha256:01dc1a60269dd729e0b48b78a5d44c0d2ee4666422f7ee75569da3ffef45879e`.
- 승조원 피해 증거 artifact: ID `10346561330`, digest `sha256:d2a22f96adb1d3437f4b83649580b5c31e7cd258f1566f5563141b1ce4af8d7a`.

### 최종 Actions artifact

| 검사 | Artifact ID | SHA-256 digest |
|---|---:|---|
| aegis-3d-render | 10346890422 | `01dc1a60269dd729e0b48b78a5d44c0d2ee4666422f7ee75569da3ffef45879e` |
| ship-stability-maneuver | 10346850630 | `71ed9b59a868efdc64f09f4de3bb14f6e0eec4d2cafb75ea3357354dcdeb7f12` |
| ship-interior-topology | 10346656039 | `e06e5981daa04451395470ce3a08378f90aa2059fbe94ccf0fa6fa907816df84` |
| ship-crew-damage | 10346561330 | `d2a22f96adb1d3437f4b83649580b5c31e7cd258f1566f5563141b1ce4af8d7a` |
| ciws-b2-maneuver | 10346341426 | `a57f3a1bbb7739ba0ca3b5e0145c353f26be37a335c404521499f5c25364436f` |
| webgl-render-probe | 10346312394 | `176774bd6ff874a60cea30fd33e78898c5aadf4f2241ced1df29732b58707cf0` |
| ship-mass-ledger | 10346212108 | `fc7461d853ae8df7b58c1d61b13fc2b506fbccdf6294879d4a795b37d243f77d` |
| ship-wave-flooding | 10346147222 | `4223f328443b75a18afdd634e7364907fa7e4ad38d3fd74d17b1b1a466cda356` |
| ship-impact-penetration | 10346112335 | `09e56b7b1632fe40d8ad1ab2aad3507a53e7e85051b1d911b4d9d12899663609` |
| ciws-b3-damage | 10346087298 | `8d22dbe552e6b2c171831f759403fb000d066c5fb8f92c5373886207aae4d4f6` |
| ship-structural-fatigue | 10346022605 | `853da399cc275004b2ab413f3f1fd45337c9c92bd2a3c74e82f58c1668bf7707` |
| ciws-b1-closure | 10345324476 | `ef5067e237a3096e1ef2626cd8b079c406c97d6eac5fc9c7b244c8aa752bfc77` |

`static-smoke`는 별도 artifact 없이 success로 종료됐다.

## 변경하지 않은 범위

- WIP01 질량 장부, WIP02 관통, WIP03 종강도·균열, WIP04 복원성, WIP05 파도 침수, WIP06 R3 내부 형상 계산은 수정하지 않았다.
- 실제 함정 승조원 편제도나 조선소 도면을 재현한 것이 아니며 의료·상해 인증 모델이 아니다. 기존 외형과 게임 시스템에 맞춘 결정적 개연성 모델이다.
- 센서 truth/track 경계, 유도, 교전권한, 무기 성능은 변경하지 않았다.

## GitHub 반영

1. `main`에서 `v48-wip07-crew-damage` 브랜치 생성.
2. 루트에 `Aegis_SIM_v48_WIP07.html`, `AEGIS_PLAN_STATUS_v48_WIP07.md` 추가.
3. WIP06 HTML과 상태 문서를 `archive/v48/WIP06/`에 원본 그대로 보존.
4. 루트의 WIP06 HTML과 상태 문서 삭제.
5. `.github/workflows/aegis-smoke.yml`, `package.json`, `tests/`의 동봉 파일을 같은 경로에 반영.
6. PR을 생성하고 13개 Actions job을 확인. 릴리스·태그는 만들지 않음.
7. 전부 통과하면 Actions 증거를 상태 문서에 추가 커밋한 뒤 `main` 병합.

HTML과 상태 문서의 SHA-256은 동봉한 `WIP07_SHA256SUMS.txt`에 기록한다.

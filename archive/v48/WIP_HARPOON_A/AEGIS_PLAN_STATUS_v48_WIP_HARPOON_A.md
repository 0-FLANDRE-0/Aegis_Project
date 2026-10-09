# v48 WIP HARPOON A — 로컬 검증 완료

- HTML: `Aegis_SIM_v48_WIP_HARPOON_A.html`
- 크기: **14,962,500 bytes**
- HTML SHA-256: `ffd976a211c530bc4d193597751e49febbd755646b865e6ad2685cd9e06aab77`
- main SHA-256: `73891bfbf0030d92323a640eee39a236610ed8d7d7f2f1586463dc3cf1a29bac`
- 기준: PR #43 병합 `main@f51247496725aa8aadad69d5c8d3449c5bbc3a81`, 벙커힐 K SHA `efe1a0994f172da878733023826e9383ed0aed3c8c9601d10177a5d9faf287df`.
- 준비 branch: [`harpoon-block1c-a`](https://github.com/0-FLANDRE-0/Aegis_Project/tree/harpoon-block1c-a). 기준 main에서 생성했으며 현재 원격에는 새 HTML·지원 자료를 아직 올리지 않았다.
- 정식 안정판 v48과 기존 DDG-119 프로필·Kh-35U/Kh-32 비행·피해 프로필을 보존한다. 이 작업은 첫 하푼 운용 단계의 WIP이며 적 함대·헬리콥터·정식 승격 완료를 뜻하지 않는다.

## 완료한 운용 경로

CG-52의 원래 Mk 141 모델에서 관 8개의 입구·후방·축·덮개를 등록하고 A1–A4/B1–B4를 고정 설치 ID로 사용한다. ARM → VLS에 전용 관 선택·발사·상태를 추가한다. DDG-119에는 하푼을 추가하지 않는다. SAM 선택, Mk 41 122개 셀, 양현 Phalanx, SPG-62, SPY·보조 레이더·EW, 구조·승조원·퇴함 계약은 기존 경로를 유지한다.

수동 적성·훈련 수상 트랙만 발사할 수 있다. UNKNOWN·FRIEND·NEUTRAL, 오래된 트랙, 불충분한 예측 basket, 빈 관, 냉각/대기 중, 손상 발사대와 위험한 자세는 차단한다. 덮개가 열린 뒤 실제 발사 순간에도 같은 조건을 다시 확인한다. 발사한 관은 그 자리에서 비며 선택 번호·다른 관의 잔탄을 이동시키지 않는다. 자함 질량에서 발사 질량 690kg을 한 번 제거한다.

INS는 발사 시점 트랙의 위치·속도·공분산을 동결해 예측한다. 이후 함정 트랙 삭제와 선택 lock 변경에 의존하지 않는다. 종말 ARH는 공통 물리 RF 반사·해면·지형·LOS·날씨에서 합성한 익명 관측을 추적하며 truth ID로 표적을 고르지 않는다. 별도의 데이터 링크나 SPG 조명은 없다.

부스터 추력·연소·분리, 관 출구 구속과 자함 속도 상속, 날개/꼬리 전개, 제트 순항·연료 감소, 해면 고도 추종, 법선력 공유 한계와 유도 전이를 60 Hz에서 처리한다. 위치·속도는 실제 추력/항력/중력/양력 적분 결과다. 분리 부스터는 독립 탄도 world 엔티티로 떨어진다. 3D는 이를 읽어 공유 모델·덮개·화염·연기를 표시한다.

실제 이동 표적함과 swept hull 접촉하면 기존 관통·지연신관·WIP12F packet·내부구획·외피·침수 경로를 사용한다. 221kg 탄두 전체와 약 97.5kg 폭약을 구분한다. 새 피격 packet을 중복 적용하지 않는다.

작전 저장은 관별 재고와 선택 관만 복원한다. 현재 CG revision은 `BUNKERHILL_HARPOON_A_1`, inventory schema는 `MK141_INVENTORY_A1`이다. 옛 명시 호환 CG 저장은 detached migration으로 초기 8발을 제공하고, 새 revision에서 inventory 누락이나 설치 ID 오류는 전체 import를 mutation 없이 거부한다. 비행 중 탄체·예약은 복원하지 않는다.

## 직접 검증

모든 검사는 같은 SHA의 최종 bytes에서 실행했다. 원자료의 입력명 `experimental.html`과 최종 배포명은 byte identical이다. seed는 `0x6d2b79f5`이며 과거 K 284건을 이 파일에서 재실행한 것으로 합산하지 않는다.

| Suite | 통과 | 범위 |
|---|---:|---|
| 정적 | 58/58 | 모든 JS 문법·압축 record 무결성·정확 재빌드·DDG 프로필·CG 원본 asset·Kh-35U/Kh-32 프로필/핵심 함수 동일·truth 경계·모델/관/credit |
| 하푼 runtime | 29/29 | 실제 익명 관측·수동 권한·발사 시 재검사·손상 차단·고정 관·질량·INS 독립·ARH·이동 표적 접촉·단일 피해·잘못된 저장 mutation 0·옛 저장 migration·DDG 미설치 |
| native WebGL | 15/15 | 실제 RAF의 모바일 ARM/VLS 버튼·선택 덮개만 열림·날개 전개·부스터 분리·피격 후 camera/draw·RESET/공유 cache·native tick·오류 0 |
| 64× 8발 workload | 9/9 | 8관 실제 수동 발사·8탄체 동시 존재·8×690kg 제거·관 번호 고정·익명 관측 저장 상한·좌표/속도/질량 finite·공통 접촉·profiler |
| CG 기존 runtime | 30/30 | 센서 역할·pointed dwell·표면/침수·함포 배속·양현 Phalanx 손상·독립 EW pod |
| DDG 기존 runtime | 14/14 | 실제 Phalanx 6조건 반복·spotting·공력/분산·장비 손상·표면/침수·배속 |
| 합계 | **155/155** | page error 0, native console error 0, core failure 0 |

새 core audit 14조건을 시작 시 기존 core self-test에 연결했다. 1×·8×·16×·64×의 실제 전체 fixed-tick accumulator에서 발사·미사일·피해·world RNG·재고 결과가 exact 일치했다. focused flight fixture와 배속 전체 실행은 구분해 기록한다.

8km/8kt 이동 표적을 A4에서 발사한 대표 접촉은 32.55초, 상대 속도 286.856m/s, 폭약 97.5kg, 실제 perforation과 지연신관 packet을 기록했다. 함정의 combat track을 발사 후 삭제해도 결과를 이어갔다. 반대 B4에서도 반대 방위의 실제 표적 접촉을 확인했다. 표적을 옮긴 70초 fixture는 강제 명중을 만들지 않았으며 이후 모든 반사체·조건에서 미스가 보장된다는 주장이 아니다.

64×에서는 최대 실장 수량 8발을 함께 운용했다. 마지막 512개 profiler sample의 하푼 phase 평균 약 0.115ms/p95 0.30ms/max 0.70ms, 전체 tick 평균 약 4.13ms/p95 5.90ms/max 7.70ms였다. 환경별 CPU 측정이며 사용자 장치 FPS 또는 모든 시나리오의 성능 보증값이 아니다. 잘못된 방향으로 쏜 탄도 강제로 표적에 적중시키지 않는다.

브라우저는 Chromium 151.0.7922.173/SwiftShader이며 geometry queue를 수동 진행하지 않았다. 핵심 관·모델·피격 UI의 실제 캡처를 보존했다. 하드웨어 GPU·사용자 모바일 장치별 시험은 미실행이다.

## 공개 근거와 남은 범위

[SOURCES.md](docs/harpoon/A/SOURCES.md)에 variant별 공개 치수·중량·추력·사거리 근거와 SIM-TUNE을 구분했다. 124km/140km 문헌 차이를 기록하고 AGM-84D의 사거리를 RGM에 혼용하지 않는다. CG-52 퇴역 직전 실제 적재 block은 미확정이며 사용자가 요청한 RGM-84D를 적용했다.

날개폭·부스터 포함 길이를 보정하고 원래 24,133 triangles를 유지했다. 4개의 날개·4개의 꼬리를 독립 조립해 62개 공유 geometry를 사용하고 균일색 텍스처 11개를 재질색으로 변환했다. 원저작자 Civorsky/CC BY 4.0와 변경 내역을 HTML·메타·문서에 보존했다. 전개 관절·덮개 힌지·회전 연출은 SIM-TUNE이다.

현재 피해 대상은 기존 WIP13A의 물리 표적함 경로다. 적 수상함 AI·다함 전투·경유점/팝업 선택·외부 표적 정보 링크·헬리콥터는 후속 범위다. 최대 사거리와 전 해상상태/재밍 행렬을 실비행 인증하지 않았다. 시커 거리·오차·SNR·공력·연료·고도·신관 시간은 공개 확정값이 아닌 게임 보정이며 일괄 명중률을 제공하지 않는다.

다음 정확한 작업은 사용자 HTML 업로드 확인 → 원격 SHA·parent 대조 → 작은 support/문서/체크섬·K 동일 blob archive 이동 반영 → 새 PR·동일 HTML CI다. 그 뒤 수상 표적함의 정식 시나리오/UI 확대와 방어 가능한 적 수상함 runtime를 하푼 운용 경로에 연결하는 단계가 적합하다. 이후 헬리콥터의 표적 정보 공급과 경유점/동시 공격을 검토한다.

## 보존·업로드 상태

K HTML/상태/SHA는 `archive/v48/WIP_BUNKERHILL_K/`로 bytes 변경 없이 이동했다. 그 SHA 파일의 당시 경로는 역사 근거로 그대로 두며 현재 검사는 새 root SHA와 support manifest를 사용한다. K workflow는 root K가 있는 경우에만 실행하고 archive를 자동 후보로 고르지 않는다. 기타 기존 root 역사 fixture는 선행 지침의 호환 예외를 유지한다.

원격 main은 그대로이며 branch만 준비했다. 프로젝트 지침 7.1에 따라 큰 HTML은 사용자가 branch에 직접 업로드한다. 로컬 완성 HTML·검사·문서가 준비되어 있지만 원격 HTML/SUPPORT 업로드·PR·새 CI·병합은 아직 완료하지 않았다. [검사 집계](docs/harpoon/A/evidence/verification-summary.json), [업로드 인계](docs/harpoon/A/GITHUB_HANDOFF.md), [체크섬](SHA256SUMS_v48_WIP_HARPOON_A.txt)을 따른다.

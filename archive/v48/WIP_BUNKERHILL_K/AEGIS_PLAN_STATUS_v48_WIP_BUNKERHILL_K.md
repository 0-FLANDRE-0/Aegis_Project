# AEGIS v48 WIP BUNKERHILL K — 함선별 SPY CIC·퇴함 구명뗏목

로컬 구현·런타임·브라우저 검사 완료 WIP. HTML `Aegis_SIM_v48_WIP_BUNKERHILL_K.html`, **14,458,866 bytes**, SHA-256 `efe1a0994f172da878733023826e9383ed0aed3c8c9601d10177a5d9faf287df`. decoded main SHA-256 `dbf339daa731b3b86408a1c5bb3c52e718975f5ad82b78d0ae76484b6db69897`. 정식 v48과 직전 J를 보존했다.

## 완료한 변경

- 기존 CIC의 DDG 고정 대각선 배열을 선택 함선의 등록 방향으로 연결했다. 벙커힐은 전·후·양현 방향의 SPY 중심각을 사용하며 source mesh의 작은 각도 오차까지 반영한다. 경계선·부하 호·F1–F4 표기를 같은 중심각으로 그린다. DDG의 기존 45°/135° 도식은 유지했다.
- SPY 작동 상태 검사에 고정된 DDG 장비명을 사용하던 경로를 선택 함선의 F1–F4 장비 ID로 바꿨다. 벙커힐 배열 손상이 CIC의 OFF 표시와 실제 센서 작동에 반영된다. 기존 손상 임계값·SPY 장비 성능·물리 배열은 보존했다.
- USN Mark 7의 공개 정원 **25명**을 공유하는 immutable 구명뗏목 모듈을 추가했다. 시뮬레이션 provision은 `ceil(profile crew / 25)`이다. 벙커힐 330명은 최대 14척, DDG-119 310명은 최대 13척이다. 실함의 비치 수량으로 주장하지 않는다.
- 기존 승조원의 실제 퇴함 경로와 탑승을 연결했다. 집결점에 도착한 생존자부터 개별 ID로 기록하며 중복·사망자·경로 차단 인원의 자동 탑승을 막는다. 퇴함 후에도 보수반 배정이 탈출 경로를 덮어쓰던 상태를 방지했다. 부상자는 이동 조건을 만족하면 퇴함한다.
- 첫 탑승자가 도착하면 뗏목을 순차 진수하고 양현을 번갈아 사용한다. 최소 진수 간격은 SIM-TUNE 4초다. 25명 충원 시 떠나며 마지막 미충원 뗏목은 퇴함 완료 또는 LOST 시 떠난다. 자유 뗏목은 함선 밖의 월드 엔티티로 유지되고 기존 고정 tick에서 표류·해면 자세·선체 이격·뗏목 간 간격을 계산한다.
- CIC에 알려진 아군 뗏목 위치·인원을 표시하고 실제 3D 해면에 간략화한 뗏목과 실제 탑승자 수를 그린다. renderer는 기존 Gerstner 해면으로 표시를 투영하며 canonical raft/ship 상태에 쓰지 않는다. 제거한 인원 instance buffer는 한 번만 해제하고 공유 geometry/material은 renderer 한 벌을 재사용한다.
- crew 패널에서 척수·탑승 인원·25명 정원을 표시한다. 작전 저장에 시간·탑승 명단·월드 위치·속도를 추가하고 전체 codec preflight 뒤에만 복원한다. 퇴함 중 저장을 읽으면 살아 있는 승조원이 다시 탈출 경로로 이동한다. 초기화는 해당 함선 소유 뗏목을 제거한다.

사용 경로는 **SHIP → 보수반 → 승조원·함 포기**다. 취소는 상태를 바꾸지 않는다. 이미 퇴함한 함선의 반복 명령은 새 뗏목이나 사람을 생성하지 않는다.

## K 직접 검사

| 검사 | 통과 | Evidence |
|---|---:|---|
| 패킹/전체 script 문법/asset/hash/소형 소스 exact 재빌드 | 45/45 | `K-package.json` |
| J→K 선언된 변경/원본 13 records/6 CG assets/두 프로필/SPY 물리 배치 | 7/7 | `K-source-audit.json` |
| 실제 CIC 배열 글자·호/4개 침로/손상 OFF/DDG 기존 pixels | 22/22 | `K-spy-cic/result.json` |
| 실제 퇴함 UI/330명/인원 보존/부상·사망/저장·상실·초기화/legacy migration | 28/28 | `K-rescue/result.json` |
| 1/8/16/64× 고정 tick의 인원·뗏목 상태 exact 일치 | 6/6 | `K-rescue-time/result.json` |
| native WebGL 14척·330명/읽기 전용/3회 제거·재생성 GPU 자원 | 12/12 | `K-rescue-3d/result.json` |
| 함선 선택·출항·DDG 기존 저장 | 17/17 | `K-startup/startup.json` |
| 고정 VLS 셀/프리셋/상부 구획/330명 배치/F 저장 migration | 21/21 | `K-controls/result.json` |
| CG 실제 회전 부품·사각·독립 손상·탄약/renderer | 26/26 | `K-integration/cg52-integration.json` |
| CG 센서 plot/익명 track/공통 융합/함포/전자전·저장 | 30/30 | `K-runtime/cg52-runtime.json` |
| 실제 Kh-32 6발 AUTO native 3D·피격 후 프레임/틱 지속 | 11/11 | `K-native-raid/result.json` |
| 0/6/7/8 m 해면·실제 수상 접촉·선택 함선 피격도/선수 좌측 | 45/45 | `K-clutter-indicator/result.json` |
| DDG 결정적 탄도·Phalanx·피해·배속 회귀 | 14/14 | `K-ddg-runtime.json.gz` |

위 **284/284**는 K와 같은 SHA-256의 HTML을 직접 검사한 결과다. 브라우저 입력 이름 `preview-05.html`은 최종 K HTML과 byte-identical이다. 원본 evidence의 입력 이름을 바꾸지 않았다. 기준 경로는 `docs/bunkerhill/K/evidence/`이며 조건과 suite 구분은 `verification-summary.json`을 따른다.

건전한 벙커힐 퇴함에서는 330명 전원이 14척에 탑승하고 마지막 뗏목에 5명이 남았다. 사망 25명·경상 20명 fixture에서는 사망자를 제외한 305명이 13척에 탑승했다. DDG에서는 310명이 13척에 탑승하고 마지막 10명을 보존했다. 10개 잘못된 신규 저장은 mutation 0으로 거부했다. 기존 J의 퇴함 0명과 퇴함 31명 저장을 각각 0척·2척으로 명시 migration했다.

DDG WIP16B 집계 및 같은 seed 반복은 exact 일치했다. 6개 case에서 총 1,132발·명중 16회이며 상세 float 최대 차이 `3.87e-13`, abs `1e-9`/rel `1e-12` 한도 안이다. 비교는 `K-ddg-baseline-comparison.json`이다. DDG CIC canvas도 J와 pixel exact로 일치했다.

native raid seed 174321, sim 71.4667→100.2667초, step 4288→6016, draw 36회, 종료 적 alive 0, scar 40개. RAM/physics fault/presentation fault/context loss/page error/crash 0. geometry generator 수동 진행 0회이며 작업 pending 중에도 화면과 tick이 계속됐다. 모든 위협의 요격이나 관통구 완료를 주장하는 검사가 아니다. native 뗏목 fixture는 임무 모드에서 우발적인 자동 raid를 끄고 정상 함선 퇴함을 검사했다. 로컬 headless Chromium/SwiftShader 검사이며 사용자 장치 FPS 측정이 아니다.

## 공개 근거·범위·보존

정원 25명은 USN DVIDS 사진 설명과 NAVY MIL-DTL-32532A 공개 scope에서 확인했다. `docs/bunkerhill/K/RESCUE_SOURCES.md`와 `rescue-public-evidence.json`에 URL·인용·날짜·SIM-TUNE 범위를 남겼다. CG-52의 정확한 비치 수량·Mod 번호·진수 위치는 미확정이다. provision·진수점·뗏목 형상·바람 표류·접촉은 SIM-TUNE이다. 뗏목의 수거·귀환·전투 피해·개별 구조 행동은 미구현이다.

이전 작전 저장에는 뗏목의 해상 위치가 없다. 전체 preflight가 통과한 detached clone에서 기록된 퇴함 인원만 새 명단으로 옮기고 함선 바깥에 근사 배치한다. 신규 저장의 위치·속도·명단은 그대로 복원한다. operational envelope v2와 CG revision `BUNKERHILL_LATE_G_1`을 유지하며 신규 rescue codec/capability를 추가했다. 잘못된 payload는 권위 상태를 바꾸지 않는다.

J의 VLS 발사 원점·미장착 크레인 칸 배기 처리, 원본 전체 SPG-62 회전, 양현 20mm/RAM 구분, SPQ-9 두 면과 SIM-TUNE 출처, 퇴장 탄체 GPU 해제, 피격 3D 복구를 보존한다. 277구획/12갑판/392연결/179장비/330명과 고정 61+61 VLS, 60 Hz 물리·120 Hz 침수/힘·20 Hz hydro를 유지한다. 원본 DDG·CG 프로필, 물리 SPY 배열, records 0–12와 여섯 CG asset이 동일하다.

J의 SPG 48자세·122 VLS/488 ESSM/12 실제 발사·양현 close-in·DDG RAM·탄체 GPU 자원·표시 오류 주입 전용 검사, H/I의 일부 추가 내부·geometry/배속 근거는 선행 evidence로 보존했다. K가 이 전용 suite를 전부 다시 실행했다고 표시하지 않는다. K에서 고정 셀/회전 부품/교전·피격 지속/센서·클러터를 직접 회귀하고 source 감사로 보존 범위를 확인했다.

## 인계

루트 실행 HTML은 최신 K 하나다. 직전 J의 HTML·상태·SHA는 `archive/v48/WIP_BUNKERHILL_J/`에서 byte 그대로 보존한다. 이전 D/E/F/G/H/I archive와 support도 유지한다. 소형 지원 파일은 `docs/bunkerhill/K/`, 최신 체크섬은 `SHA256SUMS_v48_WIP_BUNKERHILL_K.txt`, 전체 파일은 `MANIFEST.sha256`을 따른다.

모델 복사본 없이 최신 HTML에서 asset을 추출하고 STARTUP_A와 작은 모듈만으로 K를 exact 재빌드했다. D/F/H/I/J 비교본도 고정 SHA에 일치하도록 재현했다. `repro-K.json`은 별도 배포 재현 근거다. README와 준비된 workflow가 재현 절차다.

기존 branch `bunkerhill-late-profile`와 지침 7.1 사용자 대형 HTML 업로드 분담을 유지한다. 이번 작업에서 원격 업로드·CI·PR은 실행하지 않았다. 다음 단계는 K의 실제 사용자 장치·손상 후 퇴함 플레이 확인과, 공개 근거가 확보되면 CG-52 구명뗏목 비치 수량·진수 위치를 source registration으로 구체화하는 것이다.

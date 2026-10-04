# 벙커힐 J 수정 근거와 검증 범위

2026-10-03. 최신 HTML은 `Aegis_SIM_v48_WIP_BUNKERHILL_J.html`이다. 14,446,182 bytes, SHA-256 `05306084448d4b68e25f696276346d3b9b2d4899d01a6b6d5b7ae2be9e2323b6`. main SHA-256 `8c11939b004f7bb3d66f61a70e0630b1d8df2853ee024e9a81c8b29abf817f21`.

## Kh-32 AUTO 교전 중 정지

실제 Kh-32 6발을 정상 비행 모델로 발사하고 익명 센서 관측으로 AUTO 교전했다. seed 174321, 최초 거리 95 km, 물리 60 Hz. 실제 고정 틱으로 접근시킨 뒤 경사거리 약 20 km부터 일반 RAF와 3D를 켜고 16배속으로 진행했다. 이 시험은 합성 트랙을 주입하거나 geometry queue를 수동으로 진행하지 않는다.

중간 I에서 sim 81.0667초 / step 4864에 다음 예외가 재현됐다.

```text
TypeError: Cannot read properties of null (reading 'x')
  at wip148VlsCellLocal
  at view.spawnLaunchTransient
  at Object.syncMissileVisuals
  at step
```

직접 원인은 C17 VLS 배기 연출이다. 2×4 모듈의 이론상 여덟 위치를 모두 평균하면서 벙커힐의 크레인용 미장착 세 칸을 참조했다. 이 좌표는 registration에 없어서 `null`이다. 같은 시점에 별도 결함도 발견했다. 공통 좌표 함수가 전방 셀 row를 DDG의 0–3으로 잘라 벙커힐의 실제 4–7행 발사 위치를 다른 셀로 옮겼다. 출항 전 UI 좌표 고정만으로는 이 발사 경로를 고칠 수 없었다.

J는 벙커힐의 설치 row/col을 그대로 찾는다. 미장착 칸은 명확한 오류로 거부하고 실제 셀로 보정하지 않는다. C17 연출은 실장된 이웃 셀만 사용한다. 5개 셀과 3개 크레인 자리로 구성된 두 모듈도 처리한다. 배기구 중심은 기존 연출 방식에 따른 설치 셀 중심의 평균인 **SIM-TUNE 표시 좌표**이며 실함 배관·uptake 도면 재현이 아니다. DDG의 기존 row 정규화와 여덟 셀 평균은 유지한다.

원본 registration으로 122개 발사구, ESSM quad 488개 위치와 122개 합법 발사 연출을 전수 비교했다. 대표 12개 셀은 승인 트랙 fixture에서 실제 물리 발사했고 SI 위치 오차 최대 `7.11e-15 m`다. 첫 검사 입력에는 락온이 없어 기존 SARH 발사 차단이 정상 작동했다. 테스트 입력을 기존 승인 트랙 fixture로 고쳤으며 발사 권한 규칙은 변경하지 않았다. 미장착 여섯 칸은 모두 거부되고 읽기/표시 검사는 authoritative 상태를 바꾸지 않는다.

같은 seed와 Kh-32 6발의 J native 재실행은 sim 71.4667→100.2667초, step 4288→6016, 실제 draw 36회로 끝까지 진행했다. 종료 시 적 미사일 alive 0, 자함 피격 scar 40개, RAM 0, simulation/presentation fault 0, GPU context loss 0, page error/crash 0. 이는 모든 위협을 요격했다는 뜻이 아니다. 일부 피격 후에도 화면과 틱이 계속됨을 확인한 시험이다. 관통구 작업은 종료 시 여전히 pending이므로 이 시험을 geometry 완료 검사로 표기하지 않는다. H의 별도 native 관통구 완료/복원 검사는 H evidence에 보존한다.

H에서는 3D 예외가 다음 RAF 예약 전에 밖으로 빠져 전체 게임 루프가 멈출 수 있었다. I/J는 표시 예외를 별도로 기록하고 CIC로 전환해 물리 루프와 초기화를 유지한다. H의 RAF 정지와 J의 CIC 계속 진행, 3D 재개, RESET 오류 기록 삭제를 제어된 표시 예외로 비교했다. 이 복구는 물리 오류를 삼키거나 실패한 물리 틱을 계속 적분하는 기능이 아니다.

## SPG-62 접시 분리

옛 분류는 삼각형의 모든 vertex가 임의 높이 0.70 m를 넘는지에 따라 pitch 소유자를 나눴다. 이 경계가 접시·급전부와 지지부를 가로질러 실제 부품이 두 변환을 받아 갈라졌다.

원본 Float32 위치가 같은 vertex를 재질/normal seam 너머로 연결해 실제 연결 성분을 구했다. 전체 접시와 급전부는 하나의 pitch 변환을 받고 전체 pedestal와 332-face bearing fork는 yaw에 남는다. pitch pivot은 원본 축 0.95 m다. 네 조사기의 원본 여섯 성분을 각각 검사했고 삼각형 누락은 없다.

0/15/45/85° 고도 × −150/0/130° 방위 × 4대, 총 48개 자세를 독립 원본 기준과 대조했다. 최종 J 최대 위치 오차 `7.29e-15 m`. H에서 성분 분리와 최대 약 2 m 변위 오류를 먼저 재현했다. 전체 indexed source 740,819 triangles를 보존한다. 확대 화면은 `evidence/J-spg-resources/spg62-rigid-45deg.png`다.

## 벙커힐 RAM 발사와 양현 팰렁스

벙커힐 프로필은 이미 GUN 두 대였다. 그러나 `updateCIWS`가 배열 첫 번째를 팰렁스, 두 번째를 SeaRAM으로 취급해 두 번째 GUN이 실제 RAM 생성 경로로 들어갔다. H의 실제 Kh-32 6발 AUTO 비행에서 물리 RAM peak 1을 확인했으며 좌현 팰렁스는 별도 발사 시험에서 0발이었다.

GUN만 20mm 루프로, RAM만 미사일 루프로 보낸다. 실제 release에서도 타입을 확인한다. 20mm 탄은 실제 mount/installation ID를 보유하고 사격 보정과 탄약이 그 소유자에게 돌아간다. 양현 탄도·구동·사각과 공통 팰렁스 모듈을 공유하되 탄약과 3D 효과는 각각 처리한다. HUD/ARM 패널도 양현 20mm를 표시한다. 없는 SeaRAM의 렌더 상태는 null이다.

최종 J 양현 실제 발사·독립 탄약·소유자·RAM 0·HUD 15/15, DDG의 실제 RAM 발사와 탄약 소모 7/7 PASS. DDG 6-case 팰렁스 benchmark는 1,132발 / 명중 16회 등 기존 WIP16B 집계와 exact 일치, 상세 float 최대 차이 `3.87e-13`으로 기존 오차 한도 안이다.

## 반복 교전 자원 수명

퇴장한 SAM/적 ASM/wreck 메시를 장면에서 제거만 하고 owned geometry/material을 해제하지 않는 별도 누적 결함이 있었다. 반복 Kh-32 6발 생성/퇴장 네 번에서 H의 renderer geometry 341→362→383→404, texture 4→5→6→7 증가를 재현했다. 이 누적이 사용자 기기의 이번 정지를 일으켰다는 직접 증거는 없으며 확인된 결함으로 따로 기록한다.

J는 정상 퇴장과 reset에서 각 owned geometry/material을 unique Set으로 한 번만 dispose한다. 생성자가 geometry dispose에 연결한 전용 paint texture도 함께 해제된다. 공유 smoke texture를 dispose하지 않는다. 최종 J 네 반복 모두 geometry 341→320, texture 4→3으로 돌아갔고 추적한 geometry/material/전용 texture는 각각 정확히 한 번 해제됐다. 실제 native draw가 매 반복 계속됐으며 context loss 0이다.

## SPQ-9 양면 요청과 공개 근거

공개 문서의 서로 등을 맞댄 두 평면 배열은 **SPQ-9B**의 설명이다. 구형 SPQ-9A의 양면 배치는 이번 조사로 확인하지 못했다. 따라서 non-B 명칭과 구형 2D 수상 프로세서를 유지하고 요청한 두 면은 **미확정 하드웨어 배치의 SIM-TUNE**으로 명시한다. 실제 퇴역 전 CG-52의 양면 SPQ-9A 장착을 확인했다고 주장하지 않는다.

두 탐색 면은 180° 차이, SIM-TUNE 30 RPM에서 명목 1초 재방문이다. 각 면의 구조물 사각, 실제 dwell, 3D 빔이 같은 방향을 사용한다. 차폐 시 실제 재방문은 길어진다. B형 ASMD/공중 모드나 가공한 측정 고도를 추가하지 않는다. 125개 실제 센서 tick에서 두 빔과 각 사각을 검사하고 수신기 역할·익명 관측·클러터 처리도 확인했다. SPS-73은 상부의 독립 단면 안테나와 설정을 유지한다. 상세 출처와 미확정 항목은 [RADAR_SOURCES.md](RADAR_SOURCES.md)를 따른다.

## 범위와 보존

60 Hz 물리, 120 Hz 침수/힘, 20 Hz hydro와 기존 geometry frame 예산은 유지한다. 그림/진단 결과를 track authority나 자동 교전으로 전달하지 않는다. 원본 DDG 프로필, 기존 13 packed records와 CG 내장 여섯 asset은 그대로다. I→J는 정확히 두 VLS 문맥만 바뀌었고 그 외 main bytes는 동일하다.

CG operational revision `BUNKERHILL_LATE_G_1`을 유지한다. 설치 셀/장비 ID·편성·저장 codec·277구획과 승조원 배치는 호환되며 D/E/F 저장의 기존 명시 migration을 보존한다. 새 탐색 튜닝은 HTML 버전과 출처 필드로 구별한다. 초기화·물리 적분·미사일 프로필이나 저장 schema를 바꾸지 않는다.

시험은 로컬 Chromium/SwiftShader에서 수행했다. draw 지속과 자원 수명 검사이지 사용자 휴대폰의 native GPU FPS 측정이나 모든 종류의 브라우저 종료 재현이 아니다. 원격 업로드/CI/PR 실행은 이 작업에서 하지 않았다. 직접 J 검사와 I/H 선행 근거는 `evidence/verification-summary.json`에서 구분한다.

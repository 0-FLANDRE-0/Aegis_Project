# Multi Ship A — 1~2단계

출항 전에 자함, 기존 시험 표적함 유무, 적함 준비 프로필을 선택한다. 표적함은 `HULK/NONE`, 적함은 `없음/DDG-119/CG-52`다. 기본값은 기존 동작인 시험 표적함 있음·적함 없음이다. 초기 선택과 VLS 편성 화면에서 설정을 바꾸고 출항 때 확정한다. 출항 후에는 함종·배치·VLS를 바꾸지 않는다.

이번 단계는 **기준 기록과 독립 상태·컨텍스트 준비**다. 적함은 `STATE_BOUND_INACTIVE`로 등록되며 화면에도 준비 단계라고 표시한다. 실제 적함 모델 배치·항해·탐지·요격·공격·전자전은 활성화하지 않는다. `registered=2`일 수 있지만 `simulated=1`이며 기존 세계·센서·물리 루프를 두 번 실행하지 않는다.

## 상태 소유권

`createPreparedShipRuntimeA(profile, options)`는 같은 프로필을 가진 자함의 현재 상태를 복제하지 않는다. 공유 생성 함수로 별개의 VLS 고정 셀, CIWS·함포 탄창, Harpoon·SRBOC·Nulka 재고, SPG 서보, 트랙·센서 버퍼, EW 할당 상태, 실제 피해·침수·보수·구획·승조원·질량·함체 동역학 모델을 만든다. CG는 61+61셀/330명/277구획/두 Phalanx/두 함포/8 Harpoon, DDG는 32+64셀/310명/138구획/Phalanx+SeaRAM/한 함포/Harpoon 미설치를 따른다.

불변 프로필·장착 등록과 물리 세계는 공유한다. 함정의 가변 상태와 observer 버퍼는 공유하지 않는다. 바인더는 가변 객체의 중복 소유를 사전에 거부한다. 기본 인수가 자함인 기존 getter에 명시적인 runtime을 전달하면 해당 함정의 모델을 읽는다. 선택 자함의 기존 전역 alias와 UI는 자함에 유지한다. 컨텍스트 getter는 최신 바인딩을 읽으며 함종을 임시로 바꾸는 전역 context swap은 사용하지 않는다.

새 센서 버퍼와 FCS 상태는 준비 상태다. 기존 TrackStore의 전역 truth index나 자함 FCS를 적함에 연결하지 않는다. 적함 함포의 발사·해법·step 호출은 실행 지연 사유로 거부한다. 구명뗏목은 provision 정보만 준비하며 실제 controller/world 연결은 3단계다. 컨텍스트의 physicalWorld는 물리 서비스용이다. 후속 AI에 전달할 관측 전용 facade에는 이를 포함하지 않아야 한다.

## 장착·저장 계약

`damage-registration.json`은 고정된 Harpoon E의 기존 함종별 hitbox 생성 결과다. 같은 geometry·재질·target ID를 불변 등록으로 사용하며 함종·revision이 맞지 않으면 거부한다. 새 함종이나 geometry 변경 때에는 임의 AABB를 만들지 말고 등록을 재생성하고 해당 함종의 원래 생성 결과와 비교한다. 선택 자함의 기존 hitbox 생성 경로는 그대로다.

운용 저장에는 배치 설정과 `deployment` codec을 추가한다. 모든 codec 검사 후 적함 상태를 detached 생성하고 적용한다. 거부한 입력은 배치·세계·재고·피해·난수 등 authoritative 상태를 바꾸지 않는다. 옛 저장의 배치 누락은 명시적으로 `HULK/적함 없음`으로 migration한다. 현재 적함의 진행 상태·탄 비행·EW 효과를 저장한 것으로 해석하지 않는다. 전체 reset은 확정 설정으로 적함 준비 상태를 새로 만들고 표적함 유무를 유지한다.

## 재생성·검사

```bash
python docs/multiship/A/build.py archive/v48/WIP_HARPOON_E/Aegis_SIM_v48_WIP_HARPOON_E.html artifacts/Aegis_SIM_v48_WIP_MULTI_SHIP_A.html
python docs/multiship/A/verify_static.py archive/v48/WIP_HARPOON_E/Aegis_SIM_v48_WIP_HARPOON_E.html Aegis_SIM_v48_WIP_MULTI_SHIP_A.html artifacts/multiship/static
python docs/multiship/A/verify_runtime.py Aegis_SIM_v48_WIP_MULTI_SHIP_A.html artifacts/multiship/runtime
python docs/multiship/A/verify_baseline.py archive/v48/WIP_HARPOON_E/Aegis_SIM_v48_WIP_HARPOON_E.html Aegis_SIM_v48_WIP_MULTI_SHIP_A.html artifacts/multiship/baseline
python docs/multiship/A/verify_native.py Aegis_SIM_v48_WIP_MULTI_SHIP_A.html artifacts/multiship/native
```

PACK records 0~12와 모든 원본 함선·무장 asset은 동일하다. record 13과 packaging build label만 변경한다. stable v48은 그대로다. [의존성/다음 단계](DEPENDENCIES.md), [검증 집계](evidence/verification-summary.json), [GitHub 인계](GITHUB_HANDOFF.md)를 따른다.

기준 비교는 같은 seed의 전체 fixed tick에서 대기(1배속), 8발 Kh-32 AUTO(8배속), 침수(16배속)를 사용한다. raid의 초기 관측 트랙은 기존 회귀 fixture가 주입하므로 자연 탐지 성능이나 적 AI 인증으로 해석하지 않는다. 프로파일러 avg/p95/max와 개체 수는 측정 기록이며 한 번의 실행으로 속도 향상을 주장하지 않는다. native는 393×852 실제 선택과 RAF/WebGL, 제어된 Kh-32 관통 피해/실제 외판 구멍과 후속 draw·tick을 확인한다. SwiftShader 결과는 모바일 기기 FPS 인증이 아니다.

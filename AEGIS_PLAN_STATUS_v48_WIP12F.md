# AEGIS v48 WIP12F 상태

## 판정

`terminal ballistics closure 구현 및 로컬 회귀 완료`

WIP12F는 WIP12E REV5에서 확인된 장갑·신관·폭발 체계를 유지하면서 safety arming, sub-threshold delay, partial opening, kinetic spall, post-exit handoff 및 영구 장갑 patch의 연결을 마감한다.

## 저장소 기준

- 시작 main: `d8f6c32b455ed540dff60fb6f2928229279e32f8`
- 작업 브랜치: `feat/v48-wip12f-terminal-hardening`
- 기준 후보: `Aegis_SIM_v48_WIP12E_REV5_NAVAL_ARMOR_FUZE_COUPLING.html`
- 기준 후보 SHA-256: `b1a95c30dd05d5da61fc89a4a7f6e291f42564079659931d82a929bdfd0d54a4`
- 새 후보: `Aegis_SIM_v48_WIP12F.html`
- 새 후보 크기: `3,289,064 bytes`
- 새 후보 SHA-256: `887ee34656fbc18be59dfda14c8fdd35ce6558cc5626ef2fb29e4ba2f5187def`

## 핵심 불변식

1. 충돌은 안전장치를 해제하지 않는다.
2. 일반 지연신관은 최소 자극 미달 판재 뒤에서도 작동 가능한 상태로 계속 간다.
3. 직격식 신관은 접촉 순간 개시되고 이후 탄체 `FRACTURED`가 이를 소급 취소하지 않는다.
4. `PARTIAL`은 `holeAreaM2 = 0`이며 flood opening을 만들지 않는다.
5. 실제 opening은 `PERFORATED` 또는 solved blast plate failure에서만 나온다.
6. plug와 rear spall은 에너지원이 하나이고 module/crew 소비자에 한 번씩 전달된다.
7. damage event가 수락된 뒤에만 armor patch와 시각 event를 commit한다.
8. armor patch와 모든 solved scar는 reset 전까지 남는다.
9. 살아 있는 post-exit projectile은 신관과 남은 폭약 상태를 잃지 않는다.
10. Kh-32와 Kh-35U는 각자 실제 delay 범위를 가진다.
11. renderer는 immutable snapshot을 읽고 물리에 피드백하지 않는다.

## 회귀 결과

| 검사 | 결과 |
|---|---:|
| inline JavaScript parse | PASS |
| static contract | `17/17 PASS` |
| WIP12F diagnostics | `11/11 PASS` |
| WIP12A-E diagnostics | 모두 PASS |
| core selftest | `0 failures` |
| Playwright | `4/4 PASS` |
| console/page error | `0/0` |
| 실제 Kh-32 | `NORMAL_HIT`, 41 modules, 15 compartments |
| 실제 Kh-35U | `NORMAL_HIT`, 25 modules, 17 compartments |
| DUD | blast 0, scar/patch/spall 유지 |
| 함교 누적 3회 | SPY 4면 모두 정지 |
| 2D scar parity | source/top/side `111/111/111` |
| 130 s 후 scar | 유지 |

## 물리적 한계

- RHAe와 신관 임계값은 simulation tuning이며 실물 인증값이 아니다.
- full CFD, 수중 bubble pulse, hull whipping, 복합·반응장갑은 범위 밖이다.
- kinetic spall은 bounded statistical/directional model이다.
- 함포 외부탄도와 사격통제는 아직 연결하지 않았다. 다음 WIP가 WIP12F terminal API를 소비해야 한다.

상세 구현은 `docs/WIP12F_TERMINAL_HARDENING_IMPLEMENTATION.md`, 다음 함포 작업의 연결 규칙은 `docs/WIP12F_TERMINAL_HARDENING_HANDOFF.md`를 따른다.

# AEGIS v48 WIP12F 인계서

## 기준

- 저장소: `0-FLANDRE-0/Aegis_Project`
- 시작 main: `d8f6c32b455ed540dff60fb6f2928229279e32f8`
- 작업 브랜치: `feat/v48-wip12f-terminal-hardening`
- 입력 후보: `Aegis_SIM_v48_WIP12E_REV5_NAVAL_ARMOR_FUZE_COUPLING.html`
- 입력 SHA-256: `b1a95c30dd05d5da61fc89a4a7f6e291f42564079659931d82a929bdfd0d54a4`
- WIP12F 후보: `Aegis_SIM_v48_WIP12F.html`
- WIP12F 후보 SHA-256: `887ee34656fbc18be59dfda14c8fdd35ce6558cc5626ef2fb29e4ba2f5187def`
- 권위 blast mode: `COMPARTMENT_BLAST_AUTHORITY`

## 완료 범위

- 안전장치 해제와 충돌 신관 개시 분리
- 일반 지연신관의 sub-threshold contact 통과 및 다음 경계 재판정
- 대함 미사일의 독립 superquick external fallback을 명시적 SIM 가정으로 분리
- 직격식 신관의 접촉 개시와 사후 탄체 파손 순서 교정
- `PARTIAL` 개구 금지, `PERFORATED` 또는 solved blast rupture만 개구 허용
- 장갑두께/구경비에 따른 rear-spall 감쇠
- module/crew kinetic-spall 소비자 연결 및 event-ID 결정성
- 영구 `armorDamagePatches` 권위 채널과 reset 수명
- 관통 후 살아 있는 탄체·신관의 post-exit handoff
- Kh-32와 Kh-35U live 경로의 delay 범위, spall, patch 및 render-state 연결
- 불발탄의 kinetic damage·scar·patch 유지와 blast `0` 보장

## 다음 함포 WIP의 진입점

함포는 WIP12F 내부를 무기명으로 분기하지 말고 다음 순서를 사용한다.

1. 포탄별 `wip12aProjectileSpec()`을 만든다.
2. 외부탄도 결과에서 위치, 방향, body axis, 속도, 질량 및 flight arming state를 `wip12aMakeProjectileState()`에 전달한다.
3. 표적 geometry를 `wip12aTraceTerminalProjectile()`에 전달한다.
4. 반환된 `damagePacket`을 `wip12aApplyDamagePacket(..., { commit:true })`으로 정확히 한 번 적용한다.
5. `postExitHandoff`가 있으면 표적 밖 탄도 또는 재진입 경로에 넘긴다.

금지 사항:

- `wip12aApplyDamagePacket()` 뒤 별도의 legacy blast damage를 다시 적용하지 않는다.
- `PARTIAL`을 관통구나 침수 opening으로 변환하지 않는다.
- 포탄 이름으로 blast 반경·구획 피해를 분기하지 않는다.
- 안전장치를 충돌 순간 자동 해제하지 않는다.
- 렌더러가 armor patch, damage packet 또는 RNG를 변경하게 하지 않는다.

## 포탄 입력 체크리스트

| 필드 | 필수 의미 |
|---|---|
| geometry | 구경, 길이, nose/cap 형상 |
| body | 총질량, penetrator 질량, 경도, 파쇄저항, 연성 |
| payload | 폭약량, TNT 등가, 케이스/소이 질량, fragment model |
| fuze | direct/base-delay, 최소 arming 시간·거리, delay 범위, qualification profile |
| flight state | launch-cleared, 누적 비행시간·거리 |
| impact state | 표적 로컬 위치, 방향, body axis, 속도 |

HE, SAP, APHE, rocket 및 missile은 같은 구조를 사용한다. 순수 AP는 payload와 fuze를 비활성으로 두고 운동 관입·plug·rear spall만 사용한다.

## 검증된 명령

```bash
node tests/terminal-hardening-wip12f-contract.cjs
WIP12F_CHROMIUM_PATH=/path/to/chromium node /path/to/playwright/cli.js test tests/terminal-hardening-wip12f.spec.js --workers=1
```

검증 결과는 static `17/17`, Playwright `4/4`, core selftest `0 failures`, console/page error `0/0`이다.

## 관련 파일

- `Aegis_SIM_v48_WIP12F.html`
- `docs/WIP12F_TERMINAL_HARDENING_IMPLEMENTATION.md`
- `docs/WIP12F_TERMINAL_HARDENING_HANDOFF.md`
- `tests/terminal-hardening-wip12f-contract.cjs`
- `tests/terminal-hardening-wip12f.spec.js`
- `AEGIS_PLAN_STATUS_v48_WIP12F.md`
- `WIP12F_SHA256SUMS.txt`

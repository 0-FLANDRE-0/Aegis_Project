# AEGIS v48 WIP12E 상태

## 판정

`revision 4 폭발-피해 결합·영구 파괴흔적 교정 완료 / 전용 Chromium 4/4 및 계약 57/57 통과 / 전체 저장소 회귀·원격 HTML 업로드 잔여`

작업 번호는 **WIP12E로 유지**한다. `REV4`는 캐시가 이전 HTML을 재사용하는 문제를 피하기 위한 후보 파일 식별자이며 새 WIP 단계가 아니다.

현재 후보는 폭발 효과의 크기만 키우지 않는다. 동일한 구획 폭발 해석 결과가 외피·내부 파괴, 실제 구획 피해, 등록 장비 피해, 승조원 노출, 화재, 침수, 2D 인디케이터 및 3D 절삭에 연결된다. 전용 회귀는 통과했지만 저장소 전체 기존 회귀와 GitHub Actions, 원격 HTML 반영이 남아 있으므로 WIP12E를 최종 완료로 선언하지 않는다.

## 기준과 브랜치

- WIP12D PR [`#29`](https://github.com/0-FLANDRE-0/Aegis_Project/pull/29): `merged`, `2026-09-19T16:44:41Z`
- 현재 `main`: `97de0e1459e4f111e21b5bed163decc6ce782c32`
- 기준 HTML: `Aegis_SIM_v48_WIP12D.html`
- 기준 크기: `3,058,349 bytes`
- 검증한 기준 SHA-256: `8ae85b69e28e71e54137ede0fd6110bbfa358fea7b04c2a88446bf3d44f7a90c`
- 작업 브랜치: `feat/v48-wip12e-compartment-blast`
- GitHub merge-base: 위 `main` SHA와 동일, branch는 `main`보다 앞서 있고 뒤처지지 않음
- 캐시 우회 구현 후보: `Aegis_SIM_v48_WIP12E_REV4_BLAST_DAMAGE_COUPLING_FIX.html`
- 후보 크기: `3,212,922 bytes`
- 후보 SHA-256: `856ec05e4acd6c7a04bb9da580a46c550cb33341cb82e6b5cb086237930fa3a3`

## revision 4 교정

- 폭발 중심의 `core`와 약간 더 넓은 `fringe`를 하나의 피해 envelope로 정의했다.
- 도달한 구획에서 물리 pressure/impulse/thermal/fragment 결과와 TNT 질량·거리 기반 최소 충격 응답 중 큰 값을 사용한다. additive 중복 가산은 하지 않는다.
- bulkhead/portal 해석이 도달시키지 못한 구획에는 거리만으로 피해를 순간이동시키지 않는다.
- 모든 등록 physical equipment target에 동일 trace를 연결하고, 민감 전자장비·중기계·보호 위험물·일반 장비의 응답 profile을 분리했다.
- SPY, 함교, 전투지휘, mast, hangar 계열 target의 실제 module damage/operational state를 갱신한다.
- 장비 ID를 찾지 못했을 때 임의 raw system target을 만드는 fallback은 제거했다.
- direct kinetic 채널은 한 번만 병합하며, generic projectile packet의 `vlsCellDamage` 미정의 참조로 발생하던 충돌을 수정했다.
- hot products는 폭발파가 실제 도달한 구획만 대상으로 하며, coarse damage-control cell 전체에 먼저 분산한 뒤 남은 후보를 채운다.
- damage scar의 최근 96개 절단을 제거했다. reset 전까지 모든 solved scar를 유지하고 시간에 따른 복구·fade를 하지 않는다.
- 2D 상면/측면 인디케이터가 3D와 동일한 영구 scar 집합을 전부 그리며, 감사 API로 source/drawn 수를 노출한다.
- 기존 revision 3의 정확한 entry blowout, 반대편 pressure rupture, case-fragment perforation, 내부 bulkhead tear 및 WIP12D residual hole을 유지한다.

## 범용 폭발 경로

미사일·로켓·포탄이라는 이름으로 분기하지 않는다. `explosiveMassKg`, TNT 등가, casing mass, 기폭 위치·매질, 속도·방향, 관통 opening만 공통 packet에 제공한다.

1. `BlastChargeSpec`을 정규화한다.
2. bounded cell/portal solver가 immutable `BlastTrace`를 만든다.
3. core+fringe 범위 중 portal을 통해 실제 도달한 구획만 `BlastDamagePacket`을 받는다.
4. 구조·장비·승조원·열·침수 consumer가 같은 event ID와 trace hash를 각자 한 번만 소비한다.
5. 2D/3D는 solved damage를 표시할 뿐 피해를 다시 계산하지 않는다.

## 전용 검증 결과

| 검사 | 결과 |
|---|---:|
| static checks | `46/46 PASS` |
| isolated VM runtime groups | `11/11 PASS` |
| 계약 합계 | `57/57 PASS` |
| solver 64회 평균 | `2.294 ms/impact` |
| combat RNG | unchanged |
| 실제 Chromium Playwright | `4/4 PASS` |
| console/page errors | `0/0` |
| 실제 WebGL 3D 절삭·내부 tear audit | PASS |
| 2D 상면/측면 scar parity | PASS |
| 96개 초과 scar 및 130초 후 존속 | PASS |

실행 명령:

```bash
node tests/blast-damage-coupling-wip12e-rev4-contract.cjs
THREE_JS_PATH=/path/to/three.min.js npx playwright test tests/blast-damage-coupling-wip12e-rev4.spec.js --workers=1
```

## 실기 회귀 증거

seed `481232`, 100 km Kh-32 실제 Chromium 회귀에서 WIP12D의 명중 시각 `92.78333333333333 s`, 충돌 속도 `991 m/s`, 첫 접촉 `전방연돌`, residual body `4`, far-hull exit `2`를 보존했다.

한 발의 WIP12E 폭발은 다음 결과를 냈다.

- 도달 cell `43`, 실제 피해 상세 구획 `35`, 피해 physical module `42`
- entry blowout `1`, direct exterior rupture `24`, internal tear `3`, fragment perforation `36`
- planned ignition `14`, 실제 coarse fire zone `6`
- 총 breach는 hard cap `64` 안에서 종료
- unknown target 및 damage-consumer issue `0`
- solved scar `64`, 시간 경과 후 자동 복구 없음

함교 중심의 동일한 generic `500 kg TNT + 250 kg casing` packet을 반복 적용한 회귀에서는 1발 후 모든 SPY 면이 작동하고, 2발 후 전방 SPY 두 면이 `80%` 손상 임계값을 넘어 정지하며, 3발 후 네 면 모두 `100%` 손상·정지한다. 이는 특정 Kh-32 label 보정이 아니라 민감 전자장비 profile과 거리·도달 경로의 결과다.

세 번째 폭발 뒤 96개를 넘는 scar가 남았으며 최초 scar도 130 simulation seconds 뒤 2D 상면·측면과 3D에서 유지됐다.

## 권위 경계

- `COMPARTMENT_BLAST_AUTHORITY`에서는 WIP12E packet만 primary blast 피해를 적용한다.
- WIP12B terminal event는 이미 적용된 폭발을 관찰만 한다.
- WIP12D residual supplement는 제한된 기계 피해와 실제 외피 구멍만 보충하고 blast를 재생하지 않는다.
- 일반 pressure만으로 자동 발화하지 않는다. hot gas/thermal, 가연물 및 fragment assist가 점화 권위다.
- 렌더러는 immutable presentation snapshot만 읽으며 물리·피해·난수에 피드백하지 않는다.

## 원격 반영 상태와 잔여 작업

- GitHub `main`/PR #29/작업 branch 상태 확인: 완료
- 기준 WIP12D SHA-256 검증: 완료
- REV4 구현 및 전용 회귀: 완료
- 캐시 우회 REV4 HTML의 GitHub branch 업로드: 필요
- package scripts, workflow, README 및 프로젝트 지침의 WIP12E 활성화: HTML 업로드 뒤 필요
- 저장소 전체 기존 Playwright suite와 GitHub Actions: 미실행

큰 HTML은 repository의 기존 전달 규칙에 따라 GitHub UI 또는 정상 인증된 git 전송으로 올리고, 내려받은 파일의 SHA-256을 manifest와 다시 대조한다.

## 관련 파일

- `Aegis_SIM_v48_WIP12E_REV4_BLAST_DAMAGE_COUPLING_FIX.html`
- `docs/WIP12E_COMPARTMENT_BLAST_HANDOFF.md`
- `docs/WIP12E_COMPARTMENT_BLAST_IMPLEMENTATION.md`
- `tests/blast-damage-coupling-wip12e-rev4-contract.cjs`
- `tests/blast-damage-coupling-wip12e-rev4.spec.js`
- `WIP12E_MANUAL_UPLOAD.md`
- `WIP12E_SHA256SUMS.txt`

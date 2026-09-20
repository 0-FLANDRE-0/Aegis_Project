# AEGIS v48 WIP12E REV4 인계서

## 현재 기준

- 저장소: `0-FLANDRE-0/Aegis_Project`
- 작업 브랜치: `feat/v48-wip12e-compartment-blast`
- WIP12D PR `#29`: merged
- 기준 `main`: `97de0e1459e4f111e21b5bed163decc6ce782c32`
- 기준 HTML: `Aegis_SIM_v48_WIP12D.html`
- 기준 SHA-256: `8ae85b69e28e71e54137ede0fd6110bbfa358fea7b04c2a88446bf3d44f7a90c`
- 시험 후보: `Aegis_SIM_v48_WIP12E_REV4_BLAST_DAMAGE_COUPLING_FIX.html`
- 시험 후보 SHA-256: `856ec05e4acd6c7a04bb9da580a46c550cb33341cb82e6b5cb086237930fa3a3`

`REV4`는 브라우저 캐시를 피하기 위한 파일명일 뿐 작업 번호는 계속 **WIP12E**다.

## 사용자 피드백에 대한 구현 결론

이 revision은 “폭발 범위와 그보다 약간 넓은 범위의 모든 모듈·구획에 피해를 주되, 벽을 무시하지 않는 방식”으로 구현했다.

- `core`: 구획 solver가 계산한 실제 폭압·충격량·열·파편 응답
- `fringe`: TNT 등가의 세제곱근으로 정한 약간 넓은 충격 범위
- 적용값: solved channel response와 yield/range shock floor 중 큰 값
- 도달 조건: portal/bulkhead 전파가 실제로 도달한 cell만 대상
- 차폐: 닫힌 bulkhead가 버티면 거리만 가깝다는 이유로 건너편에 피해를 만들지 않음
- 장비: 해당 cell/범위의 모든 등록 physical target을 profile별로 갱신
- 표시: 동일 solved result를 2D와 3D가 소비하며 별도의 시각 전용 피해값을 만들지 않음

따라서 큰 탄두는 폭발 범위 전체의 외피와 내부 격벽을 연속적으로 찢고, 주변 구획과 장비에도 실제 수치 피해를 준다. 미사일·로켓·포탄은 모두 같은 입력 계약을 사용한다.

## 핵심 권위 흐름

1. 폭발성 terminal packet이 charge, casing, 기폭점, 매질, 속도·방향 및 projectile opening을 제공한다.
2. 구획·portal solver가 하나의 immutable `BlastTrace`를 계산한다.
3. `BlastDamagePacket`이 구조, 상세 구획, physical equipment, 승조원, 열·화재 및 침수 consumer에 한 번만 전달된다.
4. 원래 입구는 내부 기폭의 backblast로 확대되고, 반대편 외판은 pressure rupture 또는 case-fragment perforation으로 별도 파괴된다.
5. door/bulkhead failure는 `BLAST_INTERNAL_TEAR`로 남아 후속 pressure path가 된다.
6. 모든 solved scar는 reset 전까지 2D 상면·측면과 3D 내·외부에서 유지된다.

## 이번 revision의 중요한 수정

- generic damage packet 종료부의 잘못된 `vlsCellDamage` 참조를 고쳐 포탄·로켓 경로의 `ReferenceError`를 제거했다.
- 폭발 VFX와 실제 피해의 크기가 분리돼 있던 문제를 core+fringe damage envelope로 연결했다.
- SPY를 포함한 등록 장비 전체가 pressure/impulse/fragment/thermal/structural 채널을 소비한다.
- 최근 96개만 남기던 scar 절단과 age fade를 제거했다.
- 2D 상·측면 renderer에 persistent scar overlay와 감사 API를 추가했다.
- hot products를 실제 도달 cell에 분산하고 coarse zone을 우선 다양화해 대형 내부 폭발의 화재가 지나치게 적던 문제를 완화했다.
- 특정 무기명 분기 없이 동일 charge를 missile/rocket/shell carrier에서 동일하게 처리한다.

## 검증 기준값

### Kh-32 live case

seed `481232`, 100 km 조건:

| 항목 | REV4 결과 |
|---|---:|
| 명중 시각 | `92.78333333333333 s` |
| 충돌 속도 | `991 m/s` |
| 첫 접촉 | `전방연돌` |
| 도달 / 피해 상세 구획 | `43 / 35` |
| 피해 physical module | `42` |
| entry / exterior / internal / fragment breach | `1 / 24 / 3 / 36` |
| planned ignition / 실제 fire zone | `14 / 6` |
| unknown target / consumer issue | `0 / 0` |
| solved scar | `64` |

WIP12D residual body `4`, far-hull exit `2`와 flight golden은 유지한다.

### 함교 SPY 누적 회귀

동일한 generic `500 kg TNT + 250 kg casing` packet을 함교에 반복 적용한다.

| 누적 피격 | 기대 결과 |
|---:|---|
| 1 | SPY 네 면 모두 작동, 손상은 누적됨 |
| 2 | 전방 두 면이 `80%` 임계값을 넘어 정지, 후방은 작동 |
| 3 | 네 면 모두 `100%` 손상·정지 |

세 번째 피격 뒤 scar 수가 96을 넘고, 최초 scar가 130 simulation seconds 뒤에도 남아야 한다. 2D 상면/측면의 drawn count는 solved source count와 같아야 한다.

## 검증 결과

- static checks `46/46 PASS`
- isolated runtime groups `11/11 PASS`
- 계약 합계 `57/57 PASS`
- 실제 Chromium `4/4 PASS`
- console/page error `0/0`
- 2D scar parity, 3D exterior/interior cut, time-scale invariant, DUD zero-state 및 combat RNG isolation: PASS

## 다음 작업

1. 캐시 우회 REV4 HTML을 현재 WIP12E branch 루트에 같은 파일명으로 업로드한다.
2. 원격 파일을 다시 내려받아 `WIP12E_SHA256SUMS.txt`와 대조한다.
3. package/workflow가 REV4 전용 계약과 Playwright를 실행하게 한다.
4. 저장소 전체 기존 회귀와 GitHub Actions를 실행한다.
5. 통과 뒤 필요하면 검증된 REV4를 canonical `Aegis_SIM_v48_WIP12E.html`로 승격한다.

전체 설계와 model limitation은 `docs/WIP12E_COMPARTMENT_BLAST_IMPLEMENTATION.md`, 현재 판정은 `AEGIS_PLAN_STATUS_v48_WIP12E.md`를 따른다.

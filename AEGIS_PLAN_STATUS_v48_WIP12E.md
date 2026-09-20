# AEGIS v48 WIP12E 상태

## 판정

`revision 5 naval armor·fuze·external blast coupling 구현·전용 회귀·원격 반영 완료 / 전체 저장소 회귀·GitHub Actions 잔여`

작업 번호는 **WIP12E로 유지**한다. `REV5`는 캐시 우회와 시험 후보 구분을 위한 파일 식별자다.

REV5는 REV4의 구획 폭발·실피해·영구 scar 권위를 유지하면서 장갑과 신관 사이의 누락된 결정을 추가한다. 이제 비관통 고폭은 두꺼운 장갑에 임의 구멍을 만들지 않고 표면 손상과 제한된 내부 충격만 준다. 반대로 외부 접촉 폭발도 얇은 외판의 압력·충격량·판재 파괴 일을 이기면 실제 `EXTERNAL_BLAST_BLOWOUT`을 만든다.

## 기준과 브랜치

- WIP12D PR [`#29`](https://github.com/0-FLANDRE-0/Aegis_Project/pull/29): `merged`, `2026-09-19T16:44:41Z`
- 현재 `main`: `97de0e1459e4f111e21b5bed163decc6ce782c32`
- 기준 HTML: `Aegis_SIM_v48_WIP12D.html`
- 기준 크기: `3,058,349 bytes`
- 검증한 기준 SHA-256: `8ae85b69e28e71e54137ede0fd6110bbfa358fea7b04c2a88446bf3d44f7a90c`
- 작업 브랜치: `feat/v48-wip12e-compartment-blast`
- 원격 merge-base: 위 `main` SHA와 동일
- 원격 branch 상태: `main`보다 `12` commits ahead, `0` behind (REV5 구현 및 문서 마감 포함)
- REV5 구현 commit: `c07120e3d03276e8bc67fbceb2dbd11632fa3689`
- REV4 기준 후보 SHA-256: `856ec05e4acd6c7a04bb9da580a46c550cb33341cb82e6b5cb086237930fa3a3`
- REV5 캐시 우회 후보: `Aegis_SIM_v48_WIP12E_REV5_NAVAL_ARMOR_FUZE_COUPLING.html`
- REV5 후보 크기: `3,260,140 bytes`
- REV5 후보 SHA-256: `b1a95c30dd05d5da61fc89a4a7f6e291f42564079659931d82a929bdfd0d54a4`
- 원격 HTML Git blob: `beb9b090b23e73444439128d104cc39378d4fc64`
- 원격 blob 전체 재읽기 검증: `3,260,140 bytes`, SHA-256 일치

## REV5 장갑·신관 판정

### RHAe와 신관 자격

- 함정용 구조강과 장갑재는 material profile별 RHA-equivalent 계수로 정규화한다.
- homogeneous naval armor와 face-hardened naval armor solver를 활성화했다.
- 지연신관 최소 자극 profile은 `8 / 12 / 20 mm RHAe`다.
- 판정에는 RHAe 두께와 함께 normal velocity, normal impulse, plate work, obliquity 및 projectile failure를 사용한다.
- 경사 경로 길이는 `1.35×`로 제한하고 독립 normal-velocity 조건을 요구하므로 grazing hit가 두께만 부풀려 신관을 작동시키지 못한다.
- direct-action profile은 최소 두께를 요구하지 않지만 정상 속도와 작동 가능한 탄체는 계속 요구한다.
- 이 값은 `SIM_TUNED`이며 실제 비공개 신관 인증 데이터를 주장하지 않는다.

### 표면 결과와 외부 고폭

| 결과 | 외피 | 내부 결합 |
|---|---|---|
| `SCORCH` | 그을림 | 작은 구조 충격 |
| `DENT` | 소성 변형 | 제한된 충격·피로 |
| `CRATER` | 파임·균열·잔존두께 감소 | 제한된 shock/rear spall |
| `PERFORATED` | 실제 관통구 | pressure/hot gas/fragment direct path |
| `EXTERNAL_BLAST_BLOWOUT` | 외부폭압에 의한 실제 파괴구 | 파열 개구를 통한 direct path |

비관통 외부 기폭에서는 hot-gas transmission을 `0`으로 두고 pressure/fragment/damage/shock 결합에 상한을 둔다. 외판이 실패한 경우에만 물리 개구를 만들고 plate failure work를 vented blast energy에서 structural work로 재분류해 에너지 원장을 닫는다.

합성 fixture는 손상 후 유효 두께 약 `3.84 mm`인 6 mm급 외판이 500 kg TNT-equivalent 접촉 폭발에 파열하는 반면, 유효 두께 `128 mm`인 200 mm급 RHA 판은 같은 load를 막는 것을 확인한다. 이는 경계 로직 stress test이며 함정별 실측 교정값은 아니다.

## Kh-32와 Kh-35U

Kh-35U는 누락되지 않았다.

- `KH32.spec.fuze.qualificationProfileId = ANTI_SHIP_DELAY_8`
- `KH35U.spec.fuze.qualificationProfileId = ANTI_SHIP_DELAY_8`
- 두 무기는 같은 자격 판정기를 쓰지만 각자의 질량·속도·탄두·케이스·경도·형상을 유지한다.
- blast solver에는 무기명 분기가 없고 missile/rocket/shell carrier가 같은 입력에서 같은 physics hash를 낸다.

실제 Chromium live 회귀:

| 항목 | Kh-32 | Kh-35U |
|---|---:|---:|
| seed / range | `481232 / 100 km` | `481235 / 100 km` |
| 명중 시각 | `92.78333333333333 s` | `345.81666666666666 s` |
| 결과 | `NORMAL_HIT` | `NORMAL_HIT` |
| 피해 module | `41` | `25` |
| 피해 compartment | `15` | `17` |
| breach | `36` | `64` |
| planned ignition | `5` | `2` |
| combat RNG | unchanged | unchanged |

Kh-32 case는 전방 연돌 외판을 먼저 관통한 뒤 외부에서 기폭해 `EXTERNAL_DETONATION_THROUGH_ENTRY`가 됐다. 유입된 고온가스 에너지는 보존된 thermal budget 안에서 실제 도달한 구획에 재분배되며 5개 구획이 점화됐다.

## 피해·표시·영구성 회귀

- 함교 generic `500 kg TNT + 250 kg casing` 1발: SPY 네 면 모두 작동, 면별 약 `37–40` damage
- 2발: F1/F2 약 `80.8` damage로 정지, F3/F4 약 `75`로 작동
- 3발: 네 면 모두 `100` damage로 정지
- 세 번째 피격 뒤 scar: `114`
- 최초 scar의 130 simulation seconds 후 존속: PASS
- 2D top/side source-drawn parity: `114 / 114 / 114`
- damage consumer unknown target/issue: `0`

실제 WebGL audit에서는 Kh-32 entry blowout `1`, exterior rupture `28`, fragment perforation `4`, internal tear `2`를 읽었다. 외부 파괴구 `29/29`가 실제 mesh에 부착됐고 persistent internal tear `2/2`가 authority와 일치했다.

## 전용 검증 결과

| 검사 | 결과 |
|---|---:|
| inline JavaScript parse | PASS |
| REV5 static contract | `18/18 PASS` |
| REV5 armor/fuze diagnostics | `16/16 PASS` |
| core selftests | `0 failures` |
| core/fixture/budget diagnostics | PASS |
| REV5 Chromium Playwright | `3/3 PASS` |
| Kh-32/Kh-35U live hit | PASS |
| thin blowout / thick hold | PASS |
| air/fragment/partition energy closure | PASS |
| deterministic hashes / combat RNG isolation | PASS |
| console/page errors | `0/0` |
| 실제 WebGL exterior/interior audit | PASS |

실행 명령:

```bash
node tests/naval-armor-fuze-wip12e-rev5-contract.cjs
SIM_FILE=Aegis_SIM_v48_WIP12E_REV5_NAVAL_ARMOR_FUZE_COUPLING.html npx playwright test tests/naval-armor-fuze-wip12e-rev5.spec.js --workers=1
```

## 권위 경계

- `COMPARTMENT_BLAST_AUTHORITY`에서는 WIP12E packet만 primary blast 피해를 적용한다.
- WIP12B terminal event는 이미 적용된 폭발을 관찰만 한다.
- WIP12D residual supplement는 기계 피해와 실제 잔존체 구멍만 보충하며 blast를 재생하지 않는다.
- 렌더러는 immutable solved result를 읽고 물리·피해·난수에 피드백하지 않는다.
- 일반 pressure만으로 자동 발화하지 않는다. hot gas exposure, 온도, energy density, 가연물 및 fragment assist가 필요하다.
- full CFD, 수중 bubble pulse, hull whipping, 복합장갑 및 반응장갑은 이번 범위 밖이다.

## 원격 반영 상태와 잔여 작업

- 완료: REV5 HTML, 전용 테스트, 문서 및 checksum을 WIP12E branch에 commit
- 완료: 원격 REV5 HTML 전체 blob 재읽기 후 SHA-256/크기 대조
- package scripts와 workflow에 REV5 테스트 연결
- 저장소 전체 기존 Playwright suite 및 GitHub Actions 실행
- 통과 뒤 canonical `Aegis_SIM_v48_WIP12E.html` 승격 여부 결정

## 관련 파일

- `Aegis_SIM_v48_WIP12E_REV5_NAVAL_ARMOR_FUZE_COUPLING.html`
- `docs/WIP12E_COMPARTMENT_BLAST_HANDOFF.md`
- `docs/WIP12E_COMPARTMENT_BLAST_IMPLEMENTATION.md`
- `tests/naval-armor-fuze-wip12e-rev5-contract.cjs`
- `tests/naval-armor-fuze-wip12e-rev5.spec.js`
- `WIP12E_MANUAL_UPLOAD.md`
- `WIP12E_SHA256SUMS.txt`

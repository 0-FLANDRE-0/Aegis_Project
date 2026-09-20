# AEGIS v48 WIP12E REV5 인계서

## 현재 기준

- 저장소: `0-FLANDRE-0/Aegis_Project`
- 작업 브랜치: `feat/v48-wip12e-compartment-blast`
- WIP12D PR `#29`: merged
- WIP12E PR `#30`: merged at `2026-09-20T04:50:00Z`
- 병합 `main`: `c18a51433d767f56ccd1bb4ff30388dfe91505d3`
- 병합한 branch head: `61c3c4a985e198f90117808ea6ced30a12e06302`
- 기준 HTML: `Aegis_SIM_v48_WIP12D.html`
- 기준 SHA-256: `8ae85b69e28e71e54137ede0fd6110bbfa358fea7b04c2a88446bf3d44f7a90c`
- 현재 시험 후보: `Aegis_SIM_v48_WIP12E_REV5_NAVAL_ARMOR_FUZE_COUPLING.html`
- 후보 SHA-256: `b1a95c30dd05d5da61fc89a4a7f6e291f42564079659931d82a929bdfd0d54a4`
- REV5 구현 commit: `c07120e3d03276e8bc67fbceb2dbd11632fa3689`
- 원격 HTML Git blob: `beb9b090b23e73444439128d104cc39378d4fc64`
- 원격 전체 blob 검증: `3,260,140 bytes`, 위 SHA-256과 일치

`REV5`는 브라우저 캐시를 우회하고 후보를 구분하기 위한 파일명이다. 작업 번호는 계속 **WIP12E**다.

## 이번 피드백에 대한 결론

### Kh-35U 포함

Kh-35U를 빼먹지 않았다. Kh-32와 Kh-35U는 모두 live ordnance adapter에서 `ANTI_SHIP_DELAY_8` 신관 자격 판정기를 사용한다. 다만 두 무기는 각자의 질량, 속도, 탄두 폭약량, 케이스 질량, 경도 및 형상을 그대로 사용한다. 즉 “Kh-32 결과를 Kh-35U에 복사”한 것이 아니라 동일한 범용 물리 계약에 서로 다른 탄체 입력을 넣는다.

브라우저 live 회귀에서 두 무기 모두 실제 명중, WIP12E 권위 trace 생성, 구획·장비 피해 적용, 에너지 폐합 및 combat RNG 비소비를 통과했다.

### 외부 기폭과 얇은 장갑

외부에서 터진 고폭탄두도 얇은 외판을 파열시켜 실제 구멍 또는 파괴구를 만들 수 있다. 판정은 무기 이름이 아니라 다음 값으로 한다.

- 기폭점과 외판 사이 거리
- incident/reflected peak pressure
- positive-phase impulse와 dynamic pressure
- 판재의 실제 두께, 잔존 두께, 항복강도 및 유효 면적
- 외판 파괴에 쓸 수 있는 폭발 에너지와 필요한 plate work

판재가 버티면 `SCORCH`, `DENT` 또는 `CRATER`만 남고 hot gas가 내부로 직접 들어가지 않는다. 내부에는 제한된 구조 충격, 후면 spall/파편 및 구획 피로만 전달된다. 판재가 실패하면 `EXTERNAL_BLAST_BLOWOUT`을 만들고, 그 위치·법선·실제 개구면적을 침수, 피해, 2D 및 3D가 함께 소비한다.

합성 대조 fixture에서는 같은 500 kg TNT-equivalent 접촉 폭발에 대해 6 mm급 손상 외판은 파열하고 200 mm급 RHA 판은 버텼다. 이 fixture는 분기와 에너지 보존을 검증하는 stress case이며 실제 함정별 장갑 인증값을 뜻하지 않는다.

## REV5 구현 범위

- RHA-equivalent 재료 정규화와 homogeneous/face-hardened naval armor solver를 활성화했다.
- 지연신관 최소 자극 profile을 `8 / 12 / 20 mm RHAe`로 분리했다.
- 두께만으로 신관이 작동하지 않도록 normal velocity, normal impulse, plate work, obliquity 및 탄체 생존 조건을 함께 검사한다.
- grazing hit에서 경사 경로가 길다는 이유만으로 신관이 자격을 얻지 못하게 했다.
- 비관통 결과를 `SCORCH / DENT / CRATER`, 관통 결과를 `PERFORATED`로 기록한다.
- 관통 또는 얇은 외판의 폭압 파열에만 direct gas path와 물리 구멍을 허용한다.
- 내부 기폭은 원래 관통 입구를 backblast로 확대하고, 반대편 pressure rupture와 case-fragment hole을 별도로 만든다.
- 외부 기폭 후 관통구로 유입된 고온가스는 보존된 thermal budget 안에서 실제 도달 구획에 재분배된다.
- 미사일, 로켓, 포탄은 같은 `BlastChargeSpec → BlastTrace → BlastDamagePacket` 경로를 사용한다.
- 모든 solved scar는 reset 전까지 유지되며 2D 상면·측면과 3D가 같은 집합을 표시한다.

## 검증 결과

### 내장·계약 검사

- inline JavaScript parse: PASS
- REV5 static contract: `18/18 PASS`
- REV5 armor/fuze diagnostics: `16/16 PASS`
- core selftest failure: `0`
- core blast diagnostics, generic fixture diagnostics, hard-budget diagnostics: PASS
- thin-skin external blowout / thick-RHA hold / blowout energy closure: PASS
- 8/12/20 mm threshold 경계와 grazing rejection: PASS
- missile/rocket/shell carrier equivalence: PASS
- console/page error: `0/0`

### 실제 Chromium

| 회귀 | 결과 |
|---|---:|
| REV5 Playwright | `3/3 PASS` |
| Kh-32 seed `481232`, 100 km | `92.78333333333333 s`, `NORMAL_HIT` |
| Kh-32 boundary mode | `EXTERNAL_DETONATION_THROUGH_ENTRY` |
| Kh-32 피해 | `41 modules / 15 compartments / 36 breaches` |
| Kh-32 hot-product 점화 | `5 candidates / 5 planned` |
| Kh-35U seed `481235`, 100 km | `345.81666666666666 s`, `NORMAL_HIT` |
| Kh-35U 피해 | `25 modules / 17 compartments / 64 breaches` |
| Kh-35U 점화 | `2 planned` |

Kh-32 한 발의 전방 연돌 명중에서는 SPY 네 면에 각각 약 `14–35` damage가 들어갔다. 별도 generic 함교 500 kg 회귀에서는 1발 뒤 네 면 모두 작동, 2발 뒤 전방 F1/F2 정지, 3발 뒤 네 면 모두 `100` damage로 정지했다.

세 번째 함교 폭발 뒤 solved scar는 `114`개였고 최초 scar 전체가 130 simulation seconds 뒤에도 남았다. 2D 상면·측면 drawn count는 모두 source scar `114`와 일치했다.

### 실제 WebGL 3D

로컬 Three.js를 CDN 요청에만 대체 route하고 실제 renderer 코드를 실행했다.

- renderer ready, runtime fault 없음
- Kh-32 blast trace/event `1/1`
- entry blowout `1`, exterior rupture `28`, fragment perforation `4`, internal tear `2`
- 외부 파괴구 `29/29`가 실제 geometry에 부착·절삭
- 내부 pressure cell `15`, portal `2`
- persistent internal tear `2/2`, authority 일치
- WIP12D residual presentation 유지

## 권위와 한계

- 계수는 `SIM_TUNED_RHA_EQUIVALENT_NORMALIZATION_NOT_CERTIFIED_FUZE_DATA`다.
- RHAe는 서로 다른 함정용 강재와 장갑재를 하나의 판정 축에 놓기 위한 정규화 값이며 실제 제조사 보증치가 아니다.
- full CFD, 수중 bubble pulse, hull whipping, 복합장갑 및 반응장갑은 범위 밖이다.
- 외부 고폭 파열은 “탄두가 크면 무조건 구멍”이 아니다. plate response가 실패할 때만 파괴구가 생긴다.
- 신관 profile의 8/12/20 mm는 최소 자극 분류이며 관통 보장 두께가 아니다.

## 반영 완료와 다음 단계

1. 완료: REV5 HTML, 문서, checksum 및 REV5 전용 테스트를 현재 WIP12E branch에 반영했다.
2. 완료: 원격 HTML 전체 blob을 다시 읽어 SHA-256과 크기가 일치함을 확인했다.
3. 완료: package/workflow를 REV5 전용 계약과 Playwright에 연결했다.
4. 완료: PR #30 Actions run #99의 전체 `30`개 job이 성공했다.
5. 완료: PR #30을 merge commit `c18a51433d767f56ccd1bb4ff30388dfe91505d3`로 `main`에 병합했다.
6. 캐시 혼동 방지를 위해 REV5 파일명을 유지했다. canonical `Aegis_SIM_v48_WIP12E.html` 별칭은 필요할 때 별도 변경으로 승격한다.

상세 설계는 `docs/WIP12E_COMPARTMENT_BLAST_IMPLEMENTATION.md`, 현재 판정은 `AEGIS_PLAN_STATUS_v48_WIP12E.md`를 따른다.

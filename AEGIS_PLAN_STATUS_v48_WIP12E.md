# AEGIS v48 WIP12E 상태

## 판정

`revision 2 구현 완료 + 격리 런타임 검사 완료 / 실제 브라우저·전체 회귀·원격 HTML 업로드 잔여`

WIP12E를 정식 완료로 선언하지 않는다. 현재 후보본은 범용 구획 폭발 authority와 소비자/VFX 연결에 더해 사용자 Kh-32 시험에서 확인된 부족한 화재, 잘못된 파괴구 위치, entry 미확대 및 fragment hole 누락을 교정했지만, 실제 브라우저 자동 회귀와 GitHub Actions 전체 회귀가 아직 필요하다.

## 기준과 브랜치

- WIP12D PR `#29`: merged
- `main` SHA: `97de0e1459e4f111e21b5bed163decc6ce782c32`
- 기준 HTML: `Aegis_SIM_v48_WIP12D.html`
- 기준 크기: `3,058,349 bytes`
- 기준 SHA-256: `8ae85b69e28e71e54137ede0fd6110bbfa358fea7b04c2a88446bf3d44f7a90c`
- 작업 브랜치: `feat/v48-wip12e-compartment-blast`
- 브랜치 시작 SHA: `97de0e1459e4f111e21b5bed163decc6ce782c32`
- 구현 후보: `Aegis_SIM_v48_WIP12E.html`
- 후보 크기: `3,171,578 bytes`
- 후보 SHA-256: `dd8ca1bf44f8b80e6b440f36e42c37ca41d747c9ce2ffd663791e6c0ab5f01af`

## 구현된 범위

- missile/rocket/shell 공용 `BlastChargeSpec`
- WIP12C 138-space 기반 immutable blast topology adapter
- bounded event-driven cell/portal propagation
- incident/reflected pressure, positive impulse, dynamic pressure, hot gas, fragment/spall 및 structural shock 분리
- 닫힌 door/bulkhead failure와 남은 pulse의 후속 전파
- 기존/신규 exterior opening을 통한 venting
- surface-load 기반 외판 rupture와 침수 opening 단일 적용
- 원래 projectile entry 좌표의 `BLAST_ENTRY_BLOWOUT` 확대와 동일 면 중복 rupture 억제
- source/portal 기준 국부 좌표의 반대편·주변 pressure rupture
- case-fragment plate work와 실제 `BLAST_FRAGMENT_PERFORATION`
- WIP12D residual crossing 및 WIP12E breach의 flood 독립 persistent 3D hole
- solved hole area를 cosmetic morphology가 다시 부풀리지 않는 시각 권위
- 대형 내부 폭발의 고온 생성물·가연물 기반 다구획 점화
- air-blast/structural/vent/thermal/residual/truncation energy ledger
- fragment perforation work/residual/closure ledger
- legacy/shadow/authority 명시 모드와 기본 authority 전환
- ASM과 WIP12A generic projectile 경로의 동일 solver 연결
- 구조, 장비, 승조원, VLS, 화재, 침수 소비자의 공유 trace 사용
- legacy scalar blast 이중 적용 차단
- WIP12D residual supplement의 no-blast-replay 유지
- fireball, shockwave, sea-surface column/ring/spray, authoritative vent jet
- 내부 전용 instanced cell shell/portal failure 표시
- DUD zero-state, event-id idempotence 및 combat RNG 격리

## 권위 경계

- `COMPARTMENT_BLAST_AUTHORITY`에서는 WIP12E packet만 primary blast 피해를 적용한다.
- WIP12B terminal event는 이미 적용된 WIP12E blast를 관찰만 한다.
- WIP12D는 macro residual의 제한된 기계 피해와 실제 외피 구멍만 보충한다.
- 렌더러는 immutable presentation data만 읽고 피해나 난수를 계산하지 않는다.
- 폭압 자체와 inert fragment/structural shock는 자동 발화원이 아니다.

## 로컬 검증 결과

| 검사 | 결과 |
|---|---:|
| WIP12E static checks | 31/31 PASS |
| isolated VM runtime groups | 11/11 PASS |
| 합계 | 42/42 PASS |
| core diagnostic | 16/16 PASS |
| fixture diagnostic | 17/17 PASS |
| authority probe | 4/4 PASS |
| idempotence probe | 4/4 PASS |
| hard-budget probe | 5/5 PASS |
| solved-damage visual adapter | 5/5 PASS |
| dynamic breach cap | 64/64 |
| portal event cap | 384/384 |
| solver 64회 평균 | 약 2.2 ms/impact, 실행별 소폭 변동 |
| combat RNG | unchanged |

실행 명령:

```bash
node --check tests/compartment-blast-wip12e.spec.js
node tests/compartment-blast-wip12e-contract.cjs
```

revision 2의 90 kg TNT-equivalent missile fixture에서는 `0.045 m²` 초기 entry가 같은 좌표에서 `8.16 m²` backblast opening으로 확대됐고, outward vent energy를 유지했다. 같은 사건에서 case-fragment hole 2개, 서로 다른 구획의 hot-product ignition 2개 및 air/fragment ledger closure `0`을 확인했다. 이는 공개 Kh-32 실측값이 아니라 회귀용 `SIM_TUNED` 증거다.

## 준비된 브라우저 회귀

`tests/compartment-blast-wip12e.spec.js`는 다음을 검사한다.

- UI boot와 core selftest
- 모든 generic fixture와 cap probe
- seed `481232` 100 km Kh-32 live hit
- WIP12D flight/geometry/residual golden
- one blast authority와 shared crew trace
- air/fragment energy closure, cap, rupture/flood dedupe
- 원래 impact 좌표의 single entry backblast와 확대 면적
- pressure/fragment/residual physical holes
- 2개 이상 hot-product fire cell
- VFX payload, same-seed exact, DUD zero-blast

## 실행하지 못한 검사

- 실제 Chromium/Chrome Playwright 실행
- WebGL 3D audit와 screenshot
- 전체 기존 Playwright suite
- GitHub Actions WIP12E job

환경에 브라우저 실행 파일이 없고, 허용된 네트워크에서 Playwright browser binary 다운로드가 차단되어 대체하지 못했다. 이 항목을 브라우저 검증 완료로 기록하지 않는다.

## 원격 반영 상태

- branch ref 생성/확인: 완료
- 소형 문서·테스트 commit: 이 상태 문서와 함께 반영
- `Aegis_SIM_v48_WIP12E.html`: 수동 업로드 필요
- `package.json`/workflow/README/프로젝트 지침의 WIP12E 활성화: HTML 업로드 뒤 반영

큰 HTML은 repository 규칙에 따라 API/base64로 우회 업로드하지 않는다.

## 완료 전 필수 작업

1. WIP12E HTML을 branch 루트에 수동 업로드한다.
2. 원격 HTML 크기와 SHA-256을 manifest와 대조한다.
3. package scripts와 Actions에 WIP12E contract/Playwright job을 추가한다.
4. README와 프로젝트 지침의 현재 기준을 WIP12E 후보로 갱신한다.
5. 실제 브라우저 및 전체 회귀를 실행한다.
6. console/page error 0, WIP12D golden 보존 및 3D audit 통과를 확인한다.
7. 그 뒤에만 이 문서의 판정을 `완료`로 변경한다.

## 관련 파일

- `docs/WIP12E_COMPARTMENT_BLAST_HANDOFF.md`
- `docs/WIP12E_COMPARTMENT_BLAST_IMPLEMENTATION.md`
- `tests/compartment-blast-wip12e-contract.cjs`
- `tests/compartment-blast-wip12e.spec.js`
- `WIP12E_SHA256SUMS.txt`

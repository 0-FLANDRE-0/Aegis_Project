# v48 WIP HARPOON D — 발사관 자동 선택 완료

- HTML `Aegis_SIM_v48_WIP_HARPOON_D.html`, **15,283,086 bytes**, SHA-256 `e92aff9c19a074aa98c3ceca236abaa14b2a674f8417419df7a08dbc248700a1`.
- main SHA `aeaf6981dc163f3ae3ed67884830bfffb4df50eab83adb381edceda73039e683`; 기준 C SHA `b3b4f637fdfe0973e3aec566f1577401055c44235d8ccef22084aeb6e04175e7`.
- main/준비 `harpoon-block1c-a`의 K commit `f51247496725aa8aadad69d5c8d3449c5bbc3a81`과 권한을 재확인했다. 새 HTML/support/PR/CI/병합은 미실행이다.

ARM → VLS의 하푼 관별 선택창을 자동 선택 표시로 바꿨다. 장전·손상·안전 gate를 통과한 관 중 관측 표적 예상 방향에 필요한 선회가 가장 작은 관을 선택한다. 선호 bank 소진/손상 시 대체 bank로 넘어가며 관 ID/슬롯/재고를 압축하지 않는다. 발사는 계속 수동이다. cooldown·UNKNOWN/FRIEND/NEUTRAL 보호·AUTO/SEMIAUTO 금지를 유지한다. 덮개가 열리는 동안 선택 관을 pin하고 실제 release gate 실패 시 다른 관으로 바꾸지 않고 취소한다.

C의 비행/INS/ARH/무DL CIC·RF·피해·모델/3.2초 booster/연기와 DDG 미설치를 보존했다. profile revision/module/저장 schema는 그대로다. 옛 selectedTubeId는 저장 호환으로 읽되 다음 요청은 자동 선택한다. C HTML/status/SHA·workflow와 manifest는 역사 보존하고 현재 root/지원/workflow는 D다.

## 직접 검사

동일 bytes **67/67 PASS**, seed `0x6d2b79f5`. 역사 C155/B133/A155/K284는 합산하지 않는다.

| Suite | 통과 |
|---|---:|
| static | 31/31 |
| selection | 24/24 |
| clock | 3/3 |
| native | 9/9 |

실제 ARM 버튼 8회로 8개 관 사용·소진 bank 전환·5520kg 제거, 반대 표적 방향의 반대 bank·손상 fallback/요청 관 취소·pending pin·저장/reset·권한·DDG를 확인했다. 1·8·16·64× 각128틱 full accumulator 결과 exact. native RAF/전체clock의 실제 모바일 버튼 두 번·열린 실제 두 관·draw/RESET·NO DL/UI fit를 확인했고 physics/geometry queue 수동 진행은0이다. core/page/native console·simulation/presentation 오류0. SwiftShader이고 FPS 주장은 없다.

## 범위와 인계

수정은 선택/UI/version에 한정한다. source 역패치/outer HTML/원본 asset byte 보존을 검사했고 C 전체155 회귀나 B 모델/후연 전체 검사를 D에서 반복한 것으로 쓰지 않는다. 현재 변경은 로컬 전달 완료이며 원격 PR/CI/병합 완료로 표시하지 않는다.

7.1에 따라 사용자 업로드 대상은 **D HTML 하나만**이다. 업로드 뒤 exact 대조 → 작은 support/문서/체크섬·K 기존 blob archive·D workflow → PR/CI를 진행한다. archive A/B/C의 큰 HTML은 remote 신규 업로드 대상이 아니고 K+작은 A/B/C 모듈로 exact 기준을 재생성한다. 다음 기능 단계는 업로드 인계 뒤 적 수상함 runtime/시나리오 확대다.

[상세](docs/harpoon/D/README.md), [근거](docs/harpoon/D/evidence/verification-summary.json), [업로드 인계](docs/harpoon/D/GITHUB_HANDOFF.md), [SHA](SHA256SUMS_v48_WIP_HARPOON_D.txt).

## 추가 장거리 검사 — 2026-10-04, 코드 수정 없음

[별도 보고서](docs/harpoon/long-range/D/REPORT.md)와 [raw 결과](docs/harpoon/long-range/D/evidence/findings-summary.json)를 추가했다. 원본 D HTML SHA는 같으며 종전 자동 관 선택67/67에 전체 장거리 PASS를 합산하지 않는다. 이번 요청은 별도 시험으로 완료했고 발견한 운용 제한은 미수정이다.

60km 정지/15kn은 정상 fire/release 뒤 약213초에 물리 접촉했다. 100·120·124km는 표적 예측 불확실성4km gate로 정상 발사가 차단된다. 이 gate만 제외한 명시 독립 비행에서 100·120km 양 표적과124km 정지 표적은 접촉했지만124km/15kn은 최근접 중심190.775m로 빗나갔고452.167초 연료 소진·508초 해면 충돌했다. 같은 위치/시간으로 실패를 재현했다.

synthetic external cue·한 seed·기존210m hulk·개방수역·60Hz missile/target/environment focused clock이다. 함상 장거리 radar detection/offboard targeting 구현·여러 seed 성공률·기동/ECM·장거리 전체 함상/native3D는 인증하지 않는다. ship tracks 삭제·launch memory 고정·무DL·고정 틱 전역RNG 변화0·오류0을 확인했다. 아직 **장거리 운용/최대거리 moving 종말 안정성은 검증 잔여**다. 다음은 적 수상함 기능 확대에 앞서 forecast uncertainty/search basket/발사 조건 일관성과 TRACK/COAST 종말 안정성을 수정하는 것이다.

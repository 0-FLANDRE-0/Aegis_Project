# Harpoon D 장거리 별도 시험 — 제한과 실패 확인

이전 D 인계의 실제 표적 검사는 8km였다. 이번에 동일 D 알고리즘으로 60·100·120·124km의 정지/15노트 횡단 표적을 별도 시험했다. **장거리 전체 통과로 판정하지 않는다.** 정상 발사 판정에서 100·120·124km가 차단되며, 발사 제한을 제외한 독립 비행에서는 124km 이동 표적이 빗나가는 실패를 재현했다. 이번 요청은 검증으로 처리했고 게임 코드·튜닝을 바꾸지 않았다.

기준 `Aegis_SIM_v48_WIP_HARPOON_D.html`, 15,283,086 bytes, SHA `e92aff9c19a074aa98c3ceca236abaa14b2a674f8417419df7a08dbc248700a1`, main SHA `aeaf6981dc163f3ae3ed67884830bfffb4df50eab83adb381edceda73039e683`. 원본 HTML, 기존 D ZIP과 C archive를 보존했다. 이번에 수정한 것은 검증 script/근거·상태 문서다. 종전 자동 관 선택의 67/67 기록에 이 시험을 모두 PASS로 합산하지 않는다.

## 방법과 범위

Chromium에서 실제 D embedded functions를 실행했다. offline page에 검증용 bridge만 추가하고 비행·INS·ARH·익명 RF scene·해면·210m/32.2m 물리 표적함·접촉/피해 functions는 수정하지 않았다. seed `0x6d2b79f5`, 초기 위치 표준편차50m·속도0.5m/s, 표적 방위0°/운동방향90°·0/15kn, 해면/기상 모델 유지·terrain diagnostic bypass의 개방수역 조건이다. 이 cue는 합성 외부 표적정보 fixture이고 함상 레이더가 100km 수상함을 실제 탐지한 것으로 표시하지 않는다. 게임의 offboard targeting UI/체계가 구현됐다는 뜻도 아니다.

정상 판정 시험은 기존 auto-selector/fire/gate와 실제 release를 거친다. 차단된 거리의 독립 비행 시험은 diagnostic closure에서 **발사 전 gate만 제외**하고 동일 release constructor로 탄체를 초기화한다. 실제 게임의 발사 가능성을 인증하지 않으며, 이 우회는 배포 HTML에 없다. 그 뒤 함상 tracks를 삭제하고 frozen launch memory를 계속 검증했다. 표적 truth를 INS 보정·시커 lock/관측에 주입하거나 강제 명중시키지 않았다. INS→물리 RF 기반 SEARCH/ACQUIRE/TRACK/COAST→선체 접촉을 검사했다.

60Hz 고정 간격으로 maritime environment·수상 표적 dynamics/flooding·Harpoon flight를 끝까지 실행했다. 전체 함상 subsystem·네이티브 RAF/3D·64× 전체 임무를 장거리에서 실행한 시험은 아니다. 표적은 기존 empty-container hulk이고, 기동/회피·ECM·다수 표적·전쟁환경·여러 seed의 명중률·모든 발사 방위는 미검증이다. 거리·제원과 결과의 연료/오차·시커 숫자는 게임의 SIM-TUNE이며 실장비 성능 인증값이 아니다.

## 실제 비행 결과

독립 비행 행은 정상 발사 제한을 통과한 결과와 구별해야 한다. 시간은 탄체 비행 시작 기준 초다.

| 거리 km | 표적 kn | 경로 | 결과 | 비행 s | 잔여 연료 kg | 실제 INS 오차 m |
|---|---:|---|---|---:|---:|---:|
| 60 | 0 | 정상 발사 판정 | 명중 | 212.717 | 58.664 | 24.748 |
| 60 | 15 | 정상 발사 판정 | 명중 | 212.800 | 58.644 | 24.779 |
| 100 | 0 | 발사 제한을 제외한 독립 비행 | 명중 | 351.117 | 24.756 | 49.679 |
| 100 | 15 | 발사 제한을 제외한 독립 비행 | 명중 | 351.250 | 24.724 | 49.736 |
| 120 | 0 | 발사 제한을 제외한 독립 비행 | 명중 | 420.333 | 7.798 | 64.895 |
| 120 | 15 | 발사 제한을 제외한 독립 비행 | 명중 | 420.467 | 7.766 | 64.962 |
| 124 | 0 | 발사 제한을 제외한 독립 비행 | 명중 | 434.167 | 4.409 | 68.158 |
| 124 | 15 | 발사 제한을 제외한 독립 비행 | 빗나감·해면 충돌 | 508.000 | 0.000 | 84.463 |

8가지 거리/속도 조합의 물리 비행 결과는 접촉7·빗나감1이며 성공확률로 해석하지 않는다. 실패 반복 시험도 같은 508.000초·최종 SI 위치로 재현됐다. 모든 비행에서 core·page·console 오류0, 함상 track0·launch memory 고정·CIC 무관측 위치 없음·ARH 자체 획득을 확인했다. 고정 틱 내부 전역RNG 변화 계측은 environment/target/Harpoon 모두0이다. 초기 임시 검사에서는 여러 page.evaluate batch 사이의 이벤트/RAF 구간에서 전역 RNG snapshot이 달라져 전체 불변 flag가 false였으므로 그 범위를 수정했다. 최종 주 근거는 `final-gated.json`/`final-flight-only.json`이고, 재현 raw `edge-replay.json`의 옛 범위 flag는 그대로 보존한다. 해당 raw의 tick별 probe0과 실제 위치/시간 재현을 사용한다. batch 사이 RNG 변화의 정확한 callback 원인은 이번 범위에서 추적하지 않았으므로 그 구간 전체의 RNG 불변을 주장하지 않는다.

## 발견한 발사 제한

`INS_PREDICTION_BASKET_INSUFFICIENT`는 미사일 자체 INS의 실제 오차가 아니라 **발사 전 표적 위치/속도·기동의 장기 예측 불확실성**이다. 기본 4km basket 한도와 `(t² × 0.04)²` 항 때문에 초기 cue가 좋아도 장거리에서 차단된다.

| 입력 거리 | 예측 2σ 범위 | 현 발사 판정 |
|---|---:|---|
| 60km | 약2042m | 허용 |
| 100km | 약7093m | 불확실성 한도 초과 |
| 120km | 약10770m | 불확실성 한도 초과 |
| 124km | 약11598m | 불확실성 한도 초과 |
| 125km | 거리 한도 초과 | `SURFACE_TARGET_OUTSIDE_WEAPON_ENVELOPE` |

공분산을 0으로 가정해도 해당 기동 예측 항만으로 약 **78.597km**에서 4km 한도에 도달한다. 따라서 profile의 최대124km와 현재 허용되는 사격 해법 범위를 같다고 설명하면 안 된다. 한도를 무조건 늘리거나 무DL 상태에서 표적 실제 위치로 임무를 갱신하는 변경은 이번 시험에 넣지 않았다.

## 최대거리 이동 표적 실패

124km/15kn에서 SEARCH386.15초 → ACQUIRE386.23초 → TRACK386.43초를 확인했다. 430.73초/약1049m 남았을 때 COAST로 들어가며 추정 target velocity가 불안정해졌다. 최근접 중심 거리 **190.775m**/434.233초에서 실제 접촉하지 못했다. 재획득·상실·선회 이후 452.167초에 연료가 소진되고 508초에 해면 충돌했다. 공통 피해 packet/실제 target impact는0이다. 연료 소진이 첫 빗나감의 직접 원인이었다고 단정하지 않는다. 정확한 RF return 선택/velocity 추정/COAST guidance 원인은 다음 수정 전 근거리 고해상도 trace로 분리할 필요가 있다.

다음 우선 작업은 장거리 **표적 예측 불확실성·탐색 영역/발사 허용의 일관성**, 그리고 **moving-target TRACK/COAST 종말 안정성**이다. 표적 true ID/강제 lock·강제 명중이나 발사 후 DL 보정을 만들어 해결하지 않는다. 60~120km 명중 fixture가 이것들을 완성으로 만들지는 않는다.

## 근거와 재실행

- [합계/범위](evidence/findings-summary.json)
- [정상 발사 판정6건](evidence/final-gated.json)
- [독립 비행6건](evidence/final-flight-only.json)
- [거리·불확실성 gate4건](evidence/gate-probe.json)
- [124km 이동 실패 재현](evidence/edge-replay.json)
- [별도 tester](verify_range.py)

기존 repo/browser helper와 Python Playwright·Chromium이 필요하다. bundled Chromium만 설치했다면 `AEGIS_CHROMIUM_EXECUTABLE`에 그 executable path를 지정한다. original D HTML을 입력하고 결과 폴더는 repo 밖이나 artifacts 아래에 둔다.

```bash
python docs/harpoon/long-range/D/verify_range.py Aegis_SIM_v48_WIP_HARPOON_D.html artifacts/long-range/gated
python docs/harpoon/long-range/D/verify_range.py Aegis_SIM_v48_WIP_HARPOON_D.html artifacts/long-range/flight --ranges 100,120,124 --flight-only
python docs/harpoon/long-range/D/verify_range.py Aegis_SIM_v48_WIP_HARPOON_D.html artifacts/long-range/replay --ranges 124 --speeds 15 --flight-only
```

정상6+독립6+gate4+실패재현1로17개 raw scenario를 기록했다. tester의 exit0은 crash 없이 진단 실행을 마쳤다는 뜻이며 모든 거리의 정상 발사·명중 PASS라는 뜻이 아니다. source+fixture bridge hash와 source reversal을 기록했으며 새 remote upload/PR/CI/병합은 실행하지 않았다. 이전 D ZIP은 당시 자동 관 선택 인계로 그대로이고, 별도 장거리 지원 ZIP으로 새 근거/작은 문서만 추가한다.

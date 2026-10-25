# AEGIS PLAN STATUS — v48_WIP_FUZE_ZEM_A

별도 시험 브랜치 `fuze-zem-a`, 기준 `reg-k-env-d@058273c1f4b91c0d0c595e5399aaa967aa443f1c`. 최종 후보 DZT. 정식 v48 승격/main 병합 없음.

- HTML: `Aegis_SIM_v48_WIP_FUZE_ZEM_A.html` / 18,452,900 bytes / SHA-256 `edc159fa347d721d61d80228e2512665f22da0adb4f02fdf4e2dbe82789e0c9c`.
- [상세 보고서](docs/missile/fuze-zem/A/REPORT.md), [모델·SIM_TUNED 상수](docs/missile/fuze-zem/A/MODEL.md), [검증](docs/missile/fuze-zem/A/evidence/verification.json), [재현](docs/missile/fuze-zem/A/REPRODUCE.md).
- 완료: 결정론적 SAM acquisition, swept 시간 적분/빔/거리/RCS/속도/클러터 품질. 기존 처리 지연/CPA/파편 피해 분리 유지. F 재추첨안은16손실로 미승인·게임 미포함.
- 완료: ZEM 보정 부호(+), 관측 TRACK miss 종료와 복귀/대체지원/공분산 guard. 세 수정 독립검증 후 결합.
- 180발 공통 비교: D/Z/T/DZT 신규 실패0. 최종159효과/159lethal vs BASE138효과/137lethal. F16손실 회복/20회복 유지.
- 기존 회귀420+UI88, release300발×2, 자연 RF, WebGL8발×2, private/실제함수8조건 오차0, 48쌍 결정성, 120초 무표적·지정전투 hash 동일 PASS.
- 유지: B4/Kappa/TGO90, PN/APN 이득, 추진/항력/질량/최대G/사거리/배터리/시커, CPA/처리 지연/파편/Pk, 전역RNG/항법/센서 잡음, UI/저장.
- 조사만: 5km/20km 최초CPA 미스(ER338→271m, SM-6 317→223m), 과도한 raw 제어요구, post-pass phase 역전. PN/엔진/G 상향 없음.
- 남음: phase hysteresis 등 별도 설계 결정, 자연RF의 보수적 재접근 guard로 LOW_SPEED까지 남는 일부 사례, 전체 사거리 재측정(이번 미실행), 실제 폰 GPU 확인.
- 내장 ENV_D120행은 HISTORICAL, status match=false/재계산 필요. 새 링/발사판정 연결 없음.
- archive/v48/WIP_ENV_D 전달7파일 byte/blob 동일. 원격 전체 readback 영수증은 `docs/missile/fuze-zem/A/remote-publication.json`에 발행 후 추가한다.

게임 HTML에는 새 TEST_ONLY fixture/계측 wrapper가 없다. diff·신호/탐지/기폭·처리 지연 로그·A/B·그래프는 별도 REPORT ZIP에 있으며 실행 HTML은 HTML ZIP 하나로 제공한다.

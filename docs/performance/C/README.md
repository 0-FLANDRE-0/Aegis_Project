# 최적화 3단계 PERF_C

PERF_B final `d26e94194d52f0040f4d3d388b9bbce49460b440`를 기준으로 SPY 공통 대공 관측의 NIS 연관 비용을 줄인다. 등록 HTML/status/SHA/workflow 네 파일은 `archive/v48/WIP_PERF_B/`에 동일 bytes/blob으로 보존한다.

`trackRadarAssociationNisV31`만 새 파생 kernel을 사용한다. 트랙 객체를 WeakMap 키로 사용하며 마지막 kernel 하나만 보유한다. 상태6개·공분산36개·센서 원점/속도6개 전부 `Object.is`로 정확히 같은 경우에만 prediction/Jacobian/공분산 투영을 재사용한다. 배열 참조만 비교하지 않으므로 in-place EKF·수상 제약 변화도 즉시 반영한다. 측정 range/az/el/radial은 매번 현재값으로 innovation을 계산한다. 역행렬은 기존 floor/default/deg 변환을 적용한 오차4개까지 같을 때만 재사용한다. 함수 연산·행렬곱·NIS 합산 순서는 그대로다.

canonical prediction/Jacobian, EKF 예측/실제 갱신, 수상 연관, 관측 생성/센서 난수, focused/global 배정·tie order·cross-domain 게이트·Kalman 갱신 순서, 실제 발사 guard를 변경하지 않는다. 이 cache는 runtime/snapshot에 저장되지 않으며 다른 트랙 객체/함정에서 공유하지 않는다. 별도 시간/틱 기반 유효기간이나 반올림이 없다. reset/import 후 새 객체는 새 cache이며 같은 객체도 모든 현재 수치가 exact일 때만 재사용한다. GC가 제거된 트랙의 cache를 회수한다.

`build.py`는 함수 offset/SHA를 pin하고 packed main13만 교체한다. 모델/assets0~12·stablev48은 보존한다. `verify_static.py`는 full packing/syntax/scope와 native 갱신·배정·실제 발사/기존 PERF_A/B source 보존을 검사한다. `verify_radar.py`와 `radar-equivalence.cjs`는 native 함수의 differential/input mutation/gate boundary 사례와 실제 두 함종 core를 검사한다. 제어된 VM 의존성은 자연 탐지나 교전 성능 인증이 아니다.

나머지 browser/clock/방어/EW/공유/AI/피해/저장/UI 회귀도 최종 원본에 직접 실행한다. SHA·집계·동일 원본 증거는 `evidence/verification-summary.json`, 비교 성능 조건과 모든 증가/감소는 `PERFORMANCE.md`다. 호스트 CPU 처리시간을 휴대폰/실제 GPU FPS로 표현하지 않는다. Actions는 수동 workflow만 준비하고 dispatch하지 않는다. §7.1 승인으로 full original을 작업 branch에 직접 upload/readback한다.

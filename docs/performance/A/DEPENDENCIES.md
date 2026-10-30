# 다음 최적화 순서

PERF_A는 이전 read-only H4A 감사에서 확인한 반복 부품 scan·unsupported-band pod 계산·Kh-32 중복 canvas를 줄인다. 헬기/초수평선 탐지와 사용자 지정 RGM-109E Block Va는 최적화 작업 다음으로 유지한다.

1. **교전 판단·SPG-62 계산**: planner의 같은 tick·같은 owner/자세·같은 후보에 대한 반복 계산과 임시 객체를 줄인다. 센서·사통·피해가 바뀌면 무효화하고 실제 발사 검사는 계속 최신 상태를 읽는다. 판단/발사 결과와 RNG를 exact 비교한다.
2. **SPY 데이터 연관**: 반복 covariance 전처리·큰 후보 행렬과 할당을 감사한다. 기존 유효성/NIS gate·배정 순서·tentative/confirmed·진짜 관측 기준을 보존한다.
3. **피격 순간의 지연**: CG envelope cross-section의 고빈도 정렬/convex 계산을 별도 재현한다. 접촉 위치/진입 순서/관통·피해를 바꾸는 임의 좌표 반올림 대신 정확한 재사용·bounded 계산을 검증한다.
4. **3D·효과와 최종 재측정**: 기존 LOD·smoke pool/batching·RF scene cache를 활용하고, 실제 카메라에 보이는 다수 탄체/잔해/효과의 CPU·draw/resource 비용을 따로 측정한다. geometry 공유/instancing은 동적 재질·geometry disposal 소유권을 확인한 후 진행한다.

이 순서는 감사 근거에 따른 계획이다. 이후 실제 profile 결과가 우선순위를 바꿀 수 있다. fixed-step 주기를 낮추거나 탐지/방어 기능을 생략하는 방식은 사용하지 않는다. 소프트웨어 GPU 호스트 결과를 사용자 휴대폰 FPS로 표현하지 않는다.

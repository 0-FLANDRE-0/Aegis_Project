# 진행 상태 — 최종 보고서 아님

물리/정합 측정 빌드 SHA-256: `925178b5b06bcd81304f6b98da4436fda4fd85eaf7ea8de3813a981981f0da71`. MAIN SHA-256: `b0a95a0e880f79bda5950beafe1f805f91b127e49d60484a90bffa8f5751aacc`. 최종960회·거리1440시도는 이 빌드에서 새로 실행 중이다. 이전v1 및 입력캐시 보완 전v2의 미완료 행렬을 최종 통계로 섞지 않는다.

관측/KF공분산/함포 trunnion·속도/환경의 값 snapshot을 cache key와 함께 비교한다. 같은 틱의 입력 변경에도 continuation solve를 다시 실행한다. 실제 native solver를 이용한 캐시 검증은 1,1,2,3,4,5,6회 호출로 통과했고 전역RNG 변화0이다. 파편 밀도는 몸체 R²·4πsin20°로 정규화한다. 함수·상수 지문을 측정 시작 시 고정하고 브라우저에서 실행된 함수의 toString 해시를 확인한다.

281보호 함수/ENV_D120행/원본피해·SAM·RF/EKF·저장 계약 byte동일. 승인 범위 변경을 제거한 전체main은4c519 원문과 byte동일. 단계별 정합/산포/대공창 검증을 끝냈다. 최종물리18건·빠른거절12000조건 통과. 원래 회귀와 이미 승인된 기대값을 구별해 원시 실패도 보존한다. 계수·기대값·피해RNG/Pk를 결과에 맞추지 않는다.

실행: run_g7.py(3 native browser workers), run_v2_checks.py(거리→native trace→OFF/ON쌍), run_regression.py(OFF/ON 기존 회귀), 이후 run_gun_regression.py. 완주 후 REPORT.md/체크섬/ZIP/push/readback/PR까지 진행한다. main 병합·release/tag는 하지 않는다.

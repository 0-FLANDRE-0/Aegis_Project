# TRACK-B 안정화 R3 — 알고리즘 검증과 전투 안정성은 별도

**승인되지 않은 중간 후보. TRACK-B 완료본이 아니다.**

R2의 확정 하한이 0인 완전 매칭 성분에서 행·열 모두 16 이하일 때 기존 정확 alternative-forbid 경로를 추가 실행한다. 원 NIS·δ=1·dummy·native winner·S 증거는 유지한다. R2가 이미 확정한 결과는 보존한다. 잔여 성분 입력은 필요한 네 필드만 복사하여 알려지지 않은 필드를 읽지 않는다. `BUILD.json`, `MODULE_SCOPE.json`, `NATIVE_SUMMARY.json`, `PROOF_COST_PLAN.md`에 범위·실행 근거가 있다.

- 새 순수 검사 28/28, 원 정책 검사 39/39 및 실제 native 검증은 통과했다.
- 원 B strict 검사 46/47, 원 R2 잔여 검사 14/15의 정책 확장 차이는 실패 그대로 보존했다. 기존 기대값은 변경하지 않았다.
- 실제 18개 큰 그래프 중 3개의 불필요한 35회 pair 보류를 해소했다. 이는 35개 고유 표적이라는 뜻이 아니다. 기존 R2 수용 손실과 해당 자료에서 NIS-only 정확 기준 밖 신규 수용은 0이었다.
- 13기 자연 전투 ACTIVE는 90초에 초기 ASM 4기가 살아 있어 종결되지 않았다. 자함 legacy HP 0, 초기 물리 결과와 모듈 손상은 별도 보고에 보존했다. 연관 함수 통과를 전투 통과로 처리하지 않는다.
- 계측 SHADOW는 기존 B 실제 상태와 동일했다. 다른 파일의 재획득 작업에서 정상 관측을 받은 firm 파일이 `reacquiring=true`로 바뀌는 작업 소유권 오류를 실제로 확인했다. R3는 이를 수정하지 않았다. `evidence/battle-shadow-control/OWNERSHIP_PROOF.json` 및 `REACQUIRING_LINEAGE_REVIEW.md` 참조.

R4는 이 소유권 전달만 별도로 수정하는 후속 후보다. R3 소스·HTML·실패 및 미실행 자료를 보존한다. R4 검증 결과를 R3에 소급하지 않는다. R3 전체 17job 회귀와 독점 비용 측정은 실행하지 않았으며, 계획 파일의 존재를 통과로 간주하지 않는다. C55·SPQ AIR는 여전히 SHADOW-only다. main·기존 기준 브랜치·기대값·센서/무장/피해 물리 계수는 변경하지 않았다.

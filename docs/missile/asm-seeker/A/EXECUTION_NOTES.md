# 실행 메모

- 첫 60전투 실행기는 Chromium 하나를 여러 페이지에 재사용했고 5개 조건 뒤 탭이 메모리 부족으로 종료됐다. 제품 fault나 pageerror가 발생한 실행은 아니며, 완료된 5건은 보존했다.
- 재개 실행기는 조건마다 Chromium을 닫아 renderer 메모리를 회수한다. 같은 제품 SHA, 같은 frozen case, 같은 fixed-tick helper와 판정을 사용한다.
- 첫 재개 시 임시 진단 저장소가 `/dev/shm`에 Git 객체 약 4.5GB를 보유해 페이지 시작 전에 인프라 종료가 한 번 더 발생했다. 임시 객체 저장소만 제거한 뒤 재개했다. 제품·시험 입력·완료 결과는 바꾸지 않았다.
- 최종 `S3_BATTLE_RESULTS.json`에는 `QUALIFYING_COMPLETED_BATTLE`만 포함한다. 인프라 미완료 attempt를 PASS나 제품 실패로 세지 않는다.

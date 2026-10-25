# AEGIS v48 WIP NEAR_VERTICAL_PATH_FIX_A 상태

- 기준: `arh-measurement-fix-a@759fcd94bfa1081b268bfff9967f0f97088b7078`
- 최종 HTML: `Aegis_SIM_v48_WIP_NEAR_VERTICAL_PATH_FIX_A.html`
- 크기: `18,453,628 bytes`
- SHA-256: `eb1f5cebbfe991732b2855df625030b0691ff7cdd8047e9a01cc2711010b6e5f`
- 변경: `_wip79KappaPipState`의 ±60° 목표 경로각 정책 해제 + 재현된 1m 미만 수평 정규화/중첩 수치 계약 수정
- 근수직: 분리 fixture 0/5→5/5, 실제 제품 RF 경로 0/5→5/5
- 장거리 ARH: 240km 10/10 보존, release 300 성공→실패 0
- 회귀: 공통180·자연RF28 신규 실패 0, UI88/88, 도메인414/420(기존6건), 고정tick·smoke·동등성 PASS
- 미실행: 전체 ENV_D 재측정
- main 병합/release/tag: 없음

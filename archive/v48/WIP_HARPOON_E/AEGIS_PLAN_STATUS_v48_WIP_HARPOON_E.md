# v48 WIP HARPOON E — 경유점 발사와 통과 후 ARH 완료

- HTML `Aegis_SIM_v48_WIP_HARPOON_E.html`, **15,285,590 bytes**, SHA-256 `ad68f7a5e37ac066d8f3a70db0fc2aaa7e2611047112d4053c4380b94db8d842`.
- main SHA `11cf8d757821b8601da5a3a50153666e48524ea31a33de1a88d7a11a72794067`. 기준 D SHA `e92aff9c19a074aa98c3ceca236abaa14b2a674f8417419df7a08dbc248700a1`.
- 업로드 commit `a96053ba1dc56389822c17c92a632f21fcc446b2`는 K main `f51247496725aa8aadad69d5c8d3449c5bbc3a81`의 직계 자식이며 E HTML 하나를 추가했다. 원격 bytes/SHA/Git blob은 전달본과 일치하고 업로드 무결성 Actions도 통과했다. 이 revision은 지원 파일과 전체 E workflow를 포함한다. 전체 CI 및 병합 상태는 [PR #44](https://github.com/0-FLANDRE-0/Aegis_Project/pull/44)의 현재 기록을 따른다.

ARM → VLS의 HARPOON FIRE 아래 웨이포인트 지정/해제 버튼을 추가했다. 지도 탭으로 최대8점, 해제는 초안 삭제와 AIM cursor 복귀, drag/pinch는 추가0. 입력은 NAV 항로와 별도다. 마지막 점은 탐색 시작이며 마지막 leg 전방8km 중심/반경4km 검색을 계획한다. 경유점 없는 기존 관측 track INS shot은 유지하고 경유점 shot은 수동 고정 좌표 검색 계획이다. 보호 수상 track/자동교전 금지·DDG 미설치를 유지한다.

자동 관 선택 후 도어/pending에 immutable 경로를 pin한다. 실제 release 안전/권한/재고/손상을 다시 검사하고 성공할 때만 초안·edit를 지운다. 실패는 초안 보존/탄약 감소0. 다음 탄 경로는 앞선 탄을 바꾸지 않는다. INS로 중간 점 capture/최종 평면 통과를 판정하며 마지막 점 전 ARH OFF, 통과 후 SEARCH/ACQUIRE/TRACK/COAST다. DL0·측정 파일 기반 CIC FRIEND·블라인드 위치 없음/무telemetry를 보존했다.

SIM-TUNE 총 경로 +8km search +2km turn reserve ≤140km, fuel110kg/0.225kg/s, 점 간격≥2km. 공개124/약140 수치는 별도다. measured vertical extent≥3.5m·Doppler spread≤2.5m/s로 false echo association을 줄였다. 작은 선박/거친 해면 감도 저하 가능성을 명시한다. 실제 RF/LOS/짐벌/알파베타/물리 피해·3.2초 booster/nozzle/발사관 asset/renderer는 보존했다.

CG E_1/module RGM84D_BLOCK1C_E1(weapon revision HARPOON_E1), inventory A1 유지/C·B·A·G·D legacy 명시호환. route/비행은 transient/reset/import clear; capability deferred로 표시한다. D HTML/status/SHA와 D workflow는 역사 보존하고 stable v48은 unchanged다.

## 동일 최종 bytes 직접 검사

**178/178 PASS**, 역사 A/B/C/D/K 검사 합산0.

| Suite | 통과 |
|---|---:|
| static | 32/32 |
| guidance | 45/45 |
| selection | 24/24 |
| routes | 26/26 |
| knowledge | 22/22 |
| clock | 4/4 |
| range | 14/14 |
| native | 11/11 |

range의 120/124/130km×0/15kt **6/6 물리 접촉**, empty-water TRACK/강제 명중0. 단일 seed·210m hulk·terrain bypass/open sea, focused60Hz actual weather/target/ordnance이며 전체 함정/RAF 장거리·일반 명중률·최대140km 인증은 아니다. 초기 필터 전 접촉2/miss4는 별도 evidence로 보존한다. track-only 장거리 prediction basket 제한은 그대로다.

clock 1/8/16/64× 각3072 full ticks exact. 실제 CIC/마우스/두 손가락 입력·8관 재고/권한/손상·경로탄 익명 관측/EMCON·저장/reset/DDG 확인. native640×480 실제2경로/2발사·전체clock/RAF·정확 관 덮개/부스터·draw/RESET/UI fit를 확인했고 수동 physics/geometryqueue0. core/page/console·runtime/presentation faults0, SwiftShader/FPS 주장0.

[상세](docs/harpoon/E/README.md), [전달 전 검사 집계](docs/harpoon/E/evidence/verification-summary.json), [원격 인계](docs/harpoon/E/GITHUB_HANDOFF.md), [업로드 검증 기록](docs/harpoon/E/evidence/remote-publication.json), [SHA](SHA256SUMS_v48_WIP_HARPOON_E.txt). 업로드 E HTML은 수정하지 않았다. 전달 전 evidence와 ZIP은 당시 기록으로 보존하며, 현재 지원 manifest는 게시 문서를 반영한다. 전체 CI 결과는 PR의 해당 head Actions를 기준으로 한다.

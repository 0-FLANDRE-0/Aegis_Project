# AEGIS v48 WIP SOV_A 상태

기준: HELI_F2 `570e5a381fbd440852104905280fb7ffd68b1f66`. 작업 브랜치: `sovremenny-hull-a`.

**SOV_A 소프트웨어 구현·검증 완료 — 157/157 PASS, 6 suites, 페이지 오류 0.** 실제 폰 GPU의 FPS는 미측정이다.

- HTML: `Aegis_SIM_v48_WIP_SOV_A.html`
- 크기: **17,998,448 bytes**. HELI_F2 대비 **1,898,502 bytes 증가(약 11.8%)**.
- SHA-256: `1e2125e49ae0720d45f2457474753ed948324241aecf69120f5c7694ea733b28`
- [출처·운용·설계](docs/sovremenny/A/README.md), [구현 전 차이 보고](docs/sovremenny/A/CONFLICTS.md), [최종 검사](docs/sovremenny/A/evidence/verification-summary.json), [ISAR 전체 표](docs/sovremenny/A/evidence/isar-table.tsv).

## 완료

- 불변 `SOVREMENNY_956` 프로파일. 적/중립 NPC 생성·동시 배치, FLEET NAV. 자함/아군 선택·전투/네트워크 명령 차단.
- 센서 모델은 비설치 호환 형태의 수치 0. 활성 탐지/ESM/방사/공격 실행 0. VLS/함포/CIWS/RAM/하푼/SRBOC/Nulka 재고 0. 원본 장착 정보는 비활성으로 보존.
- 뷰어→sim `(x,z,y)`, 원본 수선=sim Z0. 156.5m / 공개 형폭 17.2m / 만재 7,940t / 32kt. 마스트 29.84874m를 APS와 RF에 적용.
- 오프라인 선체 단면·105개 정적 외피 그룹(정지 가동부 메시 70 포함)·133개 피해 박스·4,992개 부력 열. 렌더→물리 피드백 없음. 공통 해석기·증기기관/고정피치 응답·파도 외력·손상에 따른 추진/전력 저하.
- 24개 침수 부모 + 69개 연결 기능 공간. 보일러 4/기관 전후/발전기 4/빈 탄약고/지휘·함교/격납·거주·의무·보급. 실제 수밀 도면이 아닌 SIM_TUNED.
- 소련식 도색·원본 48,925 삼각형/81배치·정지 계층·원작 표기. 공통 해상 효과·구획/승조원·파공/변형/그을음·폐기. 변형 후 도색 속성 유지.
- 지속 손상·화재·물/파공·안정성 누적·수지·흉터를 저장/복원. 잘못된 확장은 변이 없이 거부. 기존 DDG/CG 저장/교전 정책 유지.
- ISAR 정보 자료에 Sovremenny급 추가. 분류기는 측정 특징만 사용하며 identity 자동 변경 없음.

## 대표 결과

| 검사 | 결과 |
|---|---|
| 만재 수선 | 7,940,000kg, 초기 draft 약 0m. 메시 침수 체적 7,623.340953m³ × 유효 면적 1.016134725 [SIM_TUNED] |
| 20kt 도달 | DDG 97.85s / SOV 135.42s |
| 90% 명령 속력 | DDG 173.07s / SOV 214.47s (명령 31/32kt) |
| SOV 600초 속력 | 31.9979kt |
| SOV 선회 | 30° 명령 후 반경 약 415.9m, 속력 27.48kt [SIM_TUNED] |
| 실제 OTH 흐름 | 적 SOV 30km, CG H1 실제 출격·50m, LONG/PERI 탐지→Hawklink→EMCON 수동 하푼→HIT |
| 실제 접촉 | 288.57m/s, 폭약 97.5kg, FUZE_AT_CONTACT. 발사 후 갱신 없음 |
| 침수/침몰 스트레스 | 수선 아래 −1.2m의 통제 접촉 4회 + 저장 검사 후 수밀 격리 상실. 391.0s에 LOST, 물 11731.3m³ |
| 저장 | 손상/화재/침수량/자세/표면 기록 보존, malformed 값 거부 원자성 통과 |
| 동요/시간 | 잔잔/0.9m/3m 해상 동요 확인. 동일 640 fixed ticks에서 1/8/16/64× 일치 |
| Burke→SOV 오분류 | 2.40% (54조건 × 64회) |
| SOV→Burke 오분류 | 4.89% (54조건 × 64회) |
| 기존 회귀 | DDG/CG 각각 idle/raid/damaged의 센서/교전/EW/동역학/난수 비교 통과 |

침수 스트레스는 정상 수면 위 하푼 비행과 별개다. 수밀 경계를 유지한 피격에서는 잔여 부력으로 버틸 수 있다. 공통 침몰 기준을 바꾸어 결과를 강제하지 않았다. ISAR 오분류율은 합성 측정 진단이며 실제 레이더 성능이 아니다.

## 렌더 비용과 한계

- 추가 원본: **48,925 삼각형 / 81 draw calls**. meta의 52,397 대신 실제 인덱스를 사용.
- 속성/인덱스 추정 2,396,581bytes, 디코딩 RGBA 텍스처 추정 15,466,496bytes/인스턴스. 드라이버 전체 메모리 측정값은 아니다.
- 실제 Chromium 소프트웨어 WebGL, LOW, 동일 카메라에서 숨김/표시를 교대하며 `gl.finish`까지 측정. CSS viewport [640, 480], drawing buffer [640, 480].
- 장치: `ANGLE (Google, Vulkan 1.3.0 (SwiftShader Device (Subzero) (0x0000C0DE)), SwiftShader driver)`. **실폰 FPS로 환산하지 않는다.** 모바일 viewport UI/overflow/3D와 실제 GPU 성능은 구분한다.
- 외피는 정적 단면/볼록 근사. 내부 배치·재질·RCS·CG/GM·기관/동요 응답은 SIM_TUNED이며 실제 도면/인증 성능을 주장하지 않는다.
- 작전 저장의 기존 경로·보수반 명령·강체 각속도·전투 transient 재구성 정책을 유지한다. 유체 캐시는 재생성되므로 수위의 mm 차이가 있을 수 있으나 저장 물의 양과 자세는 보존한다.

## 반영

HELI_F2의 HTML·상태·SHA·수동 워크플로 네 파일을 [같은 bytes/blob으로 보관](docs/sovremenny/A/evidence/archive-preservation.json)한다. 과거 소스/자산/stable을 보존한다. GitHub Actions는 실행하지 않으며 main/기존 브랜치를 병합하거나 새 PR을 만들지 않는다. 업로드 후 commit에 고정한 원격 원본/지원 파일을 다시 읽어 크기·SHA-256·Git blob을 대조한다. 원격 결과는 `docs/sovremenny/A/remote-publication.json`에 기록한다.

레이더/사통·모스킷/우라간/AK-130/AK-630/RBU/어뢰·EW·Ka-27·자함 선택은 다음 범위다.

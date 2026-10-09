# RGM-84D 공개 근거와 SIM-TUNE

2026-10-04에 공개 자료와 사용자 제공 모델을 대조했다. 이 표의 제원은 공개 자료의 주장이고, 시커·공력·오차·신관 등 구현 보정값은 실제 비공개 장비 성능의 재현값이 아니다.

| 항목 | 적용 | 근거와 제한 |
|---|---|---|
| 형식 | RGM-84D Block 1C | [Designation Systems](https://www.designation-systems.net/dusrm/m-84.html)의 1985년 Block 1C 설명. 사용자가 선택한 형식이며 CG-52 퇴역 직전 실제 적재 block은 확인하지 못했다. |
| 길이·직경·날개폭 | 부스터 포함 4.63m, 본체 3.84m, 직경 0.343m, 날개폭 0.914m | 같은 자료의 형식별 치수. AGM/RGM 길이를 혼용하지 않는다. |
| 질량 | 발사 690kg, 부스터 없는 본체 540kg | 같은 자료의 형식별 중량. 연료 배분은 별도 SIM-TUNE. |
| 속도 | 공개 명목 Mach 0.85, 구현 목표 289m/s | Mach는 대기 조건에 따라 변한다. 289m/s·공력 보정은 SIM-TUNE이며 실제 적분된 속도는 고정값이 아니다. |
| 사거리 | 발사 gate 상한 124km, 대안 추정 140km 기록 | [CSIS](https://missilethreat.csis.org/missile/harpoon/) Block IC 124km, Designation Systems의 RGM-84D 약 140km. AGM-D 220km와 혼동하지 않는다. 센서 관측 품질·예측 공분산 조건 때문에 상한 안에서도 발사가 거부될 수 있다. |
| 엔진·부스터 | 최대 약 3kN 터보제트, 53kN 부스터 2.9초 | Designation Systems의 J402와 표면 발사 booster 항목. 대기·스로틀·추력 곡선·90kg 추진제/60kg 분리 중량은 SIM-TUNE. |
| 유도 | 사전 입력 INS, 레이더 고도계, 종말 능동 RF | [FAS](https://man.fas.org/dod-101/sys/smart/agm-84.htm) 및 Designation Systems의 SWG-1A/발사 전 프로그램·순항·종말 설명. 이 단계는 데이터 링크·조명 없이 발사 시 저장된 표적 운동을 전파한다. 표적함의 실제 현재 위치를 유도 입력으로 읽지 않는다. |
| 탄두 | assembly 221kg, explosive fill 약 97.5kg | CSIS/Designation Systems의 전체 탄두 중량과 FAS의 215lb explosive. 221kg 전부를 TNT로 쓰지 않는다. TNT factor 1.1·탄두 구조 123.5kg·관통 재질은 SIM-TUNE. |
| 종말 방식 | 충격 지연 신관, sea-skimming | FAS의 impact delay와 공개 sea-skimming 설명. pop-up 선택은 이 단계에서 제공하지 않는다. 정확한 delay는 공개 확인되지 않아 0.015초 SIM-TUNE. |
| Mk 141 | CG-52 소스 모델의 실제 8관 | [CG-52 자료](https://www.seaforces.org/usnships/cg/CG-52-USS-Bunker-Hill.htm), [2021년 사진](https://www.seaforces.org/usnships/cg/CG-52_DAT/CG-52-USS-Bunker-Hill-133.jpg)과 모델. `weapons` mesh 1의 연결 성분 3/4/7/8/12/13/16/17에서 좌표·축·덮개를 추출했다. A/B는 서로 반대 발사 방향의 두 묶음이며 양현이라고 임의 해석하지 않는다. |
| DDG-119 | Harpoon 미설치 유지 | 기존 Flight IIA 함선 프로필·장착 형상을 보존했다. CG용 8관을 DDG에 공통 지급하지 않는다. |

## 수치가 공개 확인되지 않은 적용값

최소 발사거리 4km, 관측 나이 10초, 획득 basket 최대 4km, 순항/종말 해면 높이 15/5m, 연료 110kg/0.245kg/s, 600초 수명, 항력·양력·면적·4g 법선력 한계, INS 0.08m/s drift와 고도계 0.12m, 덮개 0.18초·관 간격 1.5초·날개 0.42초·꼬리 0.35초, 손상 75% 발사 차단은 SIM-TUNE이다.

시커의 작동 거리 14km, 탐색 범위 18km, ±45° gimbal, 16° 방위 beam, 0.1초 dwell, SNR/RCS reference·오차·탐지확률·Doppler/extent gate·4초 coast·350m track gate도 SIM-TUNE이다. 초기 획득 범위는 발사 당시 공분산의 전파와 공개되지 않은 체계 오차·표적 기동 여유로 정한다. 해면·지형·다른 반사체가 실제 RF 풀에 들어가므로 잘못된 반사, 재획득, 실수를 허용하며 명중률을 고정하지 않는다.

발사 때 저장한 위치·속도에는 센서 추정 오차가 그대로 남는다. 장거리 유도에는 그 오차와 표적 기동 때문에 더 넓은 불확실성이 생긴다. 현재 함정 자체 센서의 수상 관측 포락선은 하푼의 공개 최대 사거리와 같지 않으며, 외부 표적 정보 링크·경유점·최대사거리 인증은 후속 단계다.

## 모델 사용과 변경

사용자 뷰어 SHA-256: `b8b7ab4707c81e759998c0a1f1a7b33d0c814bf0026ecbec59a7092c7afb9a42`.

원저작자 [Civorsky](https://sketchfab.com/3d-models/missiles-37899978144a45d0bd03c3538957b145), 제목 *Missiles*, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). HTML의 MK 141 패널과 모델 메타데이터에도 출처를 보존했다.

원래 58 meshes의 24,133 triangles를 보존하고 4개의 main wing/4개의 tail을 분리해 62개 geometry로 만들었다. 본체를 늘리지 않고 main wing radial tip을 공개 0.914m span에 맞췄다. 균일색 1024² 텍스처 11개를 선형 재질 색으로 바꾸고 압축 geometry 358,658 bytes를 공유한다. 정확한 실물의 접이식 관절 구조가 공개 확정된 것은 아니며 전개 애니메이션·덮개 힌지·분리 후 회전은 표시용 SIM-TUNE이다.

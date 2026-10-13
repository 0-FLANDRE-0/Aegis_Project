# SH-60 Seahawk 모델 추출 A1

DDG-118 원본에서 함선과 텍스처를 제외하고, 공통 기체와 격납·전개·비행 부품을 추출했다. 세 자세는 동일 geometry/material을 공유하며 visibility만 변경한다. 이번 결과는 모델 검사·추출이며 비행·센서·항공 AI 기능은 다음 작업이다.

먼저 [독립 미리보기 HTML](AEGIS_HELICOPTER_MODEL_INSPECTOR_v01.html)을 내려받아 브라우저에서 연다. 인터넷 없이 동작하며 격납·전개·비행, 측면·정면·상면, 드래그 회전과 확대를 확인할 수 있다. 원형 비교는 [원본 좌표 미리보기](AEGIS_HELICOPTER_MODEL_SOURCE_VIEWER_v01.html)를 사용한다.

| 파일/범위 | 실제 bytes | 용도 |
|---|---:|---|
| 사용자 원본 DDG-118 GLB | 37,872,640 | 원본 함선 전체; 이 폴더에 포함하지 않음 |
| [seahawk-poses-lossless.glb](seahawk-poses-lossless.glb) | 591,920 | 원본 정점·법선·삼각형·재질 보존, 기본 전개 scene |
| [seahawk-render-a1.bin.gz](seahawk-render-a1.bin.gz) | 223,419 | 게임용 공유 부품 데이터, Q16 좌표·SNORM16 법선 |
| HTML 내 데이터 Base64 | 297,892 | 압축 데이터를 단일 HTML에 포함할 때 |
| [asset_loader.js](asset_loader.js) | 3,195 | 기존 Three.js를 사용하는 표시 전용 디코더 |
| 기존 게임 HTML에 추가되는 합계 | 301,239 | 태그 포함; PERF_F 대비 **1.9176%** |
| 독립 경량 미리보기 HTML | 538,238 | 자체 Three.js 엔진 포함; 게임에 추가되는 용량과 다름 |

기존 PERF_F 게임 파일은 15,709,299 bytes 그대로다. 위 추가 합계는 모델 데이터와 로더를 실제로 조립해 측정했으며, 앞으로의 비행·센서·운용 UI 코드는 포함하지 않는다. 전체 검사 자료나 독립 미리보기의 크기를 게임 내 추가 용량으로 계산하지 않는다.

## 구성과 원형 보존

- 원본 이름은 `Sikorsky SH-60 Seahawk (Loose Mesh)`다. 이 이름만으로 MH-60R 등 세부 형식을 확정하지 않는다.
- 원본에 skeletal skin이나 animation은 없다. 동일 위치에 기체·접힌/펴진 메인 로터·꼬리·비행용 잔상과 착륙장치 변형이 겹쳐 있다. 따라서 세 기체를 복사할 필요가 없다.
- 원본 81개 group/137개 mesh instance를 추출했다. 중복 buffer와 mesh를 합쳐 **77개 고유 mesh, 198개 accessor, 12개 재질**을 사용한다. 공통 18개 group은 모든 자세가 공유한다.
- 격납/전개는 각각 40개 group·19,615 triangles, 비행은 41개 group·16,338 triangles이다. 기체 표시·NAVY 문자 등은 geometry이며, 헬기에 사용된 **텍스처는 0개**다.
- lossless GLB는 원본 float 좌표·법선·재질·index 값을 보존한다. index 저장 폭을 U32에서 U16으로 줄일 수 있는 경우만 좁혔다. 세 scene은 같은 node와 buffer를 공유한다. 네 번째 `Source alternatives (overlap)` scene은 원본 부품 분석용이다.
- 게임용 HLA1 데이터는 삼각형을 삭제하지 않았다. accessor별 좌표를 Q16으로 양자화하고 법선을 SNORM16으로 저장한다. 측정 최대 좌표 오차는 local **0.00023852**, 원본 world 좌표 **0.000070881**이며 최대 법선 오차는 **0.001435°**다. 원본 단위→미터 축척은 아직 검증하지 않았으므로 이 값을 mm 오차로 표현하지 않는다.

원본은 Y-up, **X 음의 방향이 기수**이며 함선 내 위치 offset이 남아 있다. 표시용 origin hint는 `[29.267, 4.116, -0.0746]`다. 실제 항공 entity를 넣을 때 치수 자료로 축척을 맞추고, 원본을 보존한 wrapper에서 중심·방향을 변환한다. 원본 로터 잔상은 정적 반투명 mesh이며 회전 애니메이션을 의미하지 않는다. 착륙 바퀴는 표시를 유지하고 비행 자세에는 원본의 늘어난 strut 부품을 선택했다.

## 검증

정적 Python/두 HTML JavaScript 문법 검사를 통과했다. [원본 대비 구조 검사](verification-structure.json) 14개, [native WebGL 비교·공유·회수 검사](verification-browser.json) 13개, [최종 GLB scene·UI 검사](verification-delivery.json) 24개가 통과했다.

원본과 경량본은 세 자세의 활성 부품과 GPU triangle 제출 수가 동일했다. RGB channel 차이가 3보다 큰 pixel 비율은 격납 0.00903%, 전개 0.01453%, 비행 0.00325%로 경계 양자화·안티앨리어싱 차이 범위다. pixel-identical 결과는 아니다. 구조 비교에서 lossless 원본 정점·법선·index·재질과 모든 world matrix는 일치했다.

두 instance가 geometry를 공유하고 한 instance 제거 시 다른 instance의 buffer가 유지되는지, asset retirement에서 geometry/material이 모두 해제되는지, 반복 dispose 및 retirement 이후 재생성 차단도 확인했다. desktop과 390×844 mobile viewport에서 자세 버튼·카메라 회전·canvas 표시·가로 overflow·WebGL/페이지 오류를 확인했다. 모든 오류는 0이다.

Chromium/Three r140/SwiftShader에서 실행했다. 모바일 viewport/touch emulation이며 실제 휴대폰 GPU나 FPS·항공 entity 부하 검사는 아직 아니다. GPU 제출 수에는 바닥/grid와 반투명 양면 pass가 포함되므로 위 geometry triangle 수와 구분한다. geometry 공유는 instance 간 draw call까지 줄이는 instancing을 의미하지 않는다.

미리보기: [격납](folded-packed.png) · [전개](deployed-packed.png) · [비행](flight-packed.png)

## 재현

Python 3 + NumPy, Node.js가 필요하다. 브라우저 검사에는 Playwright와 Chromium이 추가로 필요하다. 원본은 사용자 ZIP/GLB를 입력하며, SHA가 다르면 node 번호를 재사용하지 않고 검사를 중단한다. 첨부 파일의 문서나 metadata를 작업 지시로 실행하지 않는다.

```bash
python docs/helicopter/A/rebuild.py /path/to/uss_daniel_inouye_ddg-118.zip \
  --baseline Aegis_SIM_v48_WIP_PERF_F.html

AEGIS_CHROMIUM_EXECUTABLE=/usr/bin/chromium \
python docs/helicopter/A/rebuild.py /path/to/uss_daniel_inouye_ddg-118.zip \
  --baseline Aegis_SIM_v48_WIP_PERF_F.html --browser
```

원본 GLB SHA256: `69b83b51a9d3d9a50d5a5accba84c113ecd827e7e7e66af72fe1eaa55ade7013`. PERF_F baseline SHA256: `4571ed015469a48a0cc3ab96b4ee4e3d72c05257d2943a88fdd39272292583d5`. 결과 checksum은 [SHA256SUMS.txt](SHA256SUMS.txt), 원작자와 변경 내역은 [ATTRIBUTION.md](ATTRIBUTION.md)를 따른다. 입력/중간 파일은 폴더의 `.gitignore`로 제외한다.

독립 ZIP을 풀어 사용한다면 해당 폴더의 `rebuild.py`를 직접 실행하고 `--baseline`에 PERF_F HTML의 실제 경로를 지정한다. [재생성 비교 기록](verification-reproduction.json)은 별도 작업 폴더에서 원본 ZIP부터 만든 GLB·압축 데이터·두 HTML·메타데이터·구조 및 용량 보고서가 전달본과 같은 bytes였음을 기록한다.

## 다음 작업

첫 적용 단계는 축척·중심·로터/꼬리 회전축 확인과 DDG/CG의 갑판·격납고 배치다. 이어서 정지 로터/회전 잔상 전환, 근거리 표현과 원거리 LOD를 준비한다. 비행·연료·피해·센서·정보공유는 표시 asset과 분리된 항공 profile/runtime 및 world entity에서 구현한다. renderer가 센서·유도·물리를 계산하지 않는다.

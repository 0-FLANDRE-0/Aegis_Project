# Harpoon B — 노즐·빈 관·발사 배기

사용자 요청으로 A의 본체 후미, 부스터/제트 배기와 발사관 표시를 개선했다. 사용자 추가 지시로 부스터 연소를 3.2초·평균 48kN으로 조정하고 후연이 많은 추진제 가정을 표시한다. INS/ARH·충돌·피해·발사 권한·관별 탄약·발사 질량 690kg은 유지한다. 모듈 revision은 HARPOON_B1, CG 작전 revision은 BUNKERHILL_HARPOON_B_1이며 동일 관별 schema의 A 저장을 명시적으로 허용한다. 입력 A HTML SHA는 `ffd976a211c530bc4d193597751e49febbd755646b865e6ad2685cd9e06aab77`로 고정한다.

## 원인과 변경

A는 원래 모델을 부스터와 본체로 나눌 때 연결 부품 일부를 본체에 남겼고 후미에 열린 노즐을 추가하지 않았다. 단일 cone 화염은 좁은 끝이 노즐을 향하고 넓은 끝이 뒤로 벌어졌다. B는 본체 후미를 연속 테이퍼로 만들고 금속 립·안쪽 벨·후퇴한 어두운 throat를 추가한다. 부스터의 shell/bell/throat도 다듬으며 연결 부품은 부스터 부착 중에만 표시한다. 본체 외피는 부스터 유무와 관계없이 유지하고 분리 때 노즐 내부가 드러난다. 본체 3.84m·전체 4.63m 길이를 늘리지 않는다.

발사관에는 앞 덮개 34 faces 뒤 약 0.102m에 같은 방향의 막힌 판이 있었다. A의 34 faces만 움직이면 그 판이 남아 구멍이 막혔다. 원래 front cover 전체 116 faces를 하나의 문으로 묶고 rear cover 58 faces를 별도로 분리했다. 발사하면 선택한 관의 앞 덮개가 열리고 후방 막이 제거되어 약 4.96m 깊이의 어두운 내부 벽이 보인다. 미발사 관은 원래 covers를 유지하고 RESET/재고 복원도 loaded 상태를 따른다. 회색 판 위에 검은 원을 그리는 방식이 아니라 실제 source index에서 막힌 faces를 분리한다. 추가로 약 1.00/1.08m 깊이에서 rack 지지판이 관을 가로막는 것을 실제 raycast로 확인했다. 관 축에 횡방향인 지지판의 원형 관통 부분만 48면 prism으로 잘라내고, 관 밖의 지지판과 원본 surface attribute는 barycentric 보간으로 보존한다. 원본의 정규화된 정수 법선은 getter로 복호화한 Float32 값으로 보간·정규화해, 정수 저장 때문에 새 지지판이 검게 보이지 않도록 한다. 490개 source faces를 부분 절단해 11,598개 표시 삼각형으로 재조립한다. 앞·뒤 covers의 1,392 faces와 절단 대상은 서로 겹치지 않는다. 지지판 절단은 ship build 시 한 번 만들고 source collision 자료는 바꾸지 않는다.

부스터는 nozzle 출구부터 시작하는 2.6m 외곽/1.86m core volume, 제트는 0.48m 외곽/0.24m core volume을 사용한다. 전자는 따뜻한 외곽과 밝은 core, 후자는 약한 푸른 배기다. 길이 방향의 opacity 감소·표면 시선각·진동을 shader에 적용하고 실제 solved thrust에 맞춰 강도를 조절한다. 분리된 부스터에는 재점화 불꽃을 붙이지 않는다. 연료 소진/엔진 비활성 상태는 plume를 숨긴다.

발사 연기는 현재 등록된 rear mouth에서 방향성 backblast로, 짧은 압력 구름은 tail이 실제로 관을 떠나는 시점의 front mouth에서 생성한다. 비행 중에는 부스터 nozzle의 실제 관측 위치를 0.60m 간격으로 샘플링해 짙은 회백색 연기를 이어 붙인다. 초기 optical alpha .96, base 1.8m, 수명 12초, 성장 .18/s와 느린 감쇠 .95를 지정한다. 발사구의 회백색 backblast도 더 큰 base .8–1.6m/alpha .65–.85/수명 5.2–8초로 보강한다. 공유 solver가 바람·팽창·연령에 따라 실제 opacity를 줄이므로 화면 전체를 고정 불투명으로 덮지 않는다. 부스터 분리 시 새 trail을 끊지만 이미 생성된 구름은 남아 표류·확산·감쇠한다. 제트 순항에는 두꺼운 연기 구름을 만들지 않는다. 공유 C13 smoke pool·HOT batch를 사용하고 launcher emitter 8개, 연기 sample 48개/탄체/프레임으로 제한한다. 게임이 멈추면 표시 시간도 멈춘다. 늦게 3D를 열어 과거 ignition이나 긴 연기 이력을 만들어내지 않는다.

## 3.2초 부스터와 공개 자료 구분

[Designation Systems](https://www.designation-systems.net/dusrm/m-84.html)의 표면 발사 booster 참고값 약 53kN·2.9초는 `public`에 그대로 둔다. 사용자가 요청한 3.2초는 `sim.boosterBurnS`, 고정 평균 추력 48kN은 `sim.boosterAverageThrustN`으로 분리한다. 단순 평균 모델에서 총추력량 153.6kN·s는 참고 153.7kN·s와 약 0.065% 차이다. 90kg 추진제/60kg 부스터 dry mass 가정을 유지하며 질량 감소는 새 연소 시간으로 계산하고 연소 종료의 실제 60Hz 틱에서 한 번 분리한다. 속도를 임의로 지정하거나 분리 시 속도를 재설정하지 않는다. exact motor grain, 압력 곡선, 제조사 Isp를 재현했다는 주장이 아니다.

**후연이 많은 고체 추진제는 사용자 설정 가정**이다. 연기 입자 수·광학량·색·화염은 VISUAL-TUNE이며 실제 추진제 화학 조성이나 특정 RGM-84D의 후연량을 공개 확인한 수치가 아니다. 공개 `53kN/2.9초`를 `3.2초`의 실물 확인값으로 바꾸지 않는다. 이 게임의 비교용 실제 rocket smoke는 RAM/ESSM/SM-2이며 별도 공대공 미사일 smoke 프로필이 있다고 주장하지 않는다. native 검사에서는 기존 emitSmoke를 분리 pool에 호출해 optical weight/metre를 측정하고 하푼의 실제 live trail과 비교한다. smoke는 표시만 변경하며 레이더 clutter·시커·전투 난수에 feedback하지 않는다.

## 참고·표시 범위

- 기존 `buildKh35uVisualMesh`의 tapered tail/open lip/recessed throat, `createAsmPlume`의 약한 터보제트와 강한 rocket 구분을 검토했다.
- 기존 `createPlume`의 이중 core/outer, `smokeTrailSamples`의 거리 기반 샘플, C13/C17의 pooled hot exhaust와 셀 발사 연출을 참고했다.
- 공개 치수·성능과 A의 source/license는 [A SOURCES](../A/SOURCES.md)를 유지한다. 모델 원저작자는 Civorsky, CC BY 4.0. B의 새로운 후미 곡선·노즐 내부·화염 색/길이·막 제거·관 내경·전개 표현은 **VISUAL-TUNED**이며 실물 제작 도면·정확한 열/광학 신호를 주장하지 않는다.
- `renderer.js`와 `visual-profile.js`는 표시 전용이다. 시뮬레이터는 기존 source 모델 geometry로 actual collision/장비 피해를 계산한다. 이번 시각적 관 개방은 피격 손상으로 생긴 breach나 재장전 기능을 추가하는 작업이 아니다.
- 하푼 follow의 실제 wheel/pinch 최소 거리만 4m로 낮춰 노즐을 가까이 볼 수 있다. 다른 함선/미사일의 camera 한도는 유지한다.

## 파일·재현

`build.py`는 A의 main renderer와 작은 profile/core 모듈을 교체하고 새 mouth 등록, 불변 visual profile, visual core audit와 Harpoon camera 한도를 추가한다. Harpoon core diff는 부스터 시간·평균 추력·질량 감소 시간 기준으로 제한한다. CG revision과 명시적 A 저장 호환을 포함한 허용 변경을 정규화한 뒤, 나머지 combat/ship/renderer source는 A와 byte 동일인지 검사한다. A의 records 0–12, CG 원본 asset 6개와 Harpoon model/launch asset 3개도 bytes 동일하다.

```sh
python docs/harpoon/A/build.py --out /tmp/harpoon-b/baseline-A.html
python docs/harpoon/B/build.py --baseline /tmp/harpoon-b/baseline-A.html --out /tmp/harpoon-b/rebuild.html
python docs/harpoon/B/author_mouths.py Aegis_SIM_v48_WIP_HARPOON_B.html --out /tmp/harpoon-b/mouths.json
python docs/harpoon/B/verify_static.py Aegis_SIM_v48_WIP_HARPOON_B.html /tmp/harpoon-b/baseline-A.html /tmp/harpoon-b/static
python docs/harpoon/B/verify_stage.py Aegis_SIM_v48_WIP_HARPOON_B.html /tmp/harpoon-b/stage
python docs/harpoon/B/verify_native.py Aegis_SIM_v48_WIP_HARPOON_B.html /tmp/harpoon-b/native
python docs/harpoon/A/verify_runtime.py Aegis_SIM_v48_WIP_HARPOON_B.html /tmp/harpoon-b/runtime
python docs/harpoon/A/verify_salvo.py Aegis_SIM_v48_WIP_HARPOON_B.html /tmp/harpoon-b/salvo
```

Python/NumPy/Node, 기존 Playwright requirements와 Chromium이 필요하다. `author_mouths.py`는 내장된 quantized source geometry와 A의 등록 좌표에서 8관의 1,392 cover faces와 지지판의 작은 원형 절단 자료를 exact 복원한다. nozzle/plume geometry는 공유하며 각 인스턴스 shader material은 종료할 때 한 번만 해제한다. 큰 추가 texture나 입자별 Object3D는 만들지 않는다.

검사 입력 `experimental.html`과 최종 B는 byte 동일이다. 실제 native RAF/UI/flight, RESET, core/console, 1/8/16/64× 결과는 `evidence/`를 따른다. 빈 관만 확대하는 이미지는 읽기 전용 검사 카메라로 촬영했다. 일반 follow·wheel·pointer는 실제 사용자 입력으로 검사하며 geometry queue를 시험용으로 진행하지 않는다. SwiftShader에서 사용자 GPU FPS를 추정하지 않는다.

## GitHub 분담

기존 `harpoon-block1c-a` branch는 확인 시 여전히 main K baseline이었다. A는 아직 remote에 업로드되지 않았으므로 사용자는 최신 B HTML 하나만 같은 branch 루트에 업로드한다. 이후 원격 SHA 확인 → 작은 A/B 지원 파일·상태·체크섬·README·지침·B workflow → PR/CI를 진행한다. A comparison은 작은 A 모듈과 기존 K blob에서 exact 재생성하며 새 대형 A archive HTML을 API/Git로 업로드하지 않는다. A HTML/상태/SHA의 동일 bytes는 로컬 archive/인계 package에 보존한다.

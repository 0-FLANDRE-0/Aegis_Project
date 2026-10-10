# v48 WIP MULTI SHIP D — 5A/5B·shadow 판단

- 원본 HTML `Aegis_SIM_v48_WIP_MULTI_SHIP_D.html`, 15,575,097 bytes.
- HTML SHA `babac7fba08e4d59628c25245b1c657a87516f6774f6ec505c2314b1e3c1bf6e`, decoded main SHA `40cfc1a25698f4b791b23c34920793f319ad9a0785e886d3df47e1f0c99539af`.
- 기준 C head `a57ed7ee1007bfa549b82b8f9f8ee8396241cae9`; C HTML SHA `e306f755cad27cd32aef4ad2dff6c108ee56511cc9909f0609434558f0865363`.
- packed main13과 표시 build label/메타데이터 변경. assets0~12·원본 모델·profile/module revision·stable v48 보존.

## 구현

각 배치 함정의 canonical owner에 FCS/SPG·탄약·VLS/ESSM4 고정 슬롯·SAM/RAM·함포탄·기관포탄·Harpoon 발사 실행을 결속했다. 원본238개 owner-dependent 함수를 build에서 검증해 재사용한다. ACTIVE profile/alias 교대와 runtime eval은 없다. DDG/CG 설치 무장·사각·손상·조준·native 신관·발사 간격/재고를 사용한다. Cross-profile SeaRAM 사거리0 오류를 고쳤다.

공통 RF와 swept 실제 body contact가 올바른 receiver ShipRuntime에 WIP12 관통/구획 폭압/파편/승조원/침수·종강도·충격을 한 번 적용한다. 같은 event 재적용 방지·launch clearance·sea ordering·관통 후 함포 잔여 handoff와 owner 장갑 patch를 유지한다. 3D 실제 탄/장착물/발사 덮개·후폭풍/terminal path/손상은 owner에 표시하며 foreign SAM/RAM/Harpoon을 자함 operator telemetry/follow에 넣지 않는다.

reset/import에서는 자함 naval impact 중복 방지 기록도 비운다. 운용 저장은 함정별 실제 finite inventory와 고정 셀 주소를 preflight/원자 복원한다. 기존 B/C schema 없는 저장만 명시 migration하며 비행/센서/동의/예약/shadow/routes는 초기화한다. 공통 world/Harpoon flight1회·owner fixed tick1회·60/120/20Hz·VLS 피해통제10Hz는 유지한다.

shadow는5Hz로 해당 observer의 measured track만 읽고 기존 CPA/NEZ/resource/salvo를 참고한다. action은 전부 WITHHOLD/executed=false, 로그 최근64개다. **적 자동 요격·EW·공격 AI는 활성화하지 않았다.** acceleration0·full BDA/alias/controller 이관은 다음5C/5D 범위다. 상대 원격발사 UI와 헬기도 없다.

## 검증 기록

최종 원본과 같은 SHA의 직접 static/guidance/실탄 battle 검사 **108/108**가 통과했다. 재시작 뒤 같은 projectile event ID가 다시 실제 피해를 적용하는 반복 실탄도 포함한다. 이전 publication의 owner 무장/근접방어/native/센서/배속/DDG/Harpoon 회귀는 pre-reset 증거로 보존하고 최종 직접 조건에 합산하지 않는다. 해당 publication의 D workflow static+13 browser suite는 PASS이며, reset 기록 초기화가 추가된 최종 head에서도 전체 suite/smoke를 다시 실행한다. latest-head CI는 [PR#48](https://github.com/0-FLANDRE-0/Aegis_Project/pull/48) checks와 [인계](docs/multiship/D/GITHUB_HANDOFF.md)를 따른다. [직접 집계](docs/multiship/D/evidence/verification-summary.json).

실제8km 양방향 Harpoon launch→INS/ARH→접촉·피해와 진단 swept contact fixture를 구분한다. native393×852 Chromium SwiftShader의 owner SAM/SPG/Harpoon/발사관·terminal path/실제 손상·카메라 read-only는 GPU FPS 인증이 아니다. 신규 함정 간120~140km battle·얇은 장비별 정밀 collision·다수 함정 성능은 후속 범위다. [구조](docs/multiship/D/README.md), [측정 조건](docs/multiship/D/PERFORMANCE.md), [다음 단계](docs/multiship/D/DEPENDENCIES.md).

C HTML/status/SHA/workflow는 `archive/v48/WIP_MULTI_SHIP_C/`에 같은 bytes로 보존했다. 안정 v48 SHA `9e786ddb1331fcd496b6b9604cec87317667ebc501e99270cc33fd6ba1ab9e83` 유지. `multiship-weapons-d`는 C PR#47 위에 연결하며 A/B/C/main을 임의 병합하지 않는다.

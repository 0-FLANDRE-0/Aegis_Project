# MAP_D 시험 준비와 경계

- 기준은 main 9f8e77f9의 MAP_C이며, 기존 C용 검사의 제품 이름/출력 폴더만 D로 이관했다. 검사 항목은 제거하지 않는다.
- `verify_rings_c.py`는 C와 D를 같은 관측/논리 사각형에서 비교한다. 기존 반지름·색·dash·채움·빗금 및 9/11px 글자 검사를 그대로 유지한다.
- 승인된 DDG3+CG3 paired 기대값은 byte 동일하다. 새 UI를 포함한 코어 SHA guard만 현재 산출물로 다시 묶는다. 자원/피해 기대값을 새로 승인하지 않는다.
- `extension-fixture.js`는 보고서용 시험 코드다. 관측 Map에 합성 트랙을 넣고 실제 CUE/release/비행 tick을 호출한다. 제품 HTML에는 포함하지 않는다.
- 독립 시험 사이에는 native gun.reset()을 사용한다. clear()는 CUE를 해제할 뿐 이전 포탄/급탄 시간이 남아 있으므로, 별도 시나리오의 초기 상태로 쓰면 안 된다.
- ENV_D.status()는 async이다. Promise.match를 읽지 않고 await 후 match를 검사한다. table/provenance 값은 변경하지 않는다.
- 경로 편집 띠는 기존 표시 규칙대로 다음 rAF에서 배치된다. 클릭 직후 동기식 is_visible 대신 visible을 기다려 검사한다.
- native 발사 저널의 releaseStep는 fixed tick 끝의 simStepCounter 증가 전 값이다. 요청 tick 시작부터 문 개방에 실제 소비된 tick은 releaseStep+1-requestStep이다. 발사 지연 계수나 native update 순서는 변경하지 않는다.
- 평상시 CG 포 사계 합집합은 360°이다. 공동 사각을 억지로 만들지 않고 기존 자세 API의25° 횡경사/270° 표적에서 내림각 제한을 검사한다. 평상시 단독 포/2문은 실제 발사 수까지 검사한다.
- 실제 자연 탐지→LOCK→정식 VLS→WebGL8과 합성 트랙 UI 시험을 구분한다. 소프트웨어 GPU의 기능 검사를 실제 휴대폰 FPS로 보고하지 않는다.
- 개발 중 fixture 오류/시점 관찰 로그는 최종 통과 수에서 제외하고 evidence/development에 별도 보존한다. 최종 acceptance는 모든 최종 증거의 HTML SHA가 납품본과 일치해야 한다.

- 새 UI 시험은 native 발사 저널/실제 shotsFired가 도착하면 그 검사 단계를 끝낸다(기존 240/400 tick 상한은 유지). 불필요한 발사 후 비행을 더 돌리지 않으며 모든 조건/거부/발사 수 검사는 유지한다. 전체 비행은 기존 하푼·종료기·자연 WebGL·world120 회귀에서 별도로 검증한다.
- 동시 SwiftShader 화면 여러 개가 CPU를 잠식하지 않도록 GPU를 사용하는 검사 프로세스만 공통 flock으로 직렬화한다. 비GPU 진단은 독립 프로세스로 병렬 실행한다. 게임의 fixed tick/배속/계수는 변경하지 않는다.

- 별도 포 사계 UI 검사에서는 active 플래그만 세우는 CSS geometry stub으로 PiP 입력을 대신하지 않는다. 실제 3D open/ready로 PiP 입력면을 마운트한 후 탭한다. 모든 기존 조건은 유지하고 표적 지정 성공을 명시적으로 검사한다.

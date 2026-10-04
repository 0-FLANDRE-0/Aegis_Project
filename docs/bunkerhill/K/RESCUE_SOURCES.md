# WIP K — 구명뗏목 공개 근거와 시뮬레이션 범위

확인일: 2026-10-04. 정원 근거와 CG-52 장착 수량을 구분한다.

## 공개 자료에서 확인한 정원

1. [미 해군 DVIDS: USS Makin Island installs life rafts onboard](https://www.dvidshub.net/image/5627398/uss-makin-island-installs-life-rafts-onboard). 촬영 2019-07-22, 게시 2019-07-30. 미 해군 사진 설명의 문구: “Commonly known as a ‘Mark 7,’ each life raft can hold up to 25 people.” USN 함정용 Mark 7의 정원은 **25명**이다. 같은 설명에 나온 Makin Island의 약 140척은 그 함정의 수량이며 벙커힐에 적용하지 않는다.
2. [NAVY MIL-DTL-32532A 공개 규격 초록](https://standards.globalspec.com/std/14468739/mil-dtl-32532a), 발행 2021-08-04. 공개 scope: “This specification covers the 25-person (Mark-7) Mod 2 and 50-Person (Mark-8) Mod 2 inflatable life rafts, including inflation system and survival gear, packed within a rigid stowage container, ready for use as abandon ship survival equipment.” 공개 초록으로 25인승 Mark 7 Mod 2를 교차 확인했다. 전체 규격을 열람한 것으로 표시하지 않는다.

20인승으로 추정하던 값을 25인승으로 적용한다. 항공기용 25인승 뗏목 자료는 함정용 Mark 7의 근거로 사용하지 않았다. DLA Quick Search 페이지가 차단 응답을 반환한 조회도 확인 근거로 사용하지 않았다.

## SIM-TUNE으로 적용한 항목

- CG-52의 퇴역 직전 구명뗏목 비치 수량·정확한 용기 위치·Mod 번호를 확정할 공개 근거는 확보하지 못했다.
- 모듈은 Mark 7 정원 25명을 공유한다. 실제 비치 목록 대신 `ceil(선택 프로필 승조원 정원 / 25)`를 시뮬레이션의 가용 상한으로 둔다. 현재 프로필의 벙커힐 330명은 최대 14척, DDG-119 310명은 최대 13척이다. 이는 실함의 비치 수량을 주장하는 값이 아니다.
- 양현의 진수 지점은 선택 함선의 원본 선체 단면과 후방 비행갑판 hardpoint로 계산한다. 세 가지 후방 위치를 순환하며 두 진수 간격은 최소 4초이다. 이 위치·간격은 실함 절차를 재현한 자료가 없는 SIM-TUNE이다.
- 뗏목의 간략화된 팔각형 고무 튜브·주황색 지붕·크기, 바람의 2.5% 표류 계수, 초기 이격 속도, 원형 접촉과 선체 이격 처리는 SIM-TUNE이다. 정밀한 구명뗏목 유체역학으로 표시하지 않는다.

## 실제 게임 동작

퇴함 버튼을 승인하면 기존 승조원이 퇴함 집결점까지 이동한다. 도착한 살아 있는 사람만 개별 ID로 탑승 명단에 기록하고 그때 뗏목을 생성한다. 경로가 막힌 사람과 사망자는 자동으로 탑승시키지 않는다. 중복 ID를 허용하지 않으며 부상자는 이동 조건을 만족하면 탑승한다.

탑승 중인 뗏목은 진수 지점에 붙어 있으며 25명이 차면 떠난다. 마지막 미충원 뗏목은 남은 생존자가 모두 퇴함하거나 함선이 LOST 상태가 되면 떠난다. 이미 떠난 뗏목은 함선과 별개의 월드 엔티티로 유지되고 기존 물리 고정 tick에서 바람·해면을 따라 움직인다. 새 게임 초기화 시 해당 함선 소유의 뗏목을 제거한다. 3D 표시에서는 기존 해면 shader 위에 투영하며 시뮬레이션 상태에 쓰지 않는다.

CIC의 주황색 뗏목 기호는 알려진 아군 생존자 위치이다. 레이더 plot이나 전투 track을 만들지 않는다. crew 패널에서 척수·탑승 인원·25명 정원을 확인할 수 있다. 구조선의 수거·귀환, 뗏목에 대한 전투 피해와 개별 구조 행동은 이번 범위에 포함하지 않았다.

## 저장 호환

신규 작전 저장은 시간·진수 상태·월드 위치·속도·개별 탑승 명단을 detached payload로 저장한다. 모든 codec의 preflight를 통과한 뒤에만 복원한다. 정원 초과, 중복 사람, 승조원 상태와 다른 명단, 잘못된 소유권과 시간·위치 등은 authoritative 쓰기 전에 거부한다.

J와 이전 저장에는 뗏목 위치가 없다. 기존 `evacuated` 기록에 있는 사람만 detached migration으로 뗏목에 배정하고 저장된 함선 위치 바깥에 근사 배치한다. 당시 해상 위치를 복원했다고 표시하지 않는다. 퇴함 인원이 없는 기존 저장에는 뗏목을 생성하지 않는다.

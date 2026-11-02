# S2 자동 착수 판정

S1에서 제품 코드 결함이 확인되었다. 공용 WIP22 시커는 EKF가 아직 없을 때 launch cue 잔차를 후보 점수의 약한 감점으로만 쓴다. TRACK-C 이탈 표본 37발은 모두 첫 `TRACK`을 목표 함정이 아닌 같은 salvo의 다른 ASM RF 반사로 확정했다. 첫 TRACK 이전 피해는 0건이고 기만체 최초 연관도 0건이었다.

수정은 `asmSeekerAssociateMeasurements`의 no-EKF 분기에만 둔다. 이미 점수 정규화에 쓰이던 range `max(1200 m, cueRange*0.12)`, azimuth `5 deg`, elevation `4 deg` 척도를 초기 획득 basket으로도 사용한다. basket 밖 후보는 EKF를 초기화하지 않는다. 실제 물체 ID나 소속은 읽지 않는다.

RF/Pd, 잡음, RCS, 빔, 탐색 구역, gimbal, 유도, 추진, 피해 계수는 그대로다. 45 km 소형 수상표적 검출 실패처럼 SNR/evidence 계수에 속하는 현상은 이번 수정 대상으로 삼지 않는다.

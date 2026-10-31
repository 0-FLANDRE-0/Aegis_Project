# GUN_B2 상태

**Phase 0 완료 · 사용자 승인 대기**

정식 시험 2,400회 / 80조건 ×30시드 / 19,163발.
제품 GUN_B1 SHA-256 `c9ec99f0b04e24127cc494833b8b1de24492a7ef0c00c2ee1432dba131f83ccc` 유지. 게임 코드/계수 변경 0.
새 B2 게임 HTML은 없으며 Phase 1은 미구현이다.

우선 결정: 센서 변경 금지 범위와 충돌하는 공중 plot receiver 원점 계약 복구를
별도 선행 수정으로 허용할지. 고정 오프셋이나 truth 사격 보정은 제안하지 않는다.

[최종 보고](PHASE0.md) · [검수](evidence/acceptance.json) · [원점 원인](ORIGIN_CONTRACT_FINDING.md)
· [미적용 설계 초안](PHASE1_PROPOSAL_DRAFT.md) · [원격 영수증](https://github.com/0-FLANDRE-0/Aegis_Project/blob/gun-b2/docs/gun/B2/REMOTE_READBACK.json).

지시서 §2/§12: **“push 후 멈추고 사용자 승인을 기다린다.”**
main 병합, release/tag, CI 변경 없음. 승인 전 구현을 진행하지 않는다.

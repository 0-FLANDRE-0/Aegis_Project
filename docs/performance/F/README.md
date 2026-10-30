# 최적화 최종 점검 PERF_F

PERF_E final `bd8962011a16cfeb4158670d3e562a92e0a52ff4` 위다. 원본 packed13의 표시용 damage job scheduler와 외부 함정 텍스처 회수만 수정한다. 모든 모델·기타 packed assets, 물리·피해·센서·교전 AI·RNG·60/120/20Hz·actual release source는 보존한다.

E에서 첫 구멍을 공개한 뒤에도 큰 주변 메쉬 작업이 끝날 때까지 다음 피격을 받지 않는 것을 CG/DDG 모두 재현했다. F는 완성된 모든 anchor가 실제 메쉬에 붙은 이후에만 최신 피격으로 나머지 quick 작업을 선점한다. 새로운 job은 다시 모든 anchor를 공개하기 전까지 선점할 수 없다. 따라서 미공개 구멍은 계속 진행하고, 빠른 연속 피격이 주변 장식 작업 뒤에서 대기하지 않는다. 캔슬은 미공개 새 버퍼만 회수하고 live cuts/original records를 유지한다. 입력이 안정되면 동일 주변 cut/fold/scorch/edges/detail이 완료된다. 외부 CG 모델 제거 시 per-presenter chain texture를 ownedTextures Set으로 한 번 dispose한다. DDG의 공유 factory textures는 해제하지 않는다. 원래 모델 재질이나 텍스처 내용은 바꾸지 않는다.

검증은 전체 기존 회귀, 같은 seed 전투·저장/RNG parity, 두 등록 모델의 최종 geometry parity에 더해 연속 3회 피격 큐, 120 simulated seconds의 세 함정 부하, 8회 native smoke/Kh32 import/reset, pending-cut 외부 함정의 실제 owner replacement/disposal을 포함한다. 제어된 cumulative scars는 구조 진단의 detached 입력이다. 실제 자연 다발 피격을 인증했다고 표현하지 않는다.

전체 기능/카메라 검사가 종료된 후 E/F native RAF second-hit latency를 직렬·AB/BA 두 회로 측정한다. generator drainage는 이 측정에 사용하지 않는다. 범위·원시 증거·한계는 PERFORMANCE.md, evidence/verification-summary.json, GITHUB_HANDOFF.md를 따른다. CPU/SwiftShader 결과는 phone/hardware GPU FPS가 아니다. 120초 simulation endurance는 실제 수시간 soak가 아니다.

full original upload/readback은 기존 §7.1 사용자 승인이다. main/이전 branch merge·새 PR·Actions dispatch는 하지 않는다. 마지막 최적화 검증 이후 다음 기능은 헬기와 초수평선 탐지, 이후 RGM-109E Block Va다.

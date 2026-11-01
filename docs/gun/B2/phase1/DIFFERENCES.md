# 원시 불일치 분류

모든 원본 검사와 실패를 보존한다. 새 기대값·허용치 갱신0. 아래는 수집된 bool 단언42개다. 별도 AIR 승인4raid+1hash는 원래 승인 manifest와 정확 대조했고, EW raw export 차이와 수상 fixture 조건은 별도 장부를 따른다.

| 모드 | 검사 | 분류 | 원인 |
|---|---|---|---|
| OFF | 1400.P2.autoOpen | PREEXISTING_ENTRYPOINT | MAP_B/E removed legacy cursor bridge. Old PIP_B test attempts obsolete cursor-based lock; canonical native exact-track UI88 passes. |
| OFF | 1400.P2.originalFields | PREEXISTING_ENTRYPOINT | MAP_B/E removed legacy cursor bridge. Old PIP_B test attempts obsolete cursor-based lock; canonical native exact-track UI88 passes. |
| OFF | 1400.P2.relockReopens | PREEXISTING_ENTRYPOINT | MAP_B/E removed legacy cursor bridge. Old PIP_B test attempts obsolete cursor-based lock; canonical native exact-track UI88 passes. |
| OFF | 1400.DD.MAIN.D4.airBlocked | PREEXISTING_B1_ASSERTION | Old blanket NOT_SURFACE_TRACK expectation; unchanged B1 migration explicitly initializes native80m/s EKF and requires VELOCITY_UNCERTAINTY blocking.213/213 actual ON/OFF. |
| OFF | 1400.DD.PIP.D4.airBlocked | PREEXISTING_B1_ASSERTION | Old blanket NOT_SURFACE_TRACK expectation; unchanged B1 migration explicitly initializes native80m/s EKF and requires VELOCITY_UNCERTAINTY blocking.213/213 actual ON/OFF. |
| OFF | 1400.CG.MAIN.D4.airBlocked | PREEXISTING_B1_ASSERTION | Old blanket NOT_SURFACE_TRACK expectation; unchanged B1 migration explicitly initializes native80m/s EKF and requires VELOCITY_UNCERTAINTY blocking.213/213 actual ON/OFF. |
| OFF | 1400.CG.PIP.D4.airBlocked | PREEXISTING_B1_ASSERTION | Old blanket NOT_SURFACE_TRACK expectation; unchanged B1 migration explicitly initializes native80m/s EKF and requires VELOCITY_UNCERTAINTY blocking.213/213 actual ON/OFF. |
| OFF | 832.DD.MAIN.D4.airBlocked | PREEXISTING_B1_ASSERTION | Old blanket NOT_SURFACE_TRACK expectation; unchanged B1 migration explicitly initializes native80m/s EKF and requires VELOCITY_UNCERTAINTY blocking.213/213 actual ON/OFF. |
| OFF | 832.DD.PIP.D4.airBlocked | PREEXISTING_B1_ASSERTION | Old blanket NOT_SURFACE_TRACK expectation; unchanged B1 migration explicitly initializes native80m/s EKF and requires VELOCITY_UNCERTAINTY blocking.213/213 actual ON/OFF. |
| OFF | 832.CG.MAIN.D4.airBlocked | PREEXISTING_B1_ASSERTION | Old blanket NOT_SURFACE_TRACK expectation; unchanged B1 migration explicitly initializes native80m/s EKF and requires VELOCITY_UNCERTAINTY blocking.213/213 actual ON/OFF. |
| OFF | 832.CG.PIP.D4.airBlocked | PREEXISTING_B1_ASSERTION | Old blanket NOT_SURFACE_TRACK expectation; unchanged B1 migration explicitly initializes native80m/s EKF and requires VELOCITY_UNCERTAINTY blocking.213/213 actual ON/OFF. |
| OFF | 1400.CG.MAIN.gunRingsNative | PREEXISTING_B1_ASSERTION | Old CG Mod2 22km label expectation, approved B1 Mod4 is24km. Existing exact migration passed OFF/ON; no new range coefficient. |
| OFF | 1400.CG.PIP.gunRingsNative | PREEXISTING_B1_ASSERTION | Old CG Mod2 22km label expectation, approved B1 Mod4 is24km. Existing exact migration passed OFF/ON; no new range coefficient. |
| OFF | 832.CG.MAIN.gunRingsNative | PREEXISTING_B1_ASSERTION | Old CG Mod2 22km label expectation, approved B1 Mod4 is24km. Existing exact migration passed OFF/ON; no new range coefficient. |
| OFF | 832.CG.PIP.gunRingsNative | PREEXISTING_B1_ASSERTION | Old CG Mod2 22km label expectation, approved B1 Mod4 is24km. Existing exact migration passed OFF/ON; no new range coefficient. |
| ON | 1400.P2.autoOpen | PREEXISTING_ENTRYPOINT | MAP_B/E removed legacy cursor bridge. Old PIP_B test attempts obsolete cursor-based lock; canonical native exact-track UI88 passes. |
| ON | 1400.P2.originalFields | PREEXISTING_ENTRYPOINT | MAP_B/E removed legacy cursor bridge. Old PIP_B test attempts obsolete cursor-based lock; canonical native exact-track UI88 passes. |
| ON | 1400.P2.relockReopens | PREEXISTING_ENTRYPOINT | MAP_B/E removed legacy cursor bridge. Old PIP_B test attempts obsolete cursor-based lock; canonical native exact-track UI88 passes. |
| ON | DDG_119_LATE_FLIGHT_IIA.relativeSweptCPA | NEW_ON_MODEL_CHANGE_UNAPPROVED | Old exact CPA fraction.5 is replaced by first accumulated beam signal+2ms. Original exact CPA assertion remains false. |
| ON | CG_52_LATE_TICONDEROGA.relativeSweptCPA | NEW_ON_MODEL_CHANGE_UNAPPROVED | Old exact CPA fraction.5 is replaced by first accumulated beam signal+2ms. Original exact CPA assertion remains false. |
| ON | harpoonSiProximity | NEW_ON_MODEL_CHANGE_UNAPPROVED | Synthetic stationary Harpoon lies exactly on the projectile axis, outside50-90deg detection annulus. No proximity event, hence no forced native termination or journal result. Adapter code is unchanged. |
| ON | nativeFinish | NEW_ON_MODEL_CHANGE_UNAPPROVED | Synthetic stationary Harpoon lies exactly on the projectile axis, outside50-90deg detection annulus. No proximity event, hence no forced native termination or journal result. Adapter code is unchanged. |
| ON | nativeAfterActionJournal | NEW_ON_MODEL_CHANGE_UNAPPROVED | Synthetic stationary Harpoon lies exactly on the projectile axis, outside50-90deg detection annulus. No proximity event, hence no forced native termination or journal result. Adapter code is unchanged. |
| ON | DD.G2.10.0 | NEW_ON_MODEL_CHANGE_UNAPPROVED | Old zero-dispersion ballistic error<.35m expectation conflicts with anchor-calibrated nonzero physical launch dispersion. Nominal solver/drag unchanged. |
| ON | DD.G2.10.280 | NEW_ON_MODEL_CHANGE_UNAPPROVED | Old zero-dispersion ballistic error<.35m expectation conflicts with anchor-calibrated nonzero physical launch dispersion. Nominal solver/drag unchanged. |
| ON | DD.G2.30.0 | NEW_ON_MODEL_CHANGE_UNAPPROVED | Old zero-dispersion ballistic error<.35m expectation conflicts with anchor-calibrated nonzero physical launch dispersion. Nominal solver/drag unchanged. |
| ON | DD.G2.30.280 | NEW_ON_MODEL_CHANGE_UNAPPROVED | Old zero-dispersion ballistic error<.35m expectation conflicts with anchor-calibrated nonzero physical launch dispersion. Nominal solver/drag unchanged. |
| ON | DD.G2.500.0 | NEW_ON_MODEL_CHANGE_UNAPPROVED | Old zero-dispersion ballistic error<.35m expectation conflicts with anchor-calibrated nonzero physical launch dispersion. Nominal solver/drag unchanged. |
| ON | DD.G2.500.280 | NEW_ON_MODEL_CHANGE_UNAPPROVED | Old zero-dispersion ballistic error<.35m expectation conflicts with anchor-calibrated nonzero physical launch dispersion. Nominal solver/drag unchanged. |
| ON | G3.prox | NEW_ON_MODEL_CHANGE_UNAPPROVED | Old axis-aligned point target never enters forward annular beam. No event is correct for that geometry; physical friendly-SAM adapter is not granted immunity. |
| ON | G3.friendlySAM | NEW_ON_MODEL_CHANGE_UNAPPROVED | Old axis-aligned point target never enters forward annular beam. No event is correct for that geometry; physical friendly-SAM adapter is not granted immunity. |
| ON | G4.nativeKill | NEW_ON_MODEL_CHANGE_UNAPPROVED | Synthetic exact r=0 burst has no positive fragment intercept time/direction. New geometric membership returns0; does not force a kill at overlap. |
| ON | CG.G2.10.0 | NEW_ON_MODEL_CHANGE_UNAPPROVED | Old zero-dispersion ballistic error<.35m expectation conflicts with anchor-calibrated nonzero physical launch dispersion. Nominal solver/drag unchanged. |
| ON | CG.G2.10.280 | NEW_ON_MODEL_CHANGE_UNAPPROVED | Old zero-dispersion ballistic error<.35m expectation conflicts with anchor-calibrated nonzero physical launch dispersion. Nominal solver/drag unchanged. |
| ON | CG.G2.30.0 | NEW_ON_MODEL_CHANGE_UNAPPROVED | Old zero-dispersion ballistic error<.35m expectation conflicts with anchor-calibrated nonzero physical launch dispersion. Nominal solver/drag unchanged. |
| ON | CG.G2.30.280 | NEW_ON_MODEL_CHANGE_UNAPPROVED | Old zero-dispersion ballistic error<.35m expectation conflicts with anchor-calibrated nonzero physical launch dispersion. Nominal solver/drag unchanged. |
| ON | CG.G2.500.0 | NEW_ON_MODEL_CHANGE_UNAPPROVED | Old zero-dispersion ballistic error<.35m expectation conflicts with anchor-calibrated nonzero physical launch dispersion. Nominal solver/drag unchanged. |
| ON | CG.G2.500.280 | NEW_ON_MODEL_CHANGE_UNAPPROVED | Old zero-dispersion ballistic error<.35m expectation conflicts with anchor-calibrated nonzero physical launch dispersion. Nominal solver/drag unchanged. |
| ON | 1400.CG.MAIN.G5.singleNative | NEW_ON_MODEL_CHANGE_UNAPPROVED | CG vertical pointing residual1.67-1.69m exceeds symmetric1.5m floor x.78=1.17m; waits until synthetic track support is blocked. WINDOW-only reproduces, ALIGNMENT-only fires; no final gate relaxation. |
| ON | 1400.CG.PIP.G5.singleNative | NEW_ON_MODEL_CHANGE_UNAPPROVED | CG vertical pointing residual1.67-1.69m exceeds symmetric1.5m floor x.78=1.17m; waits until synthetic track support is blocked. WINDOW-only reproduces, ALIGNMENT-only fires; no final gate relaxation. |
| ON | 832.CG.MAIN.G5.singleNative | NEW_ON_MODEL_CHANGE_UNAPPROVED | CG vertical pointing residual1.67-1.69m exceeds symmetric1.5m floor x.78=1.17m; waits until synthetic track support is blocked. WINDOW-only reproduces, ALIGNMENT-only fires; no final gate relaxation. |
| ON | 832.CG.PIP.G5.singleNative | NEW_ON_MODEL_CHANGE_UNAPPROVED | CG vertical pointing residual1.67-1.69m exceeds symmetric1.5m floor x.78=1.17m; waits until synthetic track support is blocked. WINDOW-only reproduces, ALIGNMENT-only fires; no final gate relaxation. |

새 ON24개 단언은 사용자 검토 사항으로 남긴다. 원래 null-dereference 중단은 원시log에 그대로 있고, continuation은 이벤트가 없을 때FALSE로 기록해 나머지 단언까지 도달한 별도 진단이다. 원래 기대를 통과로 바꾸지 않았다.

속도 우려 이후 중단한 중복 rawONMapDUI는 rc−15로 남기고 이미 실제213/213 통과한 canonicalON 이관에 연결했다. 재사용4항목은 exit:null로 표시하며 fresh실행으로 세지 않는다. [부하 정리](evidence/validation-load-reduction.json).

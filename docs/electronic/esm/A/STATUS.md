# ESM_A status

- Branch: `esm-a`
- Baseline: merged EMCON_B `main@babb4d7f6d42cc8d774feadce17d8108b3a24040`
- Current phase: Commits A-E implemented; corrected checkpoint is blocked for user approval before final packaging/PR
- Product behavior changed: ESM contacts retain anonymous historical measurements, may fuse allied raw AOA/TDOA/FDOA, may create a bounded operator-only Harpoon coordinate route without track authority, and now use DDG/CG profile-bound passive receiver adapters with full lifecycle persistence
- Broad regression runs used: 1 / 1 allowed, on pre-correction SHA `1f0b041...`; not direct evidence for the corrected SHA
- Commit A checkpoint: `ac90820`
- Commit B limited gate: PASS (`B_GATE.json`)
- Commit B checkpoint: `92ba252`
- Commit C limited gate: PASS (`C_GATE.json`)
- Commit C checkpoint: `d791fce`
- Commit D limited gate: PASS (`D_GATE.json`)
- Commit D predecessor recheck: PASS (`D_PREDECESSOR_RECHECK.json`)
- Commit E limited gate: PASS (`E_GATE.json`)
- Corrected candidate: `5dcc6201d6acf32f56d570b01bbb33b673d835505ff877e70796e60a4bd3dad7` (`22,182,527` bytes)
- Correction limited gates: B/C/D/D-predecessor/E PASS
- Corrected paired comparison: 36/42 raw exact; the 6 remaining differences are solely the required new `state.esmA` save field. Removing only that field yields 6/6 exact physical, observer and offboard state.
- Approval needed: classify the required save-schema addition and decide whether a replacement broad run is authorized for the corrected SHA.
- Release: false

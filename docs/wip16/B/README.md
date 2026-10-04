# WIP16B — C5 renderer integration

WIP16A frozen HTML remains the rebuild baseline. WIP16B changes presentation and diagnostic binding only. The compressed records 0–12 and all main-script source before the 3D renderer are byte-identical.

## Reproduced cause

The mandatory entry/exit surfaces **are found** on `HULL_3:SIM_antifoul`. On the high-quality SwiftShader interior view, repeated GPU submissions starve the cooperative geometry queue. The baseline capture reached only 221 generator yields, zero commits and geometry revision zero after 65.7 seconds. `meshMatched:false` in the old audit describes unpublished geometry; it does not prove the surface ray failed. Baseline progress is recorded in `evidence/baseline.json`.

The renderer contract also still refers to the legacy upper-starboard radar placement, 14 old mast draws, procedural Mk45 object name, WIP11 aft geometry and six separately named liferafts. The C5 model uses registered semantic assemblies, a mast-center navigation scanner, 17 mast draws and source-derived envelope diagnostics. The imported root was missing its protection-schema diagnostic binding.

## Changes

- Keep the existing canvas while the mandatory aperture job runs. Finish its cooperative geometry commit before another costly GPU submission. Simulation ticks, cuts, fold geometry, source opening area and job budgets remain unchanged.
- Bind the imported root to the existing protection schema.
- Resolve the actual navigation rotor in ship-local coordinates, including its nested mast transforms; check registered SI origin, parent chain, rotor pose, two scanner meshes, all mast parts, exactly 17 mast draws and exactly one functional navigation rotor.
- Audit current C5 envelope, model, all 96 VLS cell-to-hinge/panel bindings, gun joint hierarchy, profile binding, controls and interior/crew contracts. The old six-canister liferaft audit is explicitly inapplicable to this C5 asset; it is not recorded as passing.
- Retain the legacy audit path for `?c5model=legacy`.

No sensor performance, weapon guidance, firing, navigation, damage solver, interior topology, geometry asset or combat RNG change is included.

## Rebuild and checks

```sh
python docs/wip16/B/build_wip16b.py Aegis_SIM_v48_WIP16A.html /tmp/Aegis_SIM_v48_WIP16B.html
cmp Aegis_SIM_v48_WIP16B.html /tmp/Aegis_SIM_v48_WIP16B.html
python docs/wip16/B/tests/package16b.py Aegis_SIM_v48_WIP16B.html Aegis_SIM_v48_WIP16A.html
python docs/wip16/B/tests/render16b.py Aegis_SIM_v48_WIP16B.html artifacts/wip16b/renderer
python docs/wip16/A/tests/runtime16a.py Aegis_SIM_v48_WIP16B.html
```

Package checks cover record hashes, all executable JavaScript, source/asset preservation and exact reconstruction. Chromium checks require actual geometry replacement, clear aperture center rays on both hull sides, unchanged authoritative state, interior/crew representation and complete geometry restoration. Captures use the LOW presentation preset after the initial HIGH-preset aperture test. Runtime acceptance retains all original 13 conditions and thresholds, fixes the existing fallback boot seed before initialization, closes old phase contexts and adds a full same-seed benchmark repeat check (14 conditions total). The same-seed A and B full benchmark and spotting output match exactly.

Post-upload repetition exposed a 65 s software-GPU deadline failure while geometry was still progressing and a runtime failure with a randomly seeded initial environment. Both failures remain in the evidence. The two geometry harnesses now allow a bounded 180 s completion wait; their commit, mesh/ray and read-only assertions are unchanged. The simulator HTML and algorithms remain frozen.

Both the B workflow and `aegis-3d-render` reconstruct WIP16B to a separate temporary path and compare any uploaded HTML before testing it. The B workflow uses the uploaded file without overwriting it; before upload only, it copies the reconstruction into the candidate path. A mismatch fails the job. Other historical smoke jobs still retain their own payload selection rules.

## Delivery boundary

The user uploaded WIP16B to `WIP16` at `7562bb0925e2b85521d37fefd2c81898ed6de18a`. Remote size and Git blob exactly match the frozen local candidate. No large HTML upload through the connector, new branch, main merge, stable-version promotion or release/tag is performed. Final evidence and SHA-256 are recorded in `AEGIS_PLAN_STATUS_v48_WIP16B.md` and `evidence/upload_closeout.json`. The earlier implementation evidence remains unchanged; post-upload and upload-guard CI are recorded separately.

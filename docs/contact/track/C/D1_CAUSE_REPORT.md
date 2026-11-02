# D1 two new exact-state differences — causal replay

Status: cause reproduced; **not an automatic approval**. Exact expectations may be updated only after all directive §5 gates and the frozen60-pair statistics pass. No game code or coefficient was changed after the candidate was frozen.

Four extra replays used the same original `__CIWS_DMG_A__.run()` fixture: R4/C × seeds419015/419026. Passive physical-boundary and anonymous measurement/cost logging was added only to test builds. All four full native original D1 signatures match their uninstrumented30-seed execution exactly. Captures: `evidence/d1-cause/{R4,C}-{seed}.json.gz`; original inputs/helpers and receipt hashes are retained there. No sample was substituted into the primary30-seed dataset.

| Seed | First matching RF observation with a different accepted local file | Legacy distance choice | Candidate native P+R choice | HOLD at first fork |
|---|---|---|---|---|
|419015|step350 /5.833333s; C55 mount2; AFTER_ACTION physical `ASM:2`|file−5500002:80.4428m, corresponding NIS19.9199|file−5500003:413.7212m, NIS0.4371068|none|
|419026|step100 /1.666667s; C55 mount2; AFTER_ACTION physical `ASM:2`|file−5500001:176.3453m, corresponding NIS6.9452|file−5500003:357.2429m, NIS0.7203685|none|

The new selector does **not** choose the closest mean in metres. The more distant file has much larger native uncertainty, so the same measured innovation has smaller normalized cost. The shared δ=1 solver selects it. This is a real association change, not merely a diagnostic identifier change and not an RF/Pd or KF-gain adjustment. The full covariance inputs, measured R, unchanged native distance eligibility and the original legacy candidate distances/gates are in `ANALYSIS.json`. NIS values for the old choice were calculated offline from the recorded native inputs; no native corrector or RF calculation was rerun to create them.

Both files are still tentative at seed419015's first fork. At419026 the legacy-selected file is confirmed and the new selected file is tentative. This documents the existing-NIS preference for a diffuse file; it is not presented as universally better tracking. No compensating gate or cost weight was added. Actual defense timing and the preregistered terminal outcomes determine acceptance.

| Seed | Native RAM launch steps R4→C | First Phalanx fire R4→C | Phalanx rounds R4→C | Terminal outcome |
|---|---|---|---|---|
|419015|1024→1024|none→none|0→0|one native intercept kill in both; no ship contact|
|419026|881/1362/1711/1969→883/1374/1724/1978|1935→1925|85→80|one native damaging ship contact in both; no additional leaker/hit callback|

419026's RAM releases move by2/12/13/9 fixed ticks (maximum0.216667s), while Phalanx starts0.166667s earlier. Final impact geometry, damage details and global RNG branch then differ; the source did not alter damage/Pk RNG. R4 global RNG1105839416→C3649404874. At419015 global RNG1431530827 is unchanged; the final signature has a local file reference change and small downstream physical differences (for example terminal projectile speed changes by about2.03e−7m/s). Neither case is described as “all internal states identical.”

The full stable after-state difference lists are preserved in `evidence/D1_SIGNATURE_DELTAS.json`:35 leaves at419015 and8030 at419026. Timing/diagnostic fields have not been used to erase physical differences. Original fixture signature normalization remains unchanged.

The primary D1 result is computed from all30 fixed seeds, including these two: R4/C physical-contact leakers4/4, damaging native callbacks4/4, kills22/22, egress0/0. Every initial ASM reaches native terminal state. All30 per-seed primary differences are zero. The original `shipHits` helper counter remains8/8; it includes four explicit `miss:true,dmg:0` records per product, so it is kept separately from physical ship contacts (`D1_ANALYSIS_CONTRACT.json`). HP does not enter the acceptance rule.

The extra replay also preserves RF synthesis and local measurement records **before** association, including measurements which subsequently receive no KF update. This supplies full-stage lineage examples in addition to the120 statistical runs' accepted RF→association→KF records and batch HOLD records. Physical labels stay in the test-only recorder; no label or result is fed into tracking, identity, authorization, sensors or weapons.

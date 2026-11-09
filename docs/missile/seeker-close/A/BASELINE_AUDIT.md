# SEEKER_CLOSE_A Commit A — baseline audit

Status: **PASS**. This audit is read-only; product/RNG/save mutation count is **0**.

## Frozen baseline

- main merge commit: `78b01165bad64e9c6dc384ff070a70f868da5113`
- HP_A PR #77 head: `a3e45f7cfb5cecc1f7180e24ee3fbf35197458f5`
- HP_A product: `22,200,135` bytes, `9121c44884ff808b295a4ddff61af93a3ed47f6e8c63956acf7a3339d24836fa`
- packed main: `40,927,903` bytes, `0ea0f4535a4d193dc686ba4bba2ba86509a04ba310cad90992324e188996d464`

## Historical reference (not a current pass target)

TRACK-B R4: SEEKER_LOSS 36 / DECOY_LURE 0 / OTHER 3.  TRACK-C: 34 / 0 / 3.
Both populations contained 320 initial ASMs.  These values are retained only as an alarm and provenance record; no current-product threshold or tuning target is derived from them.

## Classification contract

Terminal categories: `DEFENSE_INTERCEPT`, `CIWS_KILL`, `DECOY_SEDUCTION`, `TARGET_HIT`, `KINEMATIC_MISS`, `SEA_IMPACT`, `GUIDANCE_CONTROL_LOSS`, `SEEKER_NO_VALID_MEASUREMENT`, `SEEKER_ASSOCIATION_DROP`, `SEEKER_GATE_REJECT`, `SEEKER_SEARCH_ACQUIRE_LOOP`, `SEEKER_COAST_TIMEOUT`, `TARGET_REMOVED_OR_INVALID`, `UNCLASSIFIED`.

Decoy stages: `NOT_DEPLOYED`, `DEPLOYED_OUTSIDE_WINDOW`, `DEPLOYED_NOT_OBSERVABLE`, `OBSERVABLE_GATE_REJECTED`, `CANDIDATE_NOT_SELECTED`, `SELECTED_THEN_RECOVERED_TARGET`, `SEDUCED`.

The classifier is AFTER_ACTION-only.  It may compare truth after terminal for diagnosis, but no physical ID or hidden coordinate enters the seeker, guidance, association, ROE, or weapon authority path.  Ambiguous evidence stays `UNCLASSIFIED`.

## Frozen function hashes

| Group | Function | Occurrence | Line | SHA-256 |
|---|---|---:|---:|---|
| common_association_state | `seekerU4SelectIndexC` | 1 | 54423 | `48d4092defacbc43c58cc735c877daae9255ff3772dd33a7f58bb326c0313393` |
| common_association_state | `seekerU4StateSnapshotC` | 1 | 54430 | `76bcfc9d9dfb2ce5b60b395f11d566948108f2e2b06015f9d6224de551afe394` |
| common_association_state | `seekerU4RecordTransitionC` | 1 | 54437 | `16c16186b3315dbfcd377fed52fbe2bb1638f2662aa73e81e9a92e70376eb539` |
| common_association_state | `seekerU4RunPolicyC` | 1 | 54448 | `ee48f1abea4f68dc3de996bca140ce4c4027bdd5625e2cbe8d87180af00b2782` |
| asm_sensor_and_guidance | `createAsmSeekerState` | 1 | 32209 | `661baabe35905ae3b27fd30e548fa5da4a59b1d45dd3ce06a4515240d749ac8c` |
| asm_sensor_and_guidance | `asmSeekerWorldRfReturnsWip13A` | 1 | 32565 | `5f275eb273168c3c8e3841e83b3194fd088b396c49456f6439350321da405fed` |
| asm_sensor_and_guidance | `asmSeekerVisibleRfReturns` | 1 | 32612 | `43a29c014c0f3e29fe4620d505e0946003ec3a09e2124c0fc87481852bab3bf1` |
| asm_sensor_and_guidance | `asmSeekerCompositeReturns` | 1 | 56865 | `a467d09f9418554a8077e20dfa151dd2285aeda670d41258388e003c26d999f7` |
| asm_sensor_and_guidance | `asmSeekerEchoMeasurement` | 1 | 32928 | `a1e5aea6d6ab3daf2a22875b068b18bc6f1070511c33fa1dc0b444e16991a0f3` |
| asm_sensor_and_guidance | `asmSeekerAssociationGates` | 1 | 32961 | `bb50dcde69cda38fdde8bd3fe019bd939748efe4e4003726d586a37bf3a4c9f6` |
| asm_sensor_and_guidance | `asmSeekerAssociateMeasurements` | 1 | 32967 | `f7ea301ede721b3dddf0e81657bcae9eea919eebf644343272d92f068c626a6e` |
| asm_sensor_and_guidance | `asmSeekerMeasurement` | 1 | 32995 | `e2fcd2be3ba67ad5f9015eb7a75d3cb4d48a3bb91a46292d33f240e0b09ec7c6` |
| asm_sensor_and_guidance | `updateAsmSeeker` | 1 | 33042 | `24e0103fbc0363a37dc43c435dc735df33ab594df47e7f229e916a8c2ceddb1b` |
| asm_sensor_and_guidance | `asmPassedTarget3D` | 1 | 32833 | `4744684c1814f723b14e038b9d318ec8c88603ecfe63551afcf216ad8e5efd35` |
| asm_sensor_and_guidance | `updateEnemyMissileBaseC52` | 1 | 33258 | `6dd99d6d500f2b382f05e4d5af523e5ee592f51eb7322bc47462fa56a372103b` |
| harpoon | `harpoonMemoryA` | 1 | 58650 | `70b445a004f1c19ce3cfaff9b95cff321590f63a096d34af33623ab274149f8a` |
| harpoon | `harpoonPredictionA` | 1 | 58659 | `1def723237831730ce425f251e1745a4e7d6c9170dd8096f80fa23c88d24b737` |
| harpoon | `harpoonRfObservationsA` | 1 | 58852 | `2643b0fc1f4be509394557150230aa3a84281a129659ff6755b334ab5dff6685` |
| harpoon | `harpoonSeekerA` | 1 | 58935 | `1eddbaea3b2bc6eb9167179c7e54337f3b246a72e7209c9a0a575a790b8a8636` |
| harpoon | `harpoonFinishA` | 1 | 58955 | `41d2b139e9154973a5c85ab925e0e9aa2d12a33c6e32dcc8849533397ce57dac` |
| harpoon | `harpoonImpactA` | 1 | 58959 | `2c4ffd5295404ddbb7afa54e89d7c21a8d3958481b941af790b98c5e20c4545b` |
| soft_kill_and_decoys | `nulkaFire15B` | 1 | 1882 | `031f0b3b9cffc8a4f649782051c8ae9776ab2c341a979bf4318df7c710fd5561` |
| soft_kill_and_decoys | `nulkaFire15B` | 2 | 3950 | `04f29ea961938eb81969a6ce7d1b5f57d8c181aff36b93bb2459cd2937355068` |
| soft_kill_and_decoys | `nulkaFlight15B` | 1 | 1909 | `42cc38001fd8821865895bd808550d8c9ed321a6e896095c84e07bda7ff98661` |
| soft_kill_and_decoys | `nulkaRfReturns15B` | 1 | 1952 | `6d43821fa8d84a23ef3a948c6071c514e0228c99ccccca6ca98ebc23efdc62a1` |
| soft_kill_and_decoys | `deployOwnChaffForThreat` | 1 | 4069 | `dd18405813750ef1ea83a5a105e670be93797771303db0631b905cfccea1c70f` |
| soft_kill_and_decoys | `deployOwnChaffForThreat` | 2 | 30694 | `11a020125b2ccd3a36e5b76205d25bb939355751ed19f4b82f60ba44dabaa576` |
| soft_kill_and_decoys | `getOwnChaffRadarReturns` | 1 | 30754 | `e82d4ad7100d385896b1d08c9a1c7d146f4541ffd945a778fbe86b4c5643fa14` |
| soft_kill_and_decoys | `updateSoftKillThreatManager` | 1 | 4087 | `dbbd6816d93aaa7a962fb4580b65acafeb75990a2b0e9155e50bb716d3208e59` |
| soft_kill_and_decoys | `updateSoftKillThreatManager` | 2 | 30293 | `6cc6f76ec5fe6fbba307643a392917774fcd574e0f1f41f73de0eb3fa247d25e` |
| soft_kill_and_decoys | `softKillDoctrineAuditSnapshot` | 1 | 4298 | `8f6397beed578412527e15caba5aea323c44ebf0b9ed1f967e9b56efaf1af499` |
| soft_kill_and_decoys | `softKillDoctrineAuditSnapshot` | 2 | 30509 | `392316b4a51a6a6f6c82a37f2411aef96db7f1bae0cacd8b00a77346bf6766ac` |

# DEFENSE_OODA_A Commit C — SHADOW gate

Status: `PASS`, authoritative evidence `C_SHADOW_GATE_ATTEMPT_7.json`.

## Candidate

- stage: `C / SHADOW`
- HTML bytes: `22,224,215`
- HTML SHA-256: `2892bf1b54fc7ea5f18d98bde768b985614c11bcbd42d328691fe6c994048034`
- packed-main SHA-256: `805e781c529842818edd6f03f4401d0041f27ff2d5954b4ec639e781aaf4c861`
- actual command provider: `LEGACY_H1`
- shadow provider: `DEFENSE_OODA_A`

## Result

Both ship profiles were run once as active owner and once as foreign-friendly
owner, then the complete pair was repeated with seed `481802`.

- active and foreign OODA reached `READY`;
- owner/profile state remained isolated;
- actual consumed command remained `LEGACY_H1`;
- forbidden/unclassified shadow differences: 0;
- validation, RNG and truth audit failures: 0;
- OODA rejection and fallback count: 0;
- MANUAL/HOLD automatic releases: 0;
- native-salvo upper bound, re-engagement reduction, stale-command rejection,
  fixed-step 1×/8×/16× equivalence and owner-local save/load: PASS;
- downlink data remained observation provenance: it did not create authority or
  local FCS, and the command schema gained no authority field;
- the existing C55 local-defense self-test remained independent and passed.

The OODA command digest, queue/phase/ready step, discrete legacy order/salvo and
all audit counters repeated exactly. The raw report also preserves diagnostic
`LEGACY_H1` floating priority-score jitter of about `1e-7` caused by the
pre-existing live tactical score. It is not an OODA input or command-digest
difference and is explicitly excluded from the OODA determinism comparison.

`C_GAMEPLAY_PARITY.json` compares the complete Integration Baseline browser
oracle after removing only the declared new save snapshot. Its normalized
gameplay digest is exact:

`f903ffc67eb8d78816d45f43bba292ec27f1c9e3aab1595b749dbb99b1995913`

No expectation, tolerance, sensor/weapon coefficient or game constant changed.

## Preserved diagnostic attempts

- attempt 1 used an incorrect MANUAL baseline before a fixture reset and also
  compared wall-clock-bearing diagnostic output;
- attempt 2 fixed the MANUAL baseline but still compared raw diagnostic output;
- attempt 3 identified that all remaining differences were only tiny legacy
  priority-score floats;
- attempt 4 stopped before assertions because the oracle called the pause
  method on the wrong diagnostic object;
- attempt 5 confirmed pausing does not eliminate the pre-existing legacy score
  jitter;
- attempt 6 established the correct OODA-specific determinism scope;
- attempt 7 repeated that scope after the downlink/stale/scale contract tests
  were added and is the authoritative pass.

These are test-harness corrections only. The stage-C product policy values were
not tuned between attempts.

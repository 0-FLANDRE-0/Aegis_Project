# U1 DTO, units, and RNG-adapter equivalence

## Status header

- IMPLEMENTED: common `EchoSample`, `ResolvedCell`, `Measurement`, `TargetCue`, and `SeekerEstimate` DTO boundary; SI unit contract; read-only profile views; pass-through RNG adapters
- TESTED: six weapon paths, 200 fixed cases per path, U0 ACTIVE versus U1 SHADOW
- APPROVED: U1 ACTIVE is permitted only because every tested legacy result is bit-equal and the adapter consumes no RNG
- UNRESOLVED: weapon-specific calculations remain delegated to their legacy implementations by design; echo/cell calculation commonality belongs to U2
- RELEASE: no release or tag; PR only

Overall: **PASS**

## Exact comparison

| Path | Cases | Different results | Page errors |
|---|---:|---:|---:|
| Kh-35U WIP22 ARH | 200 | 0 | 0 |
| Kh-32 WIP22 ARH | 200 | 0 | 0 |
| RGM-84D Harpoon ARH | 200 | 0 | 0 |
| SM-2 / ESSM Block 1 SARH and ESSM Block 2 ARH fixture | 200 | 0 | 0 |
| SM-6 Block IA ARH, air and surface modes | 200 | 0 | 0 |
| RAM Block 1A passive RF / IR | 200 | 0 | 0 |
| **Total** | **1,200** | **0** | **0** |

The baseline and U1 SHADOW runs together executed 2,400 cases. Wall time was 2,491.040 s. The detailed case-by-case result is `U1_SHADOW_EQUIVALENCE.json` (SHA-256 `61e40657ef16a684ee1fcee937ec95ee55a6c4807f9293366ba19446f9da98eb`).

## Contract audit

- Units: metres, radians, metres per second, square metres, SI-squared covariance, dimensionless SNR.
- Observation dimensions: `ACTIVE_MONOSTATIC_4D`, `SARH_BISTATIC_4D`, `PASSIVE_RF_2D`, `PASSIVE_IR_2D`.
- DTO serialization forbidden-field scan: `entityId`, `profileId`, `truthRef`, `_debugSourceId`, and the injected sentinel value were all absent.
- `truthUsed`: `false`.
- RNG policy: wrappers retain each weapon's existing handle and do not call it themselves; legacy functions remain the sole consumers, which is corroborated by exact result equality.
- Original profile objects are never written; the common profile API returns frozen SI views.

## Build identity

- U0 ACTIVE diagnostic input: `c7def46b0c696c775d08cacc6105f488e94b1f4fda08547f1d01e49b1654a757`
- U1 SHADOW diagnostic input: `ede9ed27e67a81cae0c711c746391fece282e8b17d8fa7acc5f7ee952eab00c4`
- U1 SHADOW product HTML: `5e1dd755962a8dcc7d4a002d1c9ba30e6b3ea549a6852f8dec82f33ffdf66f89`


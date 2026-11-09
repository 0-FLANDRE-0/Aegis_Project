# HP_A Commit A — baseline audit and deterministic evidence

## Frozen base

- HP_A base `main`: `82617839e64ea6b70d33ca55b13b3114cca62f3e`
- Product: `Aegis_SIM_v48_WIP_SEEKER_UNIFY_U4.html`
- Bytes: `22,195,923`
- SHA-256: `00d36aad194990b742bed3816de7eaca31ca135aef27fcf1f94106df3a6fc498`

Commit A changes no product behavior. `audit_baseline.py` freezes the packed-main
hash, relevant function hashes, every textual HP consumer, and the invalid
authority reads/writes found before implementation.

## Reproduction result

The archived Kh-35 scene (`seed 729300`, 60 km, 15 kt) was rerun through the
actual U4 missile and damage path. It hit the ship, but the present U4 outcome
was `display cache HP 13.370711...`, `FLOODING`, `irreversible=false`; therefore
the specifically reported one-shot Kh-35 false zero was **not reproduced**.
No seed search was performed.

The same exact U4 candidate already contains a deterministic authority-conflict
fixture in its frozen SOV casualty evidence: the compatibility HP is `0` while
survival is `FLOODING`, `irreversible=false`, `lost=false`. That fixture is not
mislabelled as a one-shot Kh-35 case. Its later states provide the separate
physical control: `SINKING/irreversible=true` followed by `LOST/lost=true`.

This split satisfies the pre-change gate honestly: the general defect is
reproduced on the exact base candidate, the requested Kh-35 scene is marked
non-reproduced, and the physical-loss control remains independent.

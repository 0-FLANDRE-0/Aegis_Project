# Defense call graph at the HP_A baseline

## Player / active owner

```text
owner-local sensors and received reports
  -> Track Manager (EKF, covariance, age, A3 evidence)
  -> updateTrackOperationalStateA3
  -> wip118UpdateKillAssessment / wip118ThreatRows
  -> tacticalEvaluateH1
  -> tacticalOrderH1
  -> WIP118 CPA / NEZ / inventory preview / SPG plan
  -> tacticalSalvoH1
  -> tacticalRecommendationOrderH1
  -> wip119BuildCandidateRows
  -> wip119EvaluateRow
       -> trackEngagementGateA3
       -> networkVlsGateG
       -> FCS quality / SPG reservation / reserve / reengagement / damage / EMCON
  -> wip119FireOne
  -> formal VLS/ESSM/SM-2/SM-6 release
  -> cell consumption and physical missile
```

The future port is inserted only around the four H1 decision calls shown above. WIP118 CPA/NEZ/resource preview and every WIP119 safety/execution node remain downstream and authoritative.

## Foreign friendly/enemy physical owner

```text
owner observerC(r).tracks + owner damage/inventory/FCS
  -> execution-D lexical WIP118/WIP119 copy
  -> defenseGateE + networkVlsGateG + A3/FCS/reserve gates
  -> owner launch callback

owner C55 local RF bank (every fixed tick)
  -> defenseLocalMeasurementH4A
  -> one-tick LOCAL_SELF_DEFENCE capability
  -> defenseLocalReleaseH4A (revalidation)
  -> owner RAM / Phalanx release
```

The second path never waits for WIP118/H1/OODA evaluation and is not suppressible by an advisory command.

## Cooperative and adjacent AI ownership

```text
Network G: measured packet -> owner picture -> advisory bid/lease
                              -> networkVlsGateG -> local FCS still mandatory

H2: owner observed threats + measured traffic + chart
    -> guarded maneuver -> owner navigation order

H3: owner local surface track + operator/team consent + protected picture
    -> guarded Harpoon plan -> formal launch gates

H4: strict sender/receiver packet -> formation / attack assignment
    -> H2/H3 existing commands; no remote ordnance datalink or remote FCS
```

H2, H3, H4, Network G, H1 radar/EW ownership, and all CIWS paths are outside the defense-decision provider.

## Safety invariants frozen by the browser oracle

1. `MANUAL` and foreign `HOLD` create zero automatic launches.
2. A3, network, FCS, reserve, re-engagement, damage and release gates execute after any priority/salvo advice.
3. Network assignment does not create a fire-control file.
4. C55 local RF release uses an exact mount/file/capability identity and one-tick expiry.
5. Diagnostic truth setup is outside the live decision call graph.
6. Actual collision/damage may use truth only after a weapon has passed the release boundary.

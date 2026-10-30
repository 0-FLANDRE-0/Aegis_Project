"""Gate C-only patches: Hawklink transport and native local-observation authority."""
from pathlib import Path
HERE=Path(__file__).resolve().parent

def patch(main):
    for stub in ["function heloHawklinkSnapshotE(h){return {link:{connected:false,reason:'NOT_IMPLEMENTED',recentPlotCount:0}};}\n",
                 "function heloHawklinkResetE(owner){}\n",
                 "function heloPublishRadarPlotsE(h,plots){}\n"]:
        assert main.count(stub)==1,stub
        main=main.replace(stub,'',1)
    anchor='stepObserversC(dt);stepElectronicOwnersF(dt);networkFixedStepG(dt);teamFixedStepH4();'
    assert main.count(anchor)==1
    main=main.replace(anchor,'heloHawklinkBeforeObserversE(dt);'+anchor,1)
    needle="if(!tr)return bad('NO_TRACK');if(!authority.ok)return bad(authority.reason);\n  const readiness=surfaceMissileTrackReadinessWip13C4"
    assert main.count(needle)==2,main.count(needle)
    # Preserve coordinate/search-area launches: those return before this track branch.
    replacement="if(!tr)return bad('NO_TRACK');if(!authority.ok)return bad(authority.reason);\n  // Anonymous offboard reports do not provide local fire-control release authority.\n  if(!heloHarpoonLocalObservationE(tr,cfg.maxTrackAgeS))return bad('LOCAL_SURFACE_OBSERVATION_REQUIRED');\n  const readiness=surfaceMissileTrackReadinessWip13C4"
    main=main.replace(needle,replacement)
    needle='observerClassifyC(tr,meas);networkNoteLocalG(r,tr,meas.source);trackRefreshDerivedQuality(tr);'
    assert main.count(needle)==1
    main=main.replace(needle,"observerClassifyC(tr,meas);networkNoteLocalG(r,tr,meas.source);if(tr.observationReportsC&&meas.source!=='OFFBOARD_C')tr.observationReportsC.localAtS=now;trackRefreshDerivedQuality(tr);",1)
    needle='helicopterImplemented:false,ordnanceDatalink:false'
    assert main.count(needle)==1
    main=main.replace(needle,'helicopterImplemented:true,ordnanceDatalink:false',1)
    needle="deferred:['enemyOffenseAI','defenseAssessmentAndPendingSalvos','helicopterFlightAndSensors']"
    assert main.count(needle)==1
    main=main.replace(needle,"deferred:['enemyOffenseAI','defenseAssessmentAndPendingSalvos']",1)
    anchor='// PHYSICAL ONLY: runtime identities and geometry stop at anonymous echo extraction.\n'
    assert main.count(anchor)==1
    return main.replace(anchor,(HERE/'stage_c.js').read_text()+'\n'+anchor,1)

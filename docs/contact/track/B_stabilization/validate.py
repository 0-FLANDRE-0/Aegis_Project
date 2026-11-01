"""Evidence manifest only; never runs tests or approves a changed expectation."""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import subprocess
from zoneinfo import ZoneInfo

P=Path(__file__).resolve().parent
R=P.parents[3]
sha=lambda data:hashlib.sha256(data).hexdigest()

def read(name):
    f=P/name
    return json.loads(f.read_text()) if f.exists() else None

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--require-complete',action='store_true')
    args=parser.parse_args()
    files=['BUILD.json','BUILD_SHADOW.json','SCOPE.json','SCOPE_SHADOW.json',
           'SOURCE_PROOF.json','SOURCE_PROOF_SHADOW.json','MODE_PAIR_PROOF.json',
           'NATIVE_SUMMARY.json','evidence/original-native-full/SUMMARY.json',
           'evidence/saturation-candidate.json','evidence/saturation-128.json',
           'evidence/cost/SUMMARY.json','evidence/cost/POSTCHECKS.json',
           'REGRESSION_RESULTS.json','evidence/regression/FIRST_STAGE_COMPARISON.json',
           'BATTLE_RESULTS.json']
    evidence={f:read(f) for f in files}
    checks={}
    pins=read('BASELINE_PINS.json')
    checks['originalBInputsUnchanged']=bool(pins) and all(
        (R/n).exists() and sha((R/n).read_bytes())==v for n,v in pins['files'].items())
    for suffix in ['', '_SHADOW']:
        build=evidence['BUILD'+suffix+'.json']
        proof=evidence['SOURCE_PROOF'+suffix+'.json']
        scope=evidence['SCOPE'+suffix+'.json']
        checks['frozenHtml'+suffix]=bool(build) and sha((R/build['output']).read_bytes())==build['htmlSha256']
        checks['inverseAndEnvelope'+suffix]=bool(proof) and all(proof[k] is True for k in [
            'inverseMainBytesExact','inversePackedHtmlBytesExact','nonMainEnvelopeByteExact','originalInputsStillPinned'])
        checks['protectedScope'+suffix]=bool(scope) and scope['pass'] is True and all(
            scope[k]['pass'] is True and scope[k]['protectedSymbols']==189 and scope[k]['nestedProtectedSymbols']==161
            for k in ['againstTrackA','againstTrackB'])
    pair=evidence['MODE_PAIR_PROOF.json']
    checks['singleCompileTokenDifference']=bool(pair) and pair['pass'] is True
    native=evidence['NATIVE_SUMMARY.json']
    checks['policy39AndActualNativeMetadata']=bool(native) and native['status']=='PASS' and native['allTasksComplete'] is True
    checks['old47StrictDifferenceRetained']=bool(native) and native['originalB47Strict']['passed']==46 and native['originalB47Strict']['expectedValueUpdated'] is False
    full=evidence['evidence/original-native-full/SUMMARY.json']
    checks['originalNativeAndCohortFull']=bool(full) and full['status']=='PASS' and full['allTasksComplete'] is True
    sat=evidence['evidence/saturation-candidate.json']
    checks['largeComponentCertificates']=bool(sat) and sat['status']=='PASS' and all(sat['checks'].values())
    cost=evidence['evidence/cost/SUMMARY.json']
    post=evidence['evidence/cost/POSTCHECKS.json']
    checks['exclusiveSameWorkloadCost']=bool(cost) and cost['status']=='PASS' and all(cost['checks'].values()) and bool(post) and post['status']=='PASS'
    regression=evidence['REGRESSION_RESULTS.json']
    pending=list(regression.get('pendingSuites',[])) if regression else ['ALL_REGRESSION']
    checks['originalBroadSuitesCompleted']=bool(regression) and not pending
    first=evidence['evidence/regression/FIRST_STAGE_COMPARISON.json']
    checks['d1AndPairedFullStateAgainstDeliveredB']=bool(first) and first['d1']['deliveredBExactSignatures']==30 and all(
        all(row['fullExportedDictsExactAgainstDeliveredB'].values()) for row in first['paired'])
    battle=evidence['BATTLE_RESULTS.json']
    # Completion is distinct from all battles winning/qualifying. Preserve a
    # measured defeat or unresolved lifecycle as such in the authoritative file.
    checks['battleMatrixCollected']=bool(battle) and battle.get('completedPages')==battle.get('expectedPages') and not battle.get('pending')
    additional={}
    for name in ['evidence/native-saturation/SUMMARY.json','evidence/smoke/SMOKE_RESULTS.json','evidence/original-raid-pilot/SUMMARY.json']:
        d=read(name)
        additional[name]=d
        if name.endswith('SMOKE_RESULTS.json'):
            checks[name]=bool(d) and d.get('status')=='PASS' and d.get('freshPages')==6 and all(d['checks'].values())
        elif name.endswith('original-raid-pilot/SUMMARY.json'):
            checks[name]=bool(d) and d.get('status')=='OBSERVED_FOR_REVIEW_NOT_APPROVED' and d.get('gateFailure') is None and not d.get('errors') and not d.get('faults') and all(d.get('rawCheckpointExact',{}).values()) and all(d.get('restoredNativeRefs',{}).values())
        else:
            checks[name]=bool(d) and d.get('allTasksComplete',d.get('completed',False)) is True
    missing=[k for k,v in checks.items() if not v]
    active=evidence['BUILD.json'];shadow=evidence['BUILD_SHADOW.json']
    result={
        'schema':'AEGIS_TRACK_B_STABILIZATION_VALIDATION_1',
        'generatedAtKst':datetime.datetime.now(ZoneInfo('Asia/Seoul')).isoformat(timespec='seconds'),
        'branch':'track-b-stabilization-a',
        'implementationCommit':'5718f2d25f2e069f9ebd7948360fcf468bcdbb0b',
        'parentCommit':'1d92554026d15f417d987aec519007ea9657a6b6',
        'candidateSha256':active['htmlSha256'] if active else None,
        'shadowSha256':shadow['htmlSha256'] if shadow else None,
        'trackBStatus':'INCOMPLETE',
        'r1StabilizationStatus':'FAIL_NOT_ACCEPTED',
        'deploymentRecommendation':'DO_NOT_APPROVE_R1; natural13 worsening remains unapproved. R2 is a separate follow-up candidate.',
        'evidenceComplete':not missing,'pendingEvidence':missing,'checks':checks,
        'expectedValuesUpdated':False,'tolerancesUpdated':False,
        'sensorEkfIffRoeWeaponPhysicsAiOrSaveSchemaChanged':False,
        'releaseApproved':False,'performanceApproved':False,
        'mergePrReleaseTagCreated':False,
        'strictDifferences':[
            {'id':'PAIRED_RAID_4','count':4,'status':'FAIL_UNAPPROVED','expectationsUpdated':False},
            {'id':'D1_419012_SIGNATURE','count':1,'status':'FAIL_UNAPPROVED','expectationsUpdated':False},
            {'id':'ORIGINAL_B47_COMPONENT_13','count':1,'status':'FAIL_DECLARED_POLICY_CHANGE_UNAPPROVED','expectationsUpdated':False}],
        'newObservedCombatWorsening':{
            'scenario':'NATURAL_SATURATION_13','status':'FAIL_UNAPPROVED',
            'oldBInitialAsmAliveAt90S':1,'r1InitialAsmAliveAt90S':3,
            'oldBInitialNativeInterceptKill':7,'r1InitialNativeInterceptKill':6,
            'allComparedVersionsLegacyHpAt90S':0,
            'cause':'Same native13x13 graph has13 exact distinguishable assignments but R1 lower-bound certificates release3 and hold10. This precedes filter, resalvo and subsequent physical outcome differences.',
            'globalRngOnlyExplanationRejected':True,
            'actualTerminalBattleClaim':False},
        'legacyRaidPilotScope':'TRACK-A/DDG only;1 native intercept and7 non-ownship surface-target contacts. Does not approve the four legacy paired differences.',
        'inheritedIssues':[
            {'id':'CIWS419025','status':'FAIL_UNCHANGED'},
            {'id':'CG_TO_FRIENDLY_OBSERVER_2','status':'KNOWN_DELTA_UNAPPROVED'},
            {'id':'RETIRED_EMCON_UI14','status':'INCOMPLETE_NOT_COUNTED_PASS'}],
        'shadowOnlyNotCountedAsImplemented':['C55 live association','SPQ AIR live association'],
        'limits':['>128 connected component computation bound remains',
                  'Dense128 Node per-call p95 about42ms exceeds16.7ms budget',
                  'Own/NPC epoch is asserted by current native caller; no general historical-epoch alignment',
                  'Surface position association/native Doppler correction fallback is preserved, not fully re-solved',
                  'Legacy TRACK-A truth-boundary debts are not globally fixed'],
        'evidenceFiles':{name:sha((P/name).read_bytes()) for name,data in evidence.items() if data is not None},
        'additionalEvidenceFiles':{name:sha((P/name).read_bytes()) for name,data in additional.items() if data is not None}}
    (P/'VALIDATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['trackBStatus','evidenceComplete','pendingEvidence','releaseApproved']},ensure_ascii=False))
    return 1 if args.require_complete and missing else 0

if __name__=='__main__':raise SystemExit(main())

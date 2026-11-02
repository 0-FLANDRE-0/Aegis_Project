"""Offline report and conditional expectation record; never runs a battle."""
from pathlib import Path
import collections,hashlib,json,subprocess
from approved_expectations import pair_value,value_hash,load_approval,evaluate

P=Path(__file__).resolve().parent
R=P.parents[3]
OLD=P.with_name('B_stabilization_r4')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
LABELS={'S6':'6발 포화','S13':'13발 포화','TWO':'2발','THREE':'3발(CG)','CROSS':'교차 2발'}


def approve(result):
    assert result['decision']=='USER_CONDITIONAL_APPROVAL_CRITERION_MET'
    pair_path=OLD/'evidence/regression/paired-track-a/baseline-comparison.json'
    d1_path=OLD/'evidence/regression/d1/COMPARISON.json'
    pair=json.loads(pair_path.read_text());d1=json.loads(d1_path.read_text())
    entries=[]
    cause='기존 RF/EKF 관측으로 만든 NIS 연관의 모호성 보류/인증 정책 → canonical 관측 갱신 시점·추정/공분산 → 기존 cue/교전 선택 및 VLS 소모. R4의 foreign reacquire 작업 소유권 정정도 기존 선택 타이밍에 영향을 줌. 센서·무장·피해 계수 변경 없음.'
    for row in pair['cases']:
        if row['scenario']!='raid':continue
        for check in ['samePhysicalState','sameExistingObserverState','raidInventoryDeltaBounded']:
            old=pair_value(row['pair']['baseline'],check);new=pair_value(row['pair']['candidate'],check)
            assert old!=new and row['checks'][check]is False
            entries.append({'id':f"{row['ship']}:raid:{check}",'ship':row['ship'],'scenario':'raid','check':check,
                'oldExpected':old,'newExpected':new,'oldValueSha256':value_hash(old),'newValueSha256':value_hash(new),
                'causePath':cause,'reason':'사용자 조건부 승인: 동결 R4의 60쌍 통계 전투에서 합계 유출·피격 회차가 사전 시드 변동 판정 범위 안. 기존 원시 차이는 보존하며 이 정확 값만 갱신.',
                'source':str(pair_path.relative_to(R)),'sourceSha256':sha(pair_path)})
    row=next(r for r in d1['references']['track-a']['rows']if r['seed']==419012)
    entries.append({'id':'D1:419012:signatureSha256','seed':419012,'check':'signatureSha256',
        'oldExpected':row['referenceSignature'],'newExpected':row['candidateSignature'],
        'oldValueSha256':value_hash(row['referenceSignature']),'newValueSha256':value_hash(row['candidateSignature']),
        'causePath':'tick1796 근접 NIS 대안 보류 → frame1797 canonical 추정/P/cue 값 → frame1800 native TTI/CMS cue 순서 → 최종 mount cue A002/B001. native 전투 결과·RAM3·30.633333초는 동일. R4는 이 시드에서 기존 B와 정확 서명이 동일.',
        'reason':'사용자 조건부 승인: 통계 조건 충족 후 D1 419012의 내부 상태 서명 기대값만 갱신. 다른29시드 및 419025 결과/기대값은 변경하지 않음.',
        'causeEvidence':'docs/contact/track/B/SEED419012_CAUSE_REPORT.md',
        'source':str(d1_path.relative_to(R)),'sourceSha256':sha(d1_path),
        'outcomesBefore':row['referenceGameplay'],'outcomesAfter':row['candidateGameplay']})
    q={'schema':'AEGIS_TRACK_B_R4_USER_APPROVED_EXPECTATIONS_1',
       'authorization':'최신 사용자 지시: 같은 시드 6발20/13발10/2·3·교차각10의 통계 조건을 통과하면 R4 ACTIVE, paired6 및 D1 419012 기대값, C55/SPQ AIR 범위 분할, PR 생성·병합을 승인.',
       'statisticalResultSha256':sha(P/'RESULTS.json'),'planSha256':sha(P/'PLAN.json'),
       'reviewedHtmlSha256':pair['candidateSha256'],
       'reviewedMainSha256':'6163ada1a49dc86ce8b179b81650fa2da78ecc8d9273015142a721748abf6a64',
       'oldReferenceHtmlSha256':pair['baselineSha256'],
       'originalProjectionSha256':sha(R/'docs/radar/air-origin/A/approved_expectations.py'),
       'entries':entries,'otherExpectationsChanged':0,'tolerancesChanged':0,
       'excludedUnapproved':['CIWS419025','ORIGINAL_FRIENDLY_OBSERVER_TWO','LEGACY_EMCON_UI14']}
    dest=P/'APPROVED_EXPECTATIONS.json';save(dest,q)
    loaded=load_approval(dest,(R/'Aegis_SIM_v48_WIP_TRACK_B_STABLE_D.html').read_bytes())
    comparisons=evaluate(loaded,pair,d1);assert comparisons['status']=='PASS'
    save(P/'APPROVED_COMPARISONS.json',comparisons)
    return comparisons


def main():
    result=json.loads((P/'RESULTS.json').read_text())
    assert result['actualBattles']==120 and result['allAnchorChecksPass']
    approved=result['decision']=='USER_CONDITIONAL_APPROVAL_CRITERION_MET'
    rows=[json.loads(f.read_text())for f in(P/'evidence/runs').glob('*/attempt1/METRICS_STATISTICAL.json')]
    assert len(rows)==120 and all(r['status']=='VALID'for r in rows)
    plan=json.loads((P/'PLAN.json').read_text())
    for q in plan['products'].values():assert sha(R/q['file'])==q['sha256']
    progress=json.loads((P/'evidence/PROGRESS.json').read_text())
    assert progress['completed']==120 and progress['elapsedS']<=10800
    comparison=approve(result)if approved else None
    assert approved or not(P/'APPROVED_EXPECTATIONS.json').exists()
    secondary={}
    for case in [*LABELS,'ALL']:
        secondary[case]={}
        for prod in ['B','R4']:
            rr=[r for r in rows if r['product']==prod and(case=='ALL'or r['scenario']==case)]
            secondary[case][prod]={
                'battles':len(rr),'battlesWithDamagingHit':sum(r['damagingHitRounds']>0 for r in rr),
                'kills':sum(r['kills']for r in rr),'leakers':sum(r['leakers']for r in rr),
                'damagingHitRounds':sum(r['damagingHitRounds']for r in rr),
                'wreckDamagingCallbacks':sum(r['wreckDamagingCallbacks']for r in rr),
                'egress':sum(r['egress']for r in rr),'otherNativeTerminal':sum(r['otherNativeTerminal']for r in rr),
                'floodM3':sum(r['floodM3']for r in rr),
                'endTimeS':[min(r['end']['timeS']for r in rr),max(r['end']['timeS']for r in rr)],
                'nativeCauses':dict(collections.Counter(o['nativeCause']or'EGRESS'for r in rr for o in r['initialOutcomes']))}
    save(P/'SECONDARY_COUNTS.json',secondary)
    scope={'schema':'AEGIS_TRACK_B_R4_STATISTICAL_CURRENT_STATUS_1',
           'status':'SCOPED_ACTIVE_USER_APPROVED'if approved else result['decision'],
           'activePromotionApproved':approved,'gameBytesChangedThisStage':0,
           'active':plan['products']['R4'],'baseline':plan['products']['B'],
           'statisticalResultSha256':sha(P/'RESULTS.json'),'currentReport':'docs/contact/track/B_statistics_r4/REPORT.md',
           'expectationsUpdated':7 if approved else 0,'tolerancesUpdated':0,
           'postApprovalExactResults':comparison,
           'implementedActive':['OWN_SPY_GLOBAL','OWN_SURFACE','NPC_OBSERVER','HAWKLINK_COHORT'],
           'deferredShadowOnly':['C55','SPQ_AIR'],
           'deferralApprovedToAfterTrackC':approved,
           'inheritedNotApproved':['CIWS419025','ORIGINAL_FRIENDLY_OBSERVER_TWO','LEGACY_EMCON_UI14'],
           'physicalIdSwapFalseMergeCompleteClosureClaimed':False,
           'scopeMeaning':'Observed combat outcomes statistically assessed; this does not prove physical identity lineage for all tracks. Deferred routes remain SHADOW-only.',
           'mainMergeAuthorizedByConditionalResult':approved,'mergeExecutedByThisOfflineReport':False,
           'actualMergeReceipt':'docs/contact/track/B_statistics_r4/MERGE_READBACK.json (post-merge work-branch receipt)'}
    save(P/'STATUS.json',scope)
    save(P.parent/'CURRENT.json',scope)
    text=['# TRACK-B R4 통계 전투 검토',
          '**판정: '+('사용자 조건 충족 — R4 ACTIVE 범위 승인'if approved else result['decision'])+'**',
          '기존 B/R4 제품을 변경하지 않고 60쌍·120전투(각320기 초기 ASM)를 실제 native 센서→AUTO→무장/비행→피해 경로로 실행했다. 기존1회 결과를 승인으로 대체하지 않았다.',
          '## 실행 및 판정',
          f"실행시간 {progress['elapsedS']/60:.2f}분. 상한180분 이내. 각 전투 fresh Chromium, 동시2. 모든120개 native/runtime/누락/종말 검사를 통과했다. 6발과13발 기준 시드의 과거 기록 대비 전체/90초 상태·RNG 동등성도 통과했다.",
          '초기 ASM의 native 종말 또는 자함에서30km·10초 연속 이탈 후 전체 안정5초까지 실행했다. 이탈을 격추로 세지 않으며 게임 객체를 제거하지 않았다. 자함 피격 후에도 중단하지 않았다.',
          '피격 회차는 dmg>0·miss 아님인 native shipHitHistory callback이며 잔해 추가 타격을 포함한다. 고유 초기 유출은 중복 합산하지 않는다. 피격된 전투 수도 별도로 기록한다. HP는 승인 판정에서 제외했다.',
          '같은 시드를 공유하는 시나리오를20개 seed-block으로 묶어 정확 단측 부호교환(2^20)과 층별 paired bootstrap200000회(진단 RNG20261102)를 사용했다. 사용자 지정 시드 변동 범위 규칙이며, 사전 비열등성 마진을 둔 정식 비열등성 입증으로 확대하지 않는다.',
          '| 주요 지표 | 기존 B | R4 ACTIVE | 차이 R4−B | 총 차이95% 구간 | 단측 악화 p |',
          '|---|---:|---:|---:|---|---:|']
    for k,label in [('leakers','초기 미사일 명중/유출'),('damagingHitRounds','실제 피해 피격 회차')]:
        q=result['primary'][k];lo,hi=q['paired95PercentIntervalForTotalDifference']
        text.append(f"| {label} | {q['BTotal']} | {q['R4Total']} | {q['differenceR4MinusB']:+g} | [{lo:g}, {hi:g}] | {q['oneSidedExactWorseP']:.6f} |")
    text+=['','## 조건별 결과','표의 화살표는 기존 B → R4. 격추/유출/이탈은 초기 위협만 집계한다.',
           '| 조건 | 시드쌍 | 격추 | 유출 | 피격 회차 | 피격된 전투 | 이탈 | 침수 합계 m³ |','|---|---:|---:|---:|---:|---:|---:|---:|']
    for case,label in [*LABELS.items(),('ALL','전체')]:
        a,z=secondary[case]['B'],secondary[case]['R4']
        values=[f"{a[k]}→{z[k]}"for k in ['kills','leakers','damagingHitRounds','battlesWithDamagingHit','egress']]
        text.append(f"| {label} | {a['battles']} | "+' | '.join(values)+f" | {a['floodM3']:.6f}→{z['floodM3']:.6f} |")
    text+=['','침수는 각 사전 정의한 종료 시각의 native 물량이다. B/R4의 종료 시각이 다르며 새 물리 모델로 정규화하지 않았다. 전투별 종료 시각·피해·시드 차이는 `PAIRED_RESULTS.csv`, 상세 분류/잔해 회차는 `SECONDARY_COUNTS.json`과120개 raw에 있다. 조건별 통계는 `RESULTS.json`에 별도로 보존한다.',
           '## 처리와 보존',
           ('사용자의 조건부 승인에 따라 paired6과 D1 419012의 정확 기대값7건만 갱신했다. 이전/새 전체 값·SHA·원인 경로는 `APPROVED_EXPECTATIONS.json`, 실제 정확 재비교는 `APPROVED_COMPARISONS.json`이다. 기존 원시 FAIL 기록을 덮어쓰지 않았다. paired42/42 및 D1서명30/30은 기존 native 출력에 대한 승인 기대값 재평가이며 새 게임 실행으로 세지 않는다.'if approved else'명백한 악화 또는 미결 판정이므로 ACTIVE 승격·기대값 갱신·PR 병합을 하지 않는다. 불리한 시드를 제외하거나 게임 계수를 조정하지 않는다.'),
           '기존 native364/364·paired36/42, UI213/213, 실제 WebGL8발29/29 등은 동결 R4에서 이미 실행한 자료다. 이번 추가 실행은 요청한 통계 전투뿐이다. 승인 시 도메인 실측은406/406이 되지만, 구형 EMCON UI14는 미완료로 남겨420/420이라고 쓰지 않는다.',
           '419025 피격, 이전 friendly observer2, 구형 EMCON UI14는 별도 미승인 이슈로 유지한다. C55/SPQ AIR는 '+('사용자 조건 승인으로 TRACK-C 이후로 범위를 분할했다.'if approved else'여전히 미완료다.')+' 실제 연관은 SHADOW-only 그대로다. 물리 ID 교환·오병합의 전체 lineage 완료를 주장하지 않는다.',
           '동결 게임 HTML·RF/EKF/IFF/ROE/AI/무장·피해·함정 물리·저장 스키마/계수 변경0. 판정 계산은 게임 RNG를 사용하지 않는다. `PLAN.json`은 첫 시험 전 고정했고 합계 계산 전후에 제품·helper·실행기 해시를 검증했다.',
           '## 재현·인계',
           '사전 계획/시드/예산 `PLAN.json`, 원시 `evidence/runs/`, 상태 `STATUS.json`, 계산 `analyze.py`, 승인 비교기 `approved_expectations.py`를 함께 전달한다. 원 시험의 기존 strict 결과를 그대로 생성한 뒤 `approved_expectations.py --pair 새원시비교.json --d1 새D1비교.json`으로 해시가 같은 제품의 승인7건만 정확 재평가할 수 있다.',
           'main 병합과 원격 readback의 실제 결과는 별도 `MERGE_READBACK.json`이 있을 때 그 기록을 따른다. 이 보고서 생성 자체는 병합이 아니다.']
    rendered=[]
    for line in text:
        separator='\n'if line.startswith('|')and rendered and rendered[-1].lstrip().startswith('|')else'\n\n'
        rendered.append(separator+line)
    (P/'REPORT.md').write_text(''.join(rendered).lstrip()+'\n')
    print(json.dumps({'decision':result['decision'],'approvalRecordsCreated':approved,'expectedChanges':7 if approved else 0}))


if __name__=='__main__':main()

"""Freeze the user's 2026-11-01 approval from the already-reviewed evidence."""
from pathlib import Path
import datetime,hashlib,json
from zoneinfo import ZoneInfo
from approved_expectations import SCHEMA,IDS,load_approval,pair_value,value_hash
B=Path(__file__).resolve().parent;R=B.parents[3];E=B/'evidence'
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
build=load(B/'build.json');source=E/'regression/AIR_ORIGIN_A/paired42/baseline-comparison.json';paired=load(source);causes=load(E/'cause-analysis.json');world=load(E/'world120-comparison.json')
entries=[]
for r in paired['cases']:
 if r['scenario']!='raid':continue
 c=next(x for x in causes['records']if x['mode']=='raid'and x['ship']==r['ship']);first=c['firstDifferences']
 path=[{'stage':'receiver metadata / EKF','tick':first['tracks']['tick']},{'stage':'existing AUTO release schedule','beforeTicks':[v['tick']for v in c['launches']['MAIN']],'afterTicks':[v['tick']for v in c['launches']['AIR_ORIGIN_A']]},{'stage':'existing mass ledger / 708kg SM2 removal','tick':first['massKg']['tick']},{'stage':'existing attitude integration','tick':first['heel']['tick']}]
 for check in ['samePhysicalState','sameExistingObserverState']:
  assert r['checks'][check]is False
  old=pair_value(r['pair']['baseline'],check);new=pair_value(r['pair']['candidate'],check)
  entries.append({'id':f"{r['ship']}:raid:{check}",'kind':'paired42','ship':r['ship'],'scenario':'raid','check':check,'oldExpected':old,'newExpected':new,'oldValueSha256':value_hash(old),'newValueSha256':value_hash(new),'reason':'사용자 승인: AIR receiver 원점 계약 복구의 관측·발사 시점 차이. 32초 종료점의 피해·최종 재고·표적 결과·RNG 동일. 기대값만 정확 비교로 갱신.','causePath':path,'evidence':str(source.relative_to(R))})
w=next(r for r in world if r['mode']=='combat');assert not w['same']
entries.append({'id':'world120:combat:truthSha256','kind':'world120','scenario':'combat','check':'truthSha256','oldExpected':w['beforeHash'],'newExpected':w['afterHash'],'oldValueSha256':value_hash(w['beforeHash']),'newValueSha256':value_hash(w['afterHash']),'reason':'사용자 승인: receiver 계약 복구 후 SM-6 시커 방사·표적 회피/RNG 분기 차이. 최종 항공기 운동 7필드+RNG만 변경, 자함 물리·재고·피해 동일.','causePath':[{'stage':'first observation difference','tick':56},{'stage':'same formal VLS release','tick':900},{'stage':'SM6 ACTIVE / IOG and active RF emission','tick':4032},{'stage':'target threatened/evasion and RNG consumption','tick':4034}],'evidence':'docs/radar/air-origin/A/evidence/world120-comparison.json'})
assert {r['id']for r in entries}==IDS and len(entries)==5
q={'schema':SCHEMA,'approvalDateKst':'2026-11-01','recordedAtKst':datetime.datetime.now(ZoneInfo('Asia/Seoul')).isoformat(),'approvalSource':'사용자 명시 승인 — AIR_ORIGIN_A 보고된 불일치 5건 기대값 갱신','approvalText':'AIR_ORIGIN_A 검토 완료. 보고된 불일치 5건(도메인 습격 samePhysicalState/sameExistingObserverState 4건, 전투 world120 hash 1건)의 기대값 갱신을 승인한다. 갱신 전후 값과 원인 경로를 승인 기록 파일에 남긴다. 다른 기대값·허용 오차는 건드리지 않는다.','reviewedArtifactCommit':'d597438a55189c5790c92b876199f86d55ccfb8d','reviewedBranchHead':'891fa17a836313fdb134e26dbb6cb711fbbe44da','reviewedHtml':build['output'],'reviewedHtmlSha256':build['sha256'],'reviewedMainSha256':build['mainSha256'],'baselineMainCommit':build['baseCommit'],'otherExpectationsChanged':0,'tolerancesChanged':0,'gameHtmlChanged':False,'entries':entries,'sourceEvidence':[{'path':str(p.relative_to(R)),'sha256':sha(p)}for p in [source,E/'world120-comparison.json',E/'cause-analysis.json']],'stopPolicy':'air-origin-a commit/push/readback only; user merges; gun-b2 rebase and 60-case re-diagnosis/Phase1 report are post-merge only.'}
p=B/'approved-expectations.json';assert not p.exists(),'PRESERVE_EXISTING_APPROVAL_RECORD';p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n');load_approval(p,(R/build['output']).read_bytes());print(json.dumps({'approved':len(entries),'gameHtmlChanged':False,'otherExpectationsChanged':0,'tolerancesChanged':0}))

"""Reuse exactly the approved AIR_ORIGIN_A values; no new expected values."""
from pathlib import Path
import copy,hashlib,json,sys
P=Path(__file__).resolve().parent;R=P.parents[3];A=R/'docs/radar/air-origin/A';sys.path.insert(0,str(A));from approved_expectations import load_approval,pair_value
manifest=load_approval(A/'approved-expectations.json',(R/'Aegis_SIM_v48_WIP_AIR_ORIGIN_A.html').read_bytes());f=P/'evidence/regression/ON/paired42/baseline-comparison.json';q=json.loads(f.read_text());rows=[]
for r in q['cases']:
 checks=dict(r['checks']);entries=[e for e in manifest['entries']if e.get('ship')==r['ship']and e.get('scenario')==r['scenario']]
 for e in entries:checks[e['check']]=pair_value(r['pair']['candidate'],e['check'])==e['newExpected']
 rows.append({'ship':r['ship'],'scenario':r['scenario'],'originalChecks':r['checks'],'approvedChecks':checks,'existingApprovalIds':[e['id']for e in entries]})
old=json.loads((P.parent/'phase1a/evidence/regression/ON/paired42/baseline-comparison.json').read_text());same={}
for r in q['cases']:
 b=next(x for x in old['cases']if(x['ship'],x['scenario'])==(r['ship'],r['scenario']));same[r['ship']+':'+r['scenario']]=r['pair']['candidate']==b['pair']['candidate']
result={'pass':all(all(r['approvedChecks'].values())for r in rows)and not q['errors'],'checkCount':sum(len(r['approvedChecks'])for r in rows),'rows':rows,'sameCandidateStateAsB2A':same,'newExpectedValues':0,'tolerancesChanged':0,'approvalSha256':hashlib.sha256((A/'approved-expectations.json').read_bytes()).hexdigest(),'approvalGuard':'Original manifest validates reviewed AIR_ORIGIN_A expectations; B2B scope audit proves all non-five-inch paths byte-identical to B2A.'};assert result['checkCount']==42;(P/'evidence/paired42-approved.json').write_text(json.dumps(result,indent=2)+'\n');print(result['pass'],same);raise SystemExit(not result['pass'])

"""Immutable GitHub ZIP/HTML readback; no remote writes."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,re,subprocess,time

P=Path(__file__).resolve().parent
R=P.parents[3]
spec=importlib.util.spec_from_file_location('original_streaming_github_readback',P.with_name('B_stabilization_r4')/'remote_readback.py')
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--commit',required=True);a=ap.parse_args()
    assert re.fullmatch('[0-9a-f]{40}',a.commit)
    artifact=json.loads((P/'ARTIFACTS.json').read_text());rows=artifact['archives']+[artifact['html']]
    for f in [P/'RESULTS.json',P/'STATUS.json',P/'ARTIFACTS.json',P/'APPROVED_EXPECTATIONS.json',
              R/'docs/contact/track/CURRENT.json',R/'deliverables/track-b-statistics-r4/SHA256SUMS.txt']:
        if f.exists():rows.append({'path':str(f.relative_to(R)),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
    receipts=[]
    for row in rows:
        assert old.local_sha(R/row['path'])==row['sha256']
        receipt=old.download(a.commit,row);receipts.append(receipt)
        print(json.dumps({'path':row['path'],'sha256Matches':receipt['sha256Matches'],'bytes':receipt['bytes']}),flush=True)
    names=['main','track-b-stabilization-a','track-b-association','track-a-contract-trace','friendly-contact-a','ciws-dmg-a']
    output=subprocess.check_output(['git','ls-remote','origin',*['refs/heads/'+n for n in names]],cwd=R,text=True)
    refs={line.split()[1]:line.split()[0]for line in output.splitlines()}
    assert refs['refs/heads/track-b-stabilization-a']==a.commit
    record={'schema':'AEGIS_TRACK_B_R4_STATISTICS_REMOTE_READBACK_1','stage':'PRE_MERGE_ARTIFACT_BYTES',
            'status':'PASS','artifactCommit':a.commit,'readbackUtc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
            'files':receipts,'remoteRefsAtReadback':refs,'expectedSourceBranch':'track-b-stabilization-a',
            'statisticalDecision':artifact['decision'],'mainMergeRecordedSeparately':True}
    (P/'REMOTE_READBACK.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({'status':'PASS','files':len(rows),'artifactCommit':a.commit}))


if __name__=='__main__':main()

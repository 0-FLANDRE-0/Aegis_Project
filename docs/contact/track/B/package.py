"""Separate final ACTIVE/SHADOW HTML downloads and evidence-only report ZIP."""
from pathlib import Path
import gzip,hashlib,json,zipfile

P=Path(__file__).resolve().parent;R=P.parents[3];D=R/'downloads';D.mkdir(exist_ok=True)
sha=lambda data:hashlib.sha256(data).hexdigest()
validation=json.loads((P/'VALIDATION.json').read_text())
assert validation['finalEvidenceComplete'] is True, 'Do not publish pending evidence as complete'
assert validation['releaseApproved'] is False
builds=[json.loads((P/name).read_text())for name in ['BUILD.json','BUILD_SHADOW.json']]
for build in builds:
    assert build['inverseByteExact'] is True
    assert sha((R/build['output']).read_bytes())==build['htmlSha256']
assert validation['candidateSha256']==builds[0]['htmlSha256']
assert validation['shadowSha256']==builds[1]['htmlSha256']

# Lossless transport compression, never reinterpret/reclassify an old result.
history_path=P/'RAW_COMPRESSION.json'
history=json.loads(history_path.read_text())if history_path.exists()else[]
for source in sorted((P/'evidence').rglob('*.jsonl')):
    data=source.read_bytes();target=Path(str(source)+'.gz');assert not target.exists(),target
    packed=gzip.compress(data,6,mtime=0);target.write_bytes(packed);assert gzip.decompress(packed)==data
    history.append({'original':str(source.relative_to(P)),'gzip':str(target.relative_to(P)),
                    'originalSha256':sha(data),'gzipSha256':sha(packed),
                    'originalBytes':len(data),'gzipBytes':len(packed),'losslessVerified':True})
    source.unlink()
history_path.write_text(json.dumps(history,indent=2)+'\n')

def include(path):
    return(path.is_file()and'__pycache__'not in path.parts
           and path.name not in ['REMOTE_READBACK.json','STOP_AFTER_CURRENT']
           and path.suffix not in ['.flag','.pyc','.html'])

files=[f for f in sorted(P.rglob('*'))if include(f)and f.name!='CHECKSUMS.sha256']
(P/'CHECKSUMS.sha256').write_text(''.join(sha(f.read_bytes())+'  '+str(f.relative_to(P))+'\n'for f in files))

def zip_verified(target,entries):
    with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6)as z:
        for name,source in entries:
            info=zipfile.ZipInfo(name,date_time=(2026,11,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
            z.writestr(info,source.read_bytes())
    assert target.stat().st_size<100*1024*1024,'GitHub file limit: split evidence explicitly, never omit failures'
    with zipfile.ZipFile(target)as z:
        assert z.testzip()is None
        assert z.namelist()==[name for name,_ in entries]
        for name,source in entries:assert sha(z.read(name))==sha(source.read_bytes()),name

groups={
 'HTML':[(builds[0]['output'],R/builds[0]['output'])],
 'SHADOW_HTML':[(builds[1]['output'],R/builds[1]['output'])],
 'REPORT':[('TRACK_B/'+str(f.relative_to(P)),f)for f in sorted(P.rglob('*'))if include(f)],
}
artifacts=[]
for label,entries in groups.items():
    target=D/('Aegis_SIM_v48_WIP_TRACK_B_'+label+'.zip');zip_verified(target,entries)
    artifacts.append({'kind':label,'path':str(target.relative_to(R)),'sha256':sha(target.read_bytes()),
                      'bytes':target.stat().st_size,'members':len(entries),'allMembersReadBackAndHashVerified':True})
(D/'TRACK_B_SHA256SUMS.txt').write_text(''.join(build['htmlSha256']+'  '+build['output']+'\n'for build in builds)+''.join(a['sha256']+'  '+Path(a['path']).name+'\n'for a in artifacts))
result={'schema':'AEGIS_TRACK_B_PACKAGE_1','candidateSha256':builds[0]['htmlSha256'],'shadowSha256':builds[1]['htmlSha256'],
        'artifacts':artifacts,'releaseApproved':False,'stageStatus':validation['trackBStatus'],
        'reportExcludes':['HTML files (separate ZIPs)','REMOTE_READBACK.json (post-push receipt)',
                          'coordination markers/cache'],
        'replayDependencies':'Pinned repository TRACK-A, existing fixtures and Python/Playwright/Chromium/Node/acorn; matplotlib for graphs'}
(D/'TRACK_B_ARTIFACTS.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))

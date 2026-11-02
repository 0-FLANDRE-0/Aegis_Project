"""Separate unchanged HTML ZIP and lossless statistics/report ZIP, <100MiB."""
from pathlib import Path
import hashlib,json,zipfile

P=Path(__file__).resolve().parent
R=P.parents[3]
D=R/'deliverables/track-b-statistics-r4'
sha=lambda b:hashlib.sha256(b).hexdigest()


def archive(path,files):
    expected={}
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True)as z:
        for f in sorted(files):
            rel=str(f.relative_to(R));raw=f.read_bytes();expected[rel]=sha(raw)
            info=zipfile.ZipInfo(rel,date_time=(2026,11,2,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
            z.writestr(info,raw,compress_type=zipfile.ZIP_DEFLATED,compresslevel=6)
    with zipfile.ZipFile(path)as z:
        assert z.testzip()is None and len(z.namelist())==len(set(z.namelist()))==len(expected)
        for rel,digest in expected.items():assert sha(z.read(rel))==digest
    assert path.stat().st_size<100*1024*1024,'SPLIT_ARCHIVE_REQUIRED_BEFORE_PUSH'
    return {'path':str(path.relative_to(R)),'bytes':path.stat().st_size,'sha256':sha(path.read_bytes()),
            'members':len(expected),'allMemberBytesAndCrcVerified':True}


def main():
    result=json.loads((P/'RESULTS.json').read_text());assert result['actualBattles']==120
    D.mkdir(parents=True,exist_ok=True)
    html=R/'Aegis_SIM_v48_WIP_TRACK_B_STABLE_D.html'
    assert sha(html.read_bytes())=='48b023c580db02b08f165fa7ac68f973734d82e8fb4daa5981dcc90b7e04e4ab'
    approved=result['decision']=='USER_CONDITIONAL_APPROVAL_CRITERION_MET'
    readme=D/'DOWNLOAD_README.md'
    readme.write_text('# TRACK-B R4 통계 검토 산출물\n\n'+
        ('사용자 통계 조건을 충족한 R4 ACTIVE 승인본입니다.\n\n'if approved else'미승인 R4 검토본입니다. 판정은 보고서를 확인하세요.\n\n')+
        'HTML은 이전 R4와 byte 동일하며 이번 단계에서 게임 코드를 변경하지 않았습니다. HTML ZIP을 풀어 파일을 열면 됩니다. 별도 REPORT ZIP에 통계 표·사전 계획·시드·시험 소스·원시 로그·이전/새 기대값(승인된 경우)·미해결 항목을 포함합니다.\n\n'+
        'C55/SPQ AIR는 SHADOW-only입니다. 기존419025·friendly observer2·구형 EMCON UI14는 이 통계 결과로 해결 또는 승인한 것이 아닙니다. 과거 R4 보고서는 통계 전 보존 자료이며 최신 판정은 docs/contact/track/B_statistics_r4/REPORT.md를 따릅니다.\n\n'+
        '단독 HTML과 전체 시험 환경은 다릅니다. 재현에는 저장소·기존 Python/Playwright/Chromium·고정 참조 파일이 필요합니다. 새 실행은 기존 raw를 덮어쓰지 않는 작업사본에서 수행합니다.\n\n'+
        '실제 PR 병합·원격 readback은 별도 영수증을 확인합니다. 보고서 ZIP 작성 자체는 병합이 아닙니다.\n')
    current=[f for f in P.rglob('*')if f.is_file()and'__pycache__'not in f.parts and not f.name.endswith('.tmp')
             and f.name not in ['ARTIFACTS.json','REMOTE_READBACK.json','MERGE_READBACK.json','PACKAGE_VERIFICATION.json','CHECKSUMS.sha256']]
    context=[R/'docs/contact/track/CURRENT.json',readme]
    old=P.with_name('B_stabilization_r4')
    for rel in ['REPORT.md','VALIDATION.json','SCOPE.json','BUILD.json','association.js','REGRESSION_RESULTS.json',
                'evidence/regression/paired-track-a/baseline-comparison.json','evidence/regression/d1/COMPARISON.json',
                'evidence/regression/d1/compare-track-a/419012-all-leaf-differences.json.gz']:
        context.append(old/rel)
    context+=[R/'docs/contact/track/B/SEED419012_CAUSE_REPORT.md',R/'docs/radar/air-origin/A/approved_expectations.py']
    files=sorted(set(current+context));assert all(f.exists()for f in files)
    checks=P/'CHECKSUMS.sha256'
    checks.write_text(''.join(f'{sha(f.read_bytes())}  {f.relative_to(R)}\n'for f in files)+f'{sha(html.read_bytes())}  {html.relative_to(R)}\n')
    entries=[archive(D/'TRACK_B_R4_HTML.zip',[html,readme]),archive(D/'TRACK_B_R4_STATISTICAL_REPORT.zip',files+[checks])]
    artifact={'schema':'AEGIS_TRACK_B_R4_STATISTICS_ARTIFACTS_1','decision':result['decision'],'archives':entries,
              'html':{'path':html.name,'bytes':html.stat().st_size,'sha256':sha(html.read_bytes())},
              'gameHtmlChanged':False,'allArchivesBelowGithub100MiBLimit':True,
              'manifestOutsideArchivesToAvoidSelfReferentialHash':True}
    (P/'ARTIFACTS.json').write_text(json.dumps(artifact,ensure_ascii=False,indent=2)+'\n')
    (D/'SHA256SUMS.txt').write_text(''.join(f"{r['sha256']}  {Path(r['path']).name}\n"for r in entries)+f'{sha(html.read_bytes())}  {html.name}\n')
    print(json.dumps(artifact,ensure_ascii=False))


if __name__=='__main__':main()

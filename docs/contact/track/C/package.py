"""Standalone HTML ZIP, readable report ZIP, full lossless evidence ZIP parts."""
from pathlib import Path
import hashlib,json,zipfile,zlib
P=Path(__file__).resolve().parent;R=P.parents[3];D=R/'deliverables/track-c-lifecycle-a'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def archive(path,members):
 expected={}
 with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True)as z:
  for name,source in sorted(members.items()):
   raw=source.read_bytes();expected[name]=sha(raw);info=zipfile.ZipInfo(name,date_time=(2026,11,2,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;z.writestr(info,raw,compress_type=zipfile.ZIP_DEFLATED,compresslevel=6)
 with zipfile.ZipFile(path)as z:
  assert z.testzip()is None and len(z.namelist())==len(set(z.namelist()))==len(expected)
  for name,value in expected.items():assert sha(z.read(name))==value
 assert path.stat().st_size<100*1024**2,'GITHUB100MIB_BLOB_LIMIT'
 return {'path':str(path.relative_to(R)),'bytes':path.stat().st_size,'sha256':sha(path.read_bytes()),'members':len(expected),'allMemberShaAndCrcVerified':True}
def main():
 status=json.loads((P/'STATUS.json').read_text());build=json.loads((P/'BUILD.json').read_text());assert sha((R/build['html']).read_bytes())==build['htmlSha256'];D.mkdir(parents=True,exist_ok=True)
 readme=D/'README.txt';readme.write_text('TRACK-C\n\n'+status['APPROVED']+'\n\nTRACK_C_HTML.zip: 압축을 풀고 Aegis_SIM_v48_WIP_TRACK_C.html을 여세요.\nTRACK_C_SHADOW_HTML.zip: 비교/복구용. 기본 게임과 혼동하지 마세요.\nTRACK_C_REPORT.zip: 보고서, 모든 집계/검수, 소스 diff/범위, 원인과 승인 기록, 체크섬, 재현 도구.\nTRACK_C_EVIDENCE_*.zip: 전체 고정 시드 raw, 수집/실패 시도, 모든 검증 기록. 독립 ZIP이며 같은 폴더에 모두 풀면 원래 경로로 합쳐집니다.\n\n현재 제품과 과거 후보/실패 시도의 SHA는 다릅니다. 과거 기록은 evidence/attempts 아래 있으며 최종 통과 수에 합산하지 않았습니다.\n재현 시험은 원래 GitHub 저장소와 기존 Python/Playwright/Chromium 환경을 필요로 합니다. HTML 플레이와 시험 환경은 별개입니다.\n다운로드 링크는 DOWNLOADS.md, SHA는 SHA256SUMS.txt를 확인하세요. main 실제 병합/원격 SHA는 별도 REMOTE_READBACK/MERGE_READBACK 영수증이 최종 기준입니다.\n',encoding='utf8')
 excluded={'ARTIFACTS.json','REMOTE_READBACK.json','MERGE_READBACK.json','PACKAGE_VERIFICATION.json','CHECKSUMS.sha256'}
 all_files=[f for f in P.rglob('*')if f.is_file()and'__pycache__'not in f.parts and f.name not in excluded and not f.name.startswith('_TEST_ONLY_')and not f.name.endswith('.tmp')]
 core=[f for f in all_files if 'evidence'not in f.relative_to(P).parts]
 evidence=[f for f in all_files if f not in core]
 # Keep key verification/cause receipts in the small readable report too.
 for rel in ['evidence/BUDGET.json','evidence/battles/CONTROLS.json','evidence/battles/EXPORT_CONTROLS.json','evidence/d1-cause/RESULTS.json','evidence/d1-cause/ANALYSIS.json','evidence/D1_SIGNATURE_DELTAS.json','evidence/noise-origin/RESULTS.json']:
  f=P/rel
  if f.exists():core.append(f)
 context=[R/'docs/radar/air-origin/A/approved_expectations.py',R/'docs/contact/friendly/A/BUILD.json',R/'docs/contact/friendly/A/SCOPE.json',R/'docs/contact/friendly/A/REPORT.md',R/'docs/contact/friendly/A/analysis/ciws30.json',R/'docs/contact/friendly/A/analysis/paired-observer-delta.json',R/'docs/contact/friendly/A/evidence/regression/paired-current/baseline-comparison.json']
 core+=context
 current=R/'docs/contact/track/CURRENT.json'
 if current.exists():core.append(current)
 core=sorted(set(core));assert all(f.exists()for f in core)
 # Estimate actual deflate sizes to split full evidence without omitting data.
 groups=[];group=[];size=0
 for f in sorted(evidence):
  compressor=zlib.compressobj(6,zlib.DEFLATED,-15);raw=f.read_bytes();packed=len(compressor.compress(raw)+compressor.flush())+1024+len(str(f.relative_to(R)).encode())*2
  if group and size+packed>90*1024**2:groups.append(group);group=[];size=0
  assert packed<95*1024**2;group.append(f);size+=packed
 if group:groups.append(group)
 names=['TRACK_C_HTML.zip','TRACK_C_SHADOW_HTML.zip','TRACK_C_REPORT.zip']+[f'TRACK_C_EVIDENCE_{i:02}.zip'for i in range(1,len(groups)+1)]
 downloads=D/'DOWNLOADS.md';downloads.write_text('# TRACK-C 다운로드\n\n'+status['APPROVED']+' · HTML과 검증 자료를 분리했습니다. 아래 ZIP은 GitHub에서 바로 내려받습니다.\n\n'+'\n'.join(f'- [{name}](https://github.com/0-FLANDRE-0/Aegis_Project/raw/refs/heads/track-c-lifecycle-a/deliverables/track-c-lifecycle-a/{name})'for name in names)+'\n\n전체 원시 증거는 EVIDENCE ZIP을 모두 같은 폴더에 풀어 확인하세요. 각 ZIP은 독립 압축파일입니다. 체크섬은 SHA256SUMS.txt 및 ARTIFACTS.json을 확인합니다.\n',encoding='utf8')
 files=sorted(set(all_files+context+([current]if current.exists()else[])+[readme,downloads,R/build['html'],R/'Aegis_SIM_v48_WIP_TRACK_C_SHADOW.html']))
 checks=P/'CHECKSUMS.sha256';checks.write_text(''.join(f'{sha(f.read_bytes())}  {f.relative_to(R)}\n'for f in files))
 entries=[archive(D/names[0],{build['html']:R/build['html'],'README.txt':readme}),archive(D/names[1],{'Aegis_SIM_v48_WIP_TRACK_C_SHADOW.html':R/'Aegis_SIM_v48_WIP_TRACK_C_SHADOW.html','README.txt':readme}),archive(D/names[2],{**{str(f.relative_to(R)):f for f in core+[checks,readme,downloads]}})]
 for i,files in enumerate(groups,1):entries.append(archive(D/f'TRACK_C_EVIDENCE_{i:02}.zip',{str(f.relative_to(R)):f for f in files}))
 artifact={'schema':'AEGIS_TRACK_C_ARTIFACTS_1','approval':status['APPROVED'],'html':{'path':build['html'],'bytes':(R/build['html']).stat().st_size,'sha256':build['htmlSha256']},'archives':entries,'evidenceParts':len(groups),'noSourceOrRawEvidenceOmitted':True,'selfReferentialArtifactManifestExcludedFromArchives':True};(P/'ARTIFACTS.json').write_text(json.dumps(artifact,ensure_ascii=False,indent=2)+'\n');(D/'SHA256SUMS.txt').write_text(''.join(f"{q['sha256']}  {Path(q['path']).name}\n"for q in entries)+f"{build['htmlSha256']}  {build['html']}\n");print(json.dumps(artifact))
if __name__=='__main__':main()

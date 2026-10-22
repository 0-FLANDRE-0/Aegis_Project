"""Deterministic one-HTML execution ZIP and a separate evidence/report ZIP."""
import gzip,hashlib,json,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[4];H=Path(__file__).resolve().parent
HTML='Aegis_SIM_v48_WIP_ALL4_TERM.html';EXEC='Aegis_SIM_v48_WIP_ALL4_TERM_HTML.zip';REPORT='Aegis_SIM_v48_WIP_ALL4_TERM_REPORT.zip'
sha=lambda b:hashlib.sha256(b).hexdigest()
def write_zip(path,entries):
 with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6)as z:
  for name,data in sorted(entries.items()):
   info=zipfile.ZipInfo(name,date_time=(2026,1,1,0,0,0));info.create_system=3;info.external_attr=0o100644<<16;info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,data,compresslevel=6)
 with zipfile.ZipFile(path)as z:
  assert z.testzip()is None;assert z.namelist()==sorted(entries)
  for name,data in entries.items():assert z.read(name)==data
 return {'file':path.name,'bytes':path.stat().st_size,'sha256':sha(path.read_bytes()),'members':len(entries),'crcValid':True,'allExtractedBytesVerified':True}
def main():
 raw=(R/HTML).read_bytes();write_zip(R/EXEC,{HTML:raw});firstExecution=(R/EXEC).read_bytes();entries={}
 for root in [H,R/'docs/envelope/B']:
  for src in root.rglob('*'):
   if not src.is_file()or '__pycache__'in src.parts or src.name in ['delivery.json','remote-publication.json','DELIVERY_MANIFEST.json']:continue
   assert src.suffix.lower()not in ['.html','.zip']
   data=src.read_bytes();name=str(src.relative_to(R))
   if src.suffix=='.gz':data=gzip.decompress(data);name=name[:-3]
   assert name not in entries;entries[name]=data
 for src in (R/'docs/envelope/A/results').iterdir():
  if src.suffix in ['.png','.svg']or src.name in ['envelope-table.json','trajectory-summary.csv','REPORT_ENV_A.md']:entries[str(src.relative_to(R))]=src.read_bytes()
 for name in ['docs/envelope/A/REPORT.md','docs/envelope/A/ENVELOPE_TABLE_A.json']:entries[name]=(R/name).read_bytes()
 for name in ['README.md','AEGIS_PROJECT_INSTRUCTIONS.md','AEGIS_PLAN_STATUS_v48_WIP_ALL4_TERM.md','SHA256SUMS_v48_WIP_ALL4_TERM.txt','.github/workflows/missile-b4-termination.yml']:
  entries[name]=(R/name).read_bytes()
 entries['REPORT_INDEX.md']=('''# ALL4_TERM + ENV_B 리포트

- [누적 ALL4 종료·배터리·브라우저 검수](docs/missile/termination/A/REPORT.md)
- [미사일 그래프/96조합 사거리 표/로프트 관찰/E1–E4](docs/envelope/B/REPORT.md)
- [재현 순서](docs/missile/termination/A/README.md)
- [검증 환경과 후보/재시도 구분](docs/missile/termination/A/TEST_ENVIRONMENT.md)
- [파일 목록과 SHA-256](DELIVERY_MANIFEST.json)

실행 HTML은 별도의 HTML ZIP에 있다. 이 ZIP의 원시JSON/CSV는 압축을 풀어 읽을 수 있게 수록했다. 전체 원격 readback 영수증은 발행 후 GitHub의 missile-b4-termination 브랜치 docs/missile/termination/A/remote-publication.json에 기록한다.
''').encode()
 manifest={'schema':'AEGIS_ALL4_TERM_REPORT_MANIFEST_1','htmlDeliveredSeparately':{'filename':HTML,'bytes':len(raw),'sha256':sha(raw)},'provenance':'GAME_ENGINE_COMPUTED','files':[{'path':n,'bytes':len(b),'sha256':sha(b)}for n,b in sorted(entries.items())]};manifestBytes=(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode();(H/'DELIVERY_MANIFEST.json').write_bytes(manifestBytes);entries['DELIVERY_MANIFEST.json']=manifestBytes
 report=write_zip(R/REPORT,entries);execution=write_zip(R/EXEC,{HTML:raw});assert execution['members']==1;assert firstExecution==(R/EXEC).read_bytes()
 for stem,name in [('HTML_ZIP',EXEC),('REPORT_ZIP',REPORT)]:
  (R/f'SHA256SUMS_v48_WIP_ALL4_TERM_{stem}.txt').write_text(sha((R/name).read_bytes())+'  '+name+'\n')
 out={'schema':'AEGIS_ALL4_TERM_DELIVERY_1','pass':True,'html':{'file':HTML,'bytes':len(raw),'sha256':sha(raw)},'executionZip':execution,'reportZip':report,'reportContainsExecutionHtml':False,'reportManifestEntries':len(manifest['files'])};(H/'evidence/delivery.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()

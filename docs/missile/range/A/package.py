"""Separate one-HTML execution ZIP and complete RANGE_A/ENV_C report ZIP."""
import gzip,hashlib,json,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[4];H=Path(__file__).resolve().parent
HTML='Aegis_SIM_v48_WIP_RANGE_A.html';EXEC='Aegis_SIM_v48_WIP_RANGE_A_HTML.zip';REPORT='Aegis_SIM_v48_WIP_RANGE_A_REPORT.zip'
sha=lambda b:hashlib.sha256(b).hexdigest()
def write_zip(path,entries):
 with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6)as z:
  for name,data in sorted(entries.items()):
   info=zipfile.ZipInfo(name,date_time=(2026,1,1,0,0,0));info.create_system=3;info.external_attr=0o100644<<16;info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,data,compresslevel=6)
 with zipfile.ZipFile(path)as z:
  assert z.testzip()is None and z.namelist()==sorted(entries)
  for name,data in entries.items():assert z.read(name)==data
 return {'file':path.name,'bytes':path.stat().st_size,'sha256':sha(path.read_bytes()),'members':len(entries),'crcValid':True,'allExtractedBytesVerified':True}
def main():
 assert(H/'REPORT.md').exists()and(H/'evidence/acceptance.json').exists()
 assert json.loads((H/'evidence/acceptance.json').read_text())['pass']
 raw=(R/HTML).read_bytes();write_zip(R/EXEC,{HTML:raw});first=(R/EXEC).read_bytes();entries={}
 def add(src):
  assert src.suffix.lower()not in ['.html','.zip'];data=src.read_bytes();name=str(src.relative_to(R))
  if src.suffix=='.gz':data=gzip.decompress(data);name=name[:-3]
  assert name not in entries;entries[name]=data
 for root in [H,R/'docs/envelope/C',R/'docs/envelope/B']:
  for src in root.rglob('*'):
   if not src.is_file()or'__pycache__'in src.parts or src.name in ['delivery.json','remote-publication.json','DELIVERY_MANIFEST.json']:continue
   add(src)
 old=R/'docs/missile/termination/A'
 for src in old.iterdir():
  if src.is_file()and src.suffix in ['.py','.js','.cjs','.md']:add(src)
 for src in (old/'cases').iterdir():
  if src.is_file():add(src)
 for src in (old/'kit').iterdir():
  if src.is_file():add(src)
 for src in (R/'docs/envelope/A/results').iterdir():
  if src.suffix in ['.png','.svg']or src.name in ['envelope-table.json','trajectory-summary.csv','REPORT_ENV_A.md']:add(src)
 for name in ['docs/envelope/A/REPORT.md','docs/envelope/A/ENVELOPE_TABLE_A.json','README.md','AEGIS_PROJECT_INSTRUCTIONS.md','AEGIS_PLAN_STATUS_v48_WIP_RANGE_A.md','SHA256SUMS_v48_WIP_RANGE_A.txt','.github/workflows/range-a-env-c.yml']:add(R/name)
 entries['REPORT_INDEX.md']=('''# RANGE_A + ENV_C

- [범위·0단계·변경8값·목표 도달·R1–R5](docs/missile/range/A/REPORT.md)
- [ENV_C 전체96조합·발사거리/요격거리·ENV_B 비교·120궤적](docs/envelope/C/REPORT.md)
- [저고도 이탈/횡단21건 조사 — 수정 없음](docs/envelope/C/results/LOW_ALT_INVESTIGATION.md)
- [재현](docs/envelope/C/README.md) · [검증 환경](docs/missile/range/A/TEST_ENVIRONMENT.md)
- [전체 수록 파일·체크섬](DELIVERY_MANIFEST.json)

이 ZIP에는 실행 HTML이 없다. 별도의 HTML ZIP을 받는다. 큰 원시JSON/CSV는 읽을 수 있게 풀어서 수록한다. 전체 원격 readback 영수증은 발행 후 GitHub range-a-env-c 브랜치 docs/missile/range/A/remote-publication.json에 기록한다.
''').encode()
 manifest={'schema':'AEGIS_RANGE_A_REPORT_MANIFEST_1','htmlDeliveredSeparately':{'filename':HTML,'bytes':len(raw),'sha256':sha(raw)},'provenance':'GAME_ENGINE_COMPUTED','files':[{'path':n,'bytes':len(b),'sha256':sha(b)}for n,b in sorted(entries.items())]};mb=(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode();(H/'DELIVERY_MANIFEST.json').write_bytes(mb);entries['DELIVERY_MANIFEST.json']=mb
 report=write_zip(R/REPORT,entries);execution=write_zip(R/EXEC,{HTML:raw});assert execution['members']==1 and first==(R/EXEC).read_bytes()
 for stem,name in [('HTML_ZIP',EXEC),('REPORT_ZIP',REPORT)]:(R/f'SHA256SUMS_v48_WIP_RANGE_A_{stem}.txt').write_text(sha((R/name).read_bytes())+'  '+name+'\n')
 out={'schema':'AEGIS_RANGE_A_DELIVERY_1','pass':True,'html':{'file':HTML,'bytes':len(raw),'sha256':sha(raw)},'executionZip':execution,'reportZip':report,'reportContainsExecutionHtml':False,'reportManifestEntries':len(manifest['files'])};(H/'evidence/delivery.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()

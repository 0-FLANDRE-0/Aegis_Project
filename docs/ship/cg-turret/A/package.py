from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json,zipfile
P=Path(__file__).resolve().parent;R=P.parents[3];D=R/'downloads';sha=lambda b:hashlib.sha256(b).hexdigest();game=R/'Aegis_SIM_v48_WIP_CG_TURRET_A.html'
s=json.loads((P/'BUILD_STATUS.json').read_text());assert s['scopePass']and s['renderPass']and s['originIsolationPass'];assert not s['regressionExitFailures']
execution=P/'evidence/range-execution.json';started=datetime.fromtimestamp(execution.stat().st_mtime,timezone.utc)-timedelta(seconds=json.loads(execution.read_text())['elapsedS']);finished=datetime.now(timezone.utc);clock={'testStartUtc':started.isoformat(),'finishedUtc':finished.isoformat(),'elapsedS':(finished-started).total_seconds(),'testCapS':3600,'withinCap':(finished-started).total_seconds()<=3600};assert clock['withinCap'];(P/'TASK_CLOCK.json').write_text(json.dumps(clock,indent=2)+'\n')
historical=[R/'docs/gun/B2/phase1b/evidence/range-intercept'/f'CG_52_LATE_TICONDEROGA-{b}.jsonl'for b in[0,90]]+[R/'docs/gun/B2/phase1b/evidence/g7/trials.jsonl',R/'docs/gun/B2/phase1a/evidence/surface/CG_52_LATE_TICONDEROGA-ON.jsonl',R/'docs/gun/B2/phase1b/evidence/regression-summary.json',R/'docs/gun/B2/phase1b/TEST_REUSE.json',R/'docs/gun/B2/phase1/evidence/regression/ON/webgl8/observed-world.json']
(P/'HISTORICAL_SOURCES.json').write_text(json.dumps([{'path':p.relative_to(R).as_posix(),'sha256':sha(p.read_bytes()),'zipPath':'historical/'+p.relative_to(R).as_posix(),'purpose':'B2B comparison input, not current execution'}for p in historical],indent=2)+'\n')
files=sorted(p for p in P.rglob('*')if p.is_file()and p.name not in['REMOTE_READBACK.json','CHECKSUMS.sha256','PACKAGE_RECEIPT.json']and'__pycache__'not in p.parts and p.suffix not in['.pyc','.tmp'])
(P/'CHECKSUMS.sha256').write_text(''.join(sha(p.read_bytes())+'  '+p.relative_to(R).as_posix()+'\n'for p in[game]+files));files.append(P/'CHECKSUMS.sha256');D.mkdir(exist_ok=True)
def add(z,name,data):
 i=zipfile.ZipInfo(name,(1980,1,1,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;i.external_attr=0o100644<<16;z.writestr(i,data,compresslevel=7)
gz=D/'Aegis_SIM_v48_WIP_CG_TURRET_A_HTML.zip';rz=D/'Aegis_SIM_v48_WIP_CG_TURRET_A_REPORT.zip'
with zipfile.ZipFile(gz,'w')as z:
 add(z,game.name,game.read_bytes());add(z,'SHA256SUMS.txt',(sha(game.read_bytes())+'  '+game.name+'\n').encode());add(z,'README.txt','압축을 풀고 Aegis_SIM_v48_WIP_CG_TURRET_A.html을 브라우저에서 여세요.\n'.encode())
bundle={p.relative_to(P).as_posix():p.read_bytes()for p in files};bundle.update({'historical/'+p.relative_to(R).as_posix():p.read_bytes()for p in historical});bundle['README.txt']='INDEX.html을 여세요. PC/폰 비교 캡처와 보고서, 원시시험·로그·diff·도구를 포함합니다. historical/은 B2B 비교 입력입니다. 게임 HTML은 별도 ZIP입니다.\n'.encode();bundle['BUNDLE_CHECKSUMS.sha256']=''.join(sha(v)+'  '+n+'\n'for n,v in sorted(bundle.items())).encode()
with zipfile.ZipFile(rz,'w')as z:
 for n,v in sorted(bundle.items()):add(z,n,v)
receipt=[]
for p in[gz,rz]:
 with zipfile.ZipFile(p)as z:
  assert z.testzip()is None
  if p==gz:assert z.read(game.name)==game.read_bytes()
  else:assert all(z.read(n)==v for n,v in bundle.items())
 assert p.stat().st_size<100*1024**2;receipt.append({'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes()),'crcAndMemberEquality':True})
(P/'PACKAGE_RECEIPT.json').write_text(json.dumps({'archives':receipt,'htmlSha256':sha(game.read_bytes()),'reportNoGameHtml':True},indent=2)+'\n');(D/'CG_TURRET_A_SHA256SUMS.txt').write_text(''.join(sha(p.read_bytes())+'  '+p.relative_to(R).as_posix()+'\n'for p in[game,gz,rz,P/'CHECKSUMS.sha256']));print(json.dumps({'clock':clock,'archives':receipt},indent=2))

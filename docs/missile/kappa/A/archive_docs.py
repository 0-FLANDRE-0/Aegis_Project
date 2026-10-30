"""Preserve the old delivery and visibly mark old guidance reports as historical."""
from pathlib import Path
import hashlib, json, subprocess

H = Path(__file__).resolve().parent; R = H.parents[3]
assert json.loads((H / 'evidence/verification.json').read_text())['verificationPass']
base = '5af4726113994b4e38bbfe5da8283424f04856fe'
archive = R / 'archive/v48/WIP_RANGE_RECOVERY_A'
subprocess.run(['git','sparse-checkout','add','archive/v48/WIP_RANGE_RECOVERY_A'], cwd=R, check=True)
archive.mkdir(parents=True, exist_ok=True)
names = ['Aegis_SIM_v48_WIP_RANGE_RECOVERY_A.html','AEGIS_PLAN_STATUS_v48_WIP_RANGE_RECOVERY_A.md','SHA256SUMS_v48_WIP_RANGE_RECOVERY_A.txt','Aegis_SIM_v48_WIP_RANGE_RECOVERY_A_HTML.zip','Aegis_SIM_v48_WIP_RANGE_RECOVERY_A_REPORT.zip','SHA256SUMS_v48_WIP_RANGE_RECOVERY_A_HTML_ZIP.txt','SHA256SUMS_v48_WIP_RANGE_RECOVERY_A_REPORT_ZIP.txt']
records = []
for name in names:
    original = subprocess.check_output(['git','show',base+':'+name], cwd=R)
    src = R / name; dest = archive / name
    if src.exists():
        assert src.read_bytes() == original
        subprocess.run(['git','mv','--sparse','--',name,str(dest.relative_to(R))], cwd=R, check=True)
    assert dest.read_bytes() == original
    records.append({'source':name,'archive':str(dest.relative_to(R)),'bytes':len(original),'sha256':hashlib.sha256(original).hexdigest(),'gitBlob':hashlib.sha1(b'blob '+str(len(original)).encode()+b'\0'+original).hexdigest()})
(H / 'evidence/archive.json').write_text(json.dumps({'pass':True,'files':records},indent=2)+'\n')
notice = '> **과거 유도 코드의 결과 — HISTORICAL_PRE_KAPPA_PIP_LOS**\n> 이 보고서는 Kappa 종말 수평방향 수정 전 결과다. 현재 KAPPA_PIP_LOS_A의 사거리·성공 판정으로 사용하지 않는다. 기존 측정 데이터는 보존했다. 새 제한 검증은 [KAPPA_PIP_LOS_A 보고서]({link})를 확인한다.\n\n'
metadata = []
for name, link in [('docs/envelope/C/REPORT.md','../../missile/kappa/A/REPORT.md'),('docs/missile/range/RECOVERY_A/REPORT.md','../../kappa/A/REPORT.md')]:
    p = R / name; original = subprocess.check_output(['git','show',base+':'+name], cwd=R)
    prefixed = notice.format(link=link).encode()+original
    assert p.read_bytes() in [original,prefixed]
    p.write_bytes(prefixed)
    metadata.append({'path':name,'oldSha256':hashlib.sha256(original).hexdigest(),'newSha256':hashlib.sha256(prefixed).hexdigest(),'noticeOnlyOriginalBodyPreserved':p.read_bytes().endswith(original)})
(H / 'evidence/historical-report-metadata.json').write_text(json.dumps({'pass':True,'reports':metadata},indent=2)+'\n')
intro = '''최신 시험 후보 — KAPPA_PIP_LOS_A

- `range-loft-recovery-a`의 `5af4726` 위 별도 `kappa-pip-los-a`. [HTML](Aegis_SIM_v48_WIP_KAPPA_PIP_LOS_A.html), [상태](AEGIS_PLAN_STATUS_v48_WIP_KAPPA_PIP_LOS_A.md), [SHA](SHA256SUMS_v48_WIP_KAPPA_PIP_LOS_A.txt), [보고서](docs/missile/kappa/A/REPORT.md), [실행 diff](docs/missile/kappa/A/game-change.diff).
- [실행 HTML ZIP](https://github.com/0-FLANDRE-0/Aegis_Project/raw/refs/heads/kappa-pip-los-a/Aegis_SIM_v48_WIP_KAPPA_PIP_LOS_A_HTML.zip?download=1) · [리포트 ZIP](https://github.com/0-FLANDRE-0/Aegis_Project/raw/refs/heads/kappa-pip-los-a/Aegis_SIM_v48_WIP_KAPPA_PIP_LOS_A_REPORT.zip?download=1).
- 종말 수평방향2복사본만 관측 PIP의 dx/dy로 수정했다. B4·설계/RMAX/fullLoft·추진/항력/질량/시커/신관/배터리/종료기/해면판정/UI 및 TGO90초 유지.
- 14조건 A/B×2에서 지정 해면충돌4건 모두 명중, 정상6건 유지, 횡단2/4→4/4. 기존 성공8건 유지·신규실패0. 원시 반복 비트동일, 실제월드/진단28쌍25,529샘플 오차0. 이는14조건의 제한 합격이다.
- 실행 소스에서 진단 캡슐과 함수 해시를 재생성했다. native 불일치0, 현재 사거리표는 rows0/profileHashnull/envelopeMeasured=false. ENV_C/RECOVERY_A 보고서에는 구 유도 코드의 과거 결과임을 표시했고 기존 데이터는 유지했다.
- 전체96/500km스윕, 새최대거리, 비기본정책, 전체420+UI88/자연센서 종합검사는 실행하지 않았다. 원본 RANGE_RECOVERY_A 전달세트7파일 같은 bytes/blob archive, 기존브랜치/main 병합·새PR·Actions 실행 없음.

'''
for name, heading in [('README.md','## '),('AEGIS_PROJECT_INSTRUCTIONS.md','### ')]:
    p = R / name; text = p.read_text(); marker = heading+'최신 시험 후보 — RANGE_RECOVERY_A'
    if marker in text:
        text = text.replace(marker,heading+intro+heading+'직전 시험 후보 — RANGE_RECOVERY_A (구 유도 코드)',1)
    for f in names:
        text = text.replace(']('+f+')','](archive/v48/WIP_RANGE_RECOVERY_A/'+f+')')
    p.write_text(text)
changed = subprocess.check_output(['git','diff',base,'--name-only','--','docs/envelope/C','docs/missile/range/RECOVERY_A'], cwd=R,text=True).splitlines()
assert set(changed) == {'docs/envelope/C/REPORT.md','docs/missile/range/RECOVERY_A/REPORT.md'}
print('Archived7 unchanged delivery files; only two historical-report notices changed')

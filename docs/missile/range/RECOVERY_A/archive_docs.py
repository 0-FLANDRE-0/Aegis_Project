"""Preserve the previous delivery byte-for-byte, document this trial only."""
from pathlib import Path
import hashlib, json, subprocess

H = Path(__file__).resolve().parent
R = H.parents[3]
assert json.loads((H / 'evidence/verification.json').read_text())['verificationPass']
archive = R / 'archive/v48/WIP_RANGE_A'
subprocess.run(['git', 'sparse-checkout', 'add', 'archive/v48/WIP_RANGE_A', '.github/workflows'], cwd=R, check=True)
archive.mkdir(parents=True, exist_ok=True)
files = ['Aegis_SIM_v48_WIP_RANGE_A.html', 'AEGIS_PLAN_STATUS_v48_WIP_RANGE_A.md', 'SHA256SUMS_v48_WIP_RANGE_A.txt', 'Aegis_SIM_v48_WIP_RANGE_A_HTML.zip', 'Aegis_SIM_v48_WIP_RANGE_A_REPORT.zip', 'SHA256SUMS_v48_WIP_RANGE_A_HTML_ZIP.txt', 'SHA256SUMS_v48_WIP_RANGE_A_REPORT_ZIP.txt', '.github/workflows/range-a-env-c.yml']
records = []
for name in files:
    original = subprocess.check_output(['git', 'show', 'd42284a:' + name], cwd=R)
    dest = archive / Path(name).name
    src = R / name
    if src.exists():
        assert src.read_bytes() == original
        subprocess.run(['git', 'mv', '--sparse', '--', name, str(dest.relative_to(R))], cwd=R, check=True)
    assert dest.read_bytes() == original
    records.append({'source': name, 'archive': str(dest.relative_to(R)), 'bytes': len(original), 'sha256': hashlib.sha256(original).hexdigest(), 'gitBlobUnchanged': hashlib.sha1(b'blob ' + str(len(original)).encode() + b'\0' + original).hexdigest()})
(H / 'evidence/archive.json').write_text(json.dumps({'pass': True, 'files': records}, indent=2) + '\n')
intro = '''최신 시험 후보 — RANGE_RECOVERY_A

- `range-loft-recovery-a`: RANGE_A의 fullLoftKm만 ER360→240 / SM-6 450→260. 설계목표360/450·RMAX·추진/항력/Kappa/신관/배터리/종료기/UI 유지.
- [HTML](Aegis_SIM_v48_WIP_RANGE_RECOVERY_A.html), [상태](AEGIS_PLAN_STATUS_v48_WIP_RANGE_RECOVERY_A.md), [SHA](SHA256SUMS_v48_WIP_RANGE_RECOVERY_A.txt), [제한 시험 보고](docs/missile/range/RECOVERY_A/REPORT.md), [검증](docs/missile/range/RECOVERY_A/evidence/verification.json).
- [실행 HTML ZIP](https://github.com/0-FLANDRE-0/Aegis_Project/raw/refs/heads/range-loft-recovery-a/Aegis_SIM_v48_WIP_RANGE_RECOVERY_A_HTML.zip?download=1) · [리포트 ZIP](https://github.com/0-FLANDRE-0/Aegis_Project/raw/refs/heads/range-loft-recovery-a/Aegis_SIM_v48_WIP_RANGE_RECOVERY_A_REPORT.zip?download=1).
- 정지6조건 0/6→6/6 회복, 접근300m/s는6/6 유지. 장거리 이탈150m/s는 기준판/정렬판/후보 모두0/6. 추가60km 이탈확인은 기준판6/6, 정렬판/후보5/6으로 ER60km/1km 해면충돌이 남았다. 전체 복구 완료로 판정하지 않는다.
- 본시험54조건+확인18조건 각각2회 비트동일. 실제월드/사본72조건 궤적 오차0, 진단의 월드/RNG/틱 변화0. 정적 byte 비교와 기존 종료기6fixture 통과. 전체96스윕/새최대거리/420+UI88전체회귀는 실행하지 않았다.
- 기존 ENV_C표는 보존했고 후보에서는 ‘재계산 필요’ 경고가 켜진다. 기존 RANGE_A 세트는 같은 bytes/blob으로 archive했다. main·기존브랜치 병합/새PR/Actions 실행 없음. 별도 시험 산출물과 원격전체 readback 기록을 남긴다.

'''
for name, heading in [('README.md', '## '), ('AEGIS_PROJECT_INSTRUCTIONS.md', '### ')]:
    p = R / name
    text = p.read_text()
    marker = heading + '최신 개발 기준 — 설계 사거리 정렬 WIP RANGE_A + ENV_C'
    previous = heading + '직전 개발 기준 — 설계 사거리 정렬 WIP RANGE_A + ENV_C'
    if marker in text:
        text = text.replace(marker, heading + intro + previous, 1)
    for f in files:
        if '/' not in f:
            text = text.replace('](' + f + ')', '](archive/v48/WIP_RANGE_A/' + f + ')')
    p.write_text(text)
print('Archived original delivery:', len(records), 'unchanged files; trial handoff documented')

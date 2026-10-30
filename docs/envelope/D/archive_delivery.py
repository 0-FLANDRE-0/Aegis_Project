"""Archive previous seven delivery files unchanged and publish consistent docs."""
from pathlib import Path
import hashlib,json,subprocess
H=Path(__file__).resolve().parent;R=H.parents[2]
v=json.loads((H/'evidence/verification.json').read_text());assert v['verificationPass']
b=json.loads((H/'build.json').read_text());reg=json.loads((H/'REG_K_RESULTS.json').read_text());summary=json.loads((H/'SUMMARY.json').read_text())
base='80b65143d10f0fc42072d068dacbbc69a2b78fc3';old='v48_WIP_KAPPA_PIP_LOS_A';new='v48_WIP_ENV_D'
dest=R/'archive/v48/WIP_KAPPA_PIP_LOS_A'
subprocess.run(['git','sparse-checkout','add','archive/v48/WIP_KAPPA_PIP_LOS_A'],cwd=R,check=True);dest.mkdir(parents=True,exist_ok=True)
names=[f'Aegis_SIM_{old}.html',f'AEGIS_PLAN_STATUS_{old}.md',f'SHA256SUMS_{old}.txt',f'Aegis_SIM_{old}_HTML.zip',f'Aegis_SIM_{old}_REPORT.zip',f'SHA256SUMS_{old}_HTML_ZIP.txt',f'SHA256SUMS_{old}_REPORT_ZIP.txt'];records=[]
for name in names:
 original=subprocess.check_output(['git','show',base+':'+name],cwd=R)
 if(R/name).exists():
  assert(R/name).read_bytes()==original
  subprocess.run(['git','mv','--sparse','--',name,str((dest/name).relative_to(R))],cwd=R,check=True)
 assert(dest/name).read_bytes()==original
 records.append({'source':name,'archive':str((dest/name).relative_to(R)),'bytes':len(original),'sha256':hashlib.sha256(original).hexdigest(),'gitBlob':hashlib.sha1(b'blob '+str(len(original)).encode()+b'\0'+original).hexdigest()})
(H/'evidence/archive.json').write_text(json.dumps({'pass':True,'files':records},indent=2)+'\n')
intro=f'''최신 시험 후보 — REG_K + ENV_D

- `kappa-pip-los-a` / `80b6514` 위 별도 `reg-k-env-d`. [HTML](Aegis_SIM_{new}.html), [상태](AEGIS_PLAN_STATUS_{new}.md), [SHA](SHA256SUMS_{new}.txt), [전체 보고서](docs/envelope/D/REPORT.md), [재현](docs/envelope/D/README.md).
- [실행 HTML ZIP](https://github.com/0-FLANDRE-0/Aegis_Project/raw/refs/heads/reg-k-env-d/Aegis_SIM_{new}_HTML.zip?download=1) · [리포트 ZIP](https://github.com/0-FLANDRE-0/Aegis_Project/raw/refs/heads/reg-k-env-d/Aegis_SIM_{new}_REPORT.zip?download=1).
- 게임 실행 코드·B4·Kappa·설계 사거리·추진/항력/질량/시커/신관/배터리/종료기/UI/저장 스키마 변경0. 내장 ENVELOPE_TABLE_D와 읽기 전용 상태 API만 추가했다. 지도·발사·AI 소비자 없음.
- 기존420+UI88 및 종료기/실제WebGL 검수 수집 완료. RANGE_RECOVERY_A 대비 성공→실패{reg['successToFailureCount']}건·실패→성공{reg['failureToSuccessCount']}건. 무표적120초 hash 동일, 변경된 전투120초는 별도 기록했다.
- 실제 ASM Kh-35U 기준120칸 + Kh-32 보조6칸, 거리당5개 독립 시드. 바깥/안쪽 거리와 요격점 평균/최소/최대, 경계 반복,10Hz 궤적, 해면 충돌 목록을 보존했다. 완전한 전수 측정은1회다.
- `__ENV_D__.status()`로 새120칸 계산표/프로파일/함수 해시를 확인한다. 기존 ENV_C는 과거 AIR+구 유도 결과로 보존했다. 미완성 콜백을 발견한 초기 부분 시도는 폐기 자료로 구분했다.
- 원본 {b['bytes']:,}bytes / SHA `{b['sha256']}`. 기존 KAPPA 전달7파일은 같은 bytes/blob으로 archive했다. 기존 브랜치/main 병합, 새PR, Actions 실행 없음.

'''
for name,heading in [('README.md','## '),('AEGIS_PROJECT_INSTRUCTIONS.md','### ')]:
 p=R/name;s=subprocess.check_output(['git','show',base+':'+name],cwd=R,text=True);marker=heading+'최신 시험 후보 — KAPPA_PIP_LOS_A'
 assert marker in s
 s=s.replace(marker,heading+intro+heading+'직전 시험 후보 — KAPPA_PIP_LOS_A (회귀·측정 전 기록)',1)
 for f in names:s=s.replace(']('+f+')','](archive/v48/WIP_KAPPA_PIP_LOS_A/'+f+')')
 p.write_text(s)
status=f'''# v48 WIP ENV_D 상태

- 기준 KAPPA_PIP_LOS_A `80b65143d10f0fc42072d068dacbbc69a2b78fc3`, 별도 시험 브랜치 `reg-k-env-d`.
- HTML `Aegis_SIM_{new}.html` / {b['bytes']}bytes / SHA-256 `{b['sha256']}`.
- 기존 게임 JS는 새 데이터/API 블록을 제거하면 byte 동일. 게임 함수·계수 변경0, 지도/발사/AI/저장 연결0.
- 기존420회귀+UI88, 종료기16, 자연센서→LOCK→정식VLS→전체fixed tick→실제WebGL8발 검수 완료. 이전 기준 대비 성공→실패{reg['successToFailureCount']}건, 실패→성공{reg['failureToSuccessCount']}건. 모든 결과/CPA/비행시간 차이는 보고서 CSV에 보존했다.
- 무표적120초 hash 동일. SM-6 100km/5km/접근250/seed12002 전투는 양쪽 최종 비명중이며 최근접/종료시간이 달라졌다. 수정하지 않았다.
- ENV_D 실제 ASM 피해 경로: 기본120칸+Kh-32 보조6칸,5개 독립 RNG/항법 seed. 유효 범위는5km부터 연속3/5 KILL/STRUCT_FAIL, 최대는1/5 이상 native 효과. 0km도 정의에 따른 결과다.
- 측정 {summary['measurementShots']:,}발, 전수1회. 경계와 고정 무작위30궤적만 반복. 실제 게임/독립 진단 ASM/횡단 포함6조건 오차0, world/RNG/tick 변화0.
- ENVELOPE_TABLE_D120칸, profile hash `{b['profileHash']}`. `__ENV_D__.status()` 일치. 이전 AIR용 진단/ENV_C 원시 결과는 별도로 보존했다.
- 초기 계통손상 콜백 누락 시도는 중단·무효 표시했으며 최종 표에 포함하지 않았다. 센서/교전 지원은 이상 조건, 결과는 SIM_TUNED 게임 모델이다.
- [보고서](docs/envelope/D/REPORT.md), [검증](docs/envelope/D/evidence/verification.json), [전체 표](docs/envelope/D/ENVELOPE_TABLE_D.json), [재현](docs/envelope/D/README.md).
- 실행 HTML ZIP과 리포트 ZIP 분리. 이전7파일 같은 bytes/blob 보존. 기존 브랜치/main 병합, PR, Actions 실행 없음. 원격 전체 readback 영수증은 발행 후 추가한다.
'''
(R/f'AEGIS_PLAN_STATUS_{new}.md').write_text(status)
files=[R/f'Aegis_SIM_{new}.html',R/f'AEGIS_PLAN_STATUS_{new}.md']
(R/f'SHA256SUMS_{new}.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n'for p in files))
print('Archived seven unchanged files; README/instructions/status/SHA updated together')

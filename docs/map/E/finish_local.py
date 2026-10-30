from pathlib import Path
import json,subprocess,sys,time,os
H=Path(__file__).resolve().parent;R=H.parents[2];p=H/'evidence/remaining-gpu.json'
while True:
 q=json.loads(p.read_text())if p.exists()else{}
 if any(r['exitCode']for r in q.get('rows',[])):raise SystemExit('remaining regression failed')
 if q.get('rows',[])and q['rows'][-1]['name']=='dom':break
 time.sleep(5)
for name in ['verify_delivery_world.py','finalize_domain.py','acceptance.py']:
 subprocess.run([sys.executable,str(H/name)],cwd=R,check=True)
a=json.loads((H/'evidence/acceptance.json').read_text());b=json.loads((H/'build.json').read_text())
(H/'STATE.md').write_text(f'''# MAP_E 완료 상태

- 단계: 구현·로컬 검증 완료. map-e 산출물/원격 readback 이후 PR만 제출한다.
- 기준 main: {b['baseCommit']} (MAP_D PR #57 병합본).
- HTML: {b['output']} · {b['bytes']:,} bytes.
- SHA-256: {b['sha256']}.
- 구현: ARM 제거, EMCON/ECM 팝오버, 자함 OFF/JAM/FULL, 수동 SRBOC/Nulka 팝업, 지도 하푼 MANUAL 권한, AIM 비종속 경로 편집.
- 사용자 결정: CG 개별 함포 UI 폐기·자동 2문 유지. EMCON 비방사 지정 GUI는 후속 검토(FOLLOW_UP.md), 내부 분기는 보존.
- 검증: 도메인 420, UI88/MAP_B91/경고23/추가13, MAP_C135/73/45/33/13, MAP_D84/213/145, 종료기300, 자연 WebGL8, EW94/H3 195 통과. 새 E UI277 + 단계11 + 정책33 통과.
- 보존: native281 / ENV_D120행 / NPC 커널·EA allocator byte 동일. 120초 무표적·전투 truth hash MAP_D 동일. 게임 저장 스키마 변경 0.
- 증거 출처: 표시 보정 전 native 결과는 실제 실행 SHA를 유지한다. MAP_E_UI 밖 전체 byte 동일 증거로 재사용. 최종 UI/입력·world120·WebGL8은 최종 HTML에서 재검증.
- 이관/중단: 제거된 ARM 준비는 원래 native 리스너 어댑터로 이관. 오래된 H3 스키마 기대값만 H4로 갱신. 중단된 WebGL 묶음은 전체 재실행했으며 일부 통과 로그로 대체하지 않았다.
- 저장: 새 ECM 단계 필드 없음. JAM 저장/불러오기는 기존 SK AUTO ON에서 FULL로 추론. 레거시 NJ/DJ 승인은 읽기 전용 보존.
- 산출물: HTML ZIP / REPORT ZIP / 체크섬 분리. 실제 원격 영수증/PR 주소는 remote-readback.json 참조.
- main 병합 / release / tag 생성 / CI 변경: 없음.
''')
for name in ['write_report.py','package.py']:subprocess.run([sys.executable,str(H/name)],cwd=R,check=True)
Path('/tmp/aegis-map-e/local-finalization.json').write_text(json.dumps({'pass':True,'htmlSha256':b['sha256'],'packageLog':'/tmp/aegis-map-e/local-finalization.log'},indent=2)+'\n')
# This receipt is written after archives; keep outside the checksummed docs archive.

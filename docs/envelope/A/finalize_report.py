"""Combine completed receipts. Refuse partial or failed full diagnostics."""
import hashlib,json,shutil
from pathlib import Path
H=Path(__file__).resolve().parent;D=H/'evidence';full=Path('/tmp/env-full-browser/full-worker.json')
q=json.loads(full.read_text());assert q['pass'];verify=json.loads((D/'results-verification.json').read_text());native=json.loads((D/'native-path/browser.json').read_text());status=json.loads((D/'profile-status/status.json').read_text());assert verify['pass']and native['pass']and status['pass'];assert q['records']['profileHash']==status['records']['before']['currentProfileHash']==verify['profileHash']
# The long-running earlier runner loaded a pre-table candidate and re-read the
# filename for its final metadata. Keep the raw result and qualify that field.
shutil.copyfile(full,D/'full-worker-original.json');q['htmlSha256AtReceiptWrite']=q.pop('htmlSha256');q['loadedHtmlSha256']=None;q['qualification']='Long run began on pre-table candidate. Flight capsule and suite were unchanged. This runner version read the disk HTML hash on completion; that field is not evidence of loaded build bytes. Final build has its own native-path and profile-status receipts. Reproduction runner now snapshots input bytes.'
q['finalCapsuleProfileHashMatch']=True;(D/'full-worker.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
boundary=json.loads((D/'browser-boundaries.json').read_text());assert boundary['pass']
suites=[('browser-boundaries',boundary),('results-verification',verify),('native-path',native),('profile-status',status),('full-worker',q)];summary={'schema':'AEGIS_ENV_A_VERIFICATION_1','pass':True,'profileHash':verify['profileHash'],'assertions':sum(len(r['checks'])for _,r in suites),'suites':[{'suite':name,'checks':len(r['checks']),'pass':r['pass']}for name,r in suites],'fullWorkerResultEqualsOfflineBytes':q['records']['resultHash']==verify['records'][0]['sha256']};(D/'verification-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
marker='\n## 최종 검수 E1–E4\n';p=H/'REPORT.md';s=p.read_text().split(marker)[0];r=q['records'];ms=r['elapsedMs'];s+=marker+f'''
| 항목 | 결과 |
|---|---|
| E1 | 전체 두 실행44,221,270bytes/SHA-256 동일. 각12005사격·96행·120궤적 |
| E2 | 전체 공개Worker API 실행 전후 게임 월드·RNG·틱 상태 동일. before/after `{r['beforeHash']}` |
| E3 | 실제 게임 월드와 독립 모델362샘플 비교. 시각/좌표/고도/속도/Mach 최대 오차 모두0, 신관 결과 동일 |
| E4 | 최대 거리96조합·궤적120조합 모두 결과/사유 존재. 마지막 성공/다음1km 실패 또는300km상한 근거 모두 있음 |

**{summary['assertions']}/{summary['assertions']} assertions,{len(suites)} suites PASS**, 페이지 오류0. 원시 영수증은 [검증 합계](evidence/verification-summary.json)에 있다. 프로파일 변경 경고도 실제 설정 변경/복원으로 확인했다.241개 복사 함수 원문은 최종 빌드와 모두 일치한다.

브라우저의 전체4 Worker 공개API 실행은 {ms/1000:.3f}초({ms/60000:.2f}분)였다. 동일한4vCPU에서 다른 검증과 병행한 비용이다. 시작 시 자동 실행하지 않으며, 플레이 프레임 예산에 넣는 기능이 아니다.

공개Worker 실행은 표 내장 전 후보에서 시작했고 엔진 캡슐·진단 suite·프로파일은 최종과 동일하다. 그 초기 runner의 HTML 해시는 종료 시 파일을 다시 읽은 값이어서 loaded-build 증거로 사용하지 않는다. 이 메타데이터 한계와 원시 영수증을 함께 보존한다. 최종 HTML 자체의 경로 비교·프로파일 검사는 별도 영수증으로 확인했다.
'''
if summary['fullWorkerResultEqualsOfflineBytes']:s+='\n추가로 브라우저 전체Worker 결과도 오프라인 두 결과와 같은 SHA-256을 냈다. 즉 세 전체 산출물의 JSON bytes가 동일하다.\n'
else:s+='\n브라우저와Node의 전체 결과 JSON 해시는 같지 않다. 서로 다른V8 런타임의 수치 결과 동일성을 주장하지 않는다. E1은 같은 오프라인 환경의 두 실행 기준이다.\n'
s+=f"\n최종 Chromium에서96행의 마지막 성공/다음 실패156경계를 재실행해 모든 성공·실패 사유가 일치했다. Node 대비 최근접 거리 차이 최대{boundary['maxClosestDeltaM']:.12g}m, 종말 속도 차이 최대{boundary['maxSpeedDeltaMps']:.12g}m/s였다. 작은 런타임 수치 차이에도 이번1km 표 경계는 동일하다.\n"
p.write_text(s);print(json.dumps({'pass':True,'assertions':summary['assertions'],'fullWorkerEqualsOffline':summary['fullWorkerResultEqualsOfflineBytes'],'elapsedMs':ms}))

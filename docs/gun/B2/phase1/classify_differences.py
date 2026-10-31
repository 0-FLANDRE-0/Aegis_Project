from pathlib import Path
import csv,json
P=Path(__file__).resolve().parent;q=json.loads((P/'evidence/regression-summary.json').read_text());rows=[]
for r in q['failedChecks']:
 suite,key=r['suite'],r['check'];kind=reason=None
 if suite=='raw obsolete UI88':kind='PREEXISTING_ENTRYPOINT';reason='MAP_B/E removed legacy cursor bridge. Old PIP_B test attempts obsolete cursor-based lock; canonical native exact-track UI88 passes.'
 elif suite=='raw MAP_D UI':kind='PREEXISTING_B1_ASSERTION';reason='Old blanket NOT_SURFACE_TRACK expectation; unchanged B1 migration explicitly initializes native80m/s EKF and requires VELOCITY_UNCERTAINTY blocking.213/213 actual ON/OFF.'
 elif suite=='raw MAP_D edges':kind='PREEXISTING_B1_ASSERTION';reason='Old CG Mod2 22km label expectation, approved B1 Mod4 is24km. Existing exact migration passed OFF/ON; no new range coefficient.'
 elif key.endswith('relativeSweptCPA'):kind='NEW_ON_MODEL_CHANGE_UNAPPROVED';reason='Old exact CPA fraction.5 is replaced by first accumulated beam signal+2ms. Original exact CPA assertion remains false.'
 elif 'physical-adapter-continuation'in suite:kind='NEW_ON_MODEL_CHANGE_UNAPPROVED';reason='Synthetic stationary Harpoon lies exactly on the projectile axis, outside50-90deg detection annulus. No proximity event, hence no forced native termination or journal result. Adapter code is unchanged.'
 elif '.G2.'in key:kind='NEW_ON_MODEL_CHANGE_UNAPPROVED';reason='Old zero-dispersion ballistic error<.35m expectation conflicts with anchor-calibrated nonzero physical launch dispersion. Nominal solver/drag unchanged.'
 elif key in ['G3.prox','G3.friendlySAM']:kind='NEW_ON_MODEL_CHANGE_UNAPPROVED';reason='Old axis-aligned point target never enters forward annular beam. No event is correct for that geometry; physical friendly-SAM adapter is not granted immunity.'
 elif key=='G4.nativeKill':kind='NEW_ON_MODEL_CHANGE_UNAPPROVED';reason='Synthetic exact r=0 burst has no positive fragment intercept time/direction. New geometric membership returns0; does not force a kill at overlap.'
 elif key.endswith('G5.singleNative'):kind='NEW_ON_MODEL_CHANGE_UNAPPROVED';reason='CG vertical pointing residual1.67-1.69m exceeds symmetric1.5m floor x.78=1.17m; waits until synthetic track support is blocked. WINDOW-only reproduces, ALIGNMENT-only fires; no final gate relaxation.'
 assert kind is not None,(suite,key)
 rows.append({**r,'classification':kind,'reason':reason,'expectedUpdated':False})
with(P/'evidence/classified-differences.csv').open('w',newline='')as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
lines=['# 원시 불일치 분류','', '모든 원본 검사와 실패를 보존한다. 새 기대값·허용치 갱신0. 아래는 수집된 bool 단언42개다. 별도 AIR 승인4raid+1hash는 원래 승인 manifest와 정확 대조했고, EW raw export 차이와 수상 fixture 조건은 별도 장부를 따른다.','', '| 모드 | 검사 | 분류 | 원인 |','|---|---|---|---|']
for r in rows:lines.append('| '+r['mode']+' | '+r['check']+' | '+r['classification']+' | '+r['reason']+' |')
lines+=['', '새 ON24개 단언은 사용자 검토 사항으로 남긴다. 원래 null-dereference 중단은 원시log에 그대로 있고, continuation은 이벤트가 없을 때FALSE로 기록해 나머지 단언까지 도달한 별도 진단이다. 원래 기대를 통과로 바꾸지 않았다.','', '속도 우려 이후 중단한 중복 rawONMapDUI는 rc−15로 남기고 이미 실제213/213 통과한 canonicalON 이관에 연결했다. 재사용4항목은 exit:null로 표시하며 fresh실행으로 세지 않는다. [부하 정리](evidence/validation-load-reduction.json).']
(P/'DIFFERENCES.md').write_text('\n'.join(lines)+'\n');out={'allCollectedDifferencesClassified':True,'counts':{k:sum(r['classification']==k for r in rows)for k in sorted({r['classification']for r in rows})},'newExpectationsApproved':0};(P/'evidence/difference-classification.json').write_text(json.dumps(out,indent=2)+'\n');print(out)

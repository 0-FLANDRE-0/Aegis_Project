"""Seal only current final-original checks and isolated serial timings."""
import argparse,gzip,hashlib,json,shutil,tarfile
from pathlib import Path
from suite_catalog import SUITES,ROOT
HERE=Path(__file__).resolve().parent
BASE='b4b58dcf61cff18674ec58f5798a2a15ca178ae9'
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('scratch',type=Path);p.add_argument('--checksums-only',action='store_true');a=p.parse_args();out=HERE/'evidence';out.mkdir(exist_ok=True);html=ROOT/'Aegis_SIM_v48_WIP_PERF_E.html';hs=sha(html.read_bytes())
 if not a.checksums_only:
  rows=[];captures=[];suites={'static':('docs/performance/E/verify_static.py','static.json'),**SUITES}
  for name,(script,filename)in suites.items():
   f=a.scratch/'final'/name/filename;raw=f.read_bytes();q=json.loads(raw);assert q['pass']and not q.get('errors'),name;tested=q.get('sha256',q.get('candidateSha256',q.get('htmlSha256')));assert tested==hs,(name,tested)
   groups=[q['checks']]if 'checks'in q else[c['checks']for c in q['cases']];assert all(v is True for g in groups for v in g.values()),name
   target=name+'.json'+('.gz'if len(raw)>30000 else '');data=gzip.compress(raw,9,mtime=0)if target.endswith('.gz')else raw;(out/target).write_bytes(data);rows.append({'suite':name,'checks':sum(len(g)for g in groups),'pass':True,'testedHtmlSha256':hs,'script':script,'scriptSha256':sha((ROOT/script).read_bytes()),'report':target,'reportSha256':sha(data)})
   for f in sorted(f.parent.glob('*.png')):
    target=name+'-'+f.name;shutil.copyfile(f,out/target);captures.append({'path':target,'sha256':sha(f.read_bytes()),'testedHtmlSha256':hs})
  timing={};files=[]
  for name,filename in [('cumulative','benchmark.json'),('native-latency','native-latency.json'),('native-render','native-render.json')]:
   folder=a.scratch/name;raw=(folder/filename).read_bytes();q=json.loads(raw);assert q['pass']and not q['errors']and q['sha256']==hs,name;timing[name]=q
   target=('cumulative.json'if name=='cumulative'else filename)+'.gz';data=gzip.compress(raw,9,mtime=0);(out/target).write_bytes(data);files.append({'path':target,'sha256':sha(data),'rawSha256':sha(raw),'rawBytes':len(raw)})
   for f in sorted(folder.iterdir()):
    if f.name.startswith('state-')or f.suffix=='.png':shutil.copyfile(f,out/f.name);files.append({'path':f.name,'sha256':sha(f.read_bytes()),'bytes':f.stat().st_size})
  excluded=a.scratch/'not-counted-cumulative-d-static-overlap';assert excluded.exists()
  with tarfile.open(out/'not-counted-cumulative-d-static-overlap.tar.gz','w:gz')as tar:tar.add(excluded,arcname=excluded.name)
  obsolete=a.scratch/'not-counted-pre-consume-final';oldnote=json.loads((obsolete/'note.json').read_text());(out/'not-counted-pre-consume-note.json').write_text(json.dumps(oldnote,indent=2)+'\n')
  exclusion=json.loads((excluded/'note.json').read_text());(out/'not-counted-cumulative-d-note.json').write_text(json.dumps(exclusion,indent=2)+'\n')
  manifest=json.loads((a.scratch/'perf-e.manifest.json').read_text());assert manifest['htmlSha256']==hs;assert manifest['changedPackedAssets']==[13];(out/'build-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
  b=timing['cumulative'];l=timing['native-latency'];r=timing['native-render'];n=sum(row['checks']for row in rows);ns=len(rows)
  q={'schema':'AEGIS_PERFORMANCE_E_VERIFICATION_SUMMARY_1','candidate':html.name,'candidateBytes':html.stat().st_size,'candidateSha256':hs,'mainSha256':manifest['mainSha256'],'baselineCommit':BASE,'baselineHtmlSha256':manifest['baselineSha256'],'directChecks':n,'directPass':n,'suites':rows,'captures':captures,'timings':{name:{'conditions':v['conditions'],'pairedCases':len(v['pairs']),'summary':v['summary'],'checks':v['checks'],'pass':v['pass']}for name,v in timing.items()},'timingFiles':files,'excludedAttempts':[exclusion,oldnote],'supersededOrHistoricalChecksIncluded':0,'errors':{'page':0,'core':0,'runtime':0,'presentation':0},'actions':'not dispatched; local final-original gate','pass':True};(out/'verification-summary.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
  cum='\n'.join(f"| {v['fleet']} | {v['count']} | {v['meanBefore']:.3f} | {v['meanAfter']:.3f} | {v['observedReductionPercent']:+.1f}% |"for v in b['summary'])
  latency='\n'.join(f"| {'CG-52'if v['ship'].startswith('CG')else 'DDG-119'} | {v['zM']} | {v['meanBeforeMs']/1000:.2f} | {v['meanAfterMs']/1000:.2f} | {v['observedReductionPercent']:+.1f}% |"for v in l['summary'])
  render='\n'.join(f"| {'CG-52'if v['config']['ship'].startswith('CG')else 'DDG-119'} | {v['config']['missiles']} | {v['config']['smoke']} | {v['meanBeforeMs']:.2f} | {v['meanAfterMs']:.2f} | {v['observedReductionPercent']:+.1f}% | {v['meanBeforeTransferBytes']:.0f} → {v['meanAfterTransferBytes']:.0f} |"for v in r['summary'])
  (HERE/'PERFORMANCE.md').write_text(f'''# PERF_E 최종 누적·표시 성능

HTML {q['candidateBytes']:,}bytes SHA256 `{hs}`, main `{q['mainSha256']}`. 최종 원본 직접 {n}/{n}PASS/{ns}suites, page/core/runtime/presentation 오류0. 과거/draft 검사 집계0. shape fixture·실제 GPU readback·native RAF 타이밍은 구별한다.

## 직접 누적 CPU 비교

H4A 최적화 시작 전 원본 → 최종 PERF_E를 같은 실행에서 직접 비교했다. 단계별 비율을 더하지 않는다. seed1831565813, warm120/measure240 fixed ticks, 각2회·AB/BA 반대·두 번째 조건 역순·총16쌍/32pages, 전체 회귀/카메라 종료 후 직렬 실행했다. 이전과 같은 CG 자함·optional allyCG/enemyDDG, 항공기/구표적OFF, native Kh32 helper16km/10000m/4방위의 diagnostic seeded measured tracks다. 자연 센서 획득이나 요격률 인증이 아니다. state/RNG/entity와240ticks complete가16쌍 모두 exact다. 기존 performance/profiler/lastBuildMs/lastAssessmentMs host-duration만 명시적으로 제외하며 raw states를 보존한다.

| 함정 | Kh32 | H4A ms/tick | PERF_E ms/tick | 관측 CPU 감소 |
|---:|---:|---:|---:|---:|
{cum}

첫 보고의 기록상31%/43%(단함/3함64발)는 서로 다른 실행의 잠정 절대시간 비교였다. 위 표는 격리된 직접 누적 비교로 갱신한다. 최초 H4A→D 탐색 측정은 파일 작업과 static 검사가 겹쳐 최종 개선율/PASS에 넣지 않는다. 당시 script/report/rawstates/note를 not-counted-cumulative-d-*로 보존한다.

## 실제 첫 cut/fold 제출

D→E 원본, native RAF/THREE/WebGL SwiftShader LOW640×480·자함만·물리 일시정지·x12/측면z1.5 및 갑판 주변z4/STARBOARD diagnostic Kh32 dud1회. 각2회·AB/BA 반대·순서 역전·8쌍/16pages를 위 CPU 비교 이후 다른 작업 없이 직렬 실행했다. 첫 THREE submission의 entry/exit actual cut keys와 attached geometry, native GL0, 물리/저장/RNG exact를 확인한다. generator를 강제 완료하지 않는다. E는 완성된 anchor 메쉬를 함께 먼저 보여주고 동일 주변 메쉬·장식·detail을 이어서 완성한다.

| 자함 | zM | D 평균 s | E 평균 s | 관측 지연 감소 |
|---|---:|---:|---:|---:|
{latency}

D 조사에서는 양측 anchor가 이미 matched였으며 주변 structure/fittings/sensors의42,676회 cooperative steps가 첫 공개를 막았다. D x12/z4가 약101.5초 후 실제 표시된 trace를 investigation에 보존한다. 이 D 재현으로 과거 C240초 timeout 원인을 소급 확정하지 않는다. 위 타이밍은 이번 원본끼리의 별도 완료 비교다.

## 실제 native 3D submit과 효과 전송

D→E native RAF/THREE/SwiftShader LOW480×360, warm4/measured8frames, 각2회·반대 AB/BA·조건 역순·8쌍/16pages. 물리는 paused, 자함 카메라235m·native distant64Kh32와 optional1200 제어 smoke(age2/fixedtime)를 사용한다. 멀리 있는 미사일은 frustum culling될 수 있으므로64개 근접 동시 표시 시험은 아니다. 아래 반복 연기는 시간이 고정된 GPU dirty-range 조건이며 모든 advancing-frame 효과 속도를 대표하지 않는다. source scene/drawcalls/triangles/particles 및 physical state/RNG와 native GL0를 대조한다.

| 자함 | Kh32 | 연기 입자 | D CPU ms/frame | E CPU ms/frame | 관측 CPU 감소 | driver subData bytes/frame |
|---|---:|---:|---:|---:|---:|---:|
{render}

별도 light-scene native WebGL2 getBufferSubData fixture에서 전체 GPU attribute bytes가 기존과 exact였다. 연기24개 반복 frame의 전달1728→0bytes, 위치 한 개 변경1728→4bytes를 확인했다. camera/order/origin/Float32 ULP/signed0/pending multipleflush/축소·숨김/재등장/reset도 확인했다. 버퍼 절약을 전체 게임 개선율로 바꾸지 않는다.

위 CPU와 native 제출 시간은 이 호스트의 관측이다. 소프트웨어 WebGL 절대 시간을 실제 GPU/휴대폰에 적용하지 않으며 hardware GPU 완료·FPS·자연 폭발/연속 다수 피격 효과/장시간 성능을 인증하지 않는다. 작은 감소·증가와 실행 변동을 그대로 표에 포함한다. 물리/센서/피해/RNG/고정 주기를 낮추지 않았다. Actions dispatch/CI PASS 주장은 없다.
''')
  status=f'''# v48 WIP PERF_E

PERF_D final `{BASE}` 위 performance-e. HTML **{q['candidateBytes']:,}bytes**, SHA256 `{hs}`, main `{q['mainSha256']}`.

완료: 두 등록 모델의 complete scar-anchor 메쉬를 먼저 함께 공개하고 주변 cut/fold/scorch/edges/detail을 계속한다. 현재·미공개·원본 버퍼 소유권을 유지해 incremental/cancellation/reset이 정확히 작동한다. LOD proxy는 같은 draw 전에 opening revision을 확인한다. split plane 거리와 triangle bound 임시 배열을 줄이고, 일곱 smoke instanced attributes의 exact Float32 dirty ranges만 actual native GPU에 전송한다. shader/pool/sort/opacity/물리/센서/AI/RNG/release/fixed60/120/20Hz는 보존한다.

최종 원본 직접 **{n}/{n}PASS/{ns}suites**, 오류0. CG/DDG quick/detail/sealed/추가 피격 전체 geometry attrs/index/groups/bounds/bindings exact 및 cancel/reset, 실제 native WebGL2 GPU buffers exact. 기존 전체 회귀·six strict ownship·3owner1/8/16/64·UI/카메라/물리/교전/EW/공유/저장/reset 포함. 별도 직렬 누적16쌍·native cut8쌍·render8쌍의 조건/실제 수치는 [성능](docs/performance/E/PERFORMANCE.md), 원시 증거는 [검증](docs/performance/E/evidence/verification-summary.json)을 따른다. 제어된 shape generator 완료는 latency 증거가 아니다.

D 갑판 주변 재현은 두 anchor가 matched였으며 주변 메쉬 작업 대기로 약101.5초 뒤 실제 cut이 나타났다. 최초 C timeout 자체는 소급 진단하지 않는다. 첫 탐색 H4A→D 측정은 static 작업과 겹쳐 최종 수치/PASS에서 제외하고 원본 증거를 보존한다.

원본 packed13만 변경한다. 이전 D HTML/status/SHA/manual workflow는 archive/v48/WIP_PERF_D에 samebytes/blob으로 이동했다. stablev48과 이전 증거는 보존한다. 사용자 §7.1 승인으로 full original 직접 upload·독립 원격 readback. Actions dispatch/main·선행 branch 병합/새 PR 생성 없음.

다음은 마지막 다수 동시 피격·장시간 과부하/자원 회수 점검 후 헬기/초수평선 → RGM-109E Block Va다. 이 host CPU/SwiftShader submission을 phone/hardware GPU FPS로 표현하지 않는다.
'''
  (ROOT/'AEGIS_PLAN_STATUS_v48_WIP_PERF_E.md').write_text(status)
  readme=ROOT/'README.md';text=readme.read_text().replace('## 최신 개발 기준 — 최적화 WIP PERF_D','## 직전 개발 기준 — 최적화 WIP PERF_D (당시 기록)',1)
  inst=ROOT/'AEGIS_PROJECT_INSTRUCTIONS.md';itext=inst.read_text().replace('### 최신 개발 기준 PERF_D — 최적화4단계','### 직전 개발 기준 PERF_D — 최적화4단계 (당시 기록)',1)
  for f in ['Aegis_SIM_v48_WIP_PERF_D.html','AEGIS_PLAN_STATUS_v48_WIP_PERF_D.md','SHA256SUMS_v48_WIP_PERF_D.txt']:
   text=text.replace(']('+f+')','](archive/v48/WIP_PERF_D/'+f+')');itext=itext.replace(']('+f+')','](archive/v48/WIP_PERF_D/'+f+')')
  block=f'''## 최신 개발 기준 — 최적화 WIP PERF_E

- [HTML]({html.name}), **{q['candidateBytes']:,}bytes**, SHA `{hs}`.
- 完成된 양측 anchor 구멍·변형을 먼저 공개한다. 주변 최종 메쉬와 수명/원본을 보존한다. 일곱 smoke attributes의 exact GPU dirty ranges만 전송하고 split/bound 임시 계산을 줄였다. packed13만 변경, 모델/물리/센서/AI/피해/RNG/고정 주기/발사 gate 유지.
- 최종 원본 **{n}/{n}PASS/{ns}suites**, 오류0. [상태](AEGIS_PLAN_STATUS_v48_WIP_PERF_E.md), [SHA](SHA256SUMS_v48_WIP_PERF_E.txt), [계약](docs/performance/E/README.md), [누적·3D 성능](docs/performance/E/PERFORMANCE.md), [검증](docs/performance/E/evidence/verification-summary.json).
- H4A→E 누적 CPU를 직접 같은 실행에서 측정한다. 단계별 개선율을 더하지 않는다. D→E native 피격·RAF/driver 전송은 별도이며 host/software WebGL 결과를 hardware/phone FPS로 표현하지 않는다.
- performance-e full original upload/readback, Actions dispatch/main·선행 branch 병합/새PR 없음. 다음은 다수 동시 피격·장시간 과부하/자원 회수 최종 점검 → 헬기/초수평선 → RGM-109E Block Va다.

'''.replace('完成된','완성된');readme.write_text(text.replace('## 직전 개발 기준 — 최적화 WIP PERF_D',block+'## 직전 개발 기준 — 최적화 WIP PERF_D',1))
  block=f'''### 최신 개발 기준 PERF_E — 최적화5단계

- 현재 v48_WIP_PERF_E, HTML {q['candidateBytes']:,}bytes SHA `{hs}`, main `{q['mainSha256']}`. PERF_D final `{BASE}` 위 performance-e. 현재 support/workflow/checksum은 E이고 이전 단계 문장은 당시 기록이다.
- 등록 CG/DDG quick job은 각 mesh의 ordered holes를 유지하며 모든 actual scar anchor를 먼저 완성해 함께 공개한다. 주변 작업은 계속한다. unprocessed 이전 live geometry/originals를 조기 복원·dispose하지 않으며 incremental 입력을 보존한다. final publish는 attached anchor buffers를 재사용한다. finally는 미공개 버퍼만, reset/import/retirement는 기존 lifecycle로 live cuts를 회수한다. legacy 비등록 모델은 기존 공개 경로다. LOD proxy는 같은 draw 전에 opening revision을 확인한다.
- 동일 split plane distance를 인접 edge에서 재사용하고 triangle bound의3배열을 제거한다. plane 순서/epsilon/정점/법선/색상·산술과 최종 attrs/index/groups/bounds/bindings를 보존한다.
- smoke shader/sort/pool/time/RNG를 유지하고 exact Float32 dirty range만 전송한다. pending ranges는 native onUpload 또는 r140 consumed-range 확인 이후에만 해제한다. 여러 flush/숨김/재등장/축소된 tail/camera/origin/ULP/signed0/reset과 WebGL2 GPU bytes exact를 검증한다.
- packed13만 변경, 나머지 packed/model/envelope bytes와 physical damage/flight/sensors/AI/actual release/fixed60/120/20Hz/PERF_A/B/C caches 보존. 최종 원본 {n}/{n}PASS/{ns}suites, 오류0. 누적 host CPU16쌍·native cut8쌍·RAF8쌍 직렬, 조건/한계/증거는 E docs를 따른다. generator shape fixture를 native latency로, host/SwiftShader submission을 hardware/phone FPS로 표현하지 않는다. 최초 H4A→D static-overlap timing은 제외/보존한다.
- 이전 D 네 파일 samebytes/blob archive, stablev48/이전 증거 유지. §7.1 승인 full original upload/독립 readback. Actions dispatch/main·선행 branch 병합/새 PR 없음. 다음은 다수 피격/장시간/자원 회수 최종 점검 이후 헬기 → RGM-109E Block Va다.

''';inst.write_text(itext.replace('### 직전 개발 기준 PERF_D',block+'### 직전 개발 기준 PERF_D',1))
  archive=ROOT/'archive/README.md';archive.write_text(archive.read_text()+'\n## WIP PERF_D 보존\n\n직전 D HTML/status/SHA/manual workflow 네 파일은 WIP_PERF_D에 samebytes/blob으로 이동했다. 이전 scripts/records는 당시 경로와 조건을 유지하며 현재 root/support/workflow는 PERF_E다.\n')
 q=json.loads((out/'verification-summary.json').read_text());assert q['candidateSha256']==hs
 status=ROOT/'AEGIS_PLAN_STATUS_v48_WIP_PERF_E.md';(ROOT/'SHA256SUMS_v48_WIP_PERF_E.txt').write_text(f"{hs}  {html.name}\n{sha(status.read_bytes())}  {status.name}\n")
 paths={line[66:]for line in (ROOT/'docs/performance/D/REPOSITORY_SUPPORT.sha256').read_text().splitlines()};moves={f:'archive/v48/WIP_PERF_D/'+f for f in ['Aegis_SIM_v48_WIP_PERF_D.html','AEGIS_PLAN_STATUS_v48_WIP_PERF_D.md','SHA256SUMS_v48_WIP_PERF_D.txt']};moves['.github/workflows/performance-d.yml']='archive/v48/WIP_PERF_D/performance-d.yml';paths={moves.get(f,f)for f in paths}
 paths.update(['docs/performance/D/REPOSITORY_SUPPORT.sha256','docs/performance/D/evidence/remote-publication.json',html.name,status.name,'SHA256SUMS_v48_WIP_PERF_E.txt','.github/workflows/performance-e.yml','README.md','AEGIS_PROJECT_INSTRUCTIONS.md','archive/README.md'])
 paths.update(str(f.relative_to(ROOT))for f in HERE.rglob('*')if f.is_file()and 'node_modules'not in f.parts and '__pycache__'not in f.parts and f.name not in ['REPOSITORY_SUPPORT.sha256','remote-publication.json'])
 (HERE/'REPOSITORY_SUPPORT.sha256').write_text(''.join(f'{sha((ROOT/f).read_bytes())}  {f}\n'for f in sorted(paths)));print(json.dumps({'pass':True,'checks':q['directChecks'],'suites':len(q['suites']),'supportFiles':len(paths),'sha256':hs}))
if __name__=='__main__':main()

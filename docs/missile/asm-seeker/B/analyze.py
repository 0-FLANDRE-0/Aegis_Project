"""Reduce the raw B matrix into reviewable audits without changing the product."""
from pathlib import Path
import collections,csv,html,itertools,json,statistics
P=Path(__file__).resolve().parent;D=json.loads((P/'BASELINE_DIAGNOSTICS.json').read_text())
def groups(rows,keys):
 rows=sorted(rows,key=lambda r:tuple(r['setup'][k] for k in keys))
 for k,g in itertools.groupby(rows,key=lambda r:tuple(r['setup'][x] for x in keys)):yield k,list(g)
def mean(xs):return sum(xs)/len(xs) if xs else None
def evidence(row,which):return row.get('snapshot',{}).get(which,{})
surface=[]
for key,g in groups([r for r in D['rangeCases'] if r['setup']['control']=='TARGET'],['kind','speedKt','altM','rangeKm']):
 surface.append({'kind':key[0],'speedKt':key[1],'altM':key[2],'rangeKm':key[3],'n':len(g),'rawTargetSeen':sum(bool(r['snapshot'].get('targetRaw')) for r in g),'originalPass':sum(bool(evidence(r,'original').get('pass')) for r in g),'shadowPass':sum(bool(evidence(r,'shadow').get('pass')) for r in g),'everTrack':sum(r['result']['everTrack'] for r in g),'meanOriginalScore':mean([evidence(r,'original').get('score',0) for r in g]),'meanShadowScore':mean([evidence(r,'shadow').get('score',0) for r in g]),'meanSnr':mean([r['snapshot'].get('measurement',{}).get('snr',0) for r in g]),'meanCrossExtentM':mean([r['snapshot'].get('targetEcho',{}).get('crossExtentM',0) for r in g]),'meanCrossResolutionM':mean([r['snapshot'].get('resolution',{}).get('crossM',0) for r in g])})
controls=[]
for key,g in groups([r for r in D['rangeCases'] if r['setup']['control']!='TARGET'],['control','altM','rangeKm']):
 controls.append({'control':key[0],'altM':key[1],'rangeKm':key[2],'n':len(g),'originalPass':sum(bool(evidence(r,'original').get('pass')) for r in g),'shadowPass':sum(bool(evidence(r,'shadow').get('pass')) for r in g),'originalTrack':sum(r['result']['everTrack'] for r in g)})
sam=[]
for key,g in groups(D['samArhCases'],['path','targetKind','rangeKm']):
 sam.append({'path':key[0],'targetKind':key[1],'rangeKm':key[2],'n':len(g),'echoPresent':sum(r.get('target') is not None for r in g),'originalPass':sum(bool((r.get('target')or{}).get('original',{}).get('pass')) for r in g),'shadowPass':sum(bool((r.get('target')or{}).get('shadow',{}).get('pass')) for r in g),'meanSnr':mean([(r.get('target')or{}).get('snr',0) for r in g])})
cue=[]
for key,g in groups(D['cueCases'],['label','rangeKm','speedKt','turnDeg']):
 cue.append({'label':key[0],'rangeKm':key[1],'speedKt':key[2],'turnDeg':key[3],'n':len(g),'insideBoth':sum(r['metrics']['classification']=='INSIDE_BOTH' for r in g),'searchInsideBasketOutside':sum(r['metrics']['searchInsideBasketOutside'] for r in g),'outsideSearch':sum(not r['metrics']['insideSearch'] for r in g),'everTrack':sum(r['result']['everTrack'] for r in g),'meanAzErrorDeg':mean([r['metrics']['azErrorDeg'] for r in g]),'maxAzErrorDeg':max(r['metrics']['azErrorDeg'] for r in g),'meanRangeErrorM':mean([r['metrics']['rangeErrorM'] for r in g])})
audit={'schema':'AEGIS_ASM_SEEKER_B_RANGE_AUDIT_1','inputSha256':D['inputSha256'],'elapsedS':D['elapsedS'],'caseCounts':{'surface':sum(q['n'] for q in surface),'controls':sum(q['n'] for q in controls),'samArh':sum(q['n'] for q in sam)},'surface':surface,'controls':controls,'samArh':sam,'sourceAudit':{'physicalExtents':'physicalRfReflectorRegistryWip13A2 / navalReflectorsC emit geometry-derived extentRange/Cross/Vertical','seaExtent':'maritimeRfSeaClutterFieldWip13A3 derives crossCell from range and beam-local azimuth sampling; rangeCell from existing rangeResolutionM','compositeExtent':'asmSeekerCompositeReturns uses power-weighted RMS of centroid separation plus member extents; no raw union bounding box','measurement':'asmSeekerEchoMeasurement does not add a resolution cell to extents; it reuses composite extents for glint sigma and target evidence','sharedConsumers':['Kh-32','Kh-35U','ESSM Block 2','SM-6 Block IA air','SM-6 Block IA surface']},'decision':{'resolutionDependence':'CONFIRMED','candidate':'REJECTED_BEFORE_ACTIVE','reason':'Directive-prescribed neutral-unobservable-axis normalization rejects previously valid stationary surface targets at 10-30 km. Threshold/weight fitting is prohibited.','falseAcquisition':{'seaOriginal':sum(q['originalTrack'] for q in controls if q['control']!='CHAFF'),'seaShadowPass':sum(q['shadowPass'] for q in controls if q['control']!='CHAFF'),'chaffOriginalTrack':sum(q['originalTrack'] for q in controls if q['control']=='CHAFF'),'chaffShadowPass':sum(q['shadowPass'] for q in controls if q['control']=='CHAFF')}}}
(P/'EVIDENCE_RANGE_AUDIT.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
cue_audit={'schema':'AEGIS_ASM_SEEKER_B_CUE_BASKET_AUDIT_1','cases':sum(q['n'] for q in cue),'rows':cue,'decision':{'sideEffect':'NOT_CONFIRMED','searchInsideBasketOutside':sum(q['searchInsideBasketOutside'] for q in cue),'outsideSearch':sum(q['outsideSearch'] for q in cue),'action':'NO_PRODUCT_CHANGE'}}
(P/'CUE_BASKET_AUDIT.json').write_text(json.dumps(cue_audit,ensure_ascii=False,indent=2)+'\n')
with (P/'RANGE_SCORE_TABLE.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=surface[0].keys(),lineterminator='\n');w.writeheader();w.writerows(surface)
# Compact SVG: 200 m, stationary mean scores by class/range.
W,H=920,460;colors={'DDG':'#62b5e5','CG':'#ffb347','SOV':'#7dd87d','HULK':'#dd75d8'};pts=[]
for kind in colors:
 q=[r for r in surface if r['kind']==kind and r['speedKt']==0 and r['altM']==200]
 pts.append((kind,[(70+r['rangeKm']/50*780,400-r['meanOriginalScore']*340) for r in q],[(70+r['rangeKm']/50*780,400-r['meanShadowScore']*340) for r in q]))
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><rect width="100%" height="100%" fill="#07131d"/>',f'<line x1="70" y1="{400-.55*340}" x2="850" y2="{400-.55*340}" stroke="#f66" stroke-dasharray="5 5"/><text x="855" y="{404-.55*340}" fill="#f88" font-size="12">0.55</text>']
for i in range(6):y=400-i*.2*340;svg.append(f'<line x1="70" y1="{y}" x2="850" y2="{y}" stroke="#244"/><text x="35" y="{y+4}" fill="#9ab" font-size="11">{i*.2:.1f}</text>')
for kind,a,b in pts:
 c=colors[kind];svg.append(f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x,y in a)}" fill="none" stroke="{c}" stroke-width="2"/><polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x,y in b)}" fill="none" stroke="{c}" stroke-width="2" stroke-dasharray="4 4"/>')
svg.append('<text x="70" y="25" fill="#dce" font-size="15">Kh-35U target evidence, 200 m / stationary (solid=current, dashed=resolution SHADOW)</text></svg>');(P/'range_score.svg').write_text(''.join(svg))
def mdtable(rows,fields,limit=None):
 rows=rows[:limit] if limit else rows;out=['| '+' | '.join(fields)+' |','|'+'|'.join(['---']*len(fields))+'|']
 for r in rows:out.append('| '+' | '.join(f'{r.get(k):.3f}' if isinstance(r.get(k),float) else str(r.get(k)) for k in fields)+' |')
 return '\n'.join(out)
far=[r for r in surface if r['altM']==200 and r['rangeKm'] in (40,45)];control_nonzero=[r for r in controls if r['originalPass'] or r['shadowPass'] or r['originalTrack']]
(P/'EVIDENCE_RANGE_AUDIT.md').write_text('# ASM_SEEKER_B 거리·분해능 감사\n\n- 660 수상/대조 조건 + 360 SAM ARH 조건, 오류 0.\n- 45 km/200 m에서 함정 반사는 존재하지만 해면 셀과 unresolved composite가 되어 횡폭이 약 km급으로 증가하고 `.55` 아래로 거부된다.\n- 폭은 `asmSeekerEchoMeasurement`가 임의로 더한 값이 아니다. 물리 member extent와 해면 셀 extent를 `asmSeekerCompositeReturns`가 전력 가중 RMS로 합성한 값이다. 해면 셀 횡폭 자체가 거리×빔 샘플링에 의존한다.\n- 지시서식 SHADOW는 해면 0을 유지하고 채프를 모두 거부하며 ESSM/SM-6 항공기·ASM을 유지했다. 그러나 기존 정지 함정 10–30 km 획득을 잃으므로 ACTIVE 승격 불가다.\n\n## 200 m 원거리 표본\n\n'+mdtable(far,['kind','speedKt','rangeKm','rawTargetSeen','meanSnr','meanCrossExtentM','meanCrossResolutionM','meanOriginalScore','meanShadowScore','everTrack'])+'\n\n## 오획득 변화가 있었던 대조군\n\n'+mdtable(control_nonzero,['control','altM','rangeKm','originalPass','shadowPass','originalTrack'])+'\n')
(P/'CUE_BASKET_AUDIT.md').write_text('# ASM_SEEKER_B 장거리 cue 감사\n\n- 120조건(두 ASM × 60/100/130 km × 4운동 × 5시드)을 실제 공용 시커 활성 상태에서 재생했다.\n- 탐색 구역 안·기존 바구니 밖: **0/120**. 탐색 구역 밖: **0/120**.\n- 획득 실패는 바구니가 아니라 현재 표적 검증/LOS 경로에서 발생했다. 바구니 확장 조건은 성립하지 않아 제품 변경 없음.\n\n'+mdtable(cue,['label','rangeKm','speedKt','turnDeg','insideBoth','searchInsideBasketOutside','outsideSearch','everTrack','meanAzErrorDeg','meanRangeErrorM'])+'\n')
(P/'ROOT_CAUSE.md').write_text('# ASM_SEEKER_B 원인 판정\n\n1. **분해능 의존성 Confirmed.** 장거리 함정 에코가 beam-local sea cell과 unresolved composite가 되며, sea-cell 횡폭이 broad/flat 배경 감점으로 다시 사용된다.\n2. **단순 분해능 중립화는 불충분.** 판단 불가 축을 가점·감점 모두에서 제외하면 정지 함정은 Doppler 두 항만 남아 기존 `.55`를 넘지 못한다. 임계값/가중치 재조정은 지시서상 금지이며 결과 맞춤이 된다.\n3. **필요한 후속 관측량.** 동일 range-angle-Doppler cell 안에서 표적성 판단을 하려면 주변 해면 대비 국소 signal-to-clutter contrast, dwell 간 centroid/전력 지속성, 또는 waveform 기반 range/Doppler morphology가 필요하다. 이는 지시서가 “제안만” 허용한 새 특징이라 이번 제품에는 넣지 않았다.\n4. **cue 바구니 부작용 Not confirmed.** 120조건 모두 기존 바구니 안이었다.\n5. **공용 영향.** ESSM B2와 SM-6 IA 대공/대함 모두 같은 evidence 관문을 사용한다. SHADOW에서 항공기/ASM 통과는 유지되고 채프 통과는 제거됐지만, 수상/정지 표적 퇴행 때문에 전체 후보는 승인할 수 없다.\n')
print(json.dumps({'surfaceRows':len(surface),'controlRows':len(controls),'samRows':len(sam),'cueRows':len(cue),'decision':audit['decision']}))

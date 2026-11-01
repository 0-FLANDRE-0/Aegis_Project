from pathlib import Path
import json,math
P=Path(__file__).resolve().parent;q=json.loads((P/'matching.json').read_text());assert q['within20to80'];vf=q['gurney']['vf'];vm=q['speedMedianMps'];vt=q['targetSpeedMps'];b=q['passDistanceM'];delay=q['processingDelayS'];center=q['fixedPolarCenterDeg']
def arrival(theta,speed):
 x=b/math.tan(math.radians(theta))-(speed+vt)*delay;w=-(speed+vt);a=w*w-vf*vf;bb=2*x*w;c=x*x+b*b;ds=bb*bb-4*a*c;t=min(t for t in[(-bb-math.sqrt(ds))/(2*a),(-bb+math.sqrt(ds))/(2*a)]if t>0);return {'bodyPolarDeg':math.degrees(math.atan2(b,x+w*t)),'fragmentTimeS':t}
raw=json.loads((P.parent/'phase1/evidence/native-trace/results.json').read_text());rows=[]
for r in raw['rows']:
 if not r['ship'].startswith('DDG'):continue
 c=r['condition'];t=r['traced'];field=t.get('fragment',{}).get('gunB2FragmentField',{})
 if c['rangeKm']not in[1,5,9]or not field:continue
 speed=vf*math.sin(math.radians(70))/math.tan(field['worldMinRad'])-vf*math.cos(math.radians(70));rows.append({'rangeKm':c['rangeKm'],'seed':c['seed'],'phase1ActualBurstSpeedMps':speed,'oldActualAngleDeg':field['bodyPolarDeg'],'representativePassM':b,'old70Design':arrival(70,speed),'newFixedDesign':arrival(center,speed)})
assert len(rows)==3
q['preImplementationRangeComparison']=rows;(P/'matching.json').write_text(json.dumps(q,indent=2)+'\n')
lines=['# B2A 적용 전 신관–탄두 정합 계산','',f'설계 계산 승인 범위 통과: 고정 탐지 중심 **{center:.12f}°**, 허용20~80° 안. 아직 제품에 적용하기 전의 계산 기록이다.','',f'Phase1 G7 AutoAA ON480회, 실제 기폭1417개 전체. 실제 기폭 탄속 중앙값 **{vm:.12f}m/s**. 기존 Gurney 속도 **{vf:.12f}m/s**. Kh35U 정면280m/s, 통과거리 b=12.5m, 처리지연 d=.002s.','', '기폭 순간의 탄체 병진 좌표를 쓴다. 설계점에서 파편 도달 몸체각90°이면 파편 비행시간 t=b/vf이고, x_det=(vm+vt)·(d+b/vf). 따라서 theta=atan2(b,x_det). 기존 |r+w·t|²=(vf·t)²의 양의 최소해로 다시 검산했으며 각도 오차는 부동소수 정밀도 수준이다.','', '저장된 native 관성계 파편 경계각에서 vm=vf·sin70°/tan(alpha_min)−vf·cos70°로1392개를 복원했다. 양쪽 경계각 역산은1e−8m/s 이내 일치한다. 나머지25개 ET는 동일 원본 B2를25조건 읽기 전용 재실행해 보충했다. 결과/RNG/기폭 로그는 정확히 같고, 중복 측정의 역산/직접속도 최대 오차도1e−8m/s 미만이다. 임의 표본 누락이나 명중률 기반 선택은 없다.','', '| 거리 km | Phase1 실제 기폭 탄속 m/s | 이전 실제 도달각 ° | 12.5m·옛70° 중심의 계산 도달각 ° | 12.5m·새 고정 중심의 계산 도달각 ° |','|---|---:|---:|---:|---:|']
for r in sorted(rows,key=lambda r:r['rangeKm']):lines.append(f'| {r["rangeKm"]} | {r["phase1ActualBurstSpeedMps"]:.6f} | {r["oldActualAngleDeg"]:.6f} | {r["old70Design"]["bodyPolarDeg"]:.6f} | {r["newFixedDesign"]["bodyPolarDeg"]:.6f} |')
lines+=['','앞의 실제 도달각은 기존 seed592001 실제 통과거리/신호 누적의 결과이고, 뒤의 두 열은 같은 거리별 실제 탄속을 쓰되 b=12.5m로 통일한 설계 비교다. 서로 같은 사건으로 간주하지 않는다. 새 실제 발사의 각도는 이후1440시도에 별도 기록한다.','', '새 중심은 위 대표 조건 한 곳에서 구한 고정값이다. 발별 속도에 따라 적응하지 않는다. 환형 반폭20°·반경25m·처리2ms·누적과 pass난수·파편90±20°·Gurney/피해Pk는 유지한다. 신호 누적 때문에 실제 최초 탐지가 중심각에서 정확히 일어난다고 가정하지 않는다.']
(P/'MATCHING.md').write_text('\n'.join(lines)+'\n');print('\n'.join(lines))

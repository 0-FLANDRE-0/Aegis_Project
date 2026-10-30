from pathlib import Path
import json
C=Path(__file__).resolve().parent;b=json.loads((C/'stage0/verification.json').read_text());n=json.loads((C/'stage1/verification.json').read_text());lookup={(r['weapon'],r['altM']):r for r in b['rows']}
for name,j in [('stage0',b),('stage1',n)]:
 title='변경 전 현재 엔진500km 측정' if name=='stage0' else '설계 사거리 정렬 후500km 측정'
 s=['# '+title,'','SM-2ER/SM-6, 고도1/10/20km, 정지 표적. 실제 게임 native 비행/유도/신관 경로와 기존 이상 지원 경계를 사용했다. 1km 이분 탐색 뒤 더 먼 모든 정수km를 확인했다. 실제 장비 성능과 비교하지 않는다.','',f"독립2회 각각 {j['receipts'][0]['calls']:,}사격, {j['bytes']:,}bytes 동일. SHA-256 `{j['sha256']}`.",f"벽시계 {j['receipts'][0]['elapsedMs']/1000:.3f}s / {j['receipts'][1]['elapsedMs']/1000:.3f}s. 다른 진단/브라우저 검사와 병행하여 단독 CPU 성능이 아니다.",'','| 기종 | 표적고도 | 최대 최초거리 | 실제 요격점거리 | 다음1km 실패 | 종말속도 | 최근접 |','|---|---:|---:|---:|---|---:|---:|']
 for r in j['rows']:
  f=r['firstFailure']['result'];s.append(f"| {r['weapon']} | {r['altM']/1000:g}km | {r['maxRangeKm']}km | {r['interceptPointKm']:.6f}km | {f['rangeKm']}km: {f['reason']} | {f['terminal']['speedMps']:.3f}m/s | {f['closestM']:.3f}m |")
 if name=='stage0':s+=['','이 결과를 확정·보고한 뒤8개 설계 사거리 값을 변경했다. [baseline.json](baseline.json)에 원본 HTML SHA와 source/inputs/private byte 동일성을 남겼다.']
 else:
  s+=['','| 기종 | 고도 | 변경 전→후 | 목표 | 부족분 |','|---|---:|---:|---:|---:|']
  for r in j['rows']:
   goal=360 if r['weapon']=='SM2ER' else 450;old=lookup[(r['weapon'],r['altM'])]['maxRangeKm'];s.append(f"| {r['weapon']} | {r['altM']/1000:g}km | {old}→{r['maxRangeKm']}km | {goal}km | {max(0,goal-r['maxRangeKm'])}km |")
  s+=['','8개 수치를 올리면 같은 실제 거리의 R/Rmax와 B4 fullLoft 보간 비율이 줄어 기존 스케줄러의 초기 로프트·선반이 낮아진다. 함수나 추진이 바뀌지 않아도 경로와 에너지 소모가 바뀔 수 있다. 이 결과를 추진 자체의 부족으로 단정하지 않는다. 실제 궤적과 실패 사유를 보고하고 추가 튜닝은 하지 않는다.','', '표는 각 조건의 전역1km 격자 최대이며 그 안의 모든 거리에서 명중한다는 뜻이 아니다. 360/450km 자체 사격 결과도 별도로 보고한다.']
 (C/name/'REPORT.md').write_text('\n'.join(s)+'\n')

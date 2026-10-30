"""Produce grounded UI census/classification from measured CSS boxes and sources."""
from pathlib import Path
import argparse,csv,json,re
H=Path(__file__).resolve().parent
SIZES=[(1400,900),(1400,560),(600,900),(844,390)]
def main():
 p=argparse.ArgumentParser();p.add_argument('layout',type=Path);p.add_argument('html',type=Path);p.add_argument('main',type=Path);a=p.parse_args();d=json.load(a.layout.open());source=a.main.read_text().splitlines();outer=a.html.read_text().splitlines()
 def locate(id,parent=''):
  for candidate in [id,parent]:
   if not candidate or candidate=='(no id)':continue
   for i,l in enumerate(outer):
    if re.search(r'id=[\"\']'+re.escape(candidate)+r'[\"\']',l):return 'HTML:'+str(i+1),l.strip()[:200]
   for i,l in enumerate(source):
    if candidate in l:return 'c55-game-main:'+str(i+1),l.strip()[:200]
  aliases={'(no id) #DIV>DIV:nth-child(3)':'CATALOG VIEW · PRESENTATION ONLY','(no id) #external3DView>DIV:nth-child(10)':'if(!this.floodPreviewPanel)','(no id) .external3d-toolbar.c14-topbar':'.c14-topbar','(no id) .scanline':'.scanline','(no id) .vignette':'.vignette'}
  if id in aliases:
   term=aliases[id]
   for kind,ls in [('HTML',outer),('c55-game-main',source)]:
    for i,l in enumerate(ls):
     if term in l:return kind+':'+str(i+1),l[max(0,l.find(term)-40):l.find(term)+250]
  return 'dynamic DOM / parent provider','id is generated from dataset or reusable row builder'
 def category(q):
  id=q['id'];t=(id+' '+q['label']).lower();parent=q['parent']
  if 'wip125-cell'in q['classes']or any(k in q['data']for k in ['paint','preset']):return '이지스 전용','Mk41 fwd/aft 셀 또는 SM/ESSM 편성 provider'
  if re.match(r'fleet(Speed|Rudder|Nav|View|Change)G$',id)or id in ['modeNavBtn','modeFleetBtn','modeDebugBtn','external3dBtn','external3DBackBtn']:return '공용','공용 항해/함 선택/화면 shell 조작'
  if parent in ['damageControlPanelV1','damageFloodPanelV1','dcTeamControls','dfWaveControls']and 'vls'not in id.lower():return '공용','runtime 구획/승조원/파공/물 모델의 데이터 기반 공통 컨트롤. 장비명은 선택 프로파일 데이터'
  if re.search(r'flyout|category',t):return '混合','공용 drawer/메뉴 구조; 장비별 내용을 담음'
  if re.search(r'spy|spq|spg|bridgemaster|illum|searam|phalanx|nulka|mk36|srboc|harpoon|mk45|sm2|sm6|essm|vls|sarh',t):return '이지스 전용','현재 US/AEGIS 장비 provider 호출 또는 그 편성/진단. 해당 장비를 SOV에 이식한다는 뜻 아님'
  if re.search(r'lock|autoeng|autotgt|radar|sensor|emcon|ecm|noise|decept|arm|weapon|missile|isar|aps|iff|helo|air|fleet|network|team|tactical|modeDebug',id,re.I):return '혼합','공용 조작/표시 shell에 현재 함정/항공/교전 내용이 결합'
  if parent=='NAV'or re.search(r'fullscreen|centerView|rangeBtn|spd[DU]|rud|route|undoWp|resetCamera|camera|c12|c11|c13|gfx|c14Controls|damageControl|damageFlood|shipDetail|time|pause|quit|close|copy',id,re.I):return '공용','화면/항해/공통 상태·구획·환경 조작. 장비별 내부 행/명칭은 별도 provider'
  if q['data'].get('tab')in ['NAV','FLEET']:return '공용','항해/함대 shell 탭'
  if 'time-btn'in q['classes']:return '공용','시뮬레이션 시간 UI'
  if re.search(r'mode|weapon|manual|auto|sail|loadout|preset|missile|ammo|gun|target|fire|engage',t):return '혼합','함정별 전투/편성 데이터 또는 테스트 목록을 선택하는 UI'
  return '혼합','공용 컨테이너/행이지만 현재 데이터·라벨 provider의 분리가 필요'
 controls=[]
 for q in d['controls']:
  cat,why=category(q);cat=cat.replace('混合','혼합');loc,excerpt=locate(q['id'],q['parent']);
  if loc=='dynamic DOM / parent provider':
   terms=[x for x in q['classes'].split(' ')if x]+['dataset.'+k for k in q['data']]+['data-'+re.sub(r'([A-Z])',lambda m:'-'+m[1].lower(),k)for k in q['data']]
   for term in terms:
    match=next(((i,l)for i,l in enumerate(source)if term in l),None)
    if match:loc,excerpt='c55-game-main:'+str(match[0]+1),match[1].strip()[:250];break
  if loc=='dynamic DOM / parent provider'and any(k in q['data']for k in ['targetChoice','allyChoice','allyEmcon','enemyEmcon','enemyAircraftChoice']):
   i=next(i for i,l in enumerate(source)if 'function mountDeploymentUiA('in l);loc,excerpt='c55-game-main:'+str(i+1),source[i]+'; dynamically constructed data-* choice rows'
  controls.append({**q,'category':cat,'reason':why,'code':loc,'excerpt':excerpt})
 controlCount=len(controls)
 ids={e['id']for r in d['rows']for e in r['elements']}|{'c','external3DView','controlDeckNavPage','controlDeckArmPage','controlDeckFleetPage','controlDeckAirPage','controlDeckDebugPage','drawSpySchedulerScreenOverlay'}
 for id in sorted(ids):
  if id in {q['id']for q in controls}:continue
  if id in ['c','external3DView','controlDeckNavPage','damageControlPanelV1','damageFloodPanelV1','external3DMiniCic','external3DReadout','c15CameraFlyout','c15SystemFlyout','toastWrap','c5BuildBadge']or re.search('scanline|vignette|Loading',id):cat,why='공용','공용 화면/항해/상태/구획/카메라 또는 장식 컨테이너'
  elif id in ['drawSpySchedulerScreenOverlay','wip125LoadoutOverlay']:cat,why='이지스 전용','SPY scheduler 또는 Mk41/US 탄종 편성 전용 내용'
  else:cat,why='혼합','공용 overlay/패널 틀에 현재 센서·무장·항공·도면 내용이 들어감'
  loc,excerpt=locate(id);controls.append({'id':id,'tag':'PANEL','label':id,'parent':'','category':cat,'reason':why,'code':loc,'excerpt':excerpt,'data':{},'classes':''})
 with (H/'UI_CLASSIFICATION.tsv').open('w')as f:
  w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['id_or_generated','tag','label','parent','category','reason','code_location','code_excerpt','dataset'])
  for q in controls:w.writerow([q['id']if q['id']!='(no id)'else'(no id) '+q['tag'].lower()+' '+json.dumps(q['data'],ensure_ascii=False),q['tag'],q['label'],q['parent'],q['category'],q['reason'],q['code'],q['excerpt'],json.dumps(q['data'],ensure_ascii=False)])
 ids=sorted({e['id']for r in d['rows']for e in r['elements']});lines=['# UI 레이아웃 조사 — 디자인/배치 변경 없음','','좌표는 CSS/client px의 `x,y,w,h`. 헤드리스 Chromium에서 직접 측정했다. `0×0`은 해당 조건에서 숨김/빈 컨테이너이며 수치가 없는 것으로 표시하지 않았다. 여러 조건의 UI를 동시에 열었다는 뜻이 아니다. 기본 상태와 조건부 DOM 공개 측정은 JSON에서 구별된다.','','- 가장자리 패널은 **controlDeckPanel 하나(2D)**다. 좌우 span ≥90%, 보이는 하단 경계에 닿거나 경계 아래까지 덮는지 검사한다. 기존 4/6px 여백은 붙어 있는 것으로 본다.','- 3D의 전체 변을 덮는 dock는 현재 없다. 미니 CIC, MSL STATUS, 상단 바/퀵 교전/HUD, drawer/flyout은 떠 있는 위젯이다.','- 모달·출항 편성·카탈로그는 독립 작업 화면/조건부 overlay다. 지도의 visible 영역을 영구 축소하는 dock가 아니다.','- canvas로 그리는 SPY scheduler는 DOM id가 없다. 아래에 별도 기록했다.','- 스캔라인/비네트는 장식 레이어이고 영역을 줄이지 않는다. 숨겨진 armsPanel/debugPanel은 legacy 컨테이너다.','','## 실제 사각형과 측면 도크 전환 검토','','| id 또는 기존 selector | 분류 | 1400×900 | 1400×560 | 600×900 | 844×390 | 측면 도크 전환 / 걸리는 점 |','|---|---|---|---|---|---|---|']
 def fmt(e):return ','.join(f'{e[k]:.2f}'.rstrip('0').rstrip('.')for k in ['x','y','w','h'])
 for id in ids:
  dims=[]
  for size in SIZES:
   es=[e for r in d['rows']if tuple(r['size'])==size for e in r['elements']if e['id']==id];native=[e for e in es if 'REVEALED'not in e['state']and e['visible']];revealed=[e for e in es if e['visible']];q=(native or revealed or es)[0];dims.append(fmt(q)+('†'if not native and revealed else''))
  edge=id=='controlDeckPanel';cat='가장자리(2D)'if edge else'장식'if any(x in id for x in ['scanline','vignette'])else'독립 모달/overlay'if re.search(r'Dialog|Overlay|CatalogLoading|CatalogClose',id)else'떠 있는 위젯'
  move='가능. 하단 bar/page 방향·미디어쿼리·장비 페이지 스크롤과 입력 차단 영역을 함께 설계해야 함'if edge else'모달 유지, 진입 버튼만 도크. 포커스/ESC/복사·긴 표·VLS 셀 가독성 고려'if cat=='독립 모달/overlay'else'이동 대상 아님'if cat=='장식'else'legacy 호환 컨테이너; 실제 현재 컨트롤과 중복 배치 금지'if id in ['armsPanel','debugPanel']else'가능. 메뉴/flyout의 앵커·닫기/포커스·부모 pointer-events·z-index 재설정 필요'if re.search(r'Drawer|Flyout|Controls|toolbar',id)else'가능. canvas 고정 반경/클릭 변환·DPR·최소 가독 크기를 함께 유지'if 'MiniCic'in id else'가능. 내용 길이·조건부 표시·고정 CSS anchor를 도크의 로컬 좌표로 교체'
  lines.append('| '+id.replace('|','/')+' | '+cat+' | '+' | '.join(dims)+' | '+move+' |')
 # Anonymous canvas UI is not discoverable by querying DOM boxes.
 overlay=[]
 for w,h in SIZES:
  width=min(360,max(300,w*.30));overlay.append(f'{(w-width)/2:g},6,{width:g},151')
 lines+=['| (canvas) drawSpySchedulerScreenOverlay | 떠 있는 위젯 | '+' | '.join(overlay)+' | 가능. canvas overlay를 독립 panel renderer/anchor로 분리하되 scheduler 진단 읽기만 유지 |','','† 진단에서 조건부 UI를 공개하여 얻은 위치. 기본 상태에서 떠 있다는 뜻은 아니다. `controlDeckPanel`은 탭별 높이가 다르므로 아래 표도 참조한다. 메시지/종말 결과/프로파일러 내용이 길어지면 위젯 높이가 달라질 수 있다. 이 표는 고정된 콘텐츠를 사용한 측정값이다.','','## 하단 패널 탭별 크기','','| 크기 | NAV | ARM | FLEET | AIR | DEBUG |','|---|---|---|---|---|---|']
 for size in SIZES:
  vals=[]
  for tab in ['NAV','ARM','FLEET','AIR','DEBUG']:
   rr=next(r for r in d['rows']if tuple(r['size'])==size and r['state']=='2D_'+tab);e=next(e for e in rr['elements']if e['id']=='controlDeckPanel');vals.append(fmt(e))
  lines.append('| '+'×'.join(map(str,size))+' | '+' | '.join(vals)+' |')
 lines+=['','## 미디어쿼리 경계','','| 조건 | 바꾸는 내용 |','|---|---|','| 641–980px | ARM 3열, EW 2칸·미사일 선택 3열 배치 |','| 641px 이상 & 높이 ≤520px | 하단 패널 최대 높이 확장, ARM 5열, 카드 padding/gap 축소, note 숨김 |','| ≤640px | dock 양옆/하단 4px, bar 2행/78px, NAV/DEBUG 재배치, ARM TGT/VLS/GUN/EW 하위 탭, HUD·3D 입력·damage·drawer·quick engage 크기 변경. AIR/FLEET의 동적 CSS도 포함 |','| 641–1000px | dock bar를 2행으로, utility를 다음 행 중앙으로. 980과 별개의 경계 |','| ≤700px | 손상/침수 패널의 폭·높이·safe area·터치 버튼 |','| pointer: coarse 또는 ≤640px | 3D 큰 터치 버튼/도구 모음, 미니 CIC 150px 높이와 내부 canvas 126px, MSL STATUS 46vw, help 숨김. 뒤쪽 C14/C15 규칙의 cascade도 작용 |','| prefers-reduced-motion | drawer/flyout 전환 애니메이션 제한; viewport/시뮬 시간 변경 없음 |','','CSSOM의 조건과 실제 선언 전체를 아래에 남긴다. 원본 outer CSS bytes는 SOV_A와 동일하다.','','```css']
 lines.extend(m['css']for m in d.get('media',[]));lines+=['```','','## UI 교체 분류','','`UI_CLASSIFICATION.tsv`는 현재 페이지에서 생성된 버튼·탭·입력 컨트롤 각각의 id(없으면 dataset), 분류, 이유, 코드 위치를 기록한다. `이지스 전용`은 이 프로젝트의 현 US/AEGIS 장비 provider 소속이라는 뜻이며 하푼/팰렁스가 이지스함에서만 쓰인다는 주장과 다르다. 데이터로 반복 생성되는 행/셀은 provider와 dataset으로 찾아간다. 현재 존재하지 않는 SOV 전투 버튼을 만들어 분류하지 않았다.','','이동 시 주요 제약: 짧은 가로 화면에서 HUD/메뉴/상태가 지도와 겹칠 수 있다. 이번에는 이를 숨기거나 측면 도크로 옮기지 않았다. 3D 작은 위젯을 모두 edge panel로 취급하면 기준점이 메뉴 개폐마다 흔들리므로 명시적으로 제외했다.']
 (H/'UI_LAYOUT_REPORT.md').write_text('\n'.join(lines)+'\n')
 print(json.dumps({'floating':len(ids),'controls':controlCount,'panels':len(controls)-controlCount,'mediaRules':len(d.get('media',[])),'categories':{k:sum(q['category']==k for q in controls)for k in ['공용','이지스 전용','혼합']}},ensure_ascii=False))
if __name__=='__main__':main()

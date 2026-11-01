"""Static report figures from native evidence; never a gameplay overlay."""
from pathlib import Path
import json,math,gzip
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).resolve().parent;A=P/'analysis';E=P/'evidence';O=P/'figures';O.mkdir(exist_ok=True)
def load(name):return json.loads((A/name).read_text())
def rows(name):
 f=E/name
 return [json.loads(l)for l in(f.open()if f.exists()else gzip.open(str(f)+'.gz','rt'))]
def save(fig,name):
 fig.tight_layout();fig.savefig(O/(name+'.svg'));fig.savefig(O/(name+'.png'),dpi=150);plt.close(fig)
arcs=load('arc-summary.json');fig,axs=plt.subplots(2,2,figsize=(12,5),sharex=True,sharey=True)
for i,m in enumerate([1,2]):
 for j,key in enumerate(['axis300','muzzle300']):
  ax=axs[i,j]
  for k,el in enumerate([-1,0,2,5]):
   a=next(a for a in arcs if a['mountId']==m and a['elevationDeg']==el);ax.broken_barh([(-90,180)],(k-.3,.6),facecolors='#c9ead3')
   for lo,hi in a['blockedIntervals'][key]:ax.broken_barh([(lo,hi-lo+.1)],(k-.3,.6),facecolors='#d85656')
  ax.axvline(0,c='black',lw=.7);ax.set_xlim(-80,80);ax.set_yticks(range(4),['-1°','0°','+2°','+5°']);ax.set_xlabel('Body azimuth (deg), + starboard');ax.set_ylabel('Elevation');ax.set_title(('Starboard'if m==1 else'Port')+' / '+('rotation axis'if j==0 else'muzzle'))
fig.suptitle('CG-52 structural ray obstruction at 300 m (red); 0.1° grid',y=1.02);save(fig,'cg-forward-occlusion')
cs=load('c1-sensitivity.json')
if cs:
 cs=sorted(cs,key=lambda r:r['bearing']);fig,ax=plt.subplots(figsize=(10,4));ax.bar([str(r['bearing'])for r in cs],[r['firingCases']/r['n']*100 for r in cs],color='#3385ae',label='Any 20mm fire');ax.plot([str(r['bearing'])for r in cs],[r['shipHits']/r['n']*100 for r in cs],c='#bc4848',marker='o',label='Ship hit');ax.set_ylim(0,110);ax.set_ylabel('Percent of measured seeds');ax.set_xlabel('Initial threat bearing (deg)');ax.legend();ax.set_title('CG-52 Kh-35U ×1 / AutoAA OFF / 10 seeds per bearing');save(fig,'c1-sensitivity')
ds=load('d1-cases.json');fig,axs=plt.subplots(2,1,figsize=(11,6),sharex=True);x=list(range(len(ds)));axs[0].bar(x,[r['gunRounds']for r in ds],label='20mm rounds');axs[0].bar(x,[r['ramRounds']for r in ds],bottom=[r['gunRounds']for r in ds],label='RAM missiles');axs[0].set_ylabel('Ammunition units (different types)');axs[0].legend();axs[1].bar(x,[r['hp']for r in ds],color=['#be4444'if r['hp']==0 else'#59a077'for r in ds]);axs[1].set_ylabel('Final game HP');axs[1].set_xticks(x,[str(r['seed'])[-2:]for r in ds]);axs[1].set_xlabel('Seed 4190xx');fig.suptitle('DDG-119 90° / Kh-35U ×1 / AutoAA OFF');save(fig,'d1-ammunition-hp')
damage=[d for d in load('damage-cases.json')if d['seed']in[419011,419018,419020,419026,419028]];fig,ax=plt.subplots(figsize=(10,4));bottom=[0]*len(damage)
for key,label in[('hull','Hull/longitudinal'),('propulsion','Propulsion'),('power','Power'),('cdc','CDC')]:
 vals=[d['statusTerms'][key]for d in damage];ax.bar([str(d['seed'])for d in damage],vals,bottom=bottom,label=label);bottom=[a+b for a,b in zip(bottom,vals)]
ax.axhline(100,c='red',ls='--',label='HP zero threshold');ax.set_ylabel('Native weighted damage before cap');ax.set_title('Instant HP reduction: native computeShipStatus terms');ax.legend(ncol=3,fontsize=8);save(fig,'damage-hp-terms')
d=next(d for d in rows('d1.jsonl')if d['case']['seed']==419018);fig,ax=plt.subplots(figsize=(11,4));ev=d['events']
ram={e['id']:e['tS']for e in ev if e['kind']=='WEAPON_LAUNCH'and e['type']=='RAM'}
for e in ev:
 if e['kind']=='WEAPON_END'and e['key'].startswith('RAM:'):
  i=int(e['key'].split(':')[1]);t=ram.get(i,0);ax.broken_barh([(t,e['tS']-t)],(i-.22,.44),facecolors='#6d9ec2');ax.text(e['tS']+.1,i,e['reason'],fontsize=7,va='center')
for e in ev:
 if e['kind']=='CIWS_FIRE':ax.plot(e['tS'],4,'k|',ms=18)
v=next(e['tS']for e in ev if e['kind']=='CONTACT_AUDIT'and e['mount']==1 and e['localId']==-5500001 and e['reason']=='PROTECTED_FRIEND');end=d['result']['seconds'];ax.broken_barh([(v,end-v)],(4.8,.4),facecolors='#d26f64');ax.axvline(end,c='red',ls='--');ax.text(end,5.7,'Impact / HP 0',ha='right',color='red');ax.set_yticks([1,2,3,4,5],['RAM 1','RAM 2','RAM 3','20mm shots','Local FRIEND veto']);ax.set_ylim(.5,6);ax.set_xlim(0,42);ax.set_xlabel('Native simulation time (s)');ax.set_title('DDG-119 seed 419018: local-protection veto precedes impact');save(fig,'d1-419018-timeline')
print('figures',len(list(O.glob('*.svg'))))

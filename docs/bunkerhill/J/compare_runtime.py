#!/usr/bin/env python3
import json,math,sys
from pathlib import Path
b,c=(json.loads(Path(p).read_text())for p in sys.argv[1:3]);diffs=[];errors=[]
def walk(x,y,path):
    if isinstance(x,float) and isinstance(y,float):
        if x!=y:
            allowed=math.isclose(x,y,rel_tol=1e-12,abs_tol=1e-9)
            diffs.append({'path':path,'baseline':x,'candidate':y,'absoluteDelta':abs(x-y),'withinTolerance':allowed})
            if not allowed:errors.append(path)
    elif type(x)!=type(y):errors.append(path+': type')
    elif isinstance(x,dict):
        if x.keys()!=y.keys():errors.append(path+': keys')
        for k in x.keys()&y.keys():walk(x[k],y[k],path+'.'+k)
    elif isinstance(x,list):
        if len(x)!=len(y):errors.append(path+': length')
        for i,(a,b)in enumerate(zip(x,y)):walk(a,b,path+f'[{i}]')
    elif x!=y:errors.append(path)
for field in ['phalanxSixCase','spotting']:walk(b[field],c[field],field)
r={'schema':'AEGIS_DDG119_WIP16B_REGRESSION_V1','bootSeed':c['bootSeed'],'runtimePassed':c['passed'],'runtimeTotal':c['total'],'aggregateExactlyEqual':b['phalanxSixCase']['aggregate']==c['phalanxSixCase']['aggregate'] and b['spotting']['aggregate']==c['spotting']['aggregate'],'wholeJsonExactlyEqual':not diffs and not errors,'floatComparison':{'absoluteTolerance':1e-9,'relativeTolerance':1e-12,'differences':diffs,'maxAbsoluteDelta':max((q['absoluteDelta']for q in diffs),default=0)},'errors':errors,'aggregate':c['phalanxSixCase']['aggregate']}
r['pass']=c['pass'] and b['bootSeed']==c['bootSeed'] and r['aggregateExactlyEqual'] and not errors
Path(sys.argv[3]).write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k]for k in ['runtimePassed','runtimeTotal','aggregateExactlyEqual','wholeJsonExactlyEqual','errors','pass']}));raise SystemExit(0 if r['pass']else 1)


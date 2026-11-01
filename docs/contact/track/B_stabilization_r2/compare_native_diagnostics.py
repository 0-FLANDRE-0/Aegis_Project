"""Read-only supplemental raw/header/diagnostic comparison; never approvals."""
from pathlib import Path
import gzip,hashlib,importlib.util,json
P=Path(__file__).resolve().parent;R1=P.parent/'B_stabilization';B=P.parent/'B';E=P/'evidence/native-diagnostic-deltas';E.mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('r2_native_delta_reader',P/'run_original_native.py');reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
def load(p):return json.loads(p.read_text())
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def packed(p,v):
 raw=json.dumps(v,separators=(',',':')).encode();p.write_bytes(gzip.compress(raw,6,mtime=0));return {'path':str(p.relative_to(P)),'rawSha256':hashlib.sha256(raw).hexdigest(),'gzipSha256':hashlib.sha256(p.read_bytes()).hexdigest()}
rows=[]
for label in ['shadow-off','shadow-on','active-off','active-on']:
 for suite in ['native','cohort']:
  now=load(P/'evidence/original-native-full'/f'{label}-{suite}.json');prior=load(R1/'evidence/original-native-full'/f'{label}-{suite}.json');old=load(B/('evidence/native-integration/active-on.json'if label.endswith('-on')else'evidence/native-integration/active-off.json'))if suite=='native'else load(B/'evidence/cohort-supplement/active.json')
  old_diag={'initialDiagnosticDefaults':old['initialDiagnosticDefaults'],'associationDiagnostics':old['traceB']if suite=='native'else old['diagnostics']['b'],'observationDiagnostics':old['nativeResult']['traceSnapshot']if suite=='native'else old['diagnostics']['a']}
  now_diag={'initialDiagnosticDefaults':now['initialDiagnosticDefaults'],'associationDiagnostics':now['diagnostics']['b'],'observationDiagnostics':now['diagnostics']['a']}
  prior_diag={'initialDiagnosticDefaults':prior['initialDiagnosticDefaults'],'associationDiagnostics':prior['diagnostics']['b'],'observationDiagnostics':prior['diagnostics']['a']}
  comparisons={'nativeResultVsOldB':reader.differences(old['nativeResult'],now['nativeResult']),'nativeResultVsR1':reader.differences(prior['nativeResult'],now['nativeResult']),'outerDiagnosticsVsOldB':reader.differences(old_diag,now_diag),'outerDiagnosticsVsR1':reader.differences(prior_diag,now_diag)}
  proof=packed(E/f'{label}-{suite}-all-deltas.json.gz',{'comparisons':comparisons,'noDifferingLeafIgnored':True,'oldBFieldsSource':'Unmodified published B evidence','R1FieldsSource':'Unmodified completed R1 replay evidence','controllerFieldMapping':'Explicit names map the same initial/A/B snapshot values; no field inside those values is removed.'})
  rows.append({'kind':'originalNative','label':label,'suite':suite,'deltaCounts':{k:len(v)for k,v in comparisons.items()},'proof':proof,'diagnosticDifferencesApproved':False})
for label in ['baseline','shadow','active']:
 now=load(P/'evidence/native-saturation'/f'{label}.json');prior=load(R1/'evidence/native-saturation'/f'{label}.json');comparisons={'nativeResultVsR1':reader.differences(prior['nativeResult'],now['nativeResult']),'outerDiagnosticVsR1':reader.differences(prior['actualTrace'],now['actualTrace']),'fullPrivateStateHashesVsR1':reader.differences(prior['perFixtureFullPrivateStateSha256'],now['perFixtureFullPrivateStateSha256'])};proof=packed(E/f'saturation-{label}-all-deltas.json.gz',{'comparisons':comparisons,'noDifferingLeafIgnored':True});rows.append({'kind':'nativeSaturation','label':label,'deltaCounts':{k:len(v)for k,v in comparisons.items()},'proof':proof,'diagnosticDifferencesApproved':False})
summary={'schema':'AEGIS_TRACK_B_R2_NATIVE_DIAGNOSTIC_DELTAS_1','status':'RECORDED_NOT_AN_APPROVAL','candidateSha256':load(P/'evidence/native-active/SUMMARY.json')['candidateSha256'],'moduleSha256':hashlib.sha256((P/'association.js').read_bytes()).hexdigest(),'rows':rows,'allRawDifferencesRetained':True,'existingRawOrAssertionsModified':False,'browserRuns':0,'releaseApproved':False,'note':'Original native gameplay result/state equality is scoped separately. Outer controller/association diagnostic snapshots are explicitly compared here; new fields/events are not silently called byte-identical or approved.'};write(E/'SUMMARY.json',summary);print(json.dumps({'status':summary['status'],'rows':[{'kind':r['kind'],'label':r['label'],'suite':r.get('suite'),'deltaCounts':r['deltaCounts']}for r in rows]},indent=2))

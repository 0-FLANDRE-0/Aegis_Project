from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parent;R=P.parents[3];A=P.parent/'phase1a';sha=lambda b:hashlib.sha256(b).hexdigest();scope=json.loads((P/'evidence/scope.json').read_text());assert scope['pass']
spec={
 'evidence/surface-summary.json':'Surface HE and first-hit functions are byte-identical; GUN_B1 fragment fields are referenced only by MFF airburst paths. Section7 explicitly says not to rerun surface first-hit.',
 'evidence/dispersion/validation.json':'Launch alignment and dispersion symbols/configuration are byte-identical; B2A 400-shot anchor is reused.',
 'evidence/static.json':'B2A protected-function audit is historical support; current scope independently confirms all 281 protected hashes.',
 'evidence/b2-reference/g7-off120.jsonl':'AutoAA OFF rows contain no Mk45 release/burst and all inactive paths are source-identical.',
 'TEST_REUSE.json':'Transitive ledger for SAM/common UI/EW/H3/domain/world120 evidence; current scope proves every corresponding symbol unchanged.',
 'BUILD_STATUS.json':'B2A measurement and validation status retained as the immediate baseline.',
}
items=[]
for rel,basis in spec.items():
 f=A/rel;assert f.exists();items.append({'report':f.relative_to(R).as_posix(),'sha256':sha(f.read_bytes()),'basis':basis,'freshB2BExecution':False})
q={'schema':'AEGIS_GUN_B2B_REUSE_1','authorizedBy':'INSTRUCTIONS.md section7','sourceGuard':'docs/gun/B2/phase1b/evidence/scope.json','sourceGuardSha256':sha((P/'evidence/scope.json').read_bytes()),'baselineCommit':'fa0fdde96dfcc7c0655f8ba8bc3e7a903b4591f4','baselineHtmlSha256':'9515e70cb88f7caac8dd9c0b618a104a878882a5a1c06f0967059150e2b7d516','noRelabelingAsFresh':True,'surfaceFirstHitFreshExecution':False,'items':items}
(P/'TEST_REUSE.json').write_text(json.dumps(q,indent=2)+'\n');print('reuse',len(items))

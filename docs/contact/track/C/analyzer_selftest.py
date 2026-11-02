"""Offline lineage arithmetic checks, not additional game simulations."""
from pathlib import Path
import copy,hashlib,json
import analyze
P=Path(__file__).resolve().parent
base={'step':1,'timeS':1/60,'ownerEntityId':'O1','store':'CANONICAL','trackId':1,'type':'UPDATE','decision':'ACCEPT','fields':{'rangeM':1000},'lineageStatus':'EXACT_RF_OBJECT_OR_EXACT_MEASURED_POLAR_CLONE','physicalUid':'P1','priorPhysicalUid':None,'priorPhysicalAlive':None,'knownOwnLaunch':False,'before':{'confirmed':True},'after':{'confirmed':True},'measurementUid':'RF1'}
def run(rows):return analyze.lineage({'trackCLineage':{'records':rows,'labels':[],'lifecycle':[],'seeker':[],'candidateTrace':None},'targets':[]})['counts']
def main():
 a=copy.deepcopy(base);b={**base,'trackId':2,'measurementUid':'RF2'};c={**base,'step':2,'timeS':2/60,'priorPhysicalUid':'P1','priorPhysicalAlive':True};q=run([a,b,c]);seed=[{**a,'step':0},{**b,'step':0,'physicalUid':'P2'}]
 swap=[{**a,'physicalUid':'P2','priorPhysicalUid':'P1','priorPhysicalAlive':True},{**b,'physicalUid':'P1','priorPhysicalUid':'P2','priorPhysicalAlive':True}]
 metadata={**a,'type':'ASSIGNMENT','decision':'ASSOCIATE_WITHOUT_HIT','physicalUid':'P2','priorPhysicalUid':'P1','priorPhysicalAlive':True}
 checks={'duplicatePairCountedOnce':q['simultaneouslyFirmSamePhysicalFilePairs']==1,'differentOwnersNotDuplicate':run([a,{**b,'ownerEntityId':'O2'}]).get('simultaneouslyFirmSamePhysicalFilePairs',0)==0,'differentStoresNotDuplicate':run([a,{**b,'store':'C55:1','after':{'confirmed':True,'ownFireEvidence':False}}]).get('simultaneouslyFirmSamePhysicalFilePairs',0)==0,'reciprocalSwapSeparate':run(seed+swap)['firmReciprocalIdSwap']==1,'terminalReuseNotLiveMerge':run([a,{**c,'physicalUid':'P2','priorPhysicalAlive':False}]).get('firmPhysicalFalseMerge',0)==0,'noEchoNotMeasurement':run([{**a,'fields':{},'lineageStatus':'UNLINKED'}]).get('actualMeasuredRfRecords',0)==0,'metadataIsNotFilterUpdate':run([a,metadata,c]).get('acceptedFilterUpdates')==2 and run([a,metadata,c]).get('firmPhysicalFalseMerge',0)==0,'metadataDisagreementRecordedSeparately':run([a,metadata,c])['metadataOnlyAssociationDisagreesWithFilterLineage']==1,'unknownLivenessNeverCalledDead':run([a,{**c,'physicalUid':'P2','priorPhysicalAlive':None}]).get('PREDECESSOR_PHYSICAL_LIVENESS_NOT_RECORDED')==1}
 noise={**base,'lineageStatus':'UNLINKED','physicalUid':None,'measurementUid':None,'decision':'CREATE'}
 proof={'exactOriginalRecord':noise,'physicalUid':None}
 def origin(rows,proofs):return analyze.lineage({'trackCLineage':{'records':rows,'labels':[],'lifecycle':[],'seeker':[],'candidateTrace':None},'targets':[]},proofs)['counts']
 checks['provenNoReflectorIsNotFakePhysicalId']=origin([noise],[proof]).get('receiverProcessingNoiseMeasurementsNoReflector')==1 and origin([noise],[proof]).get('exactPhysicalMeasurementFilterLinks',0)==0
 checks['provenNoiseNativeFilterBirthStillCounted']=origin([noise],[proof]).get('acceptedFilterUpdates')==1
 checks['nearbyUnprovedNoiseStillUnlinked']=origin([{**noise,'step':2}],[proof]).get('UNLINKED')==1
 assert all(checks.values()),checks;out=P/'evidence/ANALYZER_SELFTEST.json'
 if out.exists():
  archive=P/'evidence/attempts/analyzer-before-filter-vs-metadata-separation.json'
  if not archive.exists():archive.write_bytes(out.read_bytes())
 out.write_text(json.dumps({'pass':True,'checks':checks,'classification':'OFFLINE_REPORT_ARITHMETIC_NOT_GAME_SIMULATION','analyzerSha256':hashlib.sha256((P/'analyze.py').read_bytes()).hexdigest()},indent=2)+'\n');print(checks)
if __name__=='__main__':main()

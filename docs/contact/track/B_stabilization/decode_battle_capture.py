"""Losslessly restore a stored battle capture's columnar records; no game run.

Usage: python decode_battle_capture.py INPUT.json.gz OUTPUT.json
The output preserves absent keys vs null, original object-key order and all
records. Binary floating point values are read by Python's standard JSON parser.
The browser's pre-export complete JSON.stringify identity/SHA proof is retained
as transportReceipt. It precedes runner validation and separate source/passive
extraction, and is not misrepresented as a hash of Python's JSON serialization.
"""
from pathlib import Path
import argparse,gzip,importlib.util,json

P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('battle_capture_codec',P/'battle.py')
battle=importlib.util.module_from_spec(spec);spec.loader.exec_module(battle)

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('input',type=Path);ap.add_argument('output',type=Path);a=ap.parse_args()
 source=a.input.read_bytes();value=json.loads(gzip.decompress(source)if a.input.suffix=='.gz'else source)
 restored=battle.decode_capture(value);receipt=restored.get('transportReceipt')
 if receipt:
  assert receipt['jsonStringifyExact']and receipt['originalJsonSha256']==receipt['decodedJsonSha256']
  assert receipt['omittedRecords']==0 and receipt['omittedFields']==0
  assert len(restored['associationReturns'])==receipt['nativeAssociationRecordCount']
  assert len(restored['observedPlotLineage'])==receipt['lineageRecordCount']
 a.output.write_text(json.dumps(restored,ensure_ascii=False,separators=(',',':'))+'\n')
 print(json.dumps({'output':str(a.output),'associationReturns':len(restored['associationReturns']),'observedPlotLineage':len(restored['observedPlotLineage']),'transportRoundTripVerified':receipt is not None,'nativeCalls':0}))

if __name__=='__main__':main()

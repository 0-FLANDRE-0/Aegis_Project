"""HELI_D -> HELI_E, packed13 only. Previous sources/assets remain immutable."""
import argparse,base64,gzip,hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent;OLD=ROOT/'docs/helicopter/E'
BASE_SHA='843c86ac5de6f99ee3b9c24dcf425a79e5c0a55a11f0bc1cdec7c7c1546b25ac'
def rep(s,a,b,count=1):
 assert s.count(a)==count,(a[:100],s.count(a),count)
 return s.replace(a,b)
def decoded(s,i=13):return gzip.decompress(base64.b64decode(re.search(r'data-c55-index="'+str(i)+r'">(.*?)</script>',s,re.S)[1])).decode()
def patch(s):
 for f in ['motion.js','runtime.js','ui.js']:s=rep(s,(OLD/f).read_text(),(HERE/f).read_text())
 def render(folder):return (folder/'render.js').read_text().replace('__HELO_RIG_JSON__',json.dumps(json.loads((folder/'rig.json').read_text()),separators=(',',':')))
 s=rep(s,render(OLD),render(HERE))
 s=rep(s,(OLD/'stage_b.js').read_text(),(HERE/'model.js').read_text()+'\n'+(HERE/'radar.js').read_text()+'\n'+(HERE/'probes.js').read_text())
 # A named physical hook is opt-in. Default SPY/SPQ/NAV equation, RNG and
 # detection behavior remain byte-identical around these optional expressions.
 s=rep(s,'opts.physicalEchoGate(ref,{azRad:az,horizontalRangeM:h,rangeM})','opts.physicalEchoGate(ref,{azRad:az,elRad:el,horizontalRangeM:h,rangeM})')
 s=rep(s,"const beamGain=Math.exp(-2.7726*((physicalGate?.azimuthPeakGain?0:(azOff/Math.max(1e-6,halfAz))**2)+(elOff/Math.max(1e-6,halfEl))**2))","const beamGain=physicalGate?.beamGain01??Math.exp(-2.7726*((azOff/Math.max(1e-6,halfAz))**2+(elOff/Math.max(1e-6,halfEl))**2))")
 # Pass exact mode resolution/model into the existing physical sea-cell sampler.
 s=rep(s,'rangeCells:Number(opts.seaRangeCells)};','rangeCells:Number(opts.seaRangeCells),rangeResolutionFloorM:opts.aps153F?1:undefined,seaClutterModelF:opts.seaClutterModelF,minRangeM:opts.aps153F?opts.minRangeM:undefined,maxRangeLimitM:opts.aps153F?maxRangeKm*1000:undefined};')
 s=rep(s,'800,80000),minRangeM=clamp(Number(opts.minRangeM)||450,120,','800,opts.maxRangeLimitM??80000),minRangeM=clamp(Number(opts.minRangeM)||450,opts.seaClutterModelF?1:120,')
 s=rep(s,'rangeRes=clamp(Number(opts.rangeResolutionM)||110,35,500)','rangeRes=clamp(Number(opts.rangeResolutionM)||110,opts.rangeResolutionFloorM??35,500)')
 s=rep(s,'sigma0=Math.pow(10,(bp.sigma0Db+roughDb)/10)*bp.scale*(.38+.76*grazing01)*directional','sigma0=opts.seaClutterModelF?opts.seaClutterModelF({receiver:rx,rangeM:r},st):Math.pow(10,(bp.sigma0Db+roughDb)/10)*bp.scale*(.38+.76*grazing01)*directional')
 a="snr=q.signal/Math.max(1e-9,interference),pd=clamp(snr/(snr+Math.max(.1,Number(opts.pdHalfSnr)||1)),.0001,.9995);if(random()>pd)continue;"
 b="receiverF=opts.aps153F?apsCfarPhysicalF({opts,rangeM:q.rangeM,horizontalRangeM:q.h,signal:q.signal,localClutter,distributed:q.distributed,beamGain:q.beamGain,weatherQ:maritimeRfWeatherPathFactorWip13A3(band,2*q.rangeM/1000)}):null,snr=receiverF?.snr??q.signal/Math.max(1e-9,interference),pd=receiverF?.pd??clamp(snr/(snr+Math.max(.1,Number(opts.pdHalfSnr)||1)),.0001,.9995);if(random()>pd)continue;"
 s=rep(s,a,b)
 s=rep(s,'rangeSigmaM=Math.max(1,(Number(opts.rangeSigmaM)||25)*qs),azSigmaDeg=Math.max(.002,(Number(opts.azSigmaDeg)||.08)*qs)','rangeSigmaM=receiverF?.rangeSigmaM??Math.max(1,(Number(opts.rangeSigmaM)||25)*qs),azSigmaDeg=receiverF?.azSigmaDeg??Math.max(.002,(Number(opts.azSigmaDeg)||.08)*qs)')
 s=rep(s,"    return {schema:'AEGIS_ANONYMOUS_RF_DWELL_V48_WIP13B13'","    if(opts.aps153F)echoes.push(...apsNoiseEchoesF(opts,random,normal));\n    return {schema:'AEGIS_ANONYMOUS_RF_DWELL_V48_WIP13B13'")
 # Detached diagnostic physical fixtures enter only before RF synthesis. No
 # measured plot/track injection; normal live scene expression is unchanged.
 s=rep(s,'scene=shipboardRadarPhysicalSceneWip13B13(band,seaField),candidates=[];',"scene=opts.aps153F?.diagnosticReflectors?[...opts.aps153F.diagnosticReflectors,...(seaField?maritimeRfSeaClutterFieldWip13A3({...seaField,band}):[])]:shipboardRadarPhysicalSceneWip13B13(band,seaField),candidates=[];")
 s=rep(s,'candidates.push({ref,dx,dy,dz,h,rangeM,az,el,beamGain,losQ,rcsM2,signal,distributed});','candidates.push({ref,dx,dy,dz,h,rangeM,az,el,beamGain,losQ,rcsM2,signal,distributed,scanOrdinalF:physicalGate?.scanOrdinalF});')
 s=rep(s,"echoes.push({schema:'AEGIS_ANONYMOUS_RF_ECHO_V48_WIP13B13',radarId,band,x,y,z","echoes.push({...(opts.aps153F?{scanOrdinalF:q.scanOrdinalF}:{}),schema:'AEGIS_ANONYMOUS_RF_ECHO_V48_WIP13B13',radarId,band,x,y,z")
 # Physical helicopter aspect is evaluated independently for EACH receiver.
 s=rep(s,"    if(ref?._physicsKind==='NAVAL_SHIP')return navalRcsC", "    if(ref?._physicsKind==='HELICOPTER'){const a=Math.atan2(obsY-ref.y,obsX-ref.x)-(truth?.headingRad??0);return HELO_SENSOR_VALUES_E.rcsBaseM2+HELO_SENSOR_VALUES_E.rcsBroadsideM2*Math.sin(a)**2;}\n    if(ref?._physicsKind==='NAVAL_SHIP')return navalRcsC")
 s=rep(s,"function heloCiwsSourcesE(){", "function heloCiwsSourcesE(observer=null){")
 s=rep(s,'key:ref.rfId,rcs:ref.rcsM2,own:false','key:ref.rfId,rcs:observer?rfReflectorRcsM2Wip13A2(ref,\'IJ\',observer.x,observer.y,observer.z??0):ref.rcsM2,own:false')
 s=rep(s,"sources.push(...heloCiwsSourcesE());return sources;","sources.push(...heloCiwsSourcesE({x:r.navigation.positionWorld.x,y:r.navigation.positionWorld.y,z:8}));return sources;")
 s=rep(s,"    sources.push(...heloCiwsSourcesE());","    sources.push(...heloCiwsSourcesE({x:metersToWorld(o.xM),y:metersToWorld(o.yM),z:o.zM}));")
 # Replace only the publishing function; preserve link policy, reset and guards.
 a=s.index('function heloPublishRadarPlotsE(');b=s.index('function heloHawklinkResetE(',a)
 s=s[:a]+(HERE/'publisher.js').read_text()+'\n'+s[b:]
 return s
def build(raw):
 assert hashlib.sha256(raw).hexdigest()==BASE_SHA;html=raw.decode();main=patch(decoded(html)).replace('v48_WIP_HELI_D','v48_WIP_HELI_E');z=gzip.compress(main.encode(),9,mtime=0)
 m=re.search(r'data-c55-index="13">(.*?)</script>',html,re.S);html=html[:m.start(1)]+base64.b64encode(z).decode()+html[m.end(1):]
 m=re.search(r'const records=(\[.*?\]);',html,re.S);records=json.loads(m[1]);records[13].update(rawBytes=len(main.encode()),gzipBytes=len(z),sha256=hashlib.sha256(main.encode()).hexdigest());html=html[:m.start(1)]+json.dumps(records,separators=(',',':'))+html[m.end(1):]
 return html.replace('v48_WIP_HELI_D','v48_WIP_HELI_E').replace('V48_WIP_HELI_D','V48_WIP_HELI_E'),main
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('output',type=Path);a=p.parse_args();html,main=build(a.baseline.read_bytes());a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(html);a.output.with_suffix('.main.js').write_text(main);report={'baselineSha256':BASE_SHA,'htmlSha256':hashlib.sha256(html.encode()).hexdigest(),'mainSha256':hashlib.sha256(main.encode()).hexdigest(),'bytes':len(html.encode()),'addedBytes':len(html.encode())-a.baseline.stat().st_size};a.output.with_suffix('.manifest.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))

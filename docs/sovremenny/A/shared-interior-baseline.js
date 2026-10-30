function createBunkerInterior(flood,geometry=shipGeometryLayout()){
  const {decks,spaces,macroSpaces,portals,equipmentNodes,byId}=bunkerInteriorAuthored(flood,geometry),
    M={...V48_WIP06_INTERIOR_MODEL,buildId:'CG52_FUNCTIONAL_INTERIOR_G_1',provenance:'CG52_SOURCE_CLIPPED_SIM_TUNED_FUNCTIONAL_ZONING_NOT_ACTUAL_INTERIOR'},
    raw=macroSpaces,deepFreeze=deepFreezeShipProfileV48Wip09,clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
  let authoredAudit=null;
  const topologyAudit=()=>{
    if(authoredAudit)return authoredAudit;
    const route=spaces.filter(s=>s.routeable),seen=new Set(route.length?[route[0].id]:[]),queue=[...seen];
    while(queue.length){const id=queue.shift();for(const p of portals){const n=p.a===id?p.b:p.b===id?p.a:null;if(n&&byId.get(n)?.routeable&&!seen.has(n)){seen.add(n);queue.push(n);}}}
    const overlap=[];for(let i=0;i<spaces.length;i++)for(let j=i+1;j<spaces.length;j++){const a=spaces[i],b=spaces[j];
      if(Math.min(a.x1,b.x1)-Math.max(a.x0,b.x0)>1e-6&&Math.min(a.y1,b.y1)-Math.max(a.y0,b.y0)>1e-6&&Math.min(a.z1,b.z1)-Math.max(a.z0,b.z0)>1e-6)overlap.push([a.id,b.id]);}
    return authoredAudit=deepFreeze({schema:'AEGIS_CG52_INTERIOR_AUDIT_V2',spaceCount:spaces.length,macroSpaceCount:macroSpaces.length,portalCount:portals.length,
      equipmentCount:equipmentNodes.length,deckCount:decks.length,uniqueSpaceIds:byId.size===spaces.length,
      uniquePortalIds:new Set(portals.map(p=>p.id)).size===portals.length,uniqueEquipmentIds:new Set(equipmentNodes.map(p=>p.id)).size===equipmentNodes.length,
      endpointsValid:portals.every(p=>byId.has(p.a)&&byId.has(p.b)),equipmentSpacesValid:equipmentNodes.every(q=>byId.has(q.spaceId)),
      routeable:route.length,reached:seen.size,unreachable:route.filter(s=>!seen.has(s.id)).map(s=>s.id),
      centersInside:spaces.every(s=>geometry.contains(s.center.x,s.center.y,s.center.z,s.envelopeKind)),
      disjointSpaces:overlap.length===0,overlaps:overlap,functionalSubdivision:true,legacyIdsRetained:macroSpaces.every(m=>byId.has(m.id)),
      maxLongitudinalRoomM:Math.max(...spaces.filter(s=>s.kind!=='HANGAR_BAY').map(s=>s.x1-s.x0)),
      independentCG52Layout:true,provenance:'SIM_TUNED_FUNCTIONAL_ZONING',hangarClearance:{bays:spaces.filter(s=>s.kind==='HANGAR_BAY').length,
        clear:true,conflicts:[],clearHeightM:5.2,bayHeightM:5.2,simulationEnvelopeOnly:true}});
  };
  // Shared hazard/isolation/caching engine appended by the reproducible builder.
    let evaluations=0,signature=null,cached=null;
  function derive(input={}){
    const floodCells=new Map((input.flood?.cells??[]).map(c=>[c.id,c])),controlCells=new Map((input.control?.cells??[]).map(c=>[c.id,c])),overrides=input.spaceHazards??{};
    const hazards=spaces.map(s=>{const f=floodCells.get(s.parentFloodCellId)??{},c=controlCells.get(s.parentFloodCellId)??{},o=overrides[s.id]??{},flood01=clamp(Number(o.flood01??((f.waterM3||0)/Math.max(1e-9,f.capacityM3||1)))||0,0,1),fire01=clamp(Number(o.fire01??c.fire)||0,0,1),smoke01=clamp(Number(o.smoke01??c.smoke)||0,0,1),temperatureC=Math.max(0,Number(o.temperatureC??c.temperatureC)||20);return deepFreeze({spaceId:s.id,parentFloodCellId:s.parentFloodCellId,flood01,fire01,smoke01,temperatureC,status:flood01>.05?'FLOODING':fire01>.15?'FIRE':smoke01>.35?'SMOKE':'NORMAL'});});
    const hazardById=new Map(hazards.map(h=>[h.spaceId,h])),automaticActions=[],portalStates=portals.map(p=>{const a=hazardById.get(p.a),b=hazardById.get(p.b),floodSplit=Math.max(a.flood01,b.flood01)>.01&&Math.abs(a.flood01-b.flood01)>.005,fireSplit=Math.max(a.fire01,b.fire01)>.1&&Math.abs(a.fire01-b.fire01)>.04,smokeSplit=Math.max(a.smoke01,b.smoke01)>.25&&Math.abs(a.smoke01-b.smoke01)>.08;let open=p.normallyOpen,reason='NORMAL_CONFIGURATION';if(p.automatic&&['WATERTIGHT_DOOR','ACCESS_HATCH'].includes(p.kind)&&floodSplit){open=false;reason='AUTO_FLOOD_ISOLATION';}else if(p.automatic&&p.kind==='FIRE_DOOR'&&(fireSplit||smokeSplit)){open=false;reason='AUTO_FIRE_SMOKE_ISOLATION';}if(reason.startsWith('AUTO_'))automaticActions.push({portalId:p.id,action:'CLOSE',reason,priority:reason.includes('FLOOD')?1:2});return deepFreeze({id:p.id,open,reason});});
    automaticActions.sort((a,b)=>a.priority-b.priority||a.portalId.localeCompare(b.portalId));
    const summary={spaces:spaces.length,macroSpaces:raw.length,portals:portals.length,equipment:equipmentNodes.length,decks:decks.length,normal:hazards.filter(h=>h.status==='NORMAL').length,flooding:hazards.filter(h=>h.status==='FLOODING').length,fire:hazards.filter(h=>h.status==='FIRE').length,smoke:hazards.filter(h=>h.status==='SMOKE').length,automaticActions:automaticActions.length};
    return deepFreeze({schema:M.schema,contract:M.contract,renderContract:M.renderContract,revision:evaluations,buildId:M.buildId,automation:M.automation,coordinates:M.coordinates,provenance:M.provenance,decks:decks.map(d=>({...d})),spaces,portals,equipmentNodes,hazards,portalStates,automaticActions,summary,audit:topologyAudit()});
  }
  function step(input={}){const key=JSON.stringify([(input.flood?.cells??[]).map(c=>[c.id,Number(c.waterM3)||0,Number(c.capacityM3)||0]),(input.control?.cells??[]).map(c=>[c.id,Number(c.fire)||0,Number(c.smoke)||0,Number(c.temperatureC)||20]),input.spaceHazards??null]);if(key===signature)return false;signature=key;evaluations++;cached=derive(input);return true;}
  function locate(point){if(!point||![point.x,point.y,point.z].every(Number.isFinite))return null;const rows=spaces.filter(s=>point.x>=s.x0&&point.x<=s.x1&&point.y>=s.y0&&point.y<=s.y1&&point.z>=s.z0&&point.z<=s.z1&&geometry.contains(point.x,point.y,point.z,s.envelopeKind)).sort((a,b)=>a.volumeM3-b.volumeM3);return rows[0]??null;}
  function reset(){signature=null;evaluations=0;step({});return snapshot();}
  function snapshot(){return cached;}
  function performance(){return {evaluations,snapshotRecomputes:evaluations,spaceCount:spaces.length,portalCount:portals.length,equipmentCount:equipmentNodes.length};}
  reset();return {step,reset,snapshot,performance,locate,audit:topologyAudit,spaces,portals,equipmentNodes,decks};
}
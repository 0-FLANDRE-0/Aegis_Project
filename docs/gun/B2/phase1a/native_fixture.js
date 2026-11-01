// B2A USER-APPROVED TEST MIGRATIONS ONLY. No product function or coefficient replacement.
const b2aOriginalBallistic=__GB_TEST__.ballistic,b2aOriginalShell=__GB_TEST__.shellProbe,b2aOriginalBurst=__GB_TEST__.burst;
__GB_TEST__.ballistic=function(id){const flags=__GUN_B2__.snapshot().flags;__GUN_B2__.configure({dispersion:false});try{return b2aOriginalBallistic.call(this,id);}finally{__GUN_B2__.configure(flags);}};
const b2aShellText=b2aOriginalShell.toString(),b2aShellOld='y:0,z:alt,vx:0';if(b2aShellText.split(b2aShellOld).length!==2)throw Error('B2A_SHELL_FIXTURE_ANCHOR');
__GB_TEST__.shellProbe=eval('(function '+b2aShellText.replace(b2aShellOld,'y:metersToWorld(12.5),z:alt,vx:0').replace("if(kind==='SAM'){o.dead=false;","if(kind==='SAM'){o.rcsM2=.06;o.dead=false;")+')');
const b2aBurstText=b2aOriginalBurst.toString(),b2aBurstOld='positionM:{x:worldToMeters(setup.em.x),y:worldToMeters(setup.em.y),z:100}';if(b2aBurstText.split(b2aBurstOld).length!==2)throw Error('B2A_BURST_FIXTURE_ANCHOR');
__GB_TEST__.burst=eval('(function '+b2aBurstText.replace(b2aBurstOld,'positionM:{x:worldToMeters(setup.em.x)-600/_wip88GurneyFragmentSpeed(GUN_B1_SPEC.fragments),y:worldToMeters(setup.em.y)-1,z:100}')+')');
const b2aAxisRcs=eval('(function '+b2aShellText.replace("if(kind==='SAM'){o.dead=false;","if(kind==='SAM'){o.rcsM2=.06;o.dead=false;")+')');
__GB_TEST__.axisShell=c=>b2aAxisRcs.call(__GB_TEST__,c);
const b2aMissingRcs=eval('(function '+b2aShellText.replace(b2aShellOld,'y:metersToWorld(12.5),z:alt,vx:0')+')');
__GB_TEST__.missingRcsSam=()=>b2aMissingRcs.call(__GB_TEST__,{kind:'SAM'});
__GB_TEST__.zeroBurst=()=>b2aOriginalBurst.call(__GB_TEST__);

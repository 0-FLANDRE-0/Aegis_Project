const ranges={SM2:[5,10,30,60,180,20,60,100],SM2ER:[5,10,30,100,280,20,60,200],SM6:[5,10,30,100,320,20,60,250],ESSM:[5,5,15,25,40,8,15,10]};
const scenarios=[
 ['NEAR_STATIC',1000,0,0],['LOW_INBOUND',30,250,0],['MID_INBOUND',5000,250,0],['MID_STATIC',5000,0,0],
 ['LONG_STATIC',15000,0,0],['LOW_OUTBOUND',30,-250,0],['CROSSING',5000,0,250],['LONG_OUTBOUND',15000,-250,0]
];
const cells=[];
for(const weapon of ['SM2','SM2ER','SM6','ESSM']){
 scenarios.forEach(([scenario,altM,targetSpeedMps,crossSpeedMps],i)=>cells.push({cellId:weapon+'_'+scenario,scenario,weapon,rangeKm:ranges[weapon][i],altM:weapon==='ESSM'&&i===7?5000:altM,targetSpeedMps,crossSpeedMps,targetLabel:'Kh-35U'}));
 cells.push({cellId:weapon+'_HIGH_NEAR_5_20',scenario:'HIGH_NEAR_5_20',weapon,rangeKm:5,altM:20000,targetSpeedMps:0,crossSpeedMps:0,targetLabel:'Kh-35U'});
}
module.exports={cells};

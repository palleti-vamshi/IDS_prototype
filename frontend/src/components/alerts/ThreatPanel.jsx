function ThreatPanel(){

const alerts=[

{
title:"Normal Traffic",
description:"All industrial devices operating normally",
level:"LOW"
},

{
title:"MQTT Connection Stable",
description:"Gateway communication active",
level:"LOW"
},

{
title:"Suspicious Packet Detected",
description:"Waiting for IDS analysis",
level:"MEDIUM"
}

];


return(

<div className="bg-slate-800 rounded-xl p-6 mt-8">


<h2 className="text-xl font-semibold mb-5">
Security Alerts
</h2>


<div className="space-y-4">


{

alerts.map((alert,index)=>(


<div

key={index}

className="border border-slate-700 rounded-lg p-4"

>


<div className="flex justify-between">


<h3 className="font-semibold">
{alert.title}
</h3>


<span

className={

alert.level==="MEDIUM"

?

"text-orange-400"

:

"text-green-400"

}

>

{alert.level}

</span>


</div>


<p className="text-slate-400 mt-2">

{alert.description}

</p>


</div>


))

}


</div>


</div>

)

}


export default ThreatPanel;
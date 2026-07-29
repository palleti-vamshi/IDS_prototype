import { useEffect, useState } from "react";

import PageAnimation from "../../components/common/PageAnimation";

import { getAttackHistory } from "../../services/attackService";


const defaultAttacks = [

{
time:"10:45:21",
type:"MQTT Injection",
source:"192.168.1.45",
severity:"Critical",
status:"Blocked"
},

{
time:"10:40:12",
type:"Port Scanning",
source:"192.168.1.22",
severity:"High",
status:"Monitoring"
},

{
time:"10:32:55",
type:"Unauthorized Access",
source:"10.0.0.18",
severity:"Medium",
status:"Investigating"
},

{
time:"10:20:10",
type:"Normal Traffic",
source:"Gateway",
severity:"Low",
status:"Safe"
}

];



function AttackMonitoring(){


const [attacks,setAttacks]=useState(defaultAttacks);

const [loading,setLoading]=useState(false);



useEffect(()=>{


const loadAttacks = async()=>{


try{


setLoading(true);


const data = await getAttackHistory();


if(data && data.length){

setAttacks(data);

}


}

catch(error){


console.log(
"Attack API unavailable, using demo data"
);


}

finally{


setLoading(false);


}


};


loadAttacks();


},[]);




return(

<PageAnimation>


<h1 className="text-3xl font-bold mb-8">
Attack Monitoring
</h1>




{
loading &&

<p className="text-cyan-400 mb-4">
Updating threat feed...
</p>

}




<div className="grid grid-cols-4 gap-6 mb-8">


<div className="bg-slate-800 rounded-xl p-5">

<p className="text-slate-400">
Active Threats
</p>

<h2 className="text-3xl font-bold text-red-400">
03
</h2>

</div>



<div className="bg-slate-800 rounded-xl p-5">

<p className="text-slate-400">
Critical Events
</p>

<h2 className="text-3xl font-bold text-red-500">
01
</h2>

</div>



<div className="bg-slate-800 rounded-xl p-5">

<p className="text-slate-400">
Blocked Attacks
</p>

<h2 className="text-3xl font-bold text-green-400">
27
</h2>

</div>



<div className="bg-slate-800 rounded-xl p-5">

<p className="text-slate-400">
Firewall Status
</p>

<h2 className="text-3xl font-bold text-green-400">
Active
</h2>

</div>


</div>





<div className="bg-slate-800 rounded-xl p-6">


<h2 className="text-xl font-semibold mb-5">
Live Threat Feed
</h2>




<table className="w-full text-left">


<thead className="text-slate-400 border-b border-slate-700">


<tr>

<th className="p-3">
Time
</th>

<th>
Attack Type
</th>

<th>
Source
</th>

<th>
Severity
</th>

<th>
Response
</th>

</tr>


</thead>



<tbody>


{

attacks.map((attack,index)=>(


<tr

key={index}

className="border-b border-slate-700"

>


<td className="p-3">
{attack.time}
</td>


<td>
{attack.type}
</td>


<td>
{attack.source}
</td>


<td>


<span

className={

attack.severity==="Critical"

?

"text-red-400"

:

attack.severity==="High"

?

"text-yellow-400"

:

"text-green-400"

}

>

{attack.severity}

</span>


</td>



<td className="text-cyan-400">
{attack.status}
</td>


</tr>


))


}


</tbody>


</table>


</div>





<div className="bg-slate-800 rounded-xl p-6 mt-8">


<h2 className="text-xl font-semibold mb-5">
Incident Timeline
</h2>


<div className="space-y-5">


<p className="border-l-4 border-red-400 pl-4">
10:45 - MQTT Injection blocked by IDS engine
</p>


<p className="border-l-4 border-yellow-400 pl-4">
10:40 - Port scanning activity detected
</p>


<p className="border-l-4 border-green-400 pl-4">
10:20 - Network operating normally
</p>


</div>


</div>



</PageAnimation>

)

}


export default AttackMonitoring;
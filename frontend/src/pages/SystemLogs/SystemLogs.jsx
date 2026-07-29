import PageAnimation from "../../components/common/PageAnimation";


const logs = [

{
time:"10:42:12",
source:"PLC-01",
event:"Temperature threshold exceeded",
severity:"Warning",
status:"Investigating"
},

{
time:"10:38:45",
source:"MQTT Gateway",
event:"Unauthorized connection attempt",
severity:"Critical",
status:"Blocked"
},

{
time:"10:30:22",
source:"Sensor Node 14",
event:"Normal sensor heartbeat received",
severity:"Info",
status:"Normal"
},

{
time:"10:25:10",
source:"IDS Engine",
event:"Suspicious traffic detected",
severity:"High",
status:"Monitoring"
},

];



function SystemLogs(){


return(

<PageAnimation>


<h1 className="text-3xl font-bold mb-8">
System Logs
</h1>



<div className="grid grid-cols-4 gap-6 mb-8">


<div className="bg-slate-800 p-5 rounded-xl">
<p className="text-slate-400">
Total Events
</p>

<h2 className="text-3xl font-bold text-white">
1248
</h2>

</div>


<div className="bg-slate-800 p-5 rounded-xl">

<p className="text-slate-400">
Critical
</p>

<h2 className="text-3xl font-bold text-red-400">
12
</h2>

</div>



<div className="bg-slate-800 p-5 rounded-xl">

<p className="text-slate-400">
Warnings
</p>

<h2 className="text-3xl font-bold text-yellow-400">
43
</h2>

</div>



<div className="bg-slate-800 p-5 rounded-xl">

<p className="text-slate-400">
System Status
</p>

<h2 className="text-3xl font-bold text-green-400">
Stable
</h2>

</div>


</div>




<div className="bg-slate-800 rounded-xl p-6">


<table className="w-full text-left">


<thead className="text-slate-400 border-b border-slate-700">


<tr>

<th className="p-3">
Time
</th>


<th>
Source
</th>


<th>
Event
</th>


<th>
Severity
</th>


<th>
Status
</th>


</tr>


</thead>



<tbody>


{
logs.map((log,index)=>(

<tr 
key={index}
className="border-b border-slate-700"
>


<td className="p-3">
{log.time}
</td>


<td>
{log.source}
</td>


<td>
{log.event}
</td>


<td>


<span className="px-3 py-1 rounded-full bg-slate-700">

{log.severity}

</span>


</td>


<td className="text-green-400">
{log.status}
</td>


</tr>


))

}


</tbody>


</table>


</div>


</PageAnimation>

)

}


export default SystemLogs;
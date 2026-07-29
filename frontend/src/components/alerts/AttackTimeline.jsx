function AttackTimeline(){

const events=[

{
time:"10:30:15",
attack:"Port Scan Attempt",
severity:"Low",
status:"Blocked"
},

{
time:"10:25:40",
attack:"Suspicious MQTT Traffic",
severity:"Medium",
status:"Investigating"
},

{
time:"10:20:05",
attack:"Unauthorized Access",
severity:"Critical",
status:"Resolved"
}

];


return(

<div className="bg-slate-800 rounded-xl p-6 mt-8">


<h2 className="text-xl font-semibold mb-6">
Attack Timeline
</h2>


<div className="space-y-5">


{
events.map((event,index)=>(


<div

key={index}

className="flex gap-5 border-l-2 border-cyan-400 pl-5"

>


<div>

<p className="text-slate-400 text-sm">
{event.time}
</p>


<h3 className="font-semibold mt-1">
{event.attack}
</h3>


<p

className={

event.severity==="Critical"

?

"text-red-400"

:

event.severity==="Medium"

?

"text-orange-400"

:

"text-green-400"

}

>

{event.severity}

</p>


<p className="text-slate-400">
{event.status}
</p>


</div>


</div>


))

}


</div>


</div>

)

}


export default AttackTimeline;
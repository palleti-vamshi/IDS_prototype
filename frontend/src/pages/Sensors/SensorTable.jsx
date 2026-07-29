function SensorTable(){

const readings=[
{
sensor:"Temperature Sensor 01",
value:"32°C",
status:"Normal",
time:"10:20:15"
},
{
sensor:"Pressure Sensor 01",
value:"74 PSI",
status:"Stable",
time:"10:20:10"
},
{
sensor:"Temperature Sensor 02",
value:"31°C",
status:"Normal",
time:"10:20:05"
}
]


return(

<div className="bg-slate-800 rounded-xl p-6 mt-8">

<h2 className="text-xl font-semibold mb-5">
Latest Sensor Readings
</h2>


<table className="w-full text-left">

<thead>

<tr className="text-slate-400">

<th className="pb-3">
Sensor
</th>

<th>
Value
</th>

<th>
Status
</th>

<th>
Time
</th>

</tr>

</thead>


<tbody>

{
readings.map((item,index)=>(

<tr 
key={index}
className="border-t border-slate-700"
>

<td className="py-3">
{item.sensor}
</td>

<td>
{item.value}
</td>

<td className="text-green-400">
{item.status}
</td>

<td>
{item.time}
</td>


</tr>

))
}


</tbody>


</table>


</div>

)

}


export default SensorTable;
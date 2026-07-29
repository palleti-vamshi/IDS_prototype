import {
LineChart,
Line,
XAxis,
YAxis,
CartesianGrid,
Tooltip,
ResponsiveContainer
} from "recharts";


const data=[

{
time:"10:00",
temperature:28
},

{
time:"10:05",
temperature:30
},

{
time:"10:10",
temperature:32
},

{
time:"10:15",
temperature:31
},

{
time:"10:20",
temperature:33
}

];


function TemperatureChart(){


return(

<div className="bg-slate-800 rounded-xl p-6">


<h2 className="text-xl font-semibold mb-5">
Temperature Monitoring
</h2>


<ResponsiveContainer width="100%" height={300}>


<LineChart data={data}>


<CartesianGrid strokeDasharray="3 3"/>


<XAxis dataKey="time"/>


<YAxis/>


<Tooltip/>


<Line

type="monotone"

dataKey="temperature"

stroke="#22d3ee"

strokeWidth={3}

/>


</LineChart>


</ResponsiveContainer>


</div>

)

}


export default TemperatureChart;
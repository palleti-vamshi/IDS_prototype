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
pressure:70
},

{
time:"10:05",
pressure:72
},

{
time:"10:10",
pressure:74
},

{
time:"10:15",
pressure:73
},

{
time:"10:20",
pressure:75
}

];


function PressureChart(){


return(

<div className="bg-slate-800 rounded-xl p-6">


<h2 className="text-xl font-semibold mb-5">
Pressure Monitoring
</h2>


<ResponsiveContainer width="100%" height={300}>


<LineChart data={data}>


<CartesianGrid strokeDasharray="3 3"/>


<XAxis dataKey="time"/>


<YAxis/>


<Tooltip/>


<Line

type="monotone"

dataKey="pressure"

stroke="#34d399"

strokeWidth={3}

/>


</LineChart>


</ResponsiveContainer>


</div>

)

}


export default PressureChart;
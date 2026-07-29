import { useEffect, useState } from "react";

import PageAnimation from "../../components/common/PageAnimation";

import { getLatestSensors } from "../../services/sensorService";


const defaultSensors = [

{
id:"SENSOR-01",
location:"Factory Zone A",
temperature:"32°C",
pressure:"74 PSI",
status:"Online"
},

{
id:"SENSOR-02",
location:"Factory Zone B",
temperature:"34°C",
pressure:"71 PSI",
status:"Online"
},

{
id:"SENSOR-03",
location:"Cooling Unit",
temperature:"28°C",
pressure:"68 PSI",
status:"Online"
},

{
id:"SENSOR-04",
location:"Production Line",
temperature:"41°C",
pressure:"82 PSI",
status:"Warning"
}

];



function Sensors(){


const [sensors,setSensors] = useState(defaultSensors);

const [loading,setLoading] = useState(false);



useEffect(()=>{


const loadSensors = async()=>{


try{


setLoading(true);


const data = await getLatestSensors();


if(data && data.length){

setSensors(data);

}


}

catch(error){


console.log(
"Sensor API unavailable, using demo data"
);


}

finally{


setLoading(false);


}


};


loadSensors();


},[]);




return(

<PageAnimation>


<h1 className="text-3xl font-bold mb-8">
Live Sensor Monitoring
</h1>



{
loading &&

<p className="text-cyan-400 mb-4">
Updating sensor data...
</p>

}




<div className="grid grid-cols-4 gap-6 mb-8">



<div className="bg-slate-800 rounded-xl p-5">

<p className="text-slate-400">
Total Sensors
</p>

<h2 className="text-3xl font-bold text-cyan-400">
24
</h2>

</div>




<div className="bg-slate-800 rounded-xl p-5">

<p className="text-slate-400">
Online Sensors
</p>

<h2 className="text-3xl font-bold text-green-400">
23
</h2>

</div>




<div className="bg-slate-800 rounded-xl p-5">

<p className="text-slate-400">
Warnings
</p>

<h2 className="text-3xl font-bold text-yellow-400">
01
</h2>

</div>




<div className="bg-slate-800 rounded-xl p-5">

<p className="text-slate-400">
Network Status
</p>

<h2 className="text-3xl font-bold text-green-400">
Stable
</h2>

</div>



</div>





<div className="grid grid-cols-2 gap-6">


{

sensors.map((sensor,index)=>(


<div

key={index}

className="bg-slate-800 rounded-xl p-6"

>



<div className="flex justify-between mb-5">


<h2 className="text-xl font-semibold">
{sensor.id}
</h2>


<span

className={

sensor.status==="Online"

?

"text-green-400"

:

"text-yellow-400"

}

>

{sensor.status}

</span>


</div>



<p className="text-slate-400">
Location
</p>


<p className="mb-4">
{sensor.location}
</p>





<div className="grid grid-cols-2 gap-4">


<div className="bg-slate-700 p-4 rounded-lg">


<p className="text-slate-400">
Temperature
</p>


<p className="text-xl text-cyan-400">
{sensor.temperature}
</p>


</div>





<div className="bg-slate-700 p-4 rounded-lg">


<p className="text-slate-400">
Pressure
</p>


<p className="text-xl text-cyan-400">
{sensor.pressure}
</p>


</div>


</div>



</div>


))


}


</div>


</PageAnimation>

)

}


export default Sensors;
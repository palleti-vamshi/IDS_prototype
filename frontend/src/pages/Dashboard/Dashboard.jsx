import { useEffect, useState } from "react";

import ThreatPanel from "../../components/alerts/ThreatPanel";

import PageAnimation from "../../components/common/PageAnimation";

import TemperatureChart from "../../components/charts/TemperatureChart";

import PressureChart from "../../components/charts/PressureChart";

import StatCard from "../../components/cards/StatCard";

import { getDashboardStats } from "../../services/dashboardService";



const defaultStats = [

{
title:"Factory Status",
value:"Online",
status:"Operational",
icon:"🏭"
},

{
title:"MQTT Status",
value:"Connected",
status:"Communication Active",
icon:"📡"
},

{
title:"IDS Status",
value:"Running",
status:"AI Monitoring Enabled",
icon:"🛡️"
},

{
title:"Active Attacks",
value:"03",
status:"Requires Attention",
icon:"⚠️"
},

{
title:"Sensors Online",
value:"24",
status:"All Connected",
icon:"🌡️"
},

{
title:"System Uptime",
value:"99.9%",
status:"Stable",
icon:"⏱️"
},

{
title:"Packets Processed",
value:"1.2M",
status:"Normal Traffic",
icon:"📦"
},

{
title:"Threat Level",
value:"Low",
status:"Secure",
icon:"🔒"
}

];




function Dashboard(){


const [stats,setStats]=useState(defaultStats);

const [loading,setLoading]=useState(false);



useEffect(()=>{


const loadDashboard = async()=>{


try{


setLoading(true);


const data = await getDashboardStats();



if(data?.stats){

setStats(data.stats);

}


}

catch(error){


console.log(
"Dashboard API unavailable, using demo data"
);


}

finally{


setLoading(false);


}


};



loadDashboard();


},[]);





return(

<PageAnimation>


<h1 className="text-3xl font-bold mb-8">
Industrial Security Dashboard
</h1>



{
loading &&

<p className="text-cyan-400 mb-4">
Updating security status...
</p>

}





<div className="grid grid-cols-4 gap-6">


{

stats.map((item,index)=>(


<StatCard

key={index}

title={item.title}

value={item.value}

status={item.status}

icon={item.icon}

/>


))


}


</div>





<div className="grid grid-cols-2 gap-6 mt-8">


<TemperatureChart/>


<PressureChart/>


</div>





<ThreatPanel/>


</PageAnimation>

)

}


export default Dashboard;
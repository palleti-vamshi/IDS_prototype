import { useEffect, useState } from "react";

import PageAnimation from "../../components/common/PageAnimation";

import { getDatasetStats } from "../../services/datasetService";


const defaultAttacks = [

{
name:"Normal Traffic",
samples:"45000",
percentage:"65%"
},

{
name:"DoS Attack",
samples:"12000",
percentage:"17%"
},

{
name:"Port Scan",
samples:"7000",
percentage:"10%"
},

{
name:"MQTT Injection",
samples:"5000",
percentage:"8%"
}

];



function DatasetAnalytics(){


const [stats,setStats]=useState(null);

const [attacks,setAttacks]=useState(defaultAttacks);

const [loading,setLoading]=useState(false);



useEffect(()=>{


const loadDataset = async()=>{


try{


setLoading(true);


const data = await getDatasetStats();



if(data){


setStats(data);


if(data.attacks){

setAttacks(data.attacks);

}


}


}

catch(error){


console.log(
"Dataset API unavailable, using demo data"
);


}

finally{


setLoading(false);


}


};



loadDataset();


},[]);





return(

<PageAnimation>


<h1 className="text-3xl font-bold mb-8">
Dataset Analytics
</h1>




{
loading &&

<p className="text-cyan-400 mb-4">
Updating dataset information...
</p>

}





<div className="grid grid-cols-4 gap-6 mb-8">



<div className="bg-slate-800 p-5 rounded-xl">

<p className="text-slate-400">
Total Records
</p>

<h2 className="text-3xl font-bold text-cyan-400">

{
stats?.total_records || "69000"
}

</h2>

</div>




<div className="bg-slate-800 p-5 rounded-xl">

<p className="text-slate-400">
Attack Classes
</p>

<h2 className="text-3xl font-bold text-green-400">

{
stats?.attack_classes || "4"
}

</h2>

</div>




<div className="bg-slate-800 p-5 rounded-xl">

<p className="text-slate-400">
Features
</p>

<h2 className="text-3xl font-bold text-yellow-400">

{
stats?.features || "42"
}

</h2>

</div>




<div className="bg-slate-800 p-5 rounded-xl">

<p className="text-slate-400">
Dataset Status
</p>

<h2 className="text-3xl font-bold text-green-400">
Ready
</h2>

</div>



</div>







<div className="grid grid-cols-2 gap-6">



<div className="bg-slate-800 p-6 rounded-xl">


<h2 className="text-xl font-semibold mb-5">
Training Configuration
</h2>



<div className="space-y-4 text-slate-300">


<p>
Training Data:

<span className="text-cyan-400 ml-2">
80%
</span>

</p>


<p>
Testing Data:

<span className="text-cyan-400 ml-2">
20%
</span>

</p>


<p>
Model Compatibility:

<span className="text-green-400 ml-2">
Verified
</span>

</p>


<p>
Preprocessing:

<span className="text-green-400 ml-2">
Completed
</span>

</p>


</div>


</div>






<div className="bg-slate-800 p-6 rounded-xl">


<h2 className="text-xl font-semibold mb-5">
Dataset Information
</h2>


<p className="text-slate-300">
Name:

<span className="text-cyan-400 ml-2">
Industrial IDS Dataset
</span>

</p>


<p className="text-slate-300 mt-3">
Format:

<span className="text-cyan-400 ml-2">
CSV
</span>

</p>


<p className="text-slate-300 mt-3">
Source:

<span className="text-cyan-400 ml-2">
Industrial Network Sensors
</span>

</p>


</div>



</div>







<div className="bg-slate-800 p-6 rounded-xl mt-8">


<h2 className="text-xl font-semibold mb-5">
Attack Distribution
</h2>




<table className="w-full text-left">


<thead className="text-slate-400 border-b border-slate-700">


<tr>

<th className="p-3">
Category
</th>


<th>
Samples
</th>


<th>
Distribution
</th>


</tr>


</thead>



<tbody>


{

attacks.map((item,index)=>(


<tr

key={index}

className="border-b border-slate-700"

>


<td className="p-3">
{item.name}
</td>


<td>
{item.samples}
</td>


<td className="text-cyan-400">
{item.percentage}
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


export default DatasetAnalytics;
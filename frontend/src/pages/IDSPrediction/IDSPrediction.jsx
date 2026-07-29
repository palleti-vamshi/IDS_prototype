import { useState } from "react";

import PageAnimation from "../../components/common/PageAnimation";

import { getPrediction } from "../../services/predictionService";


const defaultPredictions = [

{
time:"10:42:12",
attack:"Port Scan",
confidence:"96%",
result:"Detected"
},

{
time:"10:35:40",
attack:"Normal Traffic",
confidence:"99%",
result:"Safe"
},

{
time:"10:22:18",
attack:"MQTT Injection",
confidence:"87%",
result:"Detected"
}

];



function IDSPrediction(){


const [predictions,setPredictions] = useState(defaultPredictions);

const [loading,setLoading] = useState(false);



const runPrediction = async()=>{


try{


setLoading(true);


const response = await getPrediction({

traffic:"sample industrial network traffic"

});


if(response){


const newPrediction = {

time:new Date().toLocaleTimeString(),

attack:response.attack || "Unknown",

confidence:
response.confidence || "85%",

result:
response.result || "Detected"

};


setPredictions([

newPrediction,

...predictions

]);


}


}

catch(error){


console.log(
"Prediction API unavailable, using demo data"
);


}

finally{


setLoading(false);


}


};




return(

<PageAnimation>


<h1 className="text-3xl font-bold mb-8">
IDS Prediction & AI Analysis
</h1>



<div className="grid grid-cols-4 gap-6 mb-8">


<div className="bg-slate-800 rounded-xl p-5">

<p className="text-slate-400">
AI Model Status
</p>

<h2 className="text-2xl font-bold text-green-400 mt-2">
Active
</h2>

</div>



<div className="bg-slate-800 rounded-xl p-5">

<p className="text-slate-400">
Model Accuracy
</p>

<h2 className="text-2xl font-bold text-cyan-400 mt-2">
98.7%
</h2>

</div>



<div className="bg-slate-800 rounded-xl p-5">

<p className="text-slate-400">
Threat Probability
</p>

<h2 className="text-2xl font-bold text-yellow-400 mt-2">
23%
</h2>

</div>



<div className="bg-slate-800 rounded-xl p-5">

<p className="text-slate-400">
Last Prediction
</p>

<h2 className="text-2xl font-bold text-red-400 mt-2">
Attack
</h2>

</div>


</div>





<div className="bg-slate-800 rounded-xl p-6 mb-8">


<h2 className="text-xl font-semibold mb-5">
AI Prediction Engine
</h2>


<button

onClick={runPrediction}

className="bg-cyan-500 text-black px-5 py-3 rounded-lg font-semibold"

>

{
loading
?
"Analyzing..."
:
"Run Prediction"
}

</button>


</div>






<div className="grid grid-cols-2 gap-6">



<div className="bg-slate-800 rounded-xl p-6">


<h2 className="text-xl font-semibold mb-5">
AI Confidence Score
</h2>


<div className="w-full bg-slate-700 rounded-full h-4">


<div

className="bg-cyan-400 h-4 rounded-full"

style={{
width:"87%"
}}

/>


</div>


<p className="mt-4 text-cyan-400">
87% Confidence in Current Prediction
</p>


</div>





<div className="bg-slate-800 rounded-xl p-6">


<h2 className="text-xl font-semibold mb-5">
Detection Engine
</h2>


<p className="text-slate-300">
Model:

<span className="text-cyan-400 ml-2">
LightX Neural IDS v1.0
</span>

</p>



<p className="text-slate-300 mt-3">
Algorithm:

<span className="text-cyan-400 ml-2">
Deep Learning Classifier
</span>

</p>



<p className="text-slate-300 mt-3">
Status:

<span className="text-green-400 ml-2">
Monitoring
</span>

</p>


</div>



</div>





<div className="bg-slate-800 rounded-xl p-6 mt-8">


<h2 className="text-xl font-semibold mb-5">
Prediction History
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
Confidence
</th>


<th>
Result
</th>


</tr>


</thead>



<tbody>


{

predictions.map((item,index)=>(


<tr

key={index}

className="border-b border-slate-700"

>


<td className="p-3">
{item.time}
</td>


<td>
{item.attack}
</td>


<td className="text-cyan-400">
{item.confidence}
</td>


<td

className={

item.result==="Detected"

?

"text-red-400"

:

"text-green-400"

}

>

{item.result}

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


export default IDSPrediction;
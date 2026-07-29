import PageAnimation from "../../components/common/PageAnimation";


function Settings(){


return(

<PageAnimation>


<h1 className="text-3xl font-bold mb-8">
System Settings
</h1>



<div className="grid grid-cols-2 gap-6">



<div className="bg-slate-800 rounded-xl p-6">


<h2 className="text-xl font-semibold mb-5">
IDS Configuration
</h2>


<div className="space-y-4 text-slate-300">


<p>
Detection Engine:

<span className="text-cyan-400 ml-2">
LightX AI IDS
</span>

</p>


<p>
Model Version:

<span className="text-cyan-400 ml-2">
v1.0
</span>

</p>


<p>
Monitoring Mode:

<span className="text-green-400 ml-2">
Active
</span>

</p>


<p>
Threat Detection:

<span className="text-green-400 ml-2">
Enabled
</span>

</p>


</div>


</div>






<div className="bg-slate-800 rounded-xl p-6">


<h2 className="text-xl font-semibold mb-5">
Network Configuration
</h2>


<div className="space-y-4 text-slate-300">


<p>
MQTT Broker:

<span className="text-cyan-400 ml-2">
Connected
</span>

</p>


<p>
API Server:

<span className="text-green-400 ml-2">
Online
</span>

</p>


<p>
Firewall:

<span className="text-green-400 ml-2">
Protected
</span>

</p>


<p>
Communication:

<span className="text-green-400 ml-2">
Encrypted
</span>

</p>


</div>


</div>





<div className="bg-slate-800 rounded-xl p-6">


<h2 className="text-xl font-semibold mb-5">
Security Preferences
</h2>



<div className="space-y-4">


<div className="flex justify-between">

<span>
Auto Threat Blocking
</span>

<span className="text-green-400">
ON
</span>

</div>


<div className="flex justify-between">

<span>
Real-time Alerts
</span>

<span className="text-green-400">
ON
</span>

</div>


<div className="flex justify-between">

<span>
AI Prediction
</span>

<span className="text-green-400">
ON
</span>

</div>


</div>


</div>







<div className="bg-slate-800 rounded-xl p-6">


<h2 className="text-xl font-semibold mb-5">
System Information
</h2>


<div className="space-y-4 text-slate-300">


<p>
Platform:

<span className="text-cyan-400 ml-2">
Industrial SOC
</span>

</p>


<p>
Version:

<span className="text-cyan-400 ml-2">
1.0.0
</span>

</p>


<p>
Environment:

<span className="text-cyan-400 ml-2">
Production
</span>

</p>


<p>
Status:

<span className="text-green-400 ml-2">
Operational
</span>

</p>


</div>


</div>



</div>


</PageAnimation>

)

}


export default Settings;
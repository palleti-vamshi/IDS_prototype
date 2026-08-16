import { useState } from "react";
import { NavLink } from "react-router-dom";

import {
  MdMenu,
  MdClose,
  MdDashboard,
  MdSensors,
  MdWarning,
  MdPsychology,
  MdDataset,
  MdDescription,
  MdSettings,
  MdPrecisionManufacturing
} from "react-icons/md";


function Sidebar(){

const [open,setOpen] = useState(false);


const menuItems=[

{
name:"Dashboard",
path:"/",
icon:<MdDashboard/>
},

{
name:"Sensors",
path:"/sensors",
icon:<MdSensors/>
},

{
name:"SCADA Monitor",
path:"/scada",
icon:<MdPrecisionManufacturing/>
},

{
name:"Attack Monitoring",
path:"/attacks",
icon:<MdWarning/>
},

{
name:"IDS Prediction",
path:"/prediction",
icon:<MdPsychology/>
},

{
name:"Dataset Analytics",
path:"/dataset",
icon:<MdDataset/>
},

{
name:"System Logs",
path:"/logs",
icon:<MdDescription/>
},

{
name:"Settings",
path:"/settings",
icon:<MdSettings/>
}

];


return(

<div>


{/* Mobile Menu Button */}

<button

className="md:hidden text-cyan-400 text-3xl p-4"

onClick={()=>setOpen(!open)}

>

{

open

?

<MdClose/>

:

<MdMenu/>

}

</button>



{/* Sidebar */}

<aside

className={

`

fixed md:static

top-0 left-0

h-screen

w-64

bg-slate-900

border-r border-slate-700

p-5

z-50

transform

transition-transform

duration-300

${

open

?

"translate-x-0"

:

"-translate-x-full md:translate-x-0"

}

`

}

>


<h2 className="text-xl font-bold text-cyan-400 mb-8">

Industrial SOC

</h2>



<ul className="space-y-4">


{

menuItems.map((item,index)=>(


<li key={index}>


<NavLink

to={item.path}

onClick={()=>setOpen(false)}

className={({isActive})=>

`

flex items-center gap-3

transition

duration-200

text-lg

${

isActive

?

"text-cyan-400 font-semibold"

:

"text-slate-300 hover:text-cyan-400"

}

`

}

>


<span className="text-xl">

{item.icon}

</span>


<span>

{item.name}

</span>


</NavLink>


</li>


))

}


</ul>


</aside>


</div>

)

}


export default Sidebar;
import { 
MdNotifications,
MdSecurity,
MdCircle
} from "react-icons/md";


function Navbar(){


return(

<nav className="h-16 bg-slate-900 border-b border-slate-700 flex items-center justify-between px-6">


<div className="flex items-center gap-3">


<MdSecurity className="text-cyan-400 text-2xl"/>


<div>

<h2 className="font-semibold text-white">
LightX-IDS
</h2>

<p className="text-xs text-slate-400">
Industrial Security Operations Center
</p>

</div>


</div>



<div className="flex items-center gap-6">


<div className="flex items-center gap-2">

<MdCircle className="text-green-400 text-sm"/>

<span className="text-sm text-slate-300">
System Online
</span>

</div>



<button className="relative">

<MdNotifications className="text-2xl text-slate-300 hover:text-cyan-400"/>


<span className="absolute -top-1 -right-1 bg-red-500 text-xs rounded-full px-1">

3

</span>


</button>



<div className="text-right">


<p className="text-white text-sm">
Admin User
</p>


<p className="text-xs text-slate-400">
Security Analyst
</p>


</div>


</div>


</nav>

)

}


export default Navbar;
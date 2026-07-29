import { motion } from "framer-motion";


function StatCard({title,value,status,icon}) {

return (

<motion.div

whileHover={{
scale:1.05,
y:-5
}}

transition={{
duration:0.2
}}

className="bg-slate-800 border border-slate-700 rounded-xl p-5 hover:border-cyan-400 transition"

>


<div className="flex justify-between items-center">

<h3 className="text-slate-400">
{title}
</h3>


<span className="text-cyan-400 text-xl">
{icon}
</span>


</div>


<p className="text-3xl font-bold mt-4">
{value}
</p>


<p className="text-green-400 mt-2">
{status}
</p>


</motion.div>

);

}


export default StatCard;
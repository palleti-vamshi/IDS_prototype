import { Link } from "react-router-dom";


function NotFound(){

return (

<div className="min-h-screen flex items-center justify-center bg-slate-950">


<div className="text-center">


<h1 className="text-7xl font-bold text-cyan-400">
404
</h1>


<h2 className="text-2xl text-white mt-4">
Page Not Found
</h2>


<p className="text-slate-400 mt-3">
The requested security module does not exist.
</p>



<Link

to="/"

className="inline-block mt-6 bg-cyan-500 text-black px-6 py-3 rounded-lg font-semibold"

>

Return to Dashboard

</Link>


</div>


</div>

)

}


export default NotFound;
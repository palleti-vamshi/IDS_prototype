import { useNavigate } from "react-router-dom";
import { useState } from "react";
import useAuth from "../../hooks/useAuth";


function Login(){

const navigate = useNavigate();
const {login} = useAuth();

const [email,setEmail] = useState("");
const [password,setPassword] = useState("");


const handleSubmit=(e)=>{

e.preventDefault();


login({

email,

role:"admin",

token:"dummy-token"

});


navigate("/");


};


return (

<div className="min-h-screen flex items-center justify-center bg-slate-950">

<div className="bg-slate-900 p-8 rounded-xl w-96">

<h1 className="text-3xl font-bold text-cyan-400 mb-6">
LightX-IDS Login
</h1>


<form onSubmit={handleSubmit}>


<input
className="w-full p-3 mb-4 rounded bg-slate-800"
placeholder="Email"
value={email}
onChange={(e)=>setEmail(e.target.value)}
/>


<input
className="w-full p-3 mb-4 rounded bg-slate-800"
placeholder="Password"
type="password"
value={password}
onChange={(e)=>setPassword(e.target.value)}
/>


<button
className="w-full bg-cyan-500 p-3 rounded text-black font-bold"
>
Login
</button>


</form>


</div>

</div>

)

}


export default Login;
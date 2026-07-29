function ErrorMessage({message}){

return(

<div className="bg-red-900/40 border border-red-500 rounded-xl p-5">

<h3 className="text-red-400 font-semibold">
Error
</h3>


<p className="text-slate-300 mt-2">
{message}
</p>


</div>

)

}


export default ErrorMessage;
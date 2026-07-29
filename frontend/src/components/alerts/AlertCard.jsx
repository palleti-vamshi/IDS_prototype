function AlertCard({title,message,severity}){


const colors={

Critical:"text-red-400 border-red-500",

Warning:"text-orange-400 border-orange-500",

Normal:"text-green-400 border-green-500"

};


return(

<div

className={

`

bg-slate-800

border

rounded-xl

p-5

${colors[severity]}

`

}

>


<h3 className="font-semibold text-lg">

{title}

</h3>


<p className="text-slate-300 mt-2">

{message}

</p>


<span

className="inline-block mt-3 text-sm"

>

{severity}

</span>


</div>

)

}


export default AlertCard;
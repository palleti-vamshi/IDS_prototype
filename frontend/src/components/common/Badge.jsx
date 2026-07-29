function Badge({text,type}){


const styles={

success:"bg-green-500/20 text-green-400",

warning:"bg-orange-500/20 text-orange-400",

danger:"bg-red-500/20 text-red-400"

};


return(

<span

className={

`px-3 py-1 rounded-full text-sm ${styles[type]}`

}

>

{text}

</span>

)

}


export default Badge;
import { motion } from "framer-motion";


function PageAnimation({children}){

return(

<motion.div

initial={{
opacity:0,
y:20
}}

animate={{
opacity:1,
y:0
}}

transition={{
duration:0.4
}}

>

{children}

</motion.div>

)

}


export default PageAnimation;
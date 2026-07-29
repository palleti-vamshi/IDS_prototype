const handleSubmit=(e)=>{

e.preventDefault();


login({

email,

role:"admin",

token:"dummy-token"

});


navigate("/");


};
import api from "./api";


export const getAttackHistory = async()=>{

const response = await api.get("/attacks");

return response.data;

};


export const getCurrentAttack = async()=>{

const response = await api.get("/attacks/current");

return response.data;

};
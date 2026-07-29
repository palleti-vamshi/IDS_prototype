import api from "./api";


export const getLatestSensors = async()=>{

const response = await api.get("/sensors/latest");

return response.data;

};


export const getSensorHistory = async()=>{

const response = await api.get("/sensors/history");

return response.data;

};
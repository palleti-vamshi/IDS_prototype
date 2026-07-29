import api from "./api";


export const getDatasetStats = async()=>{

const response = await api.get("/dataset/stats");

return response.data;

};
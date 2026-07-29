import api from "./api";


export const getPrediction = async(data)=>{

const response = await api.post(
"/prediction",
data
);

return response.data;

};
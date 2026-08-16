import api from "./api";

export const getLatestSCADA = async () => {
  const response = await api.get("/scada/latest");
  return response.data;
};
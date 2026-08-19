import api from "./api";

export const getDashboardStats = async () => {
    const response = await api.get("/scada/latest");

    return response.data;
};
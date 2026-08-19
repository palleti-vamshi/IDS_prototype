import SCADA from "../pages/SCADA/SCADA";
import NotFound from "../pages/NotFound/NotFound";
import Login from "../pages/Login/Login";
import Settings from "../pages/Settings/Settings";
import SystemLogs from "../pages/SystemLogs/SystemLogs";
import DatasetAnalytics from "../pages/DatasetAnalytics/DatasetAnalytics";
import IDSPrediction from "../pages/IDSPrediction/IDSPrediction";
import AttackMonitoring from "../pages/AttackMonitoring/AttackMonitoring";
import { Routes, Route } from "react-router-dom";

import Dashboard from "../pages/Dashboard/Dashboard";
import Sensors from "../pages/Sensors/Sensors";


function AppRoutes(){

return (

<Routes>

<Route 
path="/" 
element={<Dashboard/>}
/>


<Route 
path="/sensors" 
element={<Sensors/>}
/>


<Route
path="/scada"
element={<SCADA />}
/>

<Route 
path="/attacks" 
element={<AttackMonitoring/>}
/>


<Route 
path="/prediction" 
element={<IDSPrediction/>}
/>


<Route
path="/dataset"
element={<DatasetAnalytics/>}
/>


<Route
path="/logs"
element={<SystemLogs/>}
/>


<Route
path="/settings"
element={<Settings/>}
/>


<Route
path="/login"
element={<Login/>}
/>

<Route
path="*"
element={<NotFound/>}
/>

</Routes>

)

}


export default AppRoutes;
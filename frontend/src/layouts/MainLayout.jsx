import Sidebar from "../components/sidebar/Sidebar";
import Navbar from "../components/navbar/Navbar";



function MainLayout({children}) {


  return (

    <div className="flex min-h-screen bg-slate-950">


      <Sidebar/>


      <div className="flex-1">


        <Navbar/>


        <main className="p-6">
          {children}
        </main>


      </div>


    </div>

  );

}


export default MainLayout;
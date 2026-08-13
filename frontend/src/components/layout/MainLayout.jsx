import {
Outlet
}
from "react-router-dom";


import Sidebar from "./Sidebar";

import Navbar from "./Navbar";



export default function MainLayout(){


return (

<div className="
flex
bg-slate-950
min-h-screen
">


<Sidebar/>


<div className="
flex-1
flex
flex-col
">


<Navbar/>


<main className="
flex-1
overflow-auto
">


<Outlet/>


</main>


</div>


</div>


);


}
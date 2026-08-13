import {
    LayoutDashboard,
    BarChart3,
    Package,
    LineChart,
    Users,
    ShieldAlert,
    Bot,
    FileText,
    Activity,
    Settings
}
from "lucide-react";


import {
NavLink
}
from "react-router-dom";



const menu = [

{
name:"Dashboard",
path:"/",
icon:LayoutDashboard
},

{
name:"Sales",
path:"/sales",
icon:BarChart3
},

{
name:"Inventory",
path:"/inventory",
icon:Package
},

{
name:"Forecast",
path:"/forecast",
icon:LineChart
},

{
name:"Customers",
path:"/customer",
icon:Users
},

{
name:"Decision Engine",
path:"/decision",
icon:ShieldAlert
},

{
name:"AI Copilot",
path:"/copilot",
icon:Bot
},

{
name:"Reports",
path:"/reports",
icon:FileText
},

{
name:"Monitoring",
path:"/monitoring",
icon:Activity
},

{
name:"Settings",
path:"/settings",
icon:Settings
}

];



export default function Sidebar(){


return (

<aside

className="
w-64
min-h-screen
bg-slate-950
border-r
border-slate-800
p-5
"

>


<h1

className="
text-xl
font-bold
text-blue-400
mb-8
"

>

Enterprise AI

</h1>



<nav className="space-y-2">


{

menu.map((item)=>{


const Icon=item.icon;


return (

<NavLink

key={item.name}

to={item.path}

className={({isActive})=>

`
flex
items-center
gap-3
p-3
rounded-lg
transition

${

isActive

?

"bg-blue-600 text-white"

:

"text-slate-400 hover:bg-slate-800"

}

`

}

>


<Icon size={20}/>

<span>
{item.name}
</span>


</NavLink>


)


})

}



</nav>


</aside>


);

}
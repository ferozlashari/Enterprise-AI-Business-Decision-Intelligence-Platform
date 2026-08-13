import {
User
}
from "lucide-react";


import {
useContext
}
from "react";


import {
AuthContext
}
from "../../context/AuthContext";

import NotificationBell from "../../features/notifications/components/NotificationBell";



export default function Navbar(){


const {
user,
logout
}
=
useContext(AuthContext);



return (

<header

className="
h-16
bg-slate-900
border-b
border-slate-800
flex
items-center
justify-between
px-6
"

>


<h2 className="
text-white
font-semibold
">

Enterprise AI Business Intelligence

</h2>



<div className="
flex
items-center
gap-5
">


<NotificationBell />



<div className="
flex
items-center
gap-2
text-white
">


<User size={20}/>


<span>

{
user?.username || "Admin"
}

</span>


</div>



<button

onClick={logout}

className="
text-red-400
"

>

Logout

</button>



</div>



</header>


);


}
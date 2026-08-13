import { useContext } from "react";

import { Database } from "lucide-react";

import { AuthContext } from "../../context/AuthContext";

import AccountCard from "./components/AccountCard";
import ChangePasswordCard from "./components/ChangePasswordCard";
import TaskAdmin from "./components/TaskAdmin";
import CacheAdmin from "./components/CacheAdmin";


export default function Settings() {

    const { user, logout } = useContext(AuthContext);


    return (
        <div className="p-6 text-white space-y-6 max-w-3xl">

            <div>
                <h1 className="text-3xl font-bold">
                    Settings
                </h1>
                <p className="text-slate-400 mt-1">
                    Account, security, and platform administration.
                </p>
            </div>

            <AccountCard user={user} onLogout={logout} />

            <ChangePasswordCard />

            <TaskAdmin />

            <CacheAdmin />

            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">

                <div className="flex items-center gap-2 mb-2">
                    <Database size={18} className="text-slate-400" />
                    <h2 className="text-white font-bold text-xl">
                        Platform
                    </h2>
                </div>

                <p className="text-slate-400 text-sm">
                    Enterprise AI Business Decision Intelligence
                    Platform — version 1.0.0
                </p>

            </div>

        </div>
    );

}

import { User, Mail, ShieldCheck, LogOut } from "lucide-react";


export default function AccountCard({ user, onLogout }) {

    return (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">

            <h2 className="text-white font-bold text-xl mb-4">
                Account
            </h2>

            <div className="space-y-3">

                <div className="flex items-center gap-3">
                    <div className="bg-blue-500/10 text-blue-400 p-2 rounded-lg">
                        <User size={18} />
                    </div>
                    <div>
                        <p className="text-slate-400 text-xs">Username</p>
                        <p className="text-white font-medium">
                            {user?.username ?? "—"}
                        </p>
                    </div>
                </div>

                <div className="flex items-center gap-3">
                    <div className="bg-emerald-500/10 text-emerald-400 p-2 rounded-lg">
                        <Mail size={18} />
                    </div>
                    <div>
                        <p className="text-slate-400 text-xs">Email</p>
                        <p className="text-white font-medium">
                            {user?.email ?? "—"}
                        </p>
                    </div>
                </div>

                <div className="flex items-center gap-3">
                    <div className="bg-yellow-500/10 text-yellow-400 p-2 rounded-lg">
                        <ShieldCheck size={18} />
                    </div>
                    <div>
                        <p className="text-slate-400 text-xs">Role</p>
                        <p className="text-white font-medium capitalize">
                            {user?.role ?? "user"}
                        </p>
                    </div>
                </div>

            </div>

            <button
                onClick={onLogout}
                className="
                    mt-5
                    flex
                    items-center
                    gap-2
                    text-sm
                    text-red-400
                    bg-red-500/10
                    hover:bg-red-500/20
                    border
                    border-red-500/30
                    rounded-lg
                    px-4
                    py-2
                    transition
                "
            >
                <LogOut size={14} />
                Log Out
            </button>

        </div>
    );

}

import { Server, Activity, Clock } from "lucide-react";


export default function PlatformStats({ health, metrics }) {

    return (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">

            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
                <div className="flex items-center gap-2 text-slate-400 text-sm mb-1">
                    <Server size={16} />
                    Platform Status
                </div>
                <p
                    className={`
                        text-2xl
                        font-bold
                        ${
                            health?.status === "Healthy"
                                ? "text-emerald-400"
                                : "text-red-400"
                        }
                    `}
                >
                    {health?.status ?? "Unknown"}
                </p>
            </div>

            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
                <div className="flex items-center gap-2 text-slate-400 text-sm mb-1">
                    <Activity size={16} />
                    Total Requests
                </div>
                <p className="text-2xl font-bold text-white">
                    {Number(metrics?.requests ?? 0).toLocaleString()}
                </p>
            </div>

            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
                <div className="flex items-center gap-2 text-slate-400 text-sm mb-1">
                    <Clock size={16} />
                    Last Checked
                </div>
                <p className="text-2xl font-bold text-white">
                    {metrics?.time ?? health?.time ?? "—"}
                </p>
            </div>

        </div>
    );

}

import { Boxes, PackageCheck, AlertTriangle, DollarSign } from "lucide-react";


function StatCard({ title, value, icon: Icon, accent }) {

    return (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
            <div className="flex justify-between items-start">

                <div>
                    <p className="text-slate-400 text-sm">{title}</p>
                    <p className="text-2xl font-bold text-white mt-1">
                        {value}
                    </p>
                </div>

                <div className={`p-2.5 rounded-lg ${accent}`}>
                    <Icon size={20} />
                </div>

            </div>
        </div>
    );

}


export default function InventoryStats({
    records,
    avgPredicted,
    lowStockCount,
    avgUnitPrice
}) {

    return (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">

            <StatCard
                title="Records Analyzed"
                value={records.toLocaleString()}
                icon={Boxes}
                accent="bg-blue-500/10 text-blue-400"
            />

            <StatCard
                title="Predicted Inventory (avg)"
                value={avgPredicted}
                icon={PackageCheck}
                accent="bg-emerald-500/10 text-emerald-400"
            />

            <StatCard
                title="Low Stock Items"
                value={lowStockCount.toLocaleString()}
                icon={AlertTriangle}
                accent="bg-red-500/10 text-red-400"
            />

            <StatCard
                title="Avg Unit Price"
                value={`$${avgUnitPrice.toFixed(2)}`}
                icon={DollarSign}
                accent="bg-yellow-500/10 text-yellow-400"
            />

        </div>
    );

}

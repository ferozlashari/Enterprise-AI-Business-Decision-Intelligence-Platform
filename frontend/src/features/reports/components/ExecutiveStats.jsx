
import { DollarSign, Boxes, Users } from "lucide-react";

// =====================================================
// ENTERPRISE EXECUTIVE STATISTICS
// =====================================================

export default function ExecutiveStats({ summary }) {
    const revenue = Number(summary?.revenue ?? 0);
    const profit = Number(summary?.profit ?? 0);
    const inventory = Number(summary?.inventory ?? 0);
    const customers = Number(summary?.customers ?? 0);

    const formatCurrency = (value) => {
        return `$${value.toLocaleString("en-US", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        })}`;
    };

    const formatNumber = (value) => {
        return value.toLocaleString("en-US", {
            minimumFractionDigits: 0,
            maximumFractionDigits: 2,
        });
    };

    return (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">

            {/* ================= REVENUE ================= */}

            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">

                <div className="flex items-center gap-2 text-slate-400 text-sm mb-1">
                    <DollarSign size={16} />
                    Revenue
                </div>

                <p className="text-2xl font-bold text-white">
                    {formatCurrency(revenue)}
                </p>

            </div>


            {/* ================= PROFIT ================= */}

            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">

                <div className="flex items-center gap-2 text-slate-400 text-sm mb-1">
                    <DollarSign size={16} />
                    Profit
                </div>

                <p className="text-2xl font-bold text-white">
                    {formatCurrency(profit)}
                </p>

            </div>


            {/* ================= INVENTORY ================= */}

            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">

                <div className="flex items-center gap-2 text-slate-400 text-sm mb-1">
                    <Boxes size={16} />
                    Inventory
                </div>

                <p className="text-2xl font-bold text-white">
                    {formatNumber(inventory)}
                </p>

            </div>


            {/* ================= CUSTOMERS ================= */}

            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">

                <div className="flex items-center gap-2 text-slate-400 text-sm mb-1">
                    <Users size={16} />
                    Customers
                </div>

                <p className="text-2xl font-bold text-white">
                    {formatNumber(customers)}
                </p>

            </div>

        </div>
    );
}


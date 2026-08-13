import { useEffect, useMemo, useState } from "react";

import { Loader2 } from "lucide-react";

import { fetchInventory } from "./inventory.api";

import InventoryStats from "./components/InventoryStats";
import InventoryCategoryChart from "./components/InventoryCategoryChart";
import InventoryTable from "./components/InventoryTable";


export default function Inventory() {

    const [rows, setRows] = useState([]);

    const [records, setRecords] = useState(0);

    const [loading, setLoading] = useState(true);

    const [error, setError] = useState(null);


    useEffect(() => {

        loadInventory();

    }, []);


    const loadInventory = async () => {

        try {

            setLoading(true);
            setError(null);

            const data = await fetchInventory();

            const result =
                data?.result ??
                data?.inventory_prediction ??
                {};

            const inventory = Array.isArray(result?.inventory)
                ? result.inventory
                : [];

            setRows(inventory);
            setRecords(result?.records ?? inventory.length);

        } catch (err) {

            setError(
                err?.message || "Unable to load inventory intelligence."
            );

        } finally {

            setLoading(false);

        }

    };


    const totalPredicted = useMemo(() => {

        return rows.reduce(
            (sum, row) => sum + (Number(row["Predicted Inventory"]) || 0),
            0
        );

    }, [rows]);

    const avgUnitPrice = useMemo(() => {

        if (rows.length === 0) return 0;

        const total = rows.reduce(
            (sum, row) => sum + (Number(row["Unit Price"]) || 0),
            0
        );

        return total / rows.length;

    }, [rows]);

    const lowStockCount = useMemo(() => {

        return rows.filter(
            (row) => (Number(row["Predicted Inventory"]) || 0) < 3
        ).length;

    }, [rows]);

    const categoryChartData = useMemo(() => {

        const grouped = {};

        rows.forEach((row) => {

            const category = row["Category"] || "Other";

            if (!grouped[category]) {
                grouped[category] = { total: 0, count: 0 };
            }

            grouped[category].total += Number(row["Predicted Inventory"]) || 0;
            grouped[category].count += 1;

        });

        return Object.entries(grouped).map(([name, value]) => ({
            name,
            predicted: Number((value.total / value.count).toFixed(2))
        }));

    }, [rows]);


    if (loading) {

        return (
            <div className="p-6 text-white flex items-center gap-2 justify-center py-20">
                <Loader2 size={20} className="animate-spin" />
                Loading inventory intelligence...
            </div>
        );

    }


    return (
        <div className="p-6 text-white space-y-6">

            <div>
                <h1 className="text-3xl font-bold">
                    Inventory Intelligence
                </h1>
                <p className="text-slate-400 mt-1">
                    Predicted stock levels driven by the demand
                    forecasting model.
                </p>
            </div>

            {error && (
                <div
                    className="
                        bg-red-500/10
                        border
                        border-red-500/30
                        text-red-400
                        text-sm
                        rounded-lg
                        px-4
                        py-3
                    "
                >
                    {error}
                </div>
            )}

            <InventoryStats
                records={records}
                avgPredicted={
                    rows.length
                        ? (totalPredicted / rows.length).toFixed(2)
                        : "0"
                }
                lowStockCount={lowStockCount}
                avgUnitPrice={avgUnitPrice}
            />

            <InventoryCategoryChart data={categoryChartData} />

            <InventoryTable rows={rows} />

        </div>
    );

}

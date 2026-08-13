import {
    ResponsiveContainer,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip
} from "recharts";


export default function InventoryCategoryChart({ data }) {

    return (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">

            <h2 className="text-white font-bold text-xl mb-4">
                Avg Predicted Inventory by Category
            </h2>

            <div style={{ width: "100%", height: 280 }}>

                <ResponsiveContainer>

                    <BarChart data={data}>

                        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />

                        <XAxis dataKey="name" stroke="#64748b" fontSize={12} />

                        <YAxis stroke="#64748b" fontSize={12} />

                        <Tooltip
                            contentStyle={{
                                background: "#0f172a",
                                border: "1px solid #1e293b",
                                borderRadius: 8,
                                color: "#e2e8f0"
                            }}
                        />

                        <Bar dataKey="predicted" fill="#3b82f6" radius={[6, 6, 0, 0]} />

                    </BarChart>

                </ResponsiveContainer>

            </div>

        </div>
    );

}

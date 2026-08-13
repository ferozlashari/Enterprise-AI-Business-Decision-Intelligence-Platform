export default function InventoryTable({ rows }) {

    return (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">

            <h2 className="text-white font-bold text-xl mb-4">
                Product-Level Predictions
            </h2>

            {rows.length === 0 ? (

                <p className="text-slate-500 text-sm text-center py-6">
                    No inventory predictions available yet.
                </p>

            ) : (

                <div className="overflow-x-auto">

                    <table className="w-full text-sm text-left">

                        <thead>
                            <tr className="text-slate-400 border-b border-slate-800">
                                <th className="py-2 pr-4">Product</th>
                                <th className="py-2 pr-4">Category</th>
                                <th className="py-2 pr-4">Region</th>
                                <th className="py-2 pr-4">Unit Price</th>
                                <th className="py-2">Predicted Inventory</th>
                            </tr>
                        </thead>

                        <tbody>

                            {rows.slice(0, 25).map((row, index) => (

                                <tr
                                    key={`${row["Product ID"]}-${index}`}
                                    className="border-b border-slate-800/60"
                                >
                                    <td className="py-2 pr-4 text-slate-200 max-w-xs truncate">
                                        {row["Product Name"] ?? "—"}
                                    </td>
                                    <td className="py-2 pr-4 text-slate-300">
                                        {row["Category"] ?? "—"}
                                    </td>
                                    <td className="py-2 pr-4 text-slate-300">
                                        {row["Region"] ?? "—"}
                                    </td>
                                    <td className="py-2 pr-4 text-slate-300">
                                        {row["Unit Price"] != null
                                            ? `$${Number(row["Unit Price"]).toFixed(2)}`
                                            : "—"}
                                    </td>
                                    <td className="py-2 text-slate-300">
                                        {row["Predicted Inventory"] != null
                                            ? Number(row["Predicted Inventory"]).toFixed(2)
                                            : "—"}
                                    </td>
                                </tr>

                            ))}

                        </tbody>

                    </table>

                </div>

            )}

        </div>
    );

}

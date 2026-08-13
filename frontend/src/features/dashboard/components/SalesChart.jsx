
import {
    ResponsiveContainer,
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
} from "recharts";

export default function SalesChart({
    data = [],
}) {

    // =====================================================
    // NORMALIZE CHART DATA
    // =====================================================

    const chartData = Array.isArray(data)
        ? data
            .map((item, index) => {

                if (
                    !item ||
                    typeof item !== "object"
                ) {
                    return null;
                }

                const label =
                    item.month ??
                    item.category ??
                    item.name ??
                    item.date ??
                    `Item ${index + 1}`;

                const sales =
                    Number(
                        item.sales ??
                        item.value ??
                        item.revenue ??
                        0
                    );

                return {
                    month: String(label),
                    sales: Number.isFinite(sales)
                        ? sales
                        : 0,
                };
            })
            .filter(Boolean)
        : [];


    // =====================================================
    // CURRENCY FORMAT
    // =====================================================

    const formatCurrency = (value) => {

        const number =
            Number(value) || 0;

        return new Intl.NumberFormat(
            "en-US",
            {
                style: "currency",
                currency: "USD",
                maximumFractionDigits: 0,
            }
        ).format(number);
    };


    // =====================================================
    // EMPTY STATE
    // =====================================================

    if (chartData.length === 0) {

        return (
            <div
                className="
                    bg-slate-900
                    border
                    border-slate-800
                    rounded-xl
                    p-5
                    shadow-lg
                "
            >

                <h2
                    className="
                        text-white
                        font-bold
                        text-lg
                        mb-4
                    "
                >
                    Sales Revenue Trend
                </h2>

                <div
                    className="
                        h-[350px]
                        flex
                        items-center
                        justify-center
                    "
                >

                    <p
                        className="
                            text-slate-400
                            text-sm
                        "
                    >
                        No sales data available
                    </p>

                </div>

            </div>
        );
    }


    // =====================================================
    // CHART
    // =====================================================

    return (
        <div
            className="
                bg-slate-900
                border
                border-slate-800
                rounded-xl
                p-5
                shadow-lg
            "
        >

            {/* =================================================
                HEADER
            ================================================= */}

            <div
                className="
                    flex
                    flex-col
                    sm:flex-row
                    sm:justify-between
                    sm:items-center
                    gap-2
                    mb-5
                "
            >

                <div>

                    <h2
                        className="
                            text-white
                            font-bold
                            text-lg
                        "
                    >
                        Sales Revenue Trend
                    </h2>

                    <p
                        className="
                            text-slate-400
                            text-sm
                            mt-1
                        "
                    >
                        Monthly sales performance
                    </p>

                </div>


                <div
                    className="
                        text-blue-400
                        text-sm
                        font-medium
                    "
                >
                    Total Sales
                </div>

            </div>


            {/* =================================================
                CHART
            ================================================= */}

            <div className="w-full h-[350px]">

                <ResponsiveContainer
                    width="100%"
                    height="100%"
                >

                    <AreaChart
                        data={chartData}
                        margin={{
                            top: 10,
                            right: 20,
                            left: 10,
                            bottom: 10,
                        }}
                    >

                        <CartesianGrid
                            strokeDasharray="3 3"
                            stroke="#334155"
                        />


                        <XAxis
                            dataKey="month"
                            stroke="#94a3b8"
                            tick={{
                                fill: "#94a3b8",
                                fontSize: 12,
                            }}
                            tickLine={{
                                stroke: "#475569",
                            }}
                            axisLine={{
                                stroke: "#475569",
                            }}
                        />


                        <YAxis
                            stroke="#94a3b8"
                            tick={{
                                fill: "#94a3b8",
                                fontSize: 12,
                            }}
                            tickFormatter={
                                formatCurrency
                            }
                            tickLine={{
                                stroke: "#475569",
                            }}
                            axisLine={{
                                stroke: "#475569",
                            }}
                        />


                        <Tooltip
                            contentStyle={{
                                backgroundColor:
                                    "#0f172a",

                                border:
                                    "1px solid #334155",

                                borderRadius:
                                    "8px",

                                color:
                                    "#ffffff",
                            }}

                            labelStyle={{
                                color:
                                    "#cbd5e1",
                            }}

                            itemStyle={{
                                color:
                                    "#ffffff",
                            }}

                            formatter={(
                                value
                            ) => [
                                formatCurrency(
                                    value
                                ),
                                "Sales",
                            ]}
                        />


                        <Area
                            type="monotone"
                            dataKey="sales"
                            name="Total Sales"
                            stroke="#2563eb"
                            fill="#2563eb"
                            fillOpacity={0.3}
                            strokeWidth={2}
                            activeDot={{
                                r: 6,
                            }}
                        />

                    </AreaChart>

                </ResponsiveContainer>

            </div>

        </div>
    );
}


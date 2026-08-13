
import {
    ResponsiveContainer,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
} from "recharts";

// =====================================================
// ENTERPRISE AI BUSINESS DECISION INTELLIGENCE PLATFORM
//
// INVENTORY CHART
//
// Responsibilities:
// - Display available inventory
// - Display predicted demand
// - Safely consume normalized dashboard data
// - Handle empty/invalid data
// - Provide responsive visualization
//
// Expected normalized data:
//
// [
//     {
//         product: "Product A",
//         quantity: 120,
//         demand: 100
//     }
// ]
//
// =====================================================

export default function InventoryChart({
    data = [],
}) {

    // =================================================
    // NORMALIZE CHART DATA
    // =================================================

    const chartData =
        Array.isArray(data)
            ? data
                .map((item, index) => {

                    // ---------------------------------
                    // Ignore invalid records
                    // ---------------------------------

                    if (
                        !item ||
                        typeof item !== "object"
                    ) {
                        return null;
                    }


                    // ---------------------------------
                    // QUANTITY / STOCK
                    //
                    // dashboard.api.js already
                    // normalizes quantity.
                    //
                    // These are additional fallbacks
                    // for backend compatibility.
                    // ---------------------------------

                    const rawQuantity =
                        item.quantity ??
                        item.stock ??
                        item.available_stock ??
                        item.availableStock ??
                        item.current_stock ??
                        item.currentStock ??
                        item.inventory ??
                        item.Inventory ??
                        item.value ??
                        0;


                    const quantityValue =
                        Number(rawQuantity);


                    // ---------------------------------
                    // DEMAND
                    // ---------------------------------

                    const rawDemand =
                        item.demand ??
                        item.predicted_demand ??
                        item.predictedDemand ??
                        item.predicted ??
                        item.forecast ??
                        0;


                    const demandValue =
                        Number(rawDemand);


                    // ---------------------------------
                    // PRODUCT NAME
                    // ---------------------------------

                    const rawProduct =
                        item.product ??
                        item.name ??
                        item.Product ??
                        item.product_name ??
                        item.productName ??
                        item["Product Name"] ??
                        `Product ${index + 1}`;


                    const productName =
                        String(rawProduct).trim();


                    // ---------------------------------
                    // SAFE NUMBERS
                    // ---------------------------------

                    const quantity =
                        Number.isFinite(
                            quantityValue
                        )
                            ? Math.max(
                                0,
                                quantityValue
                            )
                            : 0;


                    const demand =
                        Number.isFinite(
                            demandValue
                        )
                            ? Math.max(
                                0,
                                demandValue
                            )
                            : 0;


                    return {
                        ...item,

                        product:
                            productName ||
                            `Product ${index + 1}`,

                        quantity,

                        demand,
                    };

                })
                .filter(Boolean)
            : [];


    // =================================================
    // EMPTY STATE
    // =================================================

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

                {/* -------------------------------------
                    HEADER
                ------------------------------------- */}

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
                                text-xl
                            "
                        >
                            Inventory Levels
                        </h2>


                        <p
                            className="
                                text-slate-400
                                text-sm
                                mt-1
                            "
                        >
                            Available stock versus predicted demand
                        </p>

                    </div>


                    <div
                        className="
                            text-blue-400
                            text-sm
                            font-medium
                        "
                    >
                        Inventory AI
                    </div>

                </div>


                {/* -------------------------------------
                    EMPTY MESSAGE
                ------------------------------------- */}

                <div
                    className="
                        h-[350px]
                        flex
                        items-center
                        justify-center
                    "
                >

                    <div
                        className="
                            text-center
                        "
                    >

                        <p
                            className="
                                text-slate-400
                                text-sm
                            "
                        >
                            No inventory data available
                        </p>


                        <p
                            className="
                                text-slate-600
                                text-xs
                                mt-2
                            "
                        >
                            Inventory intelligence will appear
                            when data is available.
                        </p>

                    </div>

                </div>

            </div>

        );
    }


    // =================================================
    // NUMBER FORMAT
    // =================================================

    const formatNumber = (
        value
    ) => {

        const number =
            Number(value);


        if (
            !Number.isFinite(number)
        ) {
            return "0";
        }


        return new Intl.NumberFormat(
            "en-US",
            {
                notation: "compact",
                maximumFractionDigits: 1,
            }
        ).format(number);
    };


    // =================================================
    // TOOLTIP FORMAT
    // =================================================

    const formatTooltipValue = (
        value
    ) => {

        const number =
            Number(value);


        if (
            !Number.isFinite(number)
        ) {
            return "0";
        }


        return new Intl.NumberFormat(
            "en-US",
            {
                maximumFractionDigits: 2,
            }
        ).format(number);
    };


    // =================================================
    // PRODUCT LABEL
    // =================================================

    const formatProductName = (
        value
    ) => {

        const name =
            String(
                value ?? ""
            ).trim();


        if (!name) {
            return "Product";
        }


        if (name.length <= 15) {
            return name;
        }


        return `${name.substring(
            0,
            12
        )}...`;
    };


    // =================================================
    // TOOLTIP
    // =================================================

    const tooltipFormatter = (
        value,
        name
    ) => {

        return [
            formatTooltipValue(
                value
            ),
            name,
        ];

    };


    // =================================================
    // CHART HEIGHT
    // =================================================

    const chartHeight = 350;


    // =================================================
    // RENDER
    // =================================================

    return (

        <div
            className="
                bg-slate-900
                border
                border-slate-800
                rounded-xl
                p-5
                shadow-lg
                hover:border-slate-700
                transition
                duration-200
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
                            text-xl
                        "
                    >
                        Inventory Levels
                    </h2>


                    <p
                        className="
                            text-slate-400
                            text-sm
                            mt-1
                        "
                    >
                        Available stock versus predicted demand
                    </p>

                </div>


                <div
                    className="
                        text-blue-400
                        text-sm
                        font-medium
                    "
                >
                    Inventory AI
                </div>

            </div>


            {/* =================================================
                CHART
            ================================================= */}

            <div
                className="
                    w-full
                    h-[350px]
                "
            >

                <ResponsiveContainer
                    width="100%"
                    height={chartHeight}
                >

                    <BarChart
                        data={chartData}
                        margin={{
                            top: 10,
                            right: 20,
                            left: 10,
                            bottom:
                                chartData.length > 5
                                    ? 45
                                    : 20,
                        }}
                    >

                        {/* =====================================
                            GRID
                        ===================================== */}

                        <CartesianGrid
                            strokeDasharray="3 3"
                            stroke="#334155"
                        />


                        {/* =====================================
                            X AXIS
                        ===================================== */}

                        <XAxis
                            dataKey="product"
                            stroke="#94a3b8"
                            tick={{
                                fill: "#94a3b8",
                                fontSize: 11,
                            }}
                            tickFormatter={
                                formatProductName
                            }
                            interval={0}
                            angle={
                                chartData.length > 5
                                    ? -25
                                    : 0
                            }
                            textAnchor={
                                chartData.length > 5
                                    ? "end"
                                    : "middle"
                            }
                            tickLine={{
                                stroke: "#475569",
                            }}
                            axisLine={{
                                stroke: "#475569",
                            }}
                        />


                        {/* =====================================
                            Y AXIS
                        ===================================== */}

                        <YAxis
                            stroke="#94a3b8"
                            tick={{
                                fill: "#94a3b8",
                                fontSize: 12,
                            }}
                            tickFormatter={
                                formatNumber
                            }
                            tickLine={{
                                stroke: "#475569",
                            }}
                            axisLine={{
                                stroke: "#475569",
                            }}
                        />


                        {/* =====================================
                            TOOLTIP
                        ===================================== */}

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
                                marginBottom:
                                    "4px",
                            }}

                            itemStyle={{
                                color:
                                    "#ffffff",
                            }}

                            cursor={{
                                fill:
                                    "rgba(148, 163, 184, 0.08)",
                            }}

                            formatter={
                                tooltipFormatter
                            }
                        />


                        {/* =====================================
                            LEGEND
                        ===================================== */}

                        <Legend
                            wrapperStyle={{
                                color:
                                    "#cbd5e1",

                                paddingTop:
                                    "10px",
                            }}
                        />


                        {/* =====================================
                            AVAILABLE STOCK
                        ===================================== */}

                        <Bar
                            dataKey="quantity"
                            name="Available Stock"
                            fill="#2563eb"
                            radius={[
                                4,
                                4,
                                0,
                                0,
                            ]}
                            maxBarSize={50}
                        />


                        {/* =====================================
                            PREDICTED DEMAND
                        ===================================== */}

                        <Bar
                            dataKey="demand"
                            name="Predicted Demand"
                            fill="#f59e0b"
                            radius={[
                                4,
                                4,
                                0,
                                0,
                            ]}
                            maxBarSize={50}
                        />

                    </BarChart>

                </ResponsiveContainer>

            </div>

        </div>

    );
}


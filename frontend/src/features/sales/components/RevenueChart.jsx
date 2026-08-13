
import {
    ResponsiveContainer,
    AreaChart,
    Area,
    XAxis,
    YAxis,
    Tooltip,
    CartesianGrid
} from "recharts";


// =====================================================
// MONTH ORDER
// =====================================================

const MONTH_ORDER = {

    Jan: 1,
    Feb: 2,
    Mar: 3,
    Apr: 4,
    May: 5,
    Jun: 6,
    Jul: 7,
    Aug: 8,
    Sep: 9,
    Oct: 10,
    Nov: 11,
    Dec: 12

};


// =====================================================
// FORMAT MONTH
// =====================================================

const formatMonth = (value) => {

    if (!value) {
        return "N/A";
    }

    const text =
        String(value)
            .trim();


    const normalized =
        text.charAt(0).toUpperCase() +
        text.slice(1, 3).toLowerCase();


    return MONTH_ORDER[normalized]
        ? normalized
        : text;

};


// =====================================================
// FORMAT CURRENCY
// =====================================================

const formatCurrency = (value) => {

    const number =
        Number(value) || 0;


    return new Intl.NumberFormat(
        "en-US",
        {
            style: "currency",
            currency: "USD",
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }
    ).format(number);

};


// =====================================================
// FORMAT AXIS
// =====================================================

const formatAxisValue = (value) => {

    const number =
        Number(value) || 0;


    if (
        Math.abs(number) >= 1000000
    ) {

        return `$${(
            number / 1000000
        ).toFixed(1)}M`;

    }


    if (
        Math.abs(number) >= 1000
    ) {

        return `$${(
            number / 1000
        ).toFixed(0)}K`;

    }


    return `$${number}`;

};


// =====================================================
// CUSTOM TOOLTIP
// =====================================================

function CustomTooltip({
    active,
    payload,
    label
}) {

    if (
        !active ||
        !payload ||
        payload.length === 0
    ) {

        return null;

    }


    const value =
        Number(
            payload[0]?.value
        ) || 0;


    return (

        <div
            className="
                bg-slate-950
                border
                border-slate-700
                rounded-lg
                px-4
                py-3
                shadow-xl
            "
        >

            <p
                className="
                    text-slate-400
                    text-xs
                    mb-1
                "
            >
                {formatMonth(label)}
            </p>


            <p
                className="
                    text-white
                    font-bold
                "
            >
                {formatCurrency(value)}
            </p>

        </div>

    );

}


// =====================================================
// REVENUE CHART
// =====================================================

export default function RevenueChart({

    data = []

}) {


    // =================================================
    // NORMALIZE + SORT DATA
    // =================================================

    const chartData =
        Array.isArray(data)

            ? data
                .map((item) => {

                    const month =
                        item?.month ??
                        item?.Month ??
                        item?.name ??
                        item?.period ??
                        "";

                    const sales =
                        Number(
                            item?.sales ??
                            item?.Sales ??
                            item?.revenue ??
                            item?.Revenue ??
                            item?.value ??
                            0
                        ) || 0;


                    return {

                        month:
                            formatMonth(month),

                        sales

                    };

                })
                .filter(
                    item =>
                        item.month !== "N/A"
                )
                .sort(
                    (a, b) =>
                        (
                            MONTH_ORDER[a.month] || 99
                        ) -
                        (
                            MONTH_ORDER[b.month] || 99
                        )
                )

            : [];


    // =================================================
    // EMPTY STATE
    // =================================================

    if (
        chartData.length === 0
    ) {

        return (

            <div
                className="
                    bg-slate-900
                    border
                    border-slate-800
                    rounded-xl
                    p-5
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
                        Revenue Trend
                    </h2>


                    <p
                        className="
                            text-slate-400
                            text-sm
                            mt-1
                        "
                    >
                        Monthly enterprise sales
                        performance
                    </p>

                </div>


                <div
                    className="
                        mt-6
                        h-[300px]
                        flex
                        items-center
                        justify-center
                        border
                        border-slate-800
                        rounded-lg
                    "
                >

                    <p
                        className="
                            text-slate-500
                        "
                    >
                        No sales trend data
                        available
                    </p>

                </div>

            </div>

        );

    }


    // =================================================
    // TOTAL
    // =================================================

    const totalRevenue =
        chartData.reduce(
            (
                total,
                item
            ) =>
                total +
                item.sales,
            0
        );


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
                shadow-sm
            "
        >

            {/* =========================================
                HEADER
            ========================================= */}

            <div
                className="
                    flex
                    flex-col
                    sm:flex-row
                    sm:items-start
                    sm:justify-between
                    gap-3
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
                        Revenue Trend
                    </h2>


                    <p
                        className="
                            text-slate-400
                            text-sm
                            mt-1
                        "
                    >
                        Monthly enterprise sales
                        performance
                    </p>

                </div>


                <div
                    className="
                        bg-blue-500/10
                        border
                        border-blue-500/20
                        rounded-lg
                        px-3
                        py-2
                    "
                >

                    <p
                        className="
                            text-slate-500
                            text-xs
                        "
                    >
                        Period Revenue
                    </p>


                    <p
                        className="
                            text-blue-400
                            font-bold
                            text-sm
                            mt-1
                        "
                    >
                        {formatCurrency(
                            totalRevenue
                        )}
                    </p>

                </div>

            </div>


            {/* =========================================
                CHART
            ========================================= */}

            <ResponsiveContainer
                width="100%"
                height={330}
            >

                <AreaChart
                    data={chartData}
                    margin={{
                        top: 10,
                        right: 10,
                        left: 5,
                        bottom: 5
                    }}
                >

                    <defs>

                        <linearGradient
                            id="salesGradient"
                            x1="0"
                            y1="0"
                            x2="0"
                            y2="1"
                        >

                            <stop
                                offset="0%"
                                stopColor="#3b82f6"
                                stopOpacity={0.35}
                            />

                            <stop
                                offset="100%"
                                stopColor="#3b82f6"
                                stopOpacity={0.02}
                            />

                        </linearGradient>

                    </defs>


                    <CartesianGrid
                        strokeDasharray="3 3"
                        stroke="#334155"
                        vertical={false}
                    />


                    <XAxis
                        dataKey="month"
                        tick={{
                            fill: "#94a3b8",
                            fontSize: 12
                        }}
                        axisLine={{
                            stroke: "#334155"
                        }}
                        tickLine={false}
                    />


                    <YAxis
                        tickFormatter={
                            formatAxisValue
                        }
                        tick={{
                            fill: "#94a3b8",
                            fontSize: 11
                        }}
                        axisLine={false}
                        tickLine={false}
                        width={65}
                    />


                    <Tooltip
                        content={
                            <CustomTooltip />
                        }
                    />


                    <Area
                        type="monotone"
                        dataKey="sales"
                        stroke="#60a5fa"
                        strokeWidth={3}
                        fill="url(#salesGradient)"
                        dot={{
                            r: 3,
                            fill: "#60a5fa",
                            strokeWidth: 0
                        }}
                        activeDot={{
                            r: 6
                        }}
                    />

                </AreaChart>

            </ResponsiveContainer>


            {/* =========================================
                FOOTER
            ========================================= */}

            <div
                className="
                    mt-3
                    pt-3
                    border-t
                    border-slate-800
                    flex
                    items-center
                    justify-between
                "
            >

                <span
                    className="
                        text-slate-500
                        text-xs
                    "
                >
                    {chartData.length} reporting
                    periods
                </span>


                <span
                    className="
                        text-slate-500
                        text-xs
                    "
                >
                    Revenue performance
                </span>

            </div>

        </div>

    );

}


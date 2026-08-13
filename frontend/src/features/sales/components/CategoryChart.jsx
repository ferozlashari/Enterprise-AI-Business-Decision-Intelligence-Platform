
import {
    ResponsiveContainer,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    Tooltip,
    CartesianGrid,
    Cell
} from "recharts";


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
// NORMALIZE CATEGORY
// =====================================================

const normalizeCategoryData = (
    data
) => {

    if (
        !Array.isArray(data)
    ) {

        return [];

    }


    return data

        .map((item) => {

            const category =
                item?.category ??
                item?.Category ??
                item?.name ??
                item?.Name ??
                "Unknown";


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

                category:
                    String(category),

                sales

            };

        })

        .filter(
            item =>
                item.sales >= 0
        )

        .sort(
            (a, b) =>
                b.sales - a.sales
        );

};


// =====================================================
// TOOLTIP
// =====================================================

function CustomTooltip({
    active,
    payload
}) {

    if (
        !active ||
        !payload ||
        payload.length === 0
    ) {

        return null;

    }


    const item =
        payload[0]?.payload;


    if (!item) {

        return null;

    }


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
                    text-white
                    font-semibold
                    text-sm
                "
            >
                {item.category}
            </p>


            <p
                className="
                    text-blue-400
                    font-bold
                    mt-1
                "
            >
                {formatCurrency(
                    item.sales
                )}
            </p>


            <p
                className="
                    text-slate-500
                    text-xs
                    mt-1
                "
            >
                {item.percentage.toFixed(2)}%
                of total revenue
            </p>

        </div>

    );

}


// =====================================================
// CATEGORY COLORS
// =====================================================

const BAR_COLORS = [
    "#3b82f6",
    "#8b5cf6",
    "#06b6d4",
    "#22c55e",
    "#f59e0b",
    "#ef4444"
];


// =====================================================
// CATEGORY CHART
// =====================================================

export default function CategoryChart({

    data = []

}) {


    // =================================================
    // NORMALIZE
    // =================================================

    const normalizedData =
        normalizeCategoryData(
            data
        );


    // =================================================
    // TOTAL
    // =================================================

    const totalSales =
        normalizedData.reduce(
            (
                total,
                item
            ) =>
                total +
                item.sales,
            0
        );


    // =================================================
    // ADD PERCENTAGE
    // =================================================

    const chartData =
        normalizedData.map(
            (item) => ({

                ...item,

                percentage:
                    totalSales > 0

                        ? (
                            item.sales /
                            totalSales
                        ) * 100

                        : 0

            })
        );


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

                <h2
                    className="
                        text-white
                        font-bold
                        text-xl
                    "
                >
                    Sales By Category
                </h2>


                <p
                    className="
                        text-slate-400
                        text-sm
                        mt-1
                    "
                >
                    Revenue distribution across
                    product categories
                </p>


                <div
                    className="
                        mt-5
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
                        No category data available
                    </p>

                </div>

            </div>

        );

    }


    // =================================================
    // TOP CATEGORY
    // =================================================

    const topCategory =
        chartData[0];


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
                        Sales By Category
                    </h2>


                    <p
                        className="
                            text-slate-400
                            text-sm
                            mt-1
                        "
                    >
                        Revenue distribution across
                        product categories
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
                        text-right
                    "
                >

                    <p
                        className="
                            text-slate-500
                            text-xs
                        "
                    >
                        Categories
                    </p>


                    <p
                        className="
                            text-blue-400
                            font-bold
                            text-sm
                        "
                    >
                        {chartData.length}
                    </p>

                </div>

            </div>


            {/* =========================================
                TOP CATEGORY
            ========================================= */}

            <div
                className="
                    mb-4
                    bg-slate-950/60
                    border
                    border-slate-800
                    rounded-lg
                    px-4
                    py-3
                    flex
                    items-center
                    justify-between
                    gap-4
                "
            >

                <div>

                    <p
                        className="
                            text-slate-500
                            text-xs
                        "
                    >
                        Top Category
                    </p>


                    <p
                        className="
                            text-white
                            font-semibold
                            mt-1
                        "
                    >
                        {topCategory.category}
                    </p>

                </div>


                <div
                    className="
                        text-right
                    "
                >

                    <p
                        className="
                            text-blue-400
                            font-bold
                        "
                    >
                        {formatCurrency(
                            topCategory.sales
                        )}
                    </p>


                    <p
                        className="
                            text-slate-500
                            text-xs
                            mt-1
                        "
                    >
                        {topCategory.percentage.toFixed(2)}%
                    </p>

                </div>

            </div>


            {/* =========================================
                CHART
            ========================================= */}

            <ResponsiveContainer
                width="100%"
                height={320}
            >

                <BarChart
                    data={chartData}
                    margin={{
                        top: 10,
                        right: 10,
                        left: 5,
                        bottom: 5
                    }}
                >

                    <CartesianGrid
                        strokeDasharray="3 3"
                        stroke="#334155"
                        vertical={false}
                    />


                    <XAxis
                        dataKey="category"
                        tick={{
                            fill: "#94a3b8",
                            fontSize: 11
                        }}
                        axisLine={{
                            stroke: "#334155"
                        }}
                        tickLine={false}
                        interval={0}
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


                    <Bar
                        dataKey="sales"
                        radius={[
                            6,
                            6,
                            0,
                            0
                        ]}
                        maxBarSize={70}
                    >

                        {chartData.map(
                            (
                                entry,
                                index
                            ) => (

                                <Cell
                                    key={
                                        `category-${index}`
                                    }
                                    fill={
                                        BAR_COLORS[
                                            index %
                                            BAR_COLORS.length
                                        ]
                                    }
                                />

                            )
                        )}

                    </Bar>

                </BarChart>

            </ResponsiveContainer>


            {/* =========================================
                CATEGORY SUMMARY
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
                    gap-3
                "
            >

                <span
                    className="
                        text-slate-500
                        text-xs
                    "
                >
                    Total category revenue
                </span>


                <span
                    className="
                        text-white
                        text-sm
                        font-semibold
                    "
                >
                    {formatCurrency(
                        totalSales
                    )}
                </span>

            </div>

        </div>

    );

}


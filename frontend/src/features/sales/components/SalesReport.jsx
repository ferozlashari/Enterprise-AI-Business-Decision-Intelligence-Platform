
import {
    DollarSign,
    TrendingUp,
    TrendingDown,
    Target,
    Award
} from "lucide-react";


// =====================================================
// NUMBER HELPERS
// =====================================================

const toNumber = (value) => {

    const number =
        Number(value);

    return Number.isFinite(number)
        ? number
        : 0;

};


// =====================================================
// CURRENCY FORMATTER
// =====================================================

const formatCurrency = (value) => {

    return new Intl.NumberFormat(
        "en-US",
        {
            style: "currency",
            currency: "USD",
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }
    ).format(
        toNumber(value)
    );

};


// =====================================================
// PERCENT FORMATTER
// =====================================================

const formatPercent = (value) => {

    return `${toNumber(value).toFixed(2)}%`;

};


// =====================================================
// KPI ITEM
// =====================================================

function ReportMetric({
    label,
    value,
    icon: Icon,
    iconClass = "text-blue-400",
    valueClass = "text-white"
}) {

    return (

        <div
            className="
                bg-slate-950/60
                border
                border-slate-800
                rounded-lg
                p-4
            "
        >

            <div
                className="
                    flex
                    items-center
                    gap-2
                    mb-2
                "
            >

                <Icon
                    size={17}
                    className={iconClass}
                />


                <span
                    className="
                        text-slate-400
                        text-xs
                        font-medium
                    "
                >
                    {label}
                </span>

            </div>


            <p
                className={`
                    text-xl
                    font-bold
                    ${valueClass}
                `}
            >
                {value}
            </p>

        </div>

    );

}


// =====================================================
// SALES REPORT
// =====================================================

export default function SalesReport({

    report = {}

}) {


    // =================================================
    // SAFE VALUES
    // =================================================

    const totalSales =
        toNumber(
            report?.total_sales
        );


    const averageSales =
        toNumber(
            report?.average_sales
        );


    const profit =
        toNumber(
            report?.profit
        );


    const predictedSales =
        toNumber(
            report?.predicted_sales
        );


    const growth =
        toNumber(
            report?.growth
        );


    const bestCategory =
        report?.best_category ||
        "N/A";


    const model =
        report?.model ||
        "AI Model";


    // =================================================
    // FORECAST DIFFERENCE
    // =================================================

    const forecastDifference =
        predictedSales -
        totalSales;


    const forecastDifferencePercent =
        totalSales !== 0

            ? (
                forecastDifference /
                totalSales
            ) * 100

            : 0;


    const forecastIsLower =
        forecastDifference < 0;


    // =================================================
    // PROFIT MARGIN
    // =================================================

    const profitMargin =
        totalSales !== 0

            ? (
                profit /
                totalSales
            ) * 100

            : 0;


    // =================================================
    // BUSINESS INTERPRETATION
    // =================================================

    let insight;


    if (
        forecastIsLower &&
        Math.abs(
            forecastDifferencePercent
        ) >= 5
    ) {

        insight =
            "The AI forecast indicates a significant decline compared with current sales. Management should review demand, pricing, discounts, and regional performance.";

    }

    else if (
        forecastIsLower
    ) {

        insight =
            "The AI forecast is slightly below current sales, suggesting a moderate slowdown in expected sales performance.";

    }

    else if (
        forecastDifference > 0
    ) {

        insight =
            "The AI forecast is above current sales, indicating positive expected sales momentum.";

    }

    else {

        insight =
            "The AI forecast is closely aligned with current sales performance.";

    }


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
                    gap-4
                    mb-5
                "
            >

                <div>

                    <h2
                        className="
                            text-white
                            text-xl
                            font-bold
                        "
                    >
                        Sales Report
                    </h2>


                    <p
                        className="
                            text-slate-400
                            text-sm
                            mt-1
                        "
                    >
                        Enterprise sales performance
                        summary
                    </p>

                </div>


                <div
                    className="
                        flex
                        items-center
                        gap-2
                        bg-blue-500/10
                        border
                        border-blue-500/20
                        rounded-lg
                        px-3
                        py-2
                    "
                >

                    <Target
                        size={16}
                        className="
                            text-blue-400
                        "
                    />


                    <span
                        className="
                            text-blue-400
                            text-sm
                            font-semibold
                        "
                    >
                        {model}
                    </span>

                </div>

            </div>


            {/* =========================================
                KPI GRID
            ========================================= */}

            <div
                className="
                    grid
                    grid-cols-1
                    sm:grid-cols-2
                    gap-3
                "
            >

                <ReportMetric
                    label="Total Sales"
                    value={
                        formatCurrency(
                            totalSales
                        )
                    }
                    icon={DollarSign}
                    iconClass="
                        text-blue-400
                    "
                />


                <ReportMetric
                    label="Average Sales"
                    value={
                        formatCurrency(
                            averageSales
                        )
                    }
                    icon={TrendingUp}
                    iconClass="
                        text-cyan-400
                    "
                />


                <ReportMetric
                    label="Profit"
                    value={
                        formatCurrency(
                            profit
                        )
                    }
                    icon={DollarSign}
                    iconClass="
                        text-green-400
                    "
                    valueClass="
                        text-green-400
                    "
                />


                <ReportMetric
                    label="Profit Margin"
                    value={
                        formatPercent(
                            profitMargin
                        )
                    }
                    icon={TrendingUp}
                    iconClass="
                        text-green-400
                    "
                    valueClass="
                        text-green-400
                    "
                />

            </div>


            {/* =========================================
                BEST CATEGORY
            ========================================= */}

            <div
                className="
                    mt-4
                    bg-slate-950/60
                    border
                    border-slate-800
                    rounded-lg
                    p-4
                    flex
                    items-center
                    justify-between
                    gap-4
                "
            >

                <div
                    className="
                        flex
                        items-center
                        gap-3
                    "
                >

                    <div
                        className="
                            w-10
                            h-10
                            rounded-lg
                            bg-yellow-500/10
                            flex
                            items-center
                            justify-center
                        "
                    >

                        <Award
                            size={21}
                            className="
                                text-yellow-400
                            "
                        />

                    </div>


                    <div>

                        <p
                            className="
                                text-slate-400
                                text-xs
                            "
                        >
                            Best Performing Category
                        </p>


                        <p
                            className="
                                text-white
                                font-semibold
                                mt-1
                            "
                        >
                            {bestCategory}
                        </p>

                    </div>

                </div>


                <div
                    className="
                        text-right
                    "
                >

                    <p
                        className="
                            text-slate-500
                            text-xs
                        "
                    >
                        Growth
                    </p>


                    <p
                        className={`
                            font-semibold
                            ${
                                growth >= 0
                                    ? "text-green-400"
                                    : "text-red-400"
                            }
                        `}
                    >
                        {formatPercent(
                            growth
                        )}
                    </p>

                </div>

            </div>


            {/* =========================================
                AI FORECAST ANALYSIS
            ========================================= */}

            <div
                className="
                    mt-5
                    pt-5
                    border-t
                    border-slate-800
                "
            >

                <div
                    className="
                        flex
                        items-center
                        gap-2
                        mb-4
                    "
                >

                    {forecastIsLower ? (

                        <TrendingDown
                            size={19}
                            className="
                                text-red-400
                            "
                        />

                    ) : (

                        <TrendingUp
                            size={19}
                            className="
                                text-green-400
                            "
                        />

                    )}


                    <h3
                        className="
                            text-white
                            font-semibold
                        "
                    >
                        AI Forecast Analysis
                    </h3>

                </div>


                <p
                    className="
                        text-slate-400
                        text-sm
                        mb-4
                    "
                >
                    Forecast compared with current
                    enterprise sales
                </p>


                <div
                    className="
                        grid
                        grid-cols-1
                        sm:grid-cols-3
                        gap-3
                    "
                >

                    <div>

                        <p
                            className="
                                text-slate-500
                                text-xs
                            "
                        >
                            Current Sales
                        </p>


                        <p
                            className="
                                text-white
                                font-bold
                                mt-1
                            "
                        >
                            {formatCurrency(
                                totalSales
                            )}
                        </p>

                    </div>


                    <div>

                        <p
                            className="
                                text-slate-500
                                text-xs
                            "
                        >
                            AI Forecast
                        </p>


                        <p
                            className="
                                text-blue-400
                                font-bold
                                mt-1
                            "
                        >
                            {formatCurrency(
                                predictedSales
                            )}
                        </p>

                    </div>


                    <div>

                        <p
                            className="
                                text-slate-500
                                text-xs
                            "
                        >
                            Forecast Difference
                        </p>


                        <p
                            className={`
                                font-bold
                                mt-1
                                ${
                                    forecastIsLower
                                        ? "text-red-400"
                                        : "text-green-400"
                                }
                            `}
                        >
                            {forecastDifference >= 0
                                ? "+"
                                : ""}
                            {formatCurrency(
                                forecastDifference
                            )}
                        </p>

                    </div>

                </div>


                {/* =====================================
                    AI INSIGHT
                ===================================== */}

                <div
                    className="
                        mt-4
                        bg-slate-950
                        border
                        border-slate-800
                        rounded-lg
                        p-4
                    "
                >

                    <p
                        className="
                            text-slate-400
                            text-xs
                            font-semibold
                            uppercase
                            tracking-wide
                            mb-2
                        "
                    >
                        AI Business Insight
                    </p>


                    <p
                        className="
                            text-slate-300
                            text-sm
                            leading-6
                        "
                    >
                        {insight}
                    </p>

                </div>

            </div>

        </div>

    );

}


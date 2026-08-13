
import {
    ResponsiveContainer,
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
} from "recharts";

// =====================================================
// ENTERPRISE AI BUSINESS DECISION INTELLIGENCE PLATFORM
//
// ForecastChart
//
// Responsibilities:
// - Safely render AI demand forecasts
// - Normalize multiple backend field names
// - Support forecast + actual + confidence bounds
// - Prevent chart crashes
// - Reduce crowded date labels
// - Preserve backend values
// =====================================================


// =====================================================
// SAFE NUMBER
// =====================================================

const toNumber = (value, fallback = 0) => {

    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {
        return fallback;
    }

    if (typeof value === "number") {
        return Number.isFinite(value)
            ? value
            : fallback;
    }

    if (typeof value === "boolean") {
        return value ? 1 : 0;
    }

    if (typeof value === "object") {

        const nested =
            value?.value ??
            value?.forecast ??
            value?.demand ??
            value?.prediction ??
            value?.predicted_demand ??
            value?.predictedDemand ??
            value?.yhat;

        if (nested !== undefined) {
            return toNumber(
                nested,
                fallback
            );
        }

        return fallback;
    }

    const cleaned =
        String(value)
            .replace(/,/g, "")
            .replace(/\$/g, "")
            .replace(/%/g, "")
            .trim();

    if (!cleaned) {
        return fallback;
    }

    const number = Number(cleaned);

    return Number.isFinite(number)
        ? number
        : fallback;
};


// =====================================================
// SAFE DATE
// =====================================================

const getDateValue = (item, index) => {

    if (
        !item ||
        typeof item !== "object"
    ) {
        return `Period ${index + 1}`;
    }

    const value =
        item.date ??
        item.month ??
        item.Date ??
        item.period ??
        item.ds ??
        item.timestamp ??
        item.time ??
        item.label;

    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {
        return `Period ${index + 1}`;
    }

    return String(value).trim();
};


// =====================================================
// FORECAST VALUE
// =====================================================

const getForecastValue = (item) => {

    if (typeof item === "number") {
        return item;
    }

    if (typeof item === "string") {
        return toNumber(item);
    }

    if (
        !item ||
        typeof item !== "object"
    ) {
        return 0;
    }

    return toNumber(
        item.demand ??
        item.forecast ??
        item.prediction ??
        item.predicted_demand ??
        item.predictedDemand ??
        item.yhat ??
        item.y_pred ??
        item.predicted ??
        item.value ??
        item.sales ??
        item.revenue ??
        0
    );
};


// =====================================================
// ACTUAL VALUE
// =====================================================

const getActualValue = (item) => {

    if (
        !item ||
        typeof item !== "object"
    ) {
        return null;
    }

    const value =
        item.actual ??
        item.actual_demand ??
        item.actualDemand ??
        item.actual_sales ??
        item.actualSales ??
        item.observed ??
        item.real;

    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {
        return null;
    }

    const number =
        toNumber(
            value,
            NaN
        );

    return Number.isFinite(number)
        ? Math.max(0, number)
        : null;
};


// =====================================================
// LOWER BOUND
// =====================================================

const getLowerValue = (item) => {

    if (
        !item ||
        typeof item !== "object"
    ) {
        return null;
    }

    const value =
        item.lower ??
        item.lower_bound ??
        item.lowerBound ??
        item.confidence_lower ??
        item.confidenceLower;

    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {
        return null;
    }

    const number =
        toNumber(
            value,
            NaN
        );

    return Number.isFinite(number)
        ? Math.max(0, number)
        : null;
};


// =====================================================
// UPPER BOUND
// =====================================================

const getUpperValue = (item) => {

    if (
        !item ||
        typeof item !== "object"
    ) {
        return null;
    }

    const value =
        item.upper ??
        item.upper_bound ??
        item.upperBound ??
        item.confidence_upper ??
        item.confidenceUpper;

    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {
        return null;
    }

    const number =
        toNumber(
            value,
            NaN
        );

    return Number.isFinite(number)
        ? Math.max(0, number)
        : null;
};


// =====================================================
// NORMALIZE FORECAST ITEM
// =====================================================

const normalizeForecastItem = (
    item,
    index
) => {

    if (
        typeof item === "number" ||
        typeof item === "string"
    ) {

        return {
            date: `Period ${index + 1}`,
            demand: Math.max(
                0,
                getForecastValue(item)
            ),
            actual: null,
            lower: null,
            upper: null,
        };
    }

    if (
        !item ||
        typeof item !== "object"
    ) {
        return null;
    }

    const demand =
        Math.max(
            0,
            getForecastValue(item)
        );

    return {
        ...item,

        date:
            getDateValue(
                item,
                index
            ),

        demand,

        actual:
            getActualValue(item),

        lower:
            getLowerValue(item),

        upper:
            getUpperValue(item),
    };
};


// =====================================================
// FORMAT NUMBER
// =====================================================

const formatNumber = (value) => {

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


// =====================================================
// FULL NUMBER
// =====================================================

const formatFullNumber = (value) => {

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


// =====================================================
// DATE PARSER
// =====================================================

const parseDate = (value) => {

    if (!value) {
        return null;
    }

    const stringValue =
        String(value).trim();

    if (
        /^\d{4}-\d{2}-\d{2}/.test(
            stringValue
        )
    ) {

        const date =
            new Date(
                `${stringValue.substring(
                    0,
                    10
                )}T00:00:00`
            );

        return Number.isNaN(
            date.getTime()
        )
            ? null
            : date;
    }

    const parsed =
        new Date(stringValue);

    return Number.isNaN(
        parsed.getTime()
    )
        ? null
        : parsed;
};


// =====================================================
// FORMAT X AXIS DATE
//
// Examples:
// 2024-04-01 -> Apr 24
// 2024-08-01 -> Aug 24
// 2024-12-01 -> Dec 24
//
// Period labels remain unchanged.
// =====================================================

const formatDate = (value) => {

    if (!value) {
        return "";
    }

    const stringValue =
        String(value).trim();

    const date =
        parseDate(stringValue);

    if (date) {

        return new Intl.DateTimeFormat(
            "en-US",
            {
                month: "short",
                year: "2-digit",
            }
        ).format(date);
    }

    if (
        stringValue.length > 18
    ) {

        return (
            stringValue.substring(
                0,
                15
            ) +
            "..."
        );
    }

    return stringValue;
};


// =====================================================
// FORMAT TOOLTIP DATE
// =====================================================

const formatTooltipDate = (value) => {

    if (!value) {
        return "";
    }

    const stringValue =
        String(value).trim();

    const date =
        parseDate(stringValue);

    if (date) {

        return new Intl.DateTimeFormat(
            "en-US",
            {
                month: "short",
                day: "numeric",
                year: "numeric",
            }
        ).format(date);
    }

    return stringValue;
};


// =====================================================
// CUSTOM TOOLTIP
// =====================================================

const CustomTooltip = ({
    active,
    payload,
    label,
}) => {

    if (
        !active ||
        !Array.isArray(payload) ||
        payload.length === 0
    ) {
        return null;
    }

    return (
        <div
            className="
                bg-slate-950
                border
                border-slate-700
                rounded-lg
                p-3
                shadow-xl
                min-w-[190px]
            "
        >

            <p
                className="
                    text-slate-300
                    text-sm
                    font-medium
                    mb-2
                "
            >
                {formatTooltipDate(label)}
            </p>

            <div
                className="
                    space-y-1.5
                "
            >

                {payload.map(
                    (
                        entry,
                        index
                    ) => {

                        const value =
                            entry?.value;

                        if (
                            value === null ||
                            value === undefined
                        ) {
                            return null;
                        }

                        return (
                            <div
                                key={
                                    `${entry?.dataKey ?? "value"}-${index}`
                                }
                                className="
                                    flex
                                    justify-between
                                    items-center
                                    gap-5
                                    text-sm
                                "
                            >

                                <span
                                    className="
                                        text-slate-400
                                    "
                                >
                                    {entry?.name ??
                                        "Value"}
                                </span>

                                <span
                                    className="
                                        text-white
                                        font-semibold
                                    "
                                >
                                    {formatFullNumber(
                                        value
                                    )}
                                </span>

                            </div>
                        );
                    }
                )}

            </div>

        </div>
    );
};


// =====================================================
// FORECAST CHART
// =====================================================

export default function ForecastChart({
    data = [],
}) {

    // =================================================
    // NORMALIZE DATA
    // =================================================

    const chartData =
        Array.isArray(data)
            ? data
                .map(
                    (
                        item,
                        index
                    ) =>
                        normalizeForecastItem(
                            item,
                            index
                        )
                )
                .filter(Boolean)
            : [];


    // =================================================
    // DATA FLAGS
    // =================================================

    const hasActualData =
        chartData.some(
            (item) =>
                item.actual !== null &&
                Number.isFinite(
                    item.actual
                )
        );


    const hasLowerData =
        chartData.some(
            (item) =>
                item.lower !== null &&
                Number.isFinite(
                    item.lower
                )
        );


    const hasUpperData =
        chartData.some(
            (item) =>
                item.upper !== null &&
                Number.isFinite(
                    item.upper
                )
        );


    const hasConfidenceData =
        hasLowerData ||
        hasUpperData;


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
                    shadow-lg
                "
            >

                <div
                    className="
                        flex
                        justify-between
                        items-center
                        mb-4
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
                            AI Demand Forecast
                        </h2>

                        <p
                            className="
                                text-slate-400
                                text-sm
                                mt-1
                            "
                        >
                            Predicted demand over time
                        </p>

                    </div>

                </div>

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
                            "
                        >
                            No forecast data available
                        </p>

                        <p
                            className="
                                text-slate-600
                                text-xs
                                mt-2
                            "
                        >
                            Forecast results will appear
                            here when the AI model generates
                            predictions.
                        </p>

                    </div>

                </div>

            </div>
        );
    }


    // =================================================
    // X-AXIS LABEL INTERVAL
    //
    // Instead of displaying every date:
    //
    // 04-01 08-01 12-01 04-01 ...
    //
    // display a manageable number of labels.
    // =================================================

    const labelInterval =
        chartData.length <= 8
            ? 0
            : chartData.length <= 16
                ? 1
                : chartData.length <= 30
                    ? 2
                    : Math.ceil(
                        chartData.length / 10
                    ) - 1;


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
                        AI Demand Forecast
                    </h2>

                    <p
                        className="
                            text-slate-400
                            text-sm
                            mt-1
                        "
                    >
                        Predicted demand over time
                    </p>

                </div>

                <div
                    className="
                        text-blue-400
                        text-sm
                        font-medium
                    "
                >
                    AI Forecast
                </div>

            </div>


            {/* =========================================
                CHART
            ========================================= */}

            <div
                className="
                    w-full
                    h-[350px]
                "
            >

                <ResponsiveContainer
                    width="100%"
                    height="100%"
                >

                    <LineChart
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


                        {/* =================================
                            X AXIS
                        ================================= */}

                        <XAxis
                            dataKey="date"
                            stroke="#94a3b8"
                            tick={{
                                fill: "#94a3b8",
                                fontSize: 11,
                            }}
                            tickFormatter={
                                formatDate
                            }
                            interval={
                                labelInterval
                            }
                            minTickGap={30}
                            height={35}
                        />


                        {/* =================================
                            Y AXIS
                        ================================= */}

                        <YAxis
                            stroke="#94a3b8"
                            tick={{
                                fill: "#94a3b8",
                                fontSize: 11,
                            }}
                            tickFormatter={
                                formatNumber
                            }
                            width={55}
                        />


                        {/* =================================
                            TOOLTIP
                        ================================= */}

                        <Tooltip
                            content={
                                <CustomTooltip />
                            }
                        />


                        {/* =================================
                            LEGEND
                        ================================= */}

                        {(hasActualData ||
                            hasConfidenceData) && (

                            <Legend
                                verticalAlign="top"
                                height={32}
                            />

                        )}


                        {/* =================================
                            AI FORECAST
                        ================================= */}

                        <Line
                            type="monotone"
                            dataKey="demand"
                            name="AI Forecast"
                            stroke="#2563eb"
                            strokeWidth={3}
                            dot={false}
                            activeDot={{
                                r: 5,
                            }}
                            connectNulls
                        />


                        {/* =================================
                            ACTUAL DEMAND
                        ================================= */}

                        {hasActualData && (

                            <Line
                                type="monotone"
                                dataKey="actual"
                                name="Actual Demand"
                                stroke="#22c55e"
                                strokeWidth={2.5}
                                dot={false}
                                activeDot={{
                                    r: 5,
                                }}
                                connectNulls
                            />

                        )}


                        {/* =================================
                            LOWER BOUND
                        ================================= */}

                        {hasLowerData && (

                            <Line
                                type="monotone"
                                dataKey="lower"
                                name="Lower Bound"
                                stroke="#64748b"
                                strokeWidth={1}
                                strokeDasharray="5 5"
                                dot={false}
                                connectNulls
                            />

                        )}


                        {/* =================================
                            UPPER BOUND
                        ================================= */}

                        {hasUpperData && (

                            <Line
                                type="monotone"
                                dataKey="upper"
                                name="Upper Bound"
                                stroke="#94a3b8"
                                strokeWidth={1}
                                strokeDasharray="5 5"
                                dot={false}
                                connectNulls
                            />

                        )}

                    </LineChart>

                </ResponsiveContainer>

            </div>

        </div>
    );
}


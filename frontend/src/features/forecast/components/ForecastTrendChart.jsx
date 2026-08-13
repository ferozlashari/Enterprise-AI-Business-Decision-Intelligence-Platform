
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
// SAFE NUMBER
// =====================================================

const toNumber = (value) => {
    const number = Number(value);

    return Number.isFinite(number)
        ? number
        : null;
};

// =====================================================
// FORMAT DATE
// =====================================================

const formatDate = (value) => {
    if (!value) {
        return "—";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return String(value);
    }

    return date.toLocaleDateString(
        undefined,
        {
            day: "numeric",
            month: "short",
            year: "numeric",
        }
    );
};

// =====================================================
// FORMAT VALUE
// =====================================================

const formatValue = (value) => {
    const number = toNumber(value);

    if (number === null) {
        return "—";
    }

    return number.toLocaleString(
        undefined,
        {
            maximumFractionDigits: 0,
        }
    );
};

// =====================================================
// CUSTOM TOOLTIP
//
// IMPORTANT:
// Recharts only renders this while hovering.
//
// There is NO active/default tooltip state.
// =====================================================

const ForecastTooltip = ({
    active,
    payload,
}) => {

    if (
        !active ||
        !payload ||
        payload.length === 0
    ) {
        return null;
    }

    const data =
        payload[0]?.payload;

    if (!data) {
        return null;
    }

    return (
        <div
            className="
                min-w-[220px]
                rounded-xl
                border
                border-slate-700
                bg-slate-950/95
                px-4
                py-3
                shadow-2xl
            "
        >

            {/* DATE */}

            <div
                className="
                    text-sm
                    font-semibold
                    text-white
                    mb-3
                "
            >
                {formatDate(data.date)}
            </div>


            {/* FORECAST */}

            <div
                className="
                    flex
                    items-center
                    justify-between
                    gap-6
                    mb-2
                "
            >

                <span
                    className="
                        text-sm
                        text-slate-400
                    "
                >
                    Forecast
                </span>

                <span
                    className="
                        text-sm
                        font-semibold
                        text-blue-400
                    "
                >
                    {formatValue(
                        data.forecast
                    )}
                </span>

            </div>


            {/* LOWER */}

            {data.lower !== null &&
                data.lower !== undefined && (

                <div
                    className="
                        flex
                        items-center
                        justify-between
                        gap-6
                        mb-2
                    "
                >

                    <span
                        className="
                            text-sm
                            text-slate-400
                        "
                    >
                        Lower Bound
                    </span>

                    <span
                        className="
                            text-sm
                            font-medium
                            text-slate-300
                        "
                    >
                        {formatValue(
                            data.lower
                        )}
                    </span>

                </div>

            )}


            {/* UPPER */}

            {data.upper !== null &&
                data.upper !== undefined && (

                <div
                    className="
                        flex
                        items-center
                        justify-between
                        gap-6
                    "
                >

                    <span
                        className="
                            text-sm
                            text-slate-400
                        "
                    >
                        Upper Bound
                    </span>

                    <span
                        className="
                            text-sm
                            font-medium
                            text-slate-300
                        "
                    >
                        {formatValue(
                            data.upper
                        )}
                    </span>

                </div>

            )}

        </div>
    );
};

// =====================================================
// X-AXIS DATE FORMATTER
// =====================================================

const formatXAxisDate = (value) => {

    if (!value) {
        return "";
    }

    const date = new Date(value);

    if (
        Number.isNaN(
            date.getTime()
        )
    ) {
        return "";
    }

    return date.toLocaleDateString(
        undefined,
        {
            month: "short",
            year: "numeric",
        }
    );
};

// =====================================================
// MAIN COMPONENT
// =====================================================

export default function ForecastTrendChart({
    data = [],
}) {

    // =================================================
    // SAFELY PREPARE CHART DATA
    //
    // IMPORTANT:
    // ALL POINTS ARE PRESERVED.
    // No slice.
    // No filtering to 12.
    // =================================================

    const chartData =
        Array.isArray(data)
            ? data
                .filter(
                    point =>
                        point &&
                        typeof point === "object"
                )
                .map(
                    (
                        point,
                        index
                    ) => ({

                        id:
                            point.id ??
                            index,

                        date:
                            point.date ??
                            "",

                        forecast:
                            toNumber(
                                point.forecast
                            ),

                        lower:
                            toNumber(
                                point.lower
                            ),

                        upper:
                            toNumber(
                                point.upper
                            ),

                        actual:
                            toNumber(
                                point.actual
                            ),

                    })
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
                    p-6
                "
            >

                <h2
                    className="
                        text-xl
                        font-bold
                        text-white
                    "
                >
                    Forecast Trend
                </h2>

                <p
                    className="
                        text-sm
                        text-slate-500
                        mt-2
                    "
                >
                    No forecast data is currently
                    available from the backend.
                </p>

            </div>

        );
    }


    // =================================================
    // CHART
    // =================================================

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

            {/* =========================================
                HEADER
            ========================================= */}

            <div
                className="
                    mb-5
                "
            >

                <h2
                    className="
                        text-xl
                        font-bold
                        text-white
                    "
                >
                    Forecast Trend
                </h2>

                <p
                    className="
                        text-sm
                        text-slate-500
                        mt-1
                    "
                >
                    Forecast demand with prediction
                    confidence range
                </p>

            </div>


            {/* =========================================
                CHART
            ========================================= */}

            <div
                className="
                    w-full
                    h-[420px]
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
                            stroke="rgba(148,163,184,0.12)"
                        />


                        <XAxis
                            dataKey="date"
                            tickFormatter={
                                formatXAxisDate
                            }
                            tick={{
                                fill: "#94a3b8",
                                fontSize: 12,
                            }}
                            axisLine={{
                                stroke:
                                    "rgba(148,163,184,0.2)",
                            }}
                            tickLine={false}
                            minTickGap={35}
                        />


                        <YAxis
                            tickFormatter={
                                value =>
                                    Number(
                                        value
                                    ).toLocaleString()
                            }
                            tick={{
                                fill: "#94a3b8",
                                fontSize: 12,
                            }}
                            axisLine={false}
                            tickLine={false}
                            width={70}
                        />


                        {/* =================================
                            IMPORTANT

                            Tooltip has NO active prop.

                            Therefore it is NOT permanently
                            selected.

                            It appears only on hover.
                        ================================= */}

                        <Tooltip
                            content={
                                <ForecastTooltip />
                            }
                            cursor={{
                                stroke:
                                    "rgba(148,163,184,0.35)",
                                strokeDasharray:
                                    "4 4",
                            }}
                        />


                        <Legend
                            wrapperStyle={{
                                paddingTop: "15px",
                                color: "#94a3b8",
                            }}
                        />


                        {/* =================================
                            FORECAST
                        ================================= */}

                        <Line
                            type="monotone"
                            dataKey="forecast"
                            name="Forecast"
                            stroke="#60a5fa"
                            strokeWidth={3}
                            dot={false}
                            activeDot={{
                                r: 5,
                            }}
                            connectNulls
                        />


                        {/* =================================
                            LOWER BOUND
                        ================================= */}

                        <Line
                            type="monotone"
                            dataKey="lower"
                            name="Lower Bound"
                            stroke="#64748b"
                            strokeWidth={1.5}
                            strokeDasharray="5 5"
                            dot={false}
                            activeDot={{
                                r: 4,
                            }}
                            connectNulls
                        />


                        {/* =================================
                            UPPER BOUND
                        ================================= */}

                        <Line
                            type="monotone"
                            dataKey="upper"
                            name="Upper Bound"
                            stroke="#94a3b8"
                            strokeWidth={1.5}
                            strokeDasharray="5 5"
                            dot={false}
                            activeDot={{
                                r: 4,
                            }}
                            connectNulls
                        />

                    </LineChart>

                </ResponsiveContainer>

            </div>


            {/* =========================================
                DATASET INFORMATION
            ========================================= */}

            <div
                className="
                    mt-4
                    flex
                    flex-wrap
                    items-center
                    justify-between
                    gap-3
                    text-xs
                    text-slate-500
                "
            >

                <span>
                    Showing {chartData.length} forecast
                    points from the backend
                </span>

                <span>
                    Hover over the chart to inspect
                    individual predictions
                </span>

            </div>

        </div>
    );
}



import {
    Calendar,
} from "lucide-react";


export default function ForecastTable({
    points = [],
    inventoryRecords = 0,
}) {

    // =====================================================
    // SAFE NUMBER
    // =====================================================

    const toNumberOrNull = (value) => {

        if (
            value === null ||
            value === undefined ||
            value === ""
        ) {
            return null;
        }

        const number = Number(value);

        return Number.isFinite(number)
            ? number
            : null;

    };


    // =====================================================
    // FORMAT NUMBER
    // =====================================================

    const formatNumber = (
        value,
        fallback = "—"
    ) => {

        const number =
            toNumberOrNull(value);

        if (number === null) {
            return fallback;
        }

        return number.toLocaleString(
            undefined,
            {
                maximumFractionDigits: 0,
            }
        );

    };


    // =====================================================
    // FORMAT INVENTORY RECORDS
    // =====================================================

    const formatInventoryRecords = (
        value
    ) => {

        const number =
            Number(value);

        if (
            !Number.isFinite(number)
        ) {
            return "0";
        }

        return number.toLocaleString();

    };


    // =====================================================
    // FORMAT DATE
    // =====================================================

    const formatDate = (
        value
    ) => {

        if (!value) {
            return "—";
        }

        const date =
            new Date(value);

        if (
            Number.isNaN(
                date.getTime()
            )
        ) {
            return String(value);
        }

        return date.toLocaleDateString(
            undefined,
            {
                year: "numeric",
                month: "short",
                day: "numeric",
            }
        );

    };


    // =====================================================
    // GET DATE
    // =====================================================

    const getDate = (
        point
    ) => {

        return (
            point?.date
            ??
            point?.ds
            ??
            point?.datetime
            ??
            point?.timestamp
            ??
            ""
        );

    };


    // =====================================================
    // GET FORECAST
    // =====================================================

    const getForecastValue = (
        point
    ) => {

        return (
            point?.forecast
            ??
            point?.demand
            ??
            point?.predicted_demand
            ??
            point?.prediction
            ??
            point?.predicted_sales
            ??
            point?.yhat
            ??
            null
        );

    };


    // =====================================================
    // GET LOWER BOUND
    // =====================================================

    const getLowerValue = (
        point
    ) => {

        return (
            point?.lower
            ??
            point?.lower_bound
            ??
            point?.yhat_lower
            ??
            point?.forecast_lower
            ??
            point?.prediction_lower
            ??
            null
        );

    };


    // =====================================================
    // GET UPPER BOUND
    // =====================================================

    const getUpperValue = (
        point
    ) => {

        return (
            point?.upper
            ??
            point?.upper_bound
            ??
            point?.yhat_upper
            ??
            point?.forecast_upper
            ??
            point?.prediction_upper
            ??
            null
        );

    };


    // =====================================================
    // NORMALIZE INPUT
    // =====================================================

    const normalizedPoints =
        Array.isArray(points)

            ? points

                .filter(
                    point =>
                        point &&
                        typeof point === "object"
                )

                .map(
                    (
                        point,
                        index
                    ) => {

                        const date =
                            getDate(point);

                        const parsedDate =
                            date
                                ? new Date(date)
                                : null;

                        const timestamp =
                            parsedDate &&
                            !Number.isNaN(
                                parsedDate.getTime()
                            )
                                ? parsedDate.getTime()
                                : null;

                        return {

                            ...point,

                            _tableIndex:
                                index,

                            _dateTimestamp:
                                timestamp,

                        };

                    }
                )

            : [];


    // =====================================================
    // DETECT WHETHER BACKEND PROVIDES FORECAST TYPE
    // =====================================================

    const hasForecastType =
        normalizedPoints.some(
            point =>
                point?.forecast_type !== undefined &&
                point?.forecast_type !== null
        );


    // =====================================================
    // SELECT FUTURE FORECAST POINTS
    //
    // Backend provides:
    //
    // historical:
    //     2014 → 2017
    //
    // future:
    //     2018 → 2018
    //
    // Only future records should appear here.
    // =====================================================

    let forecastPoints;


    if (hasForecastType) {

        forecastPoints =
            normalizedPoints.filter(
                point =>
                    String(
                        point?.forecast_type
                    ).toLowerCase()
                    ===
                    "future"
            );

    }

    else {

        /*
         * Backward compatibility:
         *
         * If an older backend does not provide
         * forecast_type, use the latest 12 points.
         */

        forecastPoints =
            [...normalizedPoints]
                .sort(
                    (
                        a,
                        b
                    ) => {

                        if (
                            a._dateTimestamp !== null &&
                            b._dateTimestamp !== null
                        ) {

                            return (
                                a._dateTimestamp -
                                b._dateTimestamp
                            );

                        }

                        if (
                            a._dateTimestamp !== null
                        ) {

                            return -1;

                        }

                        if (
                            b._dateTimestamp !== null
                        ) {

                            return 1;

                        }

                        return (
                            a._tableIndex -
                            b._tableIndex
                        );

                    }
                )
                .slice(-12);

    }


    // =====================================================
    // SORT FUTURE FORECAST
    //
    // Oldest → Newest
    // =====================================================

    const safePoints =
        forecastPoints
            .sort(
                (
                    a,
                    b
                ) => {

                    if (
                        a._dateTimestamp !== null &&
                        b._dateTimestamp !== null
                    ) {

                        return (
                            a._dateTimestamp -
                            b._dateTimestamp
                        );

                    }

                    if (
                        a._dateTimestamp !== null
                    ) {

                        return -1;

                    }

                    if (
                        b._dateTimestamp !== null
                    ) {

                        return 1;

                    }

                    return (
                        a._tableIndex -
                        b._tableIndex
                    );

                }
            );


    // =====================================================
    // FORECAST COUNT
    // =====================================================

    const forecastCount =
        safePoints.length;


    // =====================================================
    // TABLE
    // =====================================================

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

            {/* =================================================
                HEADER
            ================================================= */}

            <div
                className="
                    flex
                    items-center
                    gap-2
                    mb-4
                "
            >

                <Calendar
                    size={20}
                    className="text-emerald-400"
                />


                <div>

                    <h2
                        className="
                            text-white
                            font-bold
                            text-xl
                        "
                    >

                        Projected Forecast Horizon

                    </h2>


                    <p
                        className="
                            text-slate-500
                            text-xs
                            mt-0.5
                        "
                    >

                        {forecastCount} future monthly
                        predictions with confidence bounds

                    </p>

                </div>

            </div>


            {/* =================================================
                FORECAST INFORMATION
            ================================================= */}

            {safePoints.length > 0 && (

                <div
                    className="
                        mb-4
                        flex
                        flex-wrap
                        gap-3
                    "
                >

                    <div
                        className="
                            bg-slate-800/60
                            border
                            border-slate-700
                            rounded-lg
                            px-3
                            py-2
                        "
                    >

                        <span
                            className="
                                text-slate-500
                                text-xs
                            "
                        >

                            Forecast Points

                        </span>


                        <div
                            className="
                                text-white
                                font-semibold
                                mt-0.5
                            "
                        >

                            {forecastCount}

                        </div>

                    </div>


                    <div
                        className="
                            bg-slate-800/60
                            border
                            border-slate-700
                            rounded-lg
                            px-3
                            py-2
                        "
                    >

                        <span
                            className="
                                text-slate-500
                                text-xs
                            "
                        >

                            Forecast Start

                        </span>


                        <div
                            className="
                                text-white
                                font-semibold
                                mt-0.5
                            "
                        >

                            {formatDate(
                                getDate(
                                    safePoints[0]
                                )
                            )}

                        </div>

                    </div>


                    <div
                        className="
                            bg-slate-800/60
                            border
                            border-slate-700
                            rounded-lg
                            px-3
                            py-2
                        "
                    >

                        <span
                            className="
                                text-slate-500
                                text-xs
                            "
                        >

                            Forecast End

                        </span>


                        <div
                            className="
                                text-white
                                font-semibold
                                mt-0.5
                            "
                        >

                            {formatDate(
                                getDate(
                                    safePoints[
                                        safePoints.length - 1
                                    ]
                                )
                            )}

                        </div>

                    </div>

                </div>

            )}


            {/* =================================================
                EMPTY STATE
            ================================================= */}

            {safePoints.length === 0 ? (

                <div
                    className="
                        text-slate-500
                        text-sm
                        text-center
                        py-8
                    "
                >

                    No future forecast points available.

                </div>

            ) : (

                <div
                    className="
                        overflow-x-auto
                    "
                >

                    <table
                        className="
                            w-full
                            min-w-[600px]
                            text-sm
                            text-left
                        "
                    >

                        {/* =================================================
                            HEADER
                        ================================================= */}

                        <thead>

                            <tr
                                className="
                                    text-slate-400
                                    border-b
                                    border-slate-800
                                "
                            >

                                <th
                                    className="
                                        py-3
                                        px-3
                                        font-medium
                                    "
                                >

                                    Date

                                </th>


                                <th
                                    className="
                                        py-3
                                        px-3
                                        font-medium
                                    "
                                >

                                    Predicted Demand

                                </th>


                                <th
                                    className="
                                        py-3
                                        px-3
                                        font-medium
                                    "
                                >

                                    Lower Bound

                                </th>


                                <th
                                    className="
                                        py-3
                                        px-3
                                        font-medium
                                    "
                                >

                                    Upper Bound

                                </th>

                            </tr>

                        </thead>


                        {/* =================================================
                            BODY
                        ================================================= */}

                        <tbody>

                            {safePoints.map(
                                (
                                    point,
                                    index
                                ) => {

                                    const date =
                                        getDate(
                                            point
                                        );

                                    const forecast =
                                        getForecastValue(
                                            point
                                        );

                                    const lower =
                                        getLowerValue(
                                            point
                                        );

                                    const upper =
                                        getUpperValue(
                                            point
                                        );

                                    const rowKey =
                                        point?.id
                                        ??
                                        `${date || "forecast"}-${index}`;


                                    return (

                                        <tr
                                            key={rowKey}
                                            className="
                                                border-b
                                                border-slate-800/60
                                                hover:bg-slate-800/30
                                                transition
                                            "
                                        >

                                            {/* DATE */}

                                            <td
                                                className="
                                                    py-3
                                                    px-3
                                                    text-slate-200
                                                    whitespace-nowrap
                                                "
                                            >

                                                {formatDate(
                                                    date
                                                )}

                                            </td>


                                            {/* FORECAST */}

                                            <td
                                                className="
                                                    py-3
                                                    px-3
                                                    text-blue-400
                                                    font-semibold
                                                    whitespace-nowrap
                                                "
                                            >

                                                {formatNumber(
                                                    forecast
                                                )}

                                            </td>


                                            {/* LOWER */}

                                            <td
                                                className="
                                                    py-3
                                                    px-3
                                                    text-orange-400
                                                    whitespace-nowrap
                                                "
                                            >

                                                {formatNumber(
                                                    lower
                                                )}

                                            </td>


                                            {/* UPPER */}

                                            <td
                                                className="
                                                    py-3
                                                    px-3
                                                    text-purple-400
                                                    whitespace-nowrap
                                                "
                                            >

                                                {formatNumber(
                                                    upper
                                                )}

                                            </td>

                                        </tr>

                                    );

                                }
                            )}

                        </tbody>

                    </table>

                </div>

            )}


            {/* =================================================
                INVENTORY INFORMATION
            ================================================= */}

            {Number(
                inventoryRecords
            ) > 0 && (

                <div
                    className="
                        mt-4
                        pt-4
                        border-t
                        border-slate-800
                    "
                >

                    <p
                        className="
                            text-slate-500
                            text-xs
                        "
                    >

                        Inventory forecast covers{" "}

                        <span
                            className="
                                text-slate-300
                                font-semibold
                            "
                        >

                            {formatInventoryRecords(
                                inventoryRecords
                            )}

                        </span>{" "}

                        product records.

                    </p>

                </div>

            )}

        </div>

    );

}


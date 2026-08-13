
import {
    useCallback,
    useEffect,
    useMemo,
    useState,
} from "react";

import {
    Database,
    Loader2,
    RefreshCcw,
    TrendingUp,
    AlertTriangle,
} from "lucide-react";

import {
    fetchSalesForecast,
    fetchInventoryForecast,
} from "./forecast.api";

import ForecastStats from "./components/ForecastStats";
import ForecastTrendChart from "./components/ForecastTrendChart";
import ForecastTable from "./components/ForecastTable";


// =====================================================
// CONFIGURATION
// =====================================================

const FORECAST_YEAR = 2018;
const FUTURE_FORECAST_MONTHS = 12;


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
// DATE HELPERS
// =====================================================

const getPointDate = (point) => {

    if (
        !point ||
        typeof point !== "object"
    ) {
        return null;
    }

    return (
        point.date ??
        point.ds ??
        point.datetime ??
        point.timestamp ??
        point.Date ??
        null
    );
};


const parseDate = (value) => {

    if (!value) {
        return null;
    }

    const date = new Date(value);

    if (
        Number.isNaN(
            date.getTime()
        )
    ) {
        return null;
    }

    return date;
};


const formatDate = (value) => {

    const date = parseDate(value);

    if (!date) {
        return "—";
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
// FORECAST VALUE HELPERS
// =====================================================

const getForecastValue = (point) => {

    if (
        !point ||
        typeof point !== "object"
    ) {
        return null;
    }

    return toNumberOrNull(
        point.forecast ??
        point.demand ??
        point.predicted_demand ??
        point.predicted_sales ??
        point.prediction ??
        point.yhat ??
        point.yhat_forecast
    );
};


const getActualValue = (point) => {

    if (
        !point ||
        typeof point !== "object"
    ) {
        return null;
    }

    return toNumberOrNull(
        point.actual ??
        point.actual_demand ??
        point.actual_sales ??
        point.y ??
        null
    );
};


const getLowerValue = (point) => {

    if (
        !point ||
        typeof point !== "object"
    ) {
        return null;
    }

    return toNumberOrNull(
        point.lower ??
        point.lower_bound ??
        point.yhat_lower ??
        point.forecast_lower ??
        point.prediction_lower
    );
};


const getUpperValue = (point) => {

    if (
        !point ||
        typeof point !== "object"
    ) {
        return null;
    }

    return toNumberOrNull(
        point.upper ??
        point.upper_bound ??
        point.yhat_upper ??
        point.forecast_upper ??
        point.prediction_upper
    );
};


// =====================================================
// RESPONSE NORMALIZATION
// =====================================================

const normalizeSalesResponse = (
    response
) => {

    if (
        !response ||
        typeof response !== "object"
    ) {
        return {};
    }

    if (
        response.sales_forecast &&
        typeof response.sales_forecast === "object"
    ) {
        return response.sales_forecast;
    }

    if (
        response.data &&
        typeof response.data === "object" &&
        !Array.isArray(response.data)
    ) {
        return response.data;
    }

    return response;
};


const normalizeInventoryResponse = (
    response
) => {

    if (
        !response ||
        typeof response !== "object"
    ) {
        return {};
    }

    if (
        response.inventory_forecast &&
        typeof response.inventory_forecast === "object"
    ) {
        return response.inventory_forecast;
    }

    if (
        response.data &&
        typeof response.data === "object" &&
        !Array.isArray(response.data)
    ) {
        return response.data;
    }

    return response;
};


// =====================================================
// EXTRACT FORECAST POINTS
// =====================================================

const extractForecastPoints = (
    response,
    normalized
) => {

    const candidates = [

        normalized?.forecast,

        normalized?.predictions,

        normalized?.forecast_data,

        normalized?.points,

        response?.forecast,

        response?.predictions,

        response?.forecast_data,

        response?.points,

    ];

    for (
        const candidate of candidates
    ) {

        if (
            Array.isArray(candidate)
        ) {
            return candidate;
        }
    }

    return [];
};


// =====================================================
// EXTRACT INVENTORY RECORD COUNT
// =====================================================

const extractInventoryRecords = (
    response
) => {

    const inventory =
        normalizeInventoryResponse(
            response
        );

    if (
        !inventory ||
        typeof inventory !== "object"
    ) {
        return 0;
    }


    const explicitCount = Number(
        inventory.records ??
        inventory.count ??
        inventory.total_records ??
        inventory.inventory_records
    );


    if (
        Number.isFinite(
            explicitCount
        )
    ) {
        return explicitCount;
    }


    const arrays = [

        inventory.inventory,

        inventory.forecast,

        inventory.predictions,

        inventory.data,

    ];


    for (
        const value of arrays
    ) {

        if (
            Array.isArray(value)
        ) {
            return value.length;
        }
    }


    return 0;
};


// =====================================================
// ERROR MESSAGE
// =====================================================

const getErrorMessage = (
    error
) => {

    const detail =
        error?.response?.data?.detail;


    if (
        Array.isArray(detail)
    ) {

        return detail
            .map(
                item =>
                    item?.msg
            )
            .filter(Boolean)
            .join(", ");
    }


    if (
        typeof detail === "string"
    ) {
        return detail;
    }


    return (
        error?.message ??
        "Unable to load forecast intelligence."
    );
};


// =====================================================
// MAIN COMPONENT
// =====================================================

export default function Forecast() {

    // =================================================
    // STATE
    // =================================================

    const [
        forecast,
        setForecast,
    ] = useState([]);


    const [
        model,
        setModel,
    ] = useState(
        "Facebook Prophet"
    );


    const [
        inventoryRecords,
        setInventoryRecords,
    ] = useState(0);


    const [
        loading,
        setLoading,
    ] = useState(true);


    const [
        refreshing,
        setRefreshing,
    ] = useState(false);


    const [
        error,
        setError,
    ] = useState(null);


    // =================================================
    // LOAD FORECAST
    // =================================================

    const loadForecast = useCallback(
        async (
            isRefresh = false
        ) => {

            try {

                if (isRefresh) {
                    setRefreshing(true);
                } else {
                    setLoading(true);
                }


                setError(null);


                // =====================================
                // SALES FORECAST
                // =====================================

                const salesResponse =
                    await fetchSalesForecast();


                console.log(
                    "FORECAST API RESPONSE:",
                    salesResponse
                );


                const salesForecast =
                    normalizeSalesResponse(
                        salesResponse
                    );


                // =====================================
                // ALL BACKEND POINTS
                //
                // IMPORTANT:
                // Never slice here.
                //
                // Backend returns 60 points.
                // =====================================

                const points =
                    extractForecastPoints(
                        salesResponse,
                        salesForecast
                    );


                if (
                    !Array.isArray(points) ||
                    points.length === 0
                ) {

                    throw new Error(
                        "Forecast service returned no forecast points."
                    );
                }


                // =====================================
                // MODEL
                // =====================================

                const detectedModel =
                    salesForecast?.model ??
                    salesForecast?.model_name ??
                    salesForecast?.algorithm ??
                    salesForecast?.model_type ??
                    "Facebook Prophet";


                setModel(
                    String(
                        detectedModel
                    )
                );


                // =====================================
                // SAVE REAL BACKEND DATA
                // =====================================

                setForecast(
                    points
                );


                // =====================================
                // INVENTORY SERVICE
                // =====================================

                try {

                    const inventoryResponse =
                        await fetchInventoryForecast();


                    console.log(
                        "INVENTORY API RESPONSE:",
                        inventoryResponse
                    );


                    setInventoryRecords(
                        extractInventoryRecords(
                            inventoryResponse
                        )
                    );

                } catch (
                    inventoryError
                ) {

                    console.warn(
                        "Inventory forecast unavailable:",
                        inventoryError
                    );


                    setInventoryRecords(0);
                }


                // =====================================
                // BACKEND ERROR STATUS
                // =====================================

                if (
                    salesForecast?.status ===
                    "error"
                ) {

                    setError(
                        salesForecast?.message ??
                        "Forecast service returned an error."
                    );
                }

            } catch (err) {

                console.error(
                    "FORECAST LOADING ERROR:",
                    err
                );


                setError(
                    getErrorMessage(
                        err
                    )
                );

            } finally {

                setLoading(false);
                setRefreshing(false);
            }

        },
        []
    );


    // =================================================
    // INITIAL LOAD
    // =================================================

    useEffect(() => {

        loadForecast(false);

    }, [
        loadForecast,
    ]);


    // =================================================
    // NORMALIZE ALL FORECAST DATA
    //
    // THIS IS THE DATASET USED BY THE CHART.
    //
    // Expected:
    //
    // 2014 → 2015 → 2016 → 2017 → 2018
    //
    // TOTAL = 60 POINTS
    // =================================================

    const chartData = useMemo(() => {

        if (
            !Array.isArray(forecast)
        ) {
            return [];
        }


        const normalized =
            forecast
                .map(
                    (
                        point,
                        index
                    ) => {

                        const rawDate =
                            getPointDate(
                                point
                            );


                        const parsedDate =
                            parseDate(
                                rawDate
                            );


                        return {

                            id:
                                point?.id ??
                                index,


                            date:
                                rawDate
                                    ? String(
                                        rawDate
                                    )
                                    : "",


                            timestamp:
                                parsedDate
                                    ? parsedDate.getTime()
                                    : null,


                            forecast:
                                getForecastValue(
                                    point
                                ),


                            actual:
                                getActualValue(
                                    point
                                ),


                            lower:
                                getLowerValue(
                                    point
                                ),


                            upper:
                                getUpperValue(
                                    point
                                ),

                        };
                    }
                )
                .filter(Boolean);


        // =============================================
        // OLDEST → NEWEST
        // =============================================

        normalized.sort(
            (
                a,
                b
            ) => {

                if (
                    a.timestamp === null &&
                    b.timestamp === null
                ) {
                    return 0;
                }


                if (
                    a.timestamp === null
                ) {
                    return 1;
                }


                if (
                    b.timestamp === null
                ) {
                    return -1;
                }


                return (
                    a.timestamp -
                    b.timestamp
                );
            }
        );


        return normalized;

    }, [
        forecast,
    ]);


    // =================================================
    // HISTORICAL DATA
    //
    // 2014 → 2017
    // =================================================

    const historicalForecast =
        useMemo(
            () => {

                return chartData.filter(
                    item => {

                        if (
                            item.timestamp === null
                        ) {
                            return false;
                        }


                        const year =
                            new Date(
                                item.timestamp
                            ).getFullYear();


                        return (
                            year <
                            FORECAST_YEAR
                        );
                    }
                );

            },
            [
                chartData,
            ]
        );


    // =================================================
    // FUTURE FORECAST
    //
    // 2018 ONLY
    //
    // Expected = 12 points
    // =================================================

    const futureForecast =
        useMemo(
            () => {

                const future =
                    chartData.filter(
                        item => {

                            if (
                                item.timestamp === null
                            ) {
                                return false;
                            }


                            const year =
                                new Date(
                                    item.timestamp
                                ).getFullYear();


                            return (
                                year ===
                                FORECAST_YEAR
                            );
                        }
                    );


                if (
                    future.length >
                    FUTURE_FORECAST_MONTHS
                ) {

                    return future.slice(
                        -FUTURE_FORECAST_MONTHS
                    );
                }


                return future;

            },
            [
                chartData,
            ]
        );


    // =================================================
    // LATEST FUTURE FORECAST
    // =================================================

    const latestForecast =
        futureForecast.length > 0
            ? futureForecast[
                futureForecast.length - 1
            ]
            : null;


    // =================================================
    // FUTURE AVERAGE
    // =================================================

    const averageFutureForecast =
        useMemo(
            () => {

                const values =
                    futureForecast
                        .map(
                            item =>
                                Number(
                                    item.forecast
                                )
                        )
                        .filter(
                            Number.isFinite
                        );


                if (
                    values.length === 0
                ) {
                    return 0;
                }


                return (
                    values.reduce(
                        (
                            total,
                            value
                        ) =>
                            total + value,
                        0
                    ) /
                    values.length
                );

            },
            [
                futureForecast,
            ]
        );


    // =================================================
    // ALL DATA AVERAGE
    // =================================================

    const averageAllForecast =
        useMemo(
            () => {

                const values =
                    chartData
                        .map(
                            item =>
                                Number(
                                    item.forecast
                                )
                        )
                        .filter(
                            Number.isFinite
                        );


                if (
                    values.length === 0
                ) {
                    return 0;
                }


                return (
                    values.reduce(
                        (
                            total,
                            value
                        ) =>
                            total + value,
                        0
                    ) /
                    values.length
                );

            },
            [
                chartData,
            ]
        );


    // =================================================
    // DATE RANGES
    // =================================================

    const historicalStart =
        historicalForecast[0] ??
        null;


    const historicalEnd =
        historicalForecast[
            historicalForecast.length - 1
        ] ??
        null;


    const futureStart =
        futureForecast[0] ??
        null;


    const futureEnd =
        futureForecast[
            futureForecast.length - 1
        ] ??
        null;


    // =================================================
    // DATA INTEGRITY
    // =================================================

    const dataIntegrity =
        chartData.length === 60 &&
        historicalForecast.length === 48 &&
        futureForecast.length === 12;


    // =================================================
    // LOADING SCREEN
    // =================================================

    if (loading) {

        return (

            <div
                className="
                    min-h-[70vh]
                    flex
                    items-center
                    justify-center
                    text-white
                "
            >

                <div
                    className="
                        flex
                        items-center
                        gap-3
                        text-slate-300
                    "
                >

                    <Loader2
                        size={24}
                        className="
                            animate-spin
                            text-blue-400
                        "
                    />

                    <span>
                        Loading demand forecast...
                    </span>

                </div>

            </div>
        );
    }


    // =================================================
    // MAIN PAGE
    // =================================================

    return (

        <div
            className="
                p-6
                text-white
                space-y-6
            "
        >

            {/* =========================================
                HEADER
            ========================================= */}

            <div
                className="
                    flex
                    flex-col
                    lg:flex-row
                    lg:items-center
                    lg:justify-between
                    gap-4
                "
            >

                <div>

                    <div
                        className="
                            flex
                            items-center
                            gap-3
                        "
                    >

                        <div
                            className="
                                p-2
                                rounded-lg
                                bg-blue-500/10
                            "
                        >

                            <TrendingUp
                                size={26}
                                className="
                                    text-blue-400
                                "
                            />

                        </div>


                        <div>

                            <h1
                                className="
                                    text-3xl
                                    font-bold
                                "
                            >
                                Demand Forecasting
                            </h1>


                            <p
                                className="
                                    text-slate-400
                                    mt-1
                                "
                            >
                                AI-powered sales demand
                                forecasting using{" "}
                                {model}.
                            </p>

                        </div>

                    </div>

                </div>


                <button
                    type="button"
                    onClick={() =>
                        loadForecast(true)
                    }
                    disabled={refreshing}
                    className="
                        flex
                        items-center
                        justify-center
                        gap-2
                        bg-blue-600
                        hover:bg-blue-700
                        disabled:opacity-60
                        disabled:cursor-not-allowed
                        px-5
                        py-2.5
                        rounded-lg
                        text-white
                        font-semibold
                        transition
                    "
                >

                    <RefreshCcw
                        size={18}
                        className={
                            refreshing
                                ? "animate-spin"
                                : ""
                        }
                    />

                    {refreshing
                        ? "Refreshing..."
                        : "Refresh"}

                </button>

            </div>


            {/* =========================================
                ERROR
            ========================================= */}

            {error && (

                <div
                    className="
                        flex
                        items-start
                        gap-3
                        bg-red-500/10
                        border
                        border-red-500/30
                        rounded-xl
                        px-4
                        py-4
                        text-red-400
                    "
                >

                    <AlertTriangle
                        size={20}
                        className="
                            mt-0.5
                            shrink-0
                        "
                    />

                    <div>

                        <p
                            className="
                                font-semibold
                            "
                        >
                            Forecast Service Error
                        </p>

                        <p
                            className="
                                text-sm
                                mt-1
                                text-red-300
                            "
                        >
                            {error}
                        </p>

                    </div>

                </div>

            )}


            {/* =========================================
                DATASET SUMMARY
            ========================================= */}

            <section
                className="
                    bg-slate-900
                    border
                    border-slate-800
                    rounded-xl
                    p-5
                "
            >

                <div
                    className="
                        flex
                        items-center
                        gap-3
                        mb-5
                    "
                >

                    <Database
                        size={21}
                        className="
                            text-purple-400
                        "
                    />


                    <div>

                        <h2
                            className="
                                text-xl
                                font-bold
                            "
                        >
                            Forecast Dataset Summary
                        </h2>


                        <p
                            className="
                                text-xs
                                text-slate-500
                                mt-1
                            "
                        >
                            Live forecast data returned by
                            the backend forecasting service.
                        </p>

                    </div>

                </div>


                <div
                    className="
                        grid
                        grid-cols-1
                        sm:grid-cols-2
                        lg:grid-cols-4
                        gap-4
                    "
                >

                    {/* TOTAL */}

                    <div
                        className="
                            bg-slate-800/50
                            border
                            border-slate-800
                            rounded-lg
                            p-4
                        "
                    >

                        <p
                            className="
                                text-sm
                                text-slate-400
                            "
                        >
                            Total Forecast Points
                        </p>


                        <p
                            className="
                                text-2xl
                                font-bold
                                mt-1
                            "
                        >
                            {chartData.length}
                        </p>


                        <p
                            className="
                                text-xs
                                text-slate-500
                                mt-1
                            "
                        >
                            Complete backend dataset
                        </p>

                    </div>


                    {/* HISTORICAL */}

                    <div
                        className="
                            bg-slate-800/50
                            border
                            border-slate-800
                            rounded-lg
                            p-4
                        "
                    >

                        <p
                            className="
                                text-sm
                                text-slate-400
                            "
                        >
                            Historical Points
                        </p>


                        <p
                            className="
                                text-2xl
                                font-bold
                                mt-1
                            "
                        >
                            {historicalForecast.length}
                        </p>


                        <p
                            className="
                                text-xs
                                text-slate-500
                                mt-1
                            "
                        >

                            {historicalStart &&
                            historicalEnd
                                ? `${formatDate(
                                    historicalStart.date
                                )} → ${formatDate(
                                    historicalEnd.date
                                )}`
                                : "No historical data"}

                        </p>

                    </div>


                    {/* FUTURE */}

                    <div
                        className="
                            bg-slate-800/50
                            border
                            border-slate-800
                            rounded-lg
                            p-4
                        "
                    >

                        <p
                            className="
                                text-sm
                                text-slate-400
                            "
                        >
                            Future Forecast
                        </p>


                        <p
                            className="
                                text-2xl
                                font-bold
                                mt-1
                                text-blue-400
                            "
                        >
                            {futureForecast.length}
                        </p>


                        <p
                            className="
                                text-xs
                                text-slate-500
                                mt-1
                            "
                        >

                            {futureStart &&
                            futureEnd
                                ? `${formatDate(
                                    futureStart.date
                                )} → ${formatDate(
                                    futureEnd.date
                                )}`
                                : "No future data"}

                        </p>

                    </div>


                    {/* FUTURE AVERAGE */}

                    <div
                        className="
                            bg-slate-800/50
                            border
                            border-slate-800
                            rounded-lg
                            p-4
                        "
                    >

                        <p
                            className="
                                text-sm
                                text-slate-400
                            "
                        >
                            Average Future Forecast
                        </p>


                        <p
                            className="
                                text-2xl
                                font-bold
                                mt-1
                                text-emerald-400
                            "
                        >
                            {averageFutureForecast.toLocaleString(
                                undefined,
                                {
                                    maximumFractionDigits: 0,
                                }
                            )}
                        </p>


                        <p
                            className="
                                text-xs
                                text-slate-500
                                mt-1
                            "
                        >
                            Based on 12 future points
                        </p>

                    </div>

                </div>

            </section>


            {/* =========================================
                FORECAST STATS
            ========================================= */}

            <ForecastStats
                model={model}
                records={
                    futureForecast.length
                }
                latestForecast={
                    latestForecast
                }
            />


            {/* =========================================
                SECONDARY METRICS
            ========================================= */}

            <div
                className="
                    grid
                    grid-cols-1
                    md:grid-cols-3
                    gap-4
                "
            >

                <div
                    className="
                        bg-slate-900
                        border
                        border-slate-800
                        rounded-xl
                        p-5
                    "
                >

                    <div
                        className="
                            flex
                            items-center
                            gap-2
                        "
                    >

                        <TrendingUp
                            size={18}
                            className="
                                text-blue-400
                            "
                        />

                        <p
                            className="
                                text-sm
                                text-slate-400
                            "
                        >
                            Average All Forecast
                        </p>

                    </div>


                    <p
                        className="
                            text-2xl
                            font-bold
                            mt-2
                        "
                    >
                        {averageAllForecast.toLocaleString(
                            undefined,
                            {
                                maximumFractionDigits: 0,
                            }
                        )}
                    </p>


                    <p
                        className="
                            text-xs
                            text-slate-500
                            mt-1
                        "
                    >
                        Based on all {chartData.length} backend
                        points
                    </p>

                </div>


                <div
                    className="
                        bg-slate-900
                        border
                        border-slate-800
                        rounded-xl
                        p-5
                    "
                >

                    <div
                        className="
                            flex
                            items-center
                            gap-2
                        "
                    >

                        <Database
                            size={18}
                            className="
                                text-purple-400
                            "
                        />

                        <p
                            className="
                                text-sm
                                text-slate-400
                            "
                        >
                            Inventory Records
                        </p>

                    </div>


                    <p
                        className="
                            text-2xl
                            font-bold
                            mt-2
                        "
                    >
                        {inventoryRecords.toLocaleString()}
                    </p>


                    <p
                        className="
                            text-xs
                            text-slate-500
                            mt-1
                        "
                    >
                        Retrieved from inventory service
                    </p>

                </div>


                <div
                    className="
                        bg-slate-900
                        border
                        border-slate-800
                        rounded-xl
                        p-5
                    "
                >

                    <div
                        className="
                            flex
                            items-center
                            gap-2
                        "
                    >

                        <Database
                            size={18}
                            className="
                                text-emerald-400
                            "
                        />

                        <p
                            className="
                                text-sm
                                text-slate-400
                            "
                        >
                            Data Integrity
                        </p>

                    </div>


                    <p
                        className={`
                            text-2xl
                            font-bold
                            mt-2
                            ${
                                dataIntegrity
                                    ? "text-emerald-400"
                                    : "text-yellow-400"
                            }
                        `}
                    >
                        {dataIntegrity
                            ? "Verified"
                            : "Check Data"}
                    </p>


                    <p
                        className="
                            text-xs
                            text-slate-500
                            mt-1
                        "
                    >
                        60 total = 48 historical + 12 future
                    </p>

                </div>

            </div>


            {/* =========================================
                FULL FORECAST TREND
                =========================================

                ALL 60 BACKEND POINTS

                2014
                2015
                2016
                2017
                2018
            */}

            <ForecastTrendChart
                data={chartData}
            />


            {/* =========================================
                FUTURE FORECAST TABLE
                =========================================

                ONLY 2018

                Jan → Dec
            */}

            <ForecastTable
                points={
                    futureForecast
                }
                inventoryRecords={
                    inventoryRecords
                }
            />

        </div>
    );
}


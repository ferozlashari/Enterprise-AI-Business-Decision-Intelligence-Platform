
import {
    useCallback,
    useEffect,
    useState,
} from "react";

import {
    RefreshCcw,
} from "lucide-react";

import {
    fetchDashboard,
    fetchRecommendations,
    fetchAlerts,
    EMPTY_DASHBOARD,
} from "./dashboard.api";

import KPIBox from "./components/KPIBox";
import SalesChart from "./components/SalesChart";
import ForecastChart from "./components/ForecastChart";
import InventoryChart from "./components/InventoryChart";
import CustomerPie from "./components/CustomerPie";
import RecommendationCard from "./components/RecommendationCard";
import AlertCard from "./components/AlertCard";


// =====================================================
// ENTERPRISE AI BUSINESS DECISION INTELLIGENCE PLATFORM
//
// EXECUTIVE DASHBOARD
//
// Author: Feroz Ali
//
// Responsibilities:
// - Executive KPI dashboard
// - Sales analytics
// - Demand forecasting
// - Inventory analytics
// - Customer segmentation
// - AI recommendations
// - Business alerts
// - Dashboard refresh
// - Safe loading/error states
// =====================================================


// =====================================================
// SAFE NUMBER
// =====================================================

const safeNumber = (value, fallback = 0) => {
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

    const cleaned = String(value)
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
// SAFE ARRAY
// =====================================================

const safeArray = (value) => {
    return Array.isArray(value)
        ? value
        : [];
};


// =====================================================
// NORMALIZE API ARRAY RESPONSE
// =====================================================
//
// Supports:
//
// [
//     {...},
//     {...}
// ]
//
// OR:
//
// {
//     data: [...]
// }
//
// OR:
//
// {
//     results: [...]
// }
//
// OR:
//
// {
//     items: [...]
// }
//
// OR:
//
// {
//     recommendations: [...]
// }
//
// OR:
//
// {
//     alerts: [...]
// }
//
// =====================================================

const normalizeArrayResponse = (
    response,
    preferredKeys = []
) => {

    if (Array.isArray(response)) {
        return response;
    }

    if (
        response &&
        typeof response === "object"
    ) {

        // Direct data array
        if (Array.isArray(response.data)) {
            return response.data;
        }

        // Common API response names
        for (const key of preferredKeys) {

            if (
                Array.isArray(
                    response[key]
                )
            ) {
                return response[key];
            }
        }

        // Generic result/items
        if (
            Array.isArray(
                response.results
            )
        ) {
            return response.results;
        }

        if (
            Array.isArray(
                response.items
            )
        ) {
            return response.items;
        }

        // Nested API data
        if (
            response.data &&
            typeof response.data === "object"
        ) {

            for (const key of preferredKeys) {

                if (
                    Array.isArray(
                        response.data[key]
                    )
                ) {
                    return response.data[key];
                }
            }

            if (
                Array.isArray(
                    response.data.results
                )
            ) {
                return response.data.results;
            }

            if (
                Array.isArray(
                    response.data.items
                )
            ) {
                return response.data.items;
            }
        }
    }

    return [];
};


// =====================================================
// NORMALIZE DASHBOARD RESPONSE
// =====================================================

const normalizeDashboardResponse = (
    response
) => {

    if (
        !response ||
        typeof response !== "object" ||
        Array.isArray(response)
    ) {
        return null;
    }

    // -----------------------------------------------
    // Direct dashboard response
    // -----------------------------------------------

    let data = response;

    // -----------------------------------------------
    // Backend may return:
    //
    // {
    //     status: "success",
    //     data: {...}
    // }
    // -----------------------------------------------

    if (
        response.data &&
        typeof response.data === "object" &&
        !Array.isArray(response.data)
    ) {
        data = response.data;
    }

    // -----------------------------------------------
    // Another possible wrapper:
    //
    // {
    //     result: {...}
    // }
    // -----------------------------------------------

    if (
        data.result &&
        typeof data.result === "object" &&
        !Array.isArray(data.result)
    ) {
        data = data.result;
    }

    return data;
};


// =====================================================
// COMPONENT
// =====================================================

export default function Dashboard() {

    // =================================================
    // STATE
    // =================================================

    const [
        dashboard,
        setDashboard,
    ] = useState({
        ...EMPTY_DASHBOARD,
    });

    const [
        recommendations,
        setRecommendations,
    ] = useState([]);

    const [
        alerts,
        setAlerts,
    ] = useState([]);

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

    const [
        dashboardLoaded,
        setDashboardLoaded,
    ] = useState(false);


    // =================================================
    // LOAD DASHBOARD DATA
    // =================================================

    const loadData = useCallback(
        async (isRefresh = false) => {

            // -----------------------------------------
            // Loading state
            // -----------------------------------------

            if (isRefresh) {
                setRefreshing(true);
            } else {
                setLoading(true);
            }

            setError(null);

            try {

                // -------------------------------------
                // Load all dashboard resources
                // independently.
                // -------------------------------------

                const results =
                    await Promise.allSettled([
                        fetchDashboard(),
                        fetchRecommendations(),
                        fetchAlerts(),
                    ]);

                const [
                    dashboardResult,
                    recommendationResult,
                    alertResult,
                ] = results;


                // =====================================
                // DASHBOARD
                // =====================================

                if (
                    dashboardResult.status ===
                    "fulfilled"
                ) {

                    const dashboardData =
                        normalizeDashboardResponse(
                            dashboardResult.value
                        );

                    if (dashboardData) {

                        console.log(
                            "[Dashboard] Normalized dashboard:",
                            dashboardData
                        );

                        setDashboard(
                            (
                                previousDashboard
                            ) => ({
                                ...EMPTY_DASHBOARD,

                                // Preserve old values
                                // during refresh.
                                ...(isRefresh
                                    ? previousDashboard
                                    : {}),

                                // Backend values
                                ...dashboardData,

                                // ---------------------
                                // KPI normalization
                                // ---------------------

                                revenue:
                                    safeNumber(
                                        dashboardData.revenue
                                    ),

                                profit:
                                    safeNumber(
                                        dashboardData.profit
                                    ),

                                inventory:
                                    safeNumber(
                                        dashboardData.inventory
                                    ),

                                customers:
                                    safeNumber(
                                        dashboardData.customers
                                    ),

                                // ---------------------
                                // Analytics
                                // ---------------------

                                sales_trend:
                                    safeArray(
                                        dashboardData
                                            .sales_trend
                                    ),

                                forecast:
                                    safeArray(
                                        dashboardData
                                            .forecast
                                    ),

                                inventory_data:
                                    safeArray(
                                        dashboardData
                                            .inventory_data
                                    ),

                                customer_segments:
                                    safeArray(
                                        dashboardData
                                            .customer_segments
                                    ),

                                // ---------------------
                                // Alerts
                                // ---------------------

                                alerts:
                                    Math.max(
                                        0,
                                        safeNumber(
                                            dashboardData
                                                .alerts
                                        )
                                    ),

                                alert_items:
                                    safeArray(
                                        dashboardData
                                            .alert_items
                                    ),

                                // ---------------------
                                // AI status
                                // ---------------------

                                model_status:
                                    dashboardData
                                        .model_status ||
                                    "unknown",

                                // ---------------------
                                // System status
                                // ---------------------

                                status:
                                    dashboardData
                                        .status ||
                                    "unknown",
                            })
                        );

                        setDashboardLoaded(
                            true
                        );

                    } else {

                        console.error(
                            "[Dashboard] Invalid dashboard payload:",
                            dashboardResult.value
                        );

                        if (!isRefresh) {

                            setDashboard({
                                ...EMPTY_DASHBOARD,
                            });

                            setDashboardLoaded(
                                false
                            );
                        }

                        setError(
                            "Invalid dashboard data received from server."
                        );
                    }

                } else {

                    console.error(
                        "[Dashboard] Dashboard request failed:",
                        dashboardResult.reason
                    );

                    // ---------------------------------
                    // Do not destroy loaded dashboard
                    // during refresh failure.
                    // ---------------------------------

                    if (!isRefresh) {

                        setDashboard({
                            ...EMPTY_DASHBOARD,
                        });

                        setDashboardLoaded(
                            false
                        );
                    }

                    setError(
                        dashboardResult
                            .reason
                            ?.message ||
                        "Unable to load dashboard data."
                    );
                }


                // =====================================
                // RECOMMENDATIONS
                // =====================================

                if (
                    recommendationResult.status ===
                    "fulfilled"
                ) {

                    const recommendationData =
                        normalizeArrayResponse(
                            recommendationResult.value,
                            [
                                "recommendations",
                                "recommendation",
                            ]
                        );

                    console.log(
                        "[Dashboard] Recommendations:",
                        recommendationData
                    );

                    if (
                        Array.isArray(
                            recommendationData
                        )
                    ) {

                        setRecommendations(
                            recommendationData
                        );

                    } else {

                        console.warn(
                            "[Dashboard] Invalid recommendations payload."
                        );

                        // Preserve during refresh.
                        if (!isRefresh) {
                            setRecommendations(
                                []
                            );
                        }
                    }

                } else {

                    console.error(
                        "[Dashboard] Recommendations failed:",
                        recommendationResult.reason
                    );

                    // Preserve old data during refresh.
                    if (!isRefresh) {
                        setRecommendations(
                            []
                        );
                    }
                }


                // =====================================
                // ALERTS
                // =====================================

                if (
                    alertResult.status ===
                    "fulfilled"
                ) {

                    const alertData =
                        normalizeArrayResponse(
                            alertResult.value,
                            [
                                "alerts",
                                "alert_items",
                            ]
                        );

                    console.log(
                        "[Dashboard] Alerts:",
                        alertData
                    );

                    if (
                        Array.isArray(
                            alertData
                        )
                    ) {

                        setAlerts(
                            alertData
                        );

                    } else {

                        console.warn(
                            "[Dashboard] Invalid alerts payload."
                        );

                        // Preserve during refresh.
                        if (!isRefresh) {
                            setAlerts([]);
                        }
                    }

                } else {

                    console.error(
                        "[Dashboard] Alerts failed:",
                        alertResult.reason
                    );

                    // Preserve old alerts during refresh.
                    if (!isRefresh) {
                        setAlerts([]);
                    }
                }


                // =====================================
                // DASHBOARD ERROR
                // =====================================

                if (
                    dashboardResult.status ===
                    "rejected"
                ) {

                    setError(
                        dashboardResult
                            .reason
                            ?.message ||
                        "Unable to load dashboard data."
                    );
                }

            } catch (err) {

                console.error(
                    "[Dashboard] Unexpected load error:",
                    err
                );

                setError(
                    err?.message ||
                    "Unable to load dashboard data."
                );

                // -------------------------------------
                // Initial load failure
                // -------------------------------------

                if (!isRefresh) {

                    setDashboard({
                        ...EMPTY_DASHBOARD,
                    });

                    setRecommendations([]);

                    setAlerts([]);

                    setDashboardLoaded(
                        false
                    );
                }

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

        loadData(false);

    }, [loadData]);


    // =================================================
    // SAFE DATA
    // =================================================

    const safeSalesTrend =
        safeArray(
            dashboard.sales_trend
        );

    const safeForecast =
        safeArray(
            dashboard.forecast
        );

    const safeInventoryData =
        safeArray(
            dashboard.inventory_data
        );

    const safeCustomerSegments =
        safeArray(
            dashboard.customer_segments
        );

    const safeRecommendations =
        safeArray(
            recommendations
        );

    const safeAlerts =
        safeArray(
            alerts
        );


    // =================================================
    // INITIAL LOADING STATE
    // =================================================

    if (
        loading &&
        !dashboardLoaded
    ) {

        return (
            <div
                className="
                    min-h-[70vh]
                    flex
                    items-center
                    justify-center
                    p-6
                    text-white
                "
            >

                <div
                    className="
                        bg-slate-900
                        border
                        border-slate-800
                        rounded-xl
                        px-8
                        py-6
                        text-center
                        shadow-xl
                    "
                >

                    <div
                        className="
                            flex
                            items-center
                            justify-center
                            gap-3
                            text-xl
                            font-semibold
                            mb-2
                        "
                    >

                        <RefreshCcw
                            size={22}
                            className="animate-spin"
                        />

                        Loading Executive Dashboard...

                    </div>

                    <div
                        className="
                            text-slate-400
                            text-sm
                        "
                    >
                        Loading enterprise intelligence
                        data
                    </div>

                </div>

            </div>
        );
    }


    // =================================================
    // FULL ERROR STATE
    // =================================================

    if (
        !dashboardLoaded &&
        error
    ) {

        return (
            <div
                className="
                    min-h-[70vh]
                    flex
                    items-center
                    justify-center
                    p-6
                "
            >

                <div
                    className="
                        max-w-lg
                        w-full
                        bg-slate-900
                        border
                        border-red-500/30
                        rounded-xl
                        p-8
                        shadow-xl
                    "
                >

                    <h2
                        className="
                            text-2xl
                            font-bold
                            text-red-400
                            mb-3
                        "
                    >
                        Dashboard Error
                    </h2>

                    <p
                        className="
                            text-slate-300
                            mb-6
                        "
                    >
                        {error}
                    </p>

                    <button
                        type="button"
                        onClick={() =>
                            loadData(false)
                        }
                        disabled={loading}
                        className="
                            flex
                            items-center
                            gap-2
                            bg-blue-600
                            hover:bg-blue-700
                            disabled:opacity-50
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
                                loading
                                    ? "animate-spin"
                                    : ""
                            }
                        />

                        Retry

                    </button>

                </div>

            </div>
        );
    }


    // =================================================
    // MAIN DASHBOARD
    // =================================================

    return (

        <div
            className="
                p-6
                space-y-6
                text-white
            "
        >

            {/* =========================================
                HEADER
            ========================================= */}

            <div
                className="
                    flex
                    flex-col
                    md:flex-row
                    md:justify-between
                    md:items-center
                    gap-4
                "
            >

                <div>

                    <h1
                        className="
                            text-3xl
                            font-bold
                        "
                    >
                        Executive Dashboard
                    </h1>

                    <p
                        className="
                            text-slate-400
                            mt-2
                        "
                    >
                        AI Powered Business Intelligence
                        Overview
                    </p>

                </div>

                <button
                    type="button"
                    onClick={() =>
                        loadData(true)
                    }
                    disabled={refreshing}
                    className="
                        flex
                        items-center
                        justify-center
                        gap-2
                        bg-blue-600
                        hover:bg-blue-700
                        disabled:opacity-50
                        disabled:cursor-not-allowed
                        px-4
                        py-2
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
                        : "Refresh"
                    }

                </button>

            </div>


            {/* =========================================
                NON-BLOCKING ERROR
            ========================================= */}

            {error &&
                dashboardLoaded && (

                    <div
                        className="
                            bg-red-950/40
                            border
                            border-red-500/30
                            rounded-lg
                            px-4
                            py-3
                            text-red-300
                        "
                    >

                        <div
                            className="
                                flex
                                items-center
                                justify-between
                                gap-4
                            "
                        >

                            <span>
                                {error}
                            </span>

                            <button
                                type="button"
                                onClick={() =>
                                    loadData(true)
                                }
                                disabled={
                                    refreshing
                                }
                                className="
                                    text-sm
                                    font-semibold
                                    text-red-200
                                    hover:text-white
                                    underline
                                    disabled:opacity-50
                                "
                            >
                                Retry
                            </button>

                        </div>

                    </div>
                )}


            {/* =========================================
                SYSTEM STATUS
            ========================================= */}

            <div
                className="
                    flex
                    flex-wrap
                    gap-3
                "
            >

                <div
                    className="
                        bg-slate-900
                        border
                        border-slate-800
                        rounded-lg
                        px-4
                        py-2
                    "
                >

                    <span
                        className="
                            text-slate-400
                            text-sm
                        "
                    >
                        AI Model:
                    </span>

                    <span
                        className="
                            ml-2
                            text-green-400
                            font-semibold
                        "
                    >
                        {dashboard.model_status ||
                            "unknown"}
                    </span>

                </div>


                <div
                    className="
                        bg-slate-900
                        border
                        border-slate-800
                        rounded-lg
                        px-4
                        py-2
                    "
                >

                    <span
                        className="
                            text-slate-400
                            text-sm
                        "
                    >
                        Alerts:
                    </span>

                    <span
                        className="
                            ml-2
                            text-yellow-400
                            font-semibold
                        "
                    >
                        {safeNumber(
                            dashboard.alerts
                        )}
                    </span>

                </div>


                <div
                    className="
                        bg-slate-900
                        border
                        border-slate-800
                        rounded-lg
                        px-4
                        py-2
                    "
                >

                    <span
                        className="
                            text-slate-400
                            text-sm
                        "
                    >
                        System:
                    </span>

                    <span
                        className="
                            ml-2
                            text-blue-400
                            font-semibold
                            capitalize
                        "
                    >
                        {dashboard.status ||
                            "unknown"}
                    </span>

                </div>

            </div>


            {/* =========================================
                KPI CARDS
            ========================================= */}

            <div
                className="
                    grid
                    grid-cols-1
                    md:grid-cols-2
                    xl:grid-cols-4
                    gap-5
                "
            >

                <KPIBox
                    title="Revenue"
                    value={
                        safeNumber(
                            dashboard.revenue
                        )
                    }
                    type="currency"
                />

                <KPIBox
                    title="Profit"
                    value={
                        safeNumber(
                            dashboard.profit
                        )
                    }
                    type="currency"
                />

                <KPIBox
                    title="Inventory"
                    value={
                        safeNumber(
                            dashboard.inventory
                        )
                    }
                    type="number"
                />

                <KPIBox
                    title="Customers"
                    value={
                        safeNumber(
                            dashboard.customers
                        )
                    }
                    type="number"
                />

            </div>


            {/* =========================================
                SALES TREND
            ========================================= */}

            <SalesChart
                data={safeSalesTrend}
            />


            {/* =========================================
                DEMAND FORECAST
            ========================================= */}

            <ForecastChart
                data={safeForecast}
            />


            {/* =========================================
                INVENTORY + CUSTOMERS
            ========================================= */}

            <div
                className="
                    grid
                    grid-cols-1
                    xl:grid-cols-2
                    gap-6
                "
            >

                <InventoryChart
                    data={safeInventoryData}
                />

                <CustomerPie
                    data={safeCustomerSegments}
                />

            </div>


            {/* =========================================
                RECOMMENDATIONS + ALERTS
            ========================================= */}

            <div
                className="
                    grid
                    grid-cols-1
                    xl:grid-cols-2
                    gap-6
                "
            >

                <RecommendationCard
                    recommendations={
                        safeRecommendations
                    }
                />

                <AlertCard
                    alerts={
                        safeAlerts
                    }
                />

            </div>


            {/* =========================================
                REFRESH INDICATOR
            ========================================= */}

            {refreshing && (

                <div
                    className="
                        fixed
                        bottom-5
                        right-5
                        z-50
                        bg-slate-900
                        border
                        border-slate-700
                        rounded-lg
                        px-4
                        py-3
                        shadow-xl
                        flex
                        items-center
                        gap-3
                        text-sm
                        text-slate-300
                    "
                >

                    <RefreshCcw
                        size={16}
                        className="
                            animate-spin
                            text-blue-400
                        "
                    />

                    Updating enterprise
                    intelligence...

                </div>

            )}

        </div>
    );
}


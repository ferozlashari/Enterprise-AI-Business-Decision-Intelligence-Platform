import {
    useCallback,
    useEffect,
    useState
} from "react";

import {
    RefreshCcw,
    TrendingUp,
    AlertCircle
} from "lucide-react";

import {
    fetchSales,
    fetchSalesPrediction,
    fetchFeatureImportance,
    fetchSalesReport,
    fetchSalesHealth
} from "./sales.api";

import SalesKPI from "./components/SalesKPI";
import RevenueChart from "./components/RevenueChart";
import CategoryChart from "./components/CategoryChart";
import RegionChart from "./components/RegionChart";
import PredictionCard from "./components/PredictionCard";
import FeatureImportance from "./components/FeatureImportance";
import SalesReport from "./components/SalesReport";
import SalesHealth from "./components/SalesHealth";


// =====================================================
// EMPTY SALES STATE
// =====================================================

const EMPTY_SALES = {
    total_sales: 0,
    profit: 0,
    growth: 0,
    predicted_sales: 0,
    average_sales: 0,
    best_category: "N/A",
    model: "Unknown",
    sales_trend: [],
    category_sales: [],
    region_sales: []
};


// =====================================================
// EMPTY HEALTH STATE
// =====================================================

const EMPTY_HEALTH = {
    success: false,
    status: "Unknown",
    service: "Sales Intelligence API"
};


// =====================================================
// NUMBER HELPER
// =====================================================

const toNumber = (value, fallback = 0) => {

    const number = Number(value);

    return Number.isFinite(number)
        ? number
        : fallback;
};


// =====================================================
// ARRAY HELPER
// =====================================================

const toArray = (value) => {

    return Array.isArray(value)
        ? value
        : [];
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
// NORMALIZE SALES RESPONSE
// =====================================================

const normalizeSales = (data = {}) => {

    let source = data;


    // -------------------------------------------------
    // Handle:
    //
    // {
    //     sales: {...},
    //     total_sales: ...
    // }
    // -------------------------------------------------

    if (
        source?.sales &&
        typeof source.sales === "object" &&
        !Array.isArray(source.sales)
    ) {

        source = {
            ...source.sales,
            ...source
        };

    }


    // -------------------------------------------------
    // Handle nested data
    // -------------------------------------------------

    if (
        source?.data &&
        typeof source.data === "object" &&
        !Array.isArray(source.data)
    ) {

        source = {
            ...source.data,
            ...source
        };

    }


    // -------------------------------------------------
    // Handle result
    // -------------------------------------------------

    if (
        source?.result &&
        typeof source.result === "object" &&
        !Array.isArray(source.result)
    ) {

        source = {
            ...source.result,
            ...source
        };

    }


    // -------------------------------------------------
    // Handle report
    // -------------------------------------------------

    if (
        source?.report &&
        typeof source.report === "object" &&
        !Array.isArray(source.report)
    ) {

        source = {
            ...source.report,
            ...source
        };

    }


    // =================================================
    // RETURN NORMALIZED DATA
    // =================================================

    return {

        total_sales:
            toNumber(
                source?.total_sales ??
                source?.Revenue ??
                source?.revenue ??
                source?.sales
            ),


        profit:
            toNumber(
                source?.profit ??
                source?.Profit
            ),


        growth:
            toNumber(
                source?.growth ??
                source?.Growth ??
                source?.sales_growth ??
                source?.growth_rate
            ),


        predicted_sales:
            toNumber(
                source?.predicted_sales ??
                source?.prediction ??
                source?.PredictedSales ??
                source?.predictedSales
            ),


        average_sales:
            toNumber(
                source?.average_sales ??
                source?.["Average Sales"]
            ),


        best_category:
            source?.best_category ??
            source?.["Best Category"] ??
            "N/A",


        model:
            source?.model ??
            source?.Model ??
            "Unknown",


        sales_trend:
            toArray(
                source?.sales_trend ??
                source?.["Sales Trend"] ??
                source?.trend
            ),


        category_sales:
            toArray(
                source?.category_sales ??
                source?.["Category Sales"] ??
                source?.categories
            ),


        region_sales:
            toArray(
                source?.region_sales ??
                source?.["Region Sales"] ??
                source?.regions
            )

    };

};


// =====================================================
// NORMALIZE PREDICTION
// =====================================================

const normalizePrediction = (data = {}) => {

    let source = data;


    if (
        source?.prediction &&
        typeof source.prediction === "object"
    ) {

        source = source.prediction;

    }


    if (
        source?.data &&
        typeof source.data === "object"
    ) {

        source = source.data;

    }


    if (
        source?.result &&
        typeof source.result === "object"
    ) {

        source = source.result;

    }


    return {

        prediction:
            toNumber(
                source?.predicted_sales ??
                source?.prediction ??
                source?.predictedSales ??
                source?.forecast ??
                source?.value ??
                source?.sales
            ),


        model:
            source?.model ??
            source?.Model ??
            "Unknown"

    };

};


// =====================================================
// NORMALIZE FEATURES
// =====================================================

const normalizeFeatures = (data) => {

    if (Array.isArray(data)) {

        return data;

    }


    if (Array.isArray(data?.features)) {

        return data.features;

    }


    if (Array.isArray(data?.data?.features)) {

        return data.data.features;

    }


    if (Array.isArray(data?.data)) {

        return data.data;

    }


    if (Array.isArray(data?.result)) {

        return data.result;

    }


    return [];

};


// =====================================================
// NORMALIZE REPORT
// =====================================================

const normalizeReport = (data = {}) => {

    let source = data;


    if (
        source?.report &&
        typeof source.report === "object" &&
        !Array.isArray(source.report)
    ) {

        source = source.report;

    }


    if (
        source?.data?.report &&
        typeof source.data.report === "object" &&
        !Array.isArray(source.data.report)
    ) {

        source = source.data.report;

    }


    if (
        source?.data &&
        typeof source.data === "object" &&
        !Array.isArray(source.data)
    ) {

        source = source.data;

    }


    if (
        source?.result &&
        typeof source.result === "object" &&
        !Array.isArray(source.result)
    ) {

        source = source.result;

    }


    if (
        !source ||
        typeof source !== "object" ||
        Array.isArray(source)
    ) {

        return {};

    }


    return source;

};


// =====================================================
// SALES PAGE
// =====================================================

export default function Sales() {


    const [sales, setSales] =
        useState(EMPTY_SALES);


    const [features, setFeatures] =
        useState([]);


    const [report, setReport] =
        useState({});


    const [health, setHealth] =
        useState(EMPTY_HEALTH);


    const [loading, setLoading] =
        useState(true);


    const [refreshing, setRefreshing] =
        useState(false);


    const [error, setError] =
        useState(null);


    // =================================================
    // LOAD SALES DATA
    // =================================================

    const loadSales = useCallback(
        async (isRefresh = false) => {

            try {

                if (isRefresh) {

                    setRefreshing(true);

                }
                else {

                    setLoading(true);

                }


                setError(null);


                // =================================================
                // LOAD ALL SALES APIs
                // =================================================

                const [
                    salesResponse,
                    reportResponse,
                    predictionResponse,
                    featureResponse,
                    healthResponse
                ] = await Promise.all([

                    fetchSales(),

                    fetchSalesReport(),

                    fetchSalesPrediction(),

                    fetchFeatureImportance(),

                    fetchSalesHealth()

                ]);


                console.log(
                    "SALES DASHBOARD:",
                    salesResponse
                );


                console.log(
                    "SALES REPORT:",
                    reportResponse
                );


                console.log(
                    "SALES PREDICTION:",
                    predictionResponse
                );


                console.log(
                    "SALES FEATURES:",
                    featureResponse
                );


                console.log(
                    "SALES HEALTH:",
                    healthResponse
                );


                // =================================================
                // NORMALIZE
                // =================================================

                const dashboard =
                    normalizeSales(
                        salesResponse
                    );


                const reportData =
                    normalizeReport(
                        reportResponse
                    );


                const predictionData =
                    normalizePrediction(
                        predictionResponse
                    );


                const normalizedReport =
                    normalizeSales(
                        reportData
                    );


                // =================================================
                // PREDICTION
                // =================================================

                const prediction =
                    predictionData.prediction ||
                    dashboard.predicted_sales ||
                    normalizedReport.predicted_sales ||
                    0;


                // =================================================
                // MODEL
                //
                // Backend currently returns:
                //
                // "Random Forest"
                // =================================================

                const model =
                    predictionData.model !== "Unknown"
                        ? predictionData.model
                        : dashboard.model !== "Unknown"
                            ? dashboard.model
                            : normalizedReport.model !== "Unknown"
                                ? normalizedReport.model
                                : "Unknown";


                // =================================================
                // FINAL SALES DATA
                // =================================================

                const finalSales = {

                    total_sales:
                        dashboard.total_sales ||
                        normalizedReport.total_sales ||
                        0,


                    profit:
                        dashboard.profit ||
                        normalizedReport.profit ||
                        0,


                    growth:
                        dashboard.growth ??
                        normalizedReport.growth ??
                        0,


                    predicted_sales:
                        prediction,


                    average_sales:
                        dashboard.average_sales ||
                        normalizedReport.average_sales ||
                        0,


                    best_category:
                        dashboard.best_category !== "N/A"
                            ? dashboard.best_category
                            : normalizedReport.best_category ||
                              "N/A",


                    model,


                    sales_trend:
                        dashboard.sales_trend.length > 0
                            ? dashboard.sales_trend
                            : normalizedReport.sales_trend,


                    category_sales:
                        dashboard.category_sales.length > 0
                            ? dashboard.category_sales
                            : normalizedReport.category_sales,


                    region_sales:
                        dashboard.region_sales.length > 0
                            ? dashboard.region_sales
                            : normalizedReport.region_sales

                };


                console.log(
                    "FINAL SALES DATA:",
                    finalSales
                );


                // =================================================
                // UPDATE STATES
                // =================================================

                setSales(
                    finalSales
                );


                setFeatures(
                    normalizeFeatures(
                        featureResponse
                    )
                );


                setReport({

                    ...reportData,

                    total_sales:
                        finalSales.total_sales,

                    profit:
                        finalSales.profit,

                    growth:
                        finalSales.growth,

                    predicted_sales:
                        finalSales.predicted_sales,

                    average_sales:
                        finalSales.average_sales,

                    best_category:
                        finalSales.best_category,

                    model:
                        finalSales.model,

                    sales_trend:
                        finalSales.sales_trend,

                    category_sales:
                        finalSales.category_sales,

                    region_sales:
                        finalSales.region_sales

                });


                setHealth(
                    healthResponse ||
                    EMPTY_HEALTH
                );

            }

            catch (err) {

                console.error(
                    "SALES PAGE ERROR:",
                    err
                );


                const detail =
                    err?.response?.data?.detail;


                if (
                    Array.isArray(detail)
                ) {

                    setError(
                        detail
                            .map(
                                item =>
                                    item?.msg ||
                                    "Validation error"
                            )
                            .join(", ")
                    );

                }

                else if (
                    typeof detail === "string"
                ) {

                    setError(detail);

                }

                else {

                    setError(
                        err?.message ||
                        "Unable to load Sales Intelligence."
                    );

                }

            }

            finally {

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

        loadSales();

    }, [loadSales]);


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
                    bg-slate-950
                    text-white
                    p-6
                "
            >

                <div
                    className="
                        bg-slate-900
                        border
                        border-slate-800
                        rounded-2xl
                        px-10
                        py-8
                        text-center
                        shadow-xl
                    "
                >

                    <div
                        className="
                            w-10
                            h-10
                            border-4
                            border-slate-700
                            border-t-blue-500
                            rounded-full
                            animate-spin
                            mx-auto
                            mb-5
                        "
                    />

                    <div
                        className="
                            text-xl
                            font-semibold
                            mb-2
                        "
                    >

                        Loading Sales Intelligence...

                    </div>


                    <div
                        className="
                            text-slate-400
                            text-sm
                        "
                    >

                        Loading enterprise sales analytics

                    </div>

                </div>

            </div>

        );

    }


    // =================================================
    // ERROR SCREEN
    // =================================================

    if (error) {

        return (

            <div
                className="
                    min-h-[70vh]
                    flex
                    items-center
                    justify-center
                    bg-slate-950
                    p-6
                    text-white
                "
            >

                <div
                    className="
                        max-w-lg
                        w-full
                        bg-slate-900
                        border
                        border-red-500/30
                        rounded-2xl
                        p-8
                        shadow-xl
                    "
                >

                    <div
                        className="
                            flex
                            items-center
                            gap-3
                            mb-4
                        "
                    >

                        <AlertCircle
                            size={28}
                            className="text-red-400"
                        />

                        <h2
                            className="
                                text-2xl
                                font-bold
                                text-red-400
                            "
                        >

                            Sales Dashboard Error

                        </h2>

                    </div>


                    <p
                        className="
                            text-slate-300
                            mb-6
                            leading-relaxed
                        "
                    >

                        {error}

                    </p>


                    <button
                        type="button"
                        onClick={() => loadSales(true)}
                        className="
                            flex
                            items-center
                            gap-2
                            bg-blue-600
                            hover:bg-blue-700
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
                        />

                        Retry

                    </button>

                </div>

            </div>

        );

    }


    // =================================================
    // FORECAST DIFFERENCE
    // =================================================

    const forecastDifference =
        sales.predicted_sales -
        sales.total_sales;


    // =================================================
    // MAIN SALES DASHBOARD
    // =================================================

    return (

        <div
            className="
                min-h-screen
                bg-slate-950
                p-4
                sm:p-6
                lg:p-8
                space-y-6
                text-white
            "
        >


            {/* =================================================
                HEADER
            ================================================= */}

            <div
                className="
                    flex
                    flex-col
                    lg:flex-row
                    lg:items-center
                    lg:justify-between
                    gap-5
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
                                w-11
                                h-11
                                rounded-xl
                                bg-blue-500/10
                                flex
                                items-center
                                justify-center
                            "
                        >

                            <TrendingUp
                                size={24}
                                className="text-blue-400"
                            />

                        </div>


                        <div>

                            <h1
                                className="
                                    text-2xl
                                    sm:text-3xl
                                    font-bold
                                "
                            >

                                Sales Analytics

                            </h1>


                            <p
                                className="
                                    text-slate-400
                                    text-sm
                                    mt-1
                                "
                            >

                                AI Powered Enterprise Sales Intelligence

                            </p>

                        </div>

                    </div>

                </div>


                <button
                    type="button"
                    onClick={() => loadSales(true)}
                    disabled={refreshing}
                    className="
                        flex
                        items-center
                        justify-center
                        gap-2
                        bg-blue-600
                        hover:bg-blue-700
                        disabled:bg-blue-800
                        disabled:cursor-not-allowed
                        px-5
                        py-2.5
                        rounded-lg
                        text-white
                        font-semibold
                        transition
                        shadow-lg
                        shadow-blue-900/20
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


            {/* =================================================
                KPI CARDS
            ================================================= */}

            <div
                className="
                    grid
                    grid-cols-1
                    sm:grid-cols-2
                    xl:grid-cols-4
                    gap-5
                "
            >

                <SalesKPI
                    title="Total Revenue"
                    value={sales.total_sales}
                    icon="Revenue"
                    type="currency"
                />


                <SalesKPI
                    title="Profit"
                    value={sales.profit}
                    icon="Profit"
                    type="currency"
                />


                <SalesKPI
                    title="AI Prediction"
                    value={sales.predicted_sales}
                    icon="Prediction"
                    type="currency"
                />


                <SalesKPI
                    title="Growth"
                    value={sales.growth}
                    icon="Growth"
                    type="percent"
                />

            </div>


            {/* =================================================
                REVENUE TREND
            ================================================= */}

            <RevenueChart
                data={sales.sales_trend}
            />


            {/* =================================================
                CATEGORY + REGION
            ================================================= */}

            <div
                className="
                    grid
                    grid-cols-1
                    xl:grid-cols-2
                    gap-6
                "
            >

                <CategoryChart
                    data={sales.category_sales}
                />


                <RegionChart
                    data={sales.region_sales}
                />

            </div>


            {/* =================================================
                AI PREDICTION
            ================================================= */}

            <PredictionCard
                prediction={sales.predicted_sales}
                model={sales.model}
            />


            {/* =================================================
                FORECAST SUMMARY
            ================================================= */}

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
                        flex-col
                        sm:flex-row
                        sm:items-center
                        sm:justify-between
                        gap-3
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

                            AI Forecast Analysis

                        </h2>


                        <p
                            className="
                                text-slate-400
                                text-sm
                                mt-1
                            "
                        >

                            Forecast compared with current enterprise sales

                        </p>

                    </div>

                </div>


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
                            bg-slate-950
                            border
                            border-slate-800
                            rounded-lg
                            p-4
                        "
                    >

                        <p
                            className="
                                text-slate-500
                                text-sm
                            "
                        >

                            Current Sales

                        </p>


                        <p
                            className="
                                text-white
                                text-xl
                                font-bold
                                mt-1
                            "
                        >

                            {formatCurrency(
                                sales.total_sales
                            )}

                        </p>

                    </div>


                    <div
                        className="
                            bg-slate-950
                            border
                            border-slate-800
                            rounded-lg
                            p-4
                        "
                    >

                        <p
                            className="
                                text-slate-500
                                text-sm
                            "
                        >

                            AI Forecast

                        </p>


                        <p
                            className="
                                text-green-400
                                text-xl
                                font-bold
                                mt-1
                            "
                        >

                            {formatCurrency(
                                sales.predicted_sales
                            )}

                        </p>

                    </div>


                    <div
                        className="
                            bg-slate-950
                            border
                            border-slate-800
                            rounded-lg
                            p-4
                        "
                    >

                        <p
                            className="
                                text-slate-500
                                text-sm
                            "
                        >

                            Forecast Difference

                        </p>


                        <p
                            className={`
                                text-xl
                                font-bold
                                mt-1
                                ${
                                    forecastDifference >= 0
                                        ? "text-green-400"
                                        : "text-red-400"
                                }
                            `}
                        >

                            {formatCurrency(
                                forecastDifference
                            )}

                        </p>

                    </div>

                </div>

            </div>


            {/* =================================================
                FEATURE IMPORTANCE
            ================================================= */}

            <FeatureImportance
                data={features}
            />


            {/* =================================================
                REPORT + HEALTH
            ================================================= */}

            <div
                className="
                    grid
                    grid-cols-1
                    xl:grid-cols-2
                    gap-6
                "
            >

                <SalesReport
                    report={report}
                />


                <SalesHealth
                    health={health}
                />

            </div>


        </div>

    );

}
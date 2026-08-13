
import api from "../../api/axios";


// =====================================================
// EMPTY SALES
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
// SAFE NUMBER
// =====================================================

const toNumber = (value, fallback = 0) => {

    const number = Number(value);

    return Number.isFinite(number)
        ? number
        : fallback;

};


// =====================================================
// SAFE ARRAY
// =====================================================

const toArray = (value) => {

    return Array.isArray(value)
        ? value
        : [];

};


// =====================================================
// NORMALIZE SALES TREND
// =====================================================

const normalizeSalesTrend = (value) => {

    if (!Array.isArray(value)) {

        return [];

    }


    return value
        .filter(
            item =>
                item &&
                typeof item === "object"
        )
        .map(item => ({

            month:
                item.month ??
                item.Month ??
                item.name ??
                "",

            sales:
                toNumber(
                    item.sales ??
                    item.Sales ??
                    item.revenue ??
                    item.Revenue
                )

        }));

};


// =====================================================
// NORMALIZE CATEGORY SALES
// =====================================================

const normalizeCategorySales = (value) => {

    if (!Array.isArray(value)) {

        return [];

    }


    return value
        .filter(
            item =>
                item &&
                typeof item === "object"
        )
        .map(item => ({

            category:
                item.category ??
                item.Category ??
                item.name ??
                "",

            sales:
                toNumber(
                    item.sales ??
                    item.Sales ??
                    item.revenue ??
                    item.Revenue
                )

        }));

};


// =====================================================
// NORMALIZE REGION SALES
// =====================================================

const normalizeRegionSales = (value) => {

    if (!Array.isArray(value)) {

        return [];

    }


    return value
        .filter(
            item =>
                item &&
                typeof item === "object"
        )
        .map(item => ({

            region:
                item.region ??
                item.Region ??
                item.name ??
                "",

            sales:
                toNumber(
                    item.sales ??
                    item.Sales ??
                    item.revenue ??
                    item.Revenue
                )

        }));

};


// =====================================================
// NORMALIZE SALES RESPONSE
// =====================================================

const normalizeSales = (response) => {

    let data = response;


    // =================================================
    // ACTUAL BACKEND RESPONSE
    //
    // {
    //     success: true,
    //
    //     sales: {
    //         total_sales: ...,
    //         profit: ...,
    //         ...
    //     },
    //
    //     total_sales: ...
    // }
    // =================================================

    if (
        data?.sales &&
        typeof data.sales === "object" &&
        !Array.isArray(data.sales)
    ) {

        data = data.sales;

    }


    // =================================================
    // GENERIC DATA WRAPPER
    // =================================================

    if (
        data?.data &&
        typeof data.data === "object" &&
        !Array.isArray(data.data)
    ) {

        data = data.data;

    }


    // =================================================
    // RESULT WRAPPER
    // =================================================

    if (
        data?.result &&
        typeof data.result === "object" &&
        !Array.isArray(data.result)
    ) {

        data = data.result;

    }


    // =================================================
    // INVALID RESPONSE
    // =================================================

    if (
        !data ||
        typeof data !== "object" ||
        Array.isArray(data)
    ) {

        return {
            ...EMPTY_SALES
        };

    }


    // =================================================
    // SALES TREND
    // =================================================

    const salesTrend =

        Array.isArray(data.sales_trend)

            ? data.sales_trend

            : Array.isArray(data["Sales Trend"])

                ? data["Sales Trend"]

                : Array.isArray(data.trend)

                    ? data.trend

                    : [];


    // =================================================
    // CATEGORY SALES
    // =================================================

    const categorySales =

        Array.isArray(data.category_sales)

            ? data.category_sales

            : Array.isArray(data["Category Sales"])

                ? data["Category Sales"]

                : Array.isArray(data.categories)

                    ? data.categories

                    : [];


    // =================================================
    // REGION SALES
    // =================================================

    const regionSales =

        Array.isArray(data.region_sales)

            ? data.region_sales

            : Array.isArray(data["Region Sales"])

                ? data["Region Sales"]

                : Array.isArray(data.regions)

                    ? data.regions

                    : [];


    // =================================================
    // PREDICTED SALES
    // =================================================

    const predictedSales =

        toNumber(

            data.predicted_sales ??

            data.prediction ??

            data.predictedSales ??

            data.forecast ??

            0

        );


    // =================================================
    // FINAL NORMALIZED SALES
    // =================================================

    return {

        total_sales:

            toNumber(

                data.total_sales ??

                data.revenue ??

                data.Revenue ??

                data.sales ??

                data.TotalSales ??

                0

            ),


        profit:

            toNumber(

                data.profit ??

                data.Profit ??

                0

            ),


        growth:

            toNumber(

                data.growth ??

                data.sales_growth ??

                data.growth_rate ??

                0

            ),


        predicted_sales:
            predictedSales,


        average_sales:

            toNumber(

                data.average_sales ??

                data.averageSales ??

                data["Average Sales"] ??

                0

            ),


        best_category:

            data.best_category ??

            data.bestCategory ??

            data["Best Category"] ??

            "N/A",


        model:

            data.model ??

            data.model_name ??

            data.modelName ??

            "Unknown",


        sales_trend:

            normalizeSalesTrend(
                salesTrend
            ),


        category_sales:

            normalizeCategorySales(
                categorySales
            ),


        region_sales:

            normalizeRegionSales(
                regionSales
            )

    };

};


// =====================================================
// NORMALIZE PREDICTION RESPONSE
// =====================================================

const normalizePrediction = (response) => {

    let data = response;


    // =================================================
    // { prediction: {...} }
    // =================================================

    if (
        data?.prediction &&
        typeof data.prediction === "object" &&
        !Array.isArray(data.prediction)
    ) {

        data = data.prediction;

    }


    // =================================================
    // { data: {...} }
    // =================================================

    if (
        data?.data &&
        typeof data.data === "object" &&
        !Array.isArray(data.data)
    ) {

        data = data.data;

    }


    // =================================================
    // { result: {...} }
    // =================================================

    if (
        data?.result &&
        typeof data.result === "object" &&
        !Array.isArray(data.result)
    ) {

        data = data.result;

    }


    // =================================================
    // DIRECT NUMBER
    // =================================================

    if (
        typeof data === "number"
    ) {

        return {

            prediction:
                toNumber(data),

            predicted_sales:
                toNumber(data),

            model:
                "Unknown"

        };

    }


    // =================================================
    // INVALID RESPONSE
    // =================================================

    if (
        !data ||
        typeof data !== "object" ||
        Array.isArray(data)
    ) {

        return {

            prediction: 0,

            predicted_sales: 0,

            model: "Unknown"

        };

    }


    // =================================================
    // PREDICTION VALUE
    // =================================================

    const prediction =

        toNumber(

            data.prediction ??

            data.predicted_sales ??

            data.predictedSales ??

            data.forecast ??

            data.value ??

            data.sales ??

            0

        );


    // =================================================
    // MODEL
    // =================================================

    const model =

        data.model ??

        data.model_name ??

        data.modelName ??

        "Unknown";


    return {

        ...data,

        prediction:

            prediction,

        predicted_sales:

            prediction,

        model:

            model

    };

};


// =====================================================
// NORMALIZE FEATURE IMPORTANCE
// =====================================================

const normalizeFeatures = (response) => {

    let data = response;


    // =================================================
    // DIRECT ARRAY
    // =================================================

    if (
        Array.isArray(data)
    ) {

        return data;

    }


    // =================================================
    // { features: [...] }
    // =================================================

    if (
        Array.isArray(data?.features)
    ) {

        return data.features;

    }


    // =================================================
    // { data: { features: [...] } }
    // =================================================

    if (
        Array.isArray(data?.data?.features)
    ) {

        return data.data.features;

    }


    // =================================================
    // { data: [...] }
    // =================================================

    if (
        Array.isArray(data?.data)
    ) {

        return data.data;

    }


    // =================================================
    // { result: [...] }
    // =================================================

    if (
        Array.isArray(data?.result)
    ) {

        return data.result;

    }


    return [];

};


// =====================================================
// NORMALIZE REPORT
// =====================================================

const normalizeReport = (response) => {

    let data = response;


    // =================================================
    // ACTUAL BACKEND RESPONSE
    //
    // {
    //     success: true,
    //     report: {...}
    // }
    // =================================================

    if (
        data?.report &&
        typeof data.report === "object" &&
        !Array.isArray(data.report)
    ) {

        data = data.report;

    }


    // =================================================
    // { data: { report: {...} } }
    // =================================================

    else if (
        data?.data?.report &&
        typeof data.data.report === "object" &&
        !Array.isArray(data.data.report)
    ) {

        data = data.data.report;

    }


    // =================================================
    // { data: {...} }
    // =================================================

    else if (
        data?.data &&
        typeof data.data === "object" &&
        !Array.isArray(data.data)
    ) {

        data = data.data;

    }


    // =================================================
    // { result: {...} }
    // =================================================

    else if (
        data?.result &&
        typeof data.result === "object" &&
        !Array.isArray(data.result)
    ) {

        data = data.result;

    }


    // =================================================
    // INVALID
    // =================================================

    if (
        !data ||
        typeof data !== "object" ||
        Array.isArray(data)
    ) {

        return {};

    }


    return {

        ...data,


        total_sales:

            toNumber(
                data.total_sales ??
                data.revenue ??
                data.Revenue
            ),


        profit:

            toNumber(
                data.profit ??
                data.Profit
            ),


        growth:

            toNumber(
                data.growth ??
                data.sales_growth
            ),


        predicted_sales:

            toNumber(
                data.predicted_sales ??
                data.prediction ??
                data.predictedSales
            ),


        average_sales:

            toNumber(
                data.average_sales ??
                data.averageSales
            ),


        best_category:

            data.best_category ??
            data.bestCategory ??
            "N/A",


        model:

            data.model ??
            data.model_name ??
            "Unknown",


        sales_trend:

            normalizeSalesTrend(
                data.sales_trend
            ),


        category_sales:

            normalizeCategorySales(
                data.category_sales
            ),


        region_sales:

            normalizeRegionSales(
                data.region_sales
            )

    };

};


// =====================================================
// NORMALIZE HEALTH
// =====================================================

const normalizeHealth = (response) => {

    let data = response;


    // =================================================
    // { health: {...} }
    // =================================================

    if (
        data?.health &&
        typeof data.health === "object" &&
        !Array.isArray(data.health)
    ) {

        data = data.health;

    }


    // =================================================
    // { data: {...} }
    // =================================================

    if (
        data?.data &&
        typeof data.data === "object" &&
        !Array.isArray(data.data)
    ) {

        data = data.data;

    }


    // =================================================
    // { result: {...} }
    // =================================================

    if (
        data?.result &&
        typeof data.result === "object" &&
        !Array.isArray(data.result)
    ) {

        data = data.result;

    }


    // =================================================
    // INVALID
    // =================================================

    if (
        !data ||
        typeof data !== "object" ||
        Array.isArray(data)
    ) {

        return {

            success: false,

            status: "Unknown",

            service: "Sales Intelligence API"

        };

    }


    return {

        success:
            data.success ??
            true,

        status:

            data.status ??

            "Unknown",

        service:

            data.service ??

            "Sales Intelligence API"

    };

};


// =====================================================
// FETCH SALES DASHBOARD
// GET /sales/
// =====================================================

export const fetchSales = async () => {

    try {

        const response =
            await api.get(
                "/sales/"
            );


        console.log(
            "================================="
        );

        console.log(
            "SALES API RESPONSE:"
        );

        console.log(
            response.data
        );

        console.log(
            "================================="
        );


        const sales =
            normalizeSales(
                response.data
            );


        console.log(
            "NORMALIZED SALES:"
        );

        console.log(
            sales
        );


        return sales;

    }

    catch (error) {

        console.error(
            "Sales Dashboard API Error:",
            error
        );

        throw error;

    }

};


// =====================================================
// FETCH SALES PREDICTION
// GET /sales/predict
// =====================================================

export const fetchSalesPrediction = async () => {

    try {

        const response =
            await api.get(
                "/sales/predict"
            );


        console.log(
            "SALES PREDICTION API RESPONSE:",
            response.data
        );


        const prediction =
            normalizePrediction(
                response.data
            );


        console.log(
            "NORMALIZED PREDICTION:",
            prediction
        );


        return prediction;

    }

    catch (error) {

        console.error(
            "Sales Prediction API Error:",
            error
        );

        throw error;

    }

};


// =====================================================
// FETCH FEATURE IMPORTANCE
// GET /sales/feature-importance
// =====================================================

export const fetchFeatureImportance = async () => {

    try {

        const response =
            await api.get(
                "/sales/feature-importance"
            );


        console.log(
            "FEATURE IMPORTANCE API RESPONSE:",
            response.data
        );


        const features =
            normalizeFeatures(
                response.data
            );


        console.log(
            "NORMALIZED FEATURES:",
            features
        );


        return features;

    }

    catch (error) {

        console.error(
            "Feature Importance API Error:",
            error
        );

        throw error;

    }

};


// =====================================================
// FETCH SALES REPORT
// GET /sales/report
// =====================================================

export const fetchSalesReport = async () => {

    try {

        const response =
            await api.get(
                "/sales/report"
            );


        console.log(
            "SALES REPORT API RESPONSE:",
            response.data
        );


        const report =
            normalizeReport(
                response.data
            );


        console.log(
            "NORMALIZED SALES REPORT:",
            report
        );


        return report;

    }

    catch (error) {

        console.error(
            "Sales Report API Error:",
            error
        );

        throw error;

    }

};


// =====================================================
// FETCH SALES HEALTH
// GET /sales/health
// =====================================================

export const fetchSalesHealth = async () => {

    try {

        const response =
            await api.get(
                "/sales/health"
            );


        console.log(
            "SALES HEALTH API RESPONSE:",
            response.data
        );


        const health =
            normalizeHealth(
                response.data
            );


        console.log(
            "NORMALIZED SALES HEALTH:",
            health
        );


        return health;

    }

    catch (error) {

        console.error(
            "Sales Health API Error:",
            error
        );

        throw error;

    }

};


// =====================================================
// RUN SALES BACKGROUND TASK
// POST /tasks/sales
// =====================================================

export const runSalesTask = async (
    payload = {}
) => {

    try {

        const response =
            await api.post(
                "/tasks/sales",
                payload
            );


        console.log(
            "SALES TASK API RESPONSE:",
            response.data
        );


        return response.data || {};

    }

    catch (error) {

        console.error(
            "Sales Task API Error:",
            error
        );

        throw error;

    }

};


// =====================================================
// EXPORT HELPERS
// =====================================================

export {

    EMPTY_SALES,

    toNumber,

    toArray,

    normalizeSales,

    normalizePrediction,

    normalizeFeatures,

    normalizeReport,

    normalizeHealth

};


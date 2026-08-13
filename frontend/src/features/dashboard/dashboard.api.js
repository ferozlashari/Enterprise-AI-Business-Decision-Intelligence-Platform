
import api from "../../api/axios";

// =====================================================
// ENTERPRISE AI BUSINESS DECISION INTELLIGENCE PLATFORM
//
// DASHBOARD API
//
// Author: Feroz Ali
//
// Responsibilities:
// - Dashboard API communication
// - FastAPI response unwrapping
// - KPI normalization
// - Sales trend normalization
// - Forecast normalization
// - Inventory normalization
// - Customer segmentation normalization
// - Duplicate customer segment aggregation
// - Recommendation normalization
// - Alert normalization
// - Safe Axios error handling
// =====================================================


// =====================================================
// EMPTY DASHBOARD
// =====================================================

export const EMPTY_DASHBOARD = {
    revenue: 0,
    profit: 0,
    inventory: 0,
    customers: 0,

    sales_trend: [],
    forecast: [],
    inventory_data: [],
    customer_segments: [],

    model_status: "unknown",

    alerts: 0,
    alert_items: [],

    recommendations: [],

    status: "unknown",
};


// =====================================================
// TYPE HELPERS
// =====================================================

const isObject = (value) => {
    return (
        value !== null &&
        typeof value === "object" &&
        !Array.isArray(value)
    );
};


const isArray = (value) => {
    return Array.isArray(value);
};


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
// SAFE INTEGER
// =====================================================

const toInteger = (value, fallback = 0) => {

    const number = toNumber(
        value,
        fallback
    );

    return Number.isFinite(number)
        ? Math.trunc(number)
        : fallback;
};


// =====================================================
// FIRST VALID VALUE
// =====================================================

const firstValue = (...values) => {

    for (const value of values) {

        if (
            value !== undefined &&
            value !== null &&
            value !== ""
        ) {
            return value;
        }
    }

    return undefined;
};


// =====================================================
// SAFE STRING
// =====================================================

const toStringValue = (
    value,
    fallback = ""
) => {

    if (
        value === null ||
        value === undefined
    ) {
        return fallback;
    }

    const result = String(value).trim();

    return result || fallback;
};


// =====================================================
// SAFE BOOLEAN
// =====================================================

const toBoolean = (
    value,
    fallback = false
) => {

    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {
        return fallback;
    }

    if (typeof value === "boolean") {
        return value;
    }

    if (typeof value === "number") {
        return value !== 0;
    }

    if (typeof value === "string") {

        const normalized =
            value
                .trim()
                .toLowerCase();

        if (
            normalized === "true" ||
            normalized === "1" ||
            normalized === "yes" ||
            normalized === "y"
        ) {
            return true;
        }

        if (
            normalized === "false" ||
            normalized === "0" ||
            normalized === "no" ||
            normalized === "n"
        ) {
            return false;
        }
    }

    return fallback;
};


// =====================================================
// UNWRAP AXIOS RESPONSE
// =====================================================

const unwrapAxiosResponse = (response) => {

    if (!response) {
        return null;
    }

    // Axios response:
    //
    // {
    //     data: {...},
    //     status: 200,
    //     headers: {...}
    // }

    if (
        isObject(response) &&
        response.data !== undefined
    ) {
        return response.data;
    }

    return response;
};


// =====================================================
// DASHBOARD PAYLOAD UNWRAPPER
//
// Supports:
//
// {
//     dashboard: {...}
// }
//
// {
//     executive: {...}
// }
//
// {
//     payload: {...}
// }
//
// {
//     result: {...}
// }
//
// {
//     data: {...}
// }
//
// IMPORTANT:
//
// We intentionally DO NOT blindly unwrap data.data.
// "data" may legitimately contain analytics data.
// =====================================================

const unwrapDashboardPayload = (
    response,
    maxDepth = 8
) => {

    let data =
        unwrapAxiosResponse(response);

    if (
        !data ||
        !isObject(data)
    ) {
        return null;
    }

    let depth = 0;

    while (
        depth < maxDepth &&
        isObject(data)
    ) {

        const candidates = [

            data.dashboard,

            data.executive,

            data.payload,

            data.result,

        ];

        let next = null;

        for (
            const candidate
            of candidates
        ) {

            if (
                isObject(candidate)
            ) {

                next = candidate;

                break;
            }
        }

        if (
            !next ||
            next === data
        ) {
            break;
        }

        data = next;

        depth += 1;
    }

    return data;
};


// =====================================================
// NORMALIZE SALES TREND
// =====================================================

const normalizeSalesTrend = (
    value
) => {

    if (!isArray(value)) {
        return [];
    }

    return value
        .map(
            (item, index) => {

                // ---------------------------------
                // NUMBER
                // ---------------------------------

                if (
                    typeof item === "number"
                ) {

                    const sales =
                        toNumber(item);

                    return {

                        month:
                            `Period ${index + 1}`,

                        sales,

                        value:
                            sales,
                    };
                }


                // ---------------------------------
                // STRING
                // ---------------------------------

                if (
                    typeof item === "string"
                ) {

                    const numericValue =
                        toNumber(item);

                    return {

                        month:
                            `Period ${index + 1}`,

                        sales:
                            numericValue,

                        value:
                            numericValue,
                    };
                }


                // ---------------------------------
                // OBJECT
                // ---------------------------------

                if (
                    isObject(item)
                ) {

                    const sales =
                        toNumber(
                            firstValue(

                                item.sales,

                                item.Sales,

                                item.value,

                                item.revenue,

                                item.total_sales,

                                item.totalSales,

                                item.predicted_sales,

                                item.predictedSales,

                                item.y,

                                item.amount,

                            )
                        );

                    const month =
                        firstValue(

                            item.month,

                            item.Month,

                            item.date,

                            item.Date,

                            item.period,

                            item.Period,

                            item.name,

                            item.label,

                            item.x,

                        );

                    return {

                        ...item,

                        month:
                            toStringValue(
                                month,
                                `Period ${index + 1}`
                            ),

                        sales,

                        value:
                            sales,
                    };
                }

                return null;
            }
        )
        .filter(Boolean);
};


// =====================================================
// NORMALIZE FORECAST
// =====================================================

const normalizeForecast = (
    value
) => {

    if (!isArray(value)) {
        return [];
    }

    return value
        .map(
            (item, index) => {

                // ---------------------------------
                // NUMBER
                // ---------------------------------

                if (
                    typeof item === "number"
                ) {

                    const forecast =
                        toNumber(item);

                    return {

                        date:
                            `Period ${index + 1}`,

                        forecast,

                        demand:
                            forecast,

                        value:
                            forecast,

                        actual:
                            null,

                        lower:
                            null,

                        upper:
                            null,
                    };
                }


                // ---------------------------------
                // STRING
                // ---------------------------------

                if (
                    typeof item === "string"
                ) {

                    const numericValue =
                        toNumber(item);

                    return {

                        date:
                            `Period ${index + 1}`,

                        forecast:
                            numericValue,

                        demand:
                            numericValue,

                        value:
                            numericValue,

                        actual:
                            null,

                        lower:
                            null,

                        upper:
                            null,
                    };
                }


                // ---------------------------------
                // OBJECT
                // ---------------------------------

                if (
                    isObject(item)
                ) {

                    const forecastValue =
                        toNumber(
                            firstValue(

                                item.forecast,

                                item.Forecast,

                                item.demand,

                                item.prediction,

                                item.predicted,

                                item.predicted_demand,

                                item.predictedDemand,

                                item.yhat,

                                item.y_pred,

                                item.value,

                                item.sales,

                                item.revenue,

                            )
                        );

                    const actual =
                        item.actual !== undefined &&
                        item.actual !== null &&
                        item.actual !== ""
                            ? toNumber(
                                item.actual
                            )
                            : null;

                    const lower =
                        item.lower !== undefined &&
                        item.lower !== null &&
                        item.lower !== ""
                            ? toNumber(
                                item.lower
                            )
                            : null;

                    const upper =
                        item.upper !== undefined &&
                        item.upper !== null &&
                        item.upper !== ""
                            ? toNumber(
                                item.upper
                            )
                            : null;

                    const date =
                        firstValue(

                            item.date,

                            item.Date,

                            item.month,

                            item.Month,

                            item.period,

                            item.Period,

                            item.ds,

                            item.timestamp,

                            item.name,

                        );

                    const demand =
                        toNumber(
                            firstValue(

                                item.demand,

                                item.forecast,

                                item.prediction,

                                item.predicted,

                                item.predicted_demand,

                                item.predictedDemand,

                                item.yhat,

                                item.value,

                                forecastValue,

                            )
                        );

                    return {

                        ...item,

                        date:
                            toStringValue(
                                date,
                                `Period ${index + 1}`
                            ),

                        forecast:
                            forecastValue,

                        demand,

                        value:
                            forecastValue,

                        actual,

                        lower,

                        upper,
                    };
                }

                return null;
            }
        )
        .filter(Boolean);
};


// =====================================================
// NORMALIZE INVENTORY DATA
// =====================================================

const normalizeInventoryData = (
    value
) => {

    if (!isArray(value)) {
        return [];
    }

    return value
        .map(
            (item, index) => {

                // ---------------------------------
                // NUMBER
                // ---------------------------------

                if (
                    typeof item === "number"
                ) {

                    const quantity =
                        Math.max(
                            0,
                            toNumber(item)
                        );

                    return {

                        product:
                            `Product ${index + 1}`,

                        quantity,

                        demand:
                            0,

                        value:
                            quantity,
                    };
                }


                // ---------------------------------
                // STRING
                // ---------------------------------

                if (
                    typeof item === "string"
                ) {

                    const quantity =
                        Math.max(
                            0,
                            toNumber(item)
                        );

                    return {

                        product:
                            `Product ${index + 1}`,

                        quantity,

                        demand:
                            0,

                        value:
                            quantity,
                    };
                }


                // ---------------------------------
                // OBJECT
                // ---------------------------------

                if (
                    isObject(item)
                ) {

                    const quantity =
                        Math.max(
                            0,
                            toNumber(
                                firstValue(

                                    item.quantity,

                                    item.Quantity,

                                    item.stock,

                                    item.Stock,

                                    item.inventory,

                                    item.Inventory,

                                    item.current_stock,

                                    item.currentStock,

                                    item.available_stock,

                                    item.availableStock,

                                    item.inventory_units,

                                    item.inventoryUnits,

                                    item.units,

                                    item.value,

                                )
                            )
                        );

                    const demand =
                        Math.max(
                            0,
                            toNumber(
                                firstValue(

                                    item.demand,

                                    item.Demand,

                                    item.predictedDemand,

                                    item.predicted_demand,

                                    item.predicted,

                                    item.forecast,

                                    item.predicted_sales,

                                    item.predictedSales,

                                )
                            )
                        );

                    const product =
                        firstValue(

                            item.product,

                            item.Product,

                            item.name,

                            item.Name,

                            item["Product Name"],

                            item.product_name,

                            item.productName,

                            item.sku,

                            item.SKU,

                        );

                    return {

                        ...item,

                        product:
                            toStringValue(
                                product,
                                `Product ${index + 1}`
                            ),

                        quantity,

                        demand,

                        value:
                            quantity,
                    };
                }

                return null;
            }
        )
        .filter(Boolean);
};


// =====================================================
// NORMALIZE CUSTOMER SEGMENTS
//
// Duplicate segment names are merged.
//
// Example:
//
// Potential Value: 54
// Potential Value: 47
//
// becomes:
//
// Potential Value: 101
// =====================================================

const normalizeCustomerSegments = (
    value
) => {

    if (!isArray(value)) {
        return [];
    }

    const segmentMap =
        new Map();

    value.forEach(
        (item, index) => {

            // ---------------------------------
            // STRING
            // ---------------------------------

            if (
                typeof item === "string"
            ) {

                const segment =
                    toStringValue(
                        item,
                        `Segment ${index + 1}`
                    );

                const key =
                    segment
                        .trim()
                        .replace(/\s+/g, " ")
                        .toLowerCase();

                if (
                    !segmentMap.has(key)
                ) {

                    segmentMap.set(
                        key,
                        {

                            name:
                                segment,

                            segment:
                                segment,

                            customers:
                                0,

                            value:
                                0,
                        }
                    );
                }

                return;
            }


            // ---------------------------------
            // NUMBER
            // ---------------------------------

            if (
                typeof item === "number"
            ) {

                const count =
                    Math.max(
                        0,
                        toInteger(item)
                    );

                const segment =
                    `Segment ${index + 1}`;

                const key =
                    segment.toLowerCase();

                if (
                    !segmentMap.has(key)
                ) {

                    segmentMap.set(
                        key,
                        {

                            name:
                                segment,

                            segment:
                                segment,

                            customers:
                                count,

                            value:
                                count,
                        }
                    );

                } else {

                    const existing =
                        segmentMap.get(key);

                    existing.customers +=
                        count;

                    existing.value =
                        existing.customers;
                }

                return;
            }


            // ---------------------------------
            // INVALID
            // ---------------------------------

            if (
                !isObject(item)
            ) {
                return;
            }


            // ---------------------------------
            // CUSTOMER COUNT
            // ---------------------------------

            const customers =
                Math.max(
                    0,
                    toInteger(
                        firstValue(

                            item.customers,

                            item.Customers,

                            item.customer_count,

                            item.customerCount,

                            item.count,

                            item.total_customers,

                            item.totalCustomers,

                            item.value,

                            item.size,

                        )
                    )
                );


            // ---------------------------------
            // SEGMENT NAME
            // ---------------------------------

            const rawName =
                firstValue(

                    item.segment,

                    item.Segment,

                    item.name,

                    item.Name,

                    item.label,

                    item.customer_segment,

                    item.customerSegment,

                    item.cluster,

                    item.Cluster,

                );

            const segment =
                toStringValue(
                    rawName,
                    `Segment ${index + 1}`
                );


            // ---------------------------------
            // NORMALIZED KEY
            // ---------------------------------

            const key =
                segment
                    .trim()
                    .replace(/\s+/g, " ")
                    .toLowerCase();


            // ---------------------------------
            // CREATE
            // ---------------------------------

            if (
                !segmentMap.has(key)
            ) {

                segmentMap.set(
                    key,
                    {

                        ...item,

                        name:
                            segment,

                        segment:
                            segment,

                        customers,

                        value:
                            customers,
                    }
                );

            }

            // ---------------------------------
            // MERGE
            // ---------------------------------

            else {

                const existing =
                    segmentMap.get(key);

                existing.customers +=
                    customers;

                existing.value =
                    existing.customers;
            }
        }
    );

    return Array.from(
        segmentMap.values()
    );
};


// =====================================================
// CLUSTER OBJECT → CUSTOMER SEGMENTS
// =====================================================

const normalizeClusters = (
    clusters
) => {

    if (
        !isObject(clusters)
    ) {
        return [];
    }

    return Object.entries(
        clusters
    )
        .map(
            ([cluster, count]) => {

                const numericCount =
                    Math.max(
                        0,
                        toInteger(count)
                    );

                return {

                    name:
                        `Cluster ${cluster}`,

                    segment:
                        `Cluster ${cluster}`,

                    cluster,

                    customers:
                        numericCount,

                    value:
                        numericCount,
                };
            }
        );
};


// =====================================================
// NORMALIZE ALERTS
// =====================================================

const normalizeAlerts = (
    value
) => {

    if (!isArray(value)) {
        return [];
    }

    return value
        .map(
            (item, index) => {

                // ---------------------------------
                // PRIMITIVE
                // ---------------------------------

                if (
                    !isObject(item)
                ) {

                    return {

                        id:
                            index + 1,

                        severity:
                            "MEDIUM",

                        title:
                            "Business Alert",

                        message:
                            toStringValue(
                                item,
                                ""
                            ),

                        category:
                            "System",

                        alert_type:
                            "SYSTEM",

                        is_read:
                            false,

                        is_resolved:
                            false,

                        time:
                            null,
                    };
                }


                return {

                    ...item,

                    id:
                        item.id ??
                        item.alert_id ??
                        item.alertId ??
                        index + 1,

                    severity:
                        toStringValue(
                            firstValue(

                                item.severity,

                                item.Severity,

                                item.priority,

                                item.level,

                            ),
                            "MEDIUM"
                        ),

                    title:
                        toStringValue(
                            firstValue(

                                item.title,

                                item.Title,

                                item.name,

                                item.alert_title,

                                item.alertTitle,

                            ),
                            "Business Alert"
                        ),

                    message:
                        toStringValue(
                            firstValue(

                                item.message,

                                item.Message,

                                item.description,

                                item.reason,

                                item.details,

                            ),
                            ""
                        ),

                    category:
                        toStringValue(
                            firstValue(

                                item.category,

                                item.module,

                                item.type,

                            ),
                            "System"
                        ),

                    alert_type:
                        toStringValue(
                            firstValue(

                                item.alert_type,

                                item.alertType,

                                item.type,

                            ),
                            "SYSTEM"
                        ),

                    is_read:
                        toBoolean(
                            firstValue(

                                item.is_read,

                                item.isRead,

                                false,

                            )
                        ),

                    is_resolved:
                        toBoolean(
                            firstValue(

                                item.is_resolved,

                                item.isResolved,

                                false,

                            )
                        ),

                    time:
                        firstValue(

                            item.time,

                            item.created_at,

                            item.createdAt,

                            item.timestamp,

                            item.date,

                        ) ?? null,
                };
            }
        )
        .filter(Boolean);
};


// =====================================================
// NORMALIZE RECOMMENDATIONS
// =====================================================

const normalizeRecommendations = (
    value
) => {

    if (!isArray(value)) {
        return [];
    }

    return value
        .map(
            (item, index) => {

                // ---------------------------------
                // PRIMITIVE
                // ---------------------------------

                if (
                    !isObject(item)
                ) {

                    const text =
                        toStringValue(
                            item,
                            ""
                        );

                    return {

                        id:
                            index + 1,

                        title:
                            "Recommendation",

                        recommendation:
                            text,

                        description:
                            text,
                    };
                }


                return {

                    ...item,

                    id:
                        item.id ??
                        item.recommendation_id ??
                        item.recommendationId ??
                        index + 1,

                    title:
                        toStringValue(
                            firstValue(

                                item.title,

                                item.name,

                                item.recommendation_title,

                                item.recommendationTitle,

                                item.action,

                            ),
                            "Recommendation"
                        ),

                    recommendation:
                        toStringValue(
                            firstValue(

                                item.recommendation,

                                item.action,

                                item.description,

                                item.message,

                                item.title,

                            ),
                            ""
                        ),

                    description:
                        toStringValue(
                            firstValue(

                                item.description,

                                item.message,

                                item.recommendation,

                                item.action,

                            ),
                            ""
                        ),
                };
            }
        )
        .filter(Boolean);
};


// =====================================================
// NORMALIZE DASHBOARD RESPONSE
// =====================================================

export const normalizeDashboard = (
    response
) => {

    const data =
        unwrapDashboardPayload(
            response
        );

    if (
        !data ||
        !isObject(data)
    ) {

        return {
            ...EMPTY_DASHBOARD,
        };
    }


    // =================================================
    // METRICS
    // =================================================

    const metrics =
        isObject(data.metrics)
            ? data.metrics
            : {};

    const kpis =
        isObject(data.kpis)
            ? data.kpis
            : {};

    const summary =
        isObject(data.summary)
            ? data.summary
            : {};

    const executive =
        isObject(data.executive)
            ? data.executive
            : {};


    // =================================================
    // REVENUE
    // =================================================

    const revenue =
        Math.max(
            0,
            toNumber(
                firstValue(

                    data.revenue,

                    data.total_revenue,

                    data.totalRevenue,

                    data.total_sales,

                    data.totalSales,

                    data["Total Sales"],

                    data["Total Revenue"],

                    metrics.revenue,

                    metrics.total_revenue,

                    metrics.totalRevenue,

                    metrics.total_sales,

                    kpis.revenue,

                    kpis.total_revenue,

                    summary.revenue,

                    summary.total_revenue,

                    executive.revenue,

                )
            )
        );


    // =================================================
    // PROFIT
    // =================================================

    const profit =
        toNumber(
            firstValue(

                data.profit,

                data.total_profit,

                data.totalProfit,

                data.net_profit,

                data.netProfit,

                data["Profit"],

                data["Total Profit"],

                metrics.profit,

                metrics.total_profit,

                metrics.totalProfit,

                kpis.profit,

                kpis.total_profit,

                summary.profit,

                summary.total_profit,

                executive.profit,

            )
        );


    // =================================================
    // INVENTORY
    // =================================================

    const inventory =
        Math.max(
            0,
            toNumber(
                firstValue(

                    data.inventory,

                    data.inventory_units,

                    data.inventoryUnits,

                    data.current_stock,

                    data.currentStock,

                    data.total_inventory,

                    data.totalInventory,

                    data.stock,

                    metrics.inventory,

                    metrics.inventory_units,

                    metrics.inventoryUnits,

                    kpis.inventory,

                    kpis.inventory_units,

                    summary.inventory,

                    summary.total_inventory,

                    executive.inventory,

                )
            )
        );


    // =================================================
    // CUSTOMERS
    // =================================================

    const customers =
        Math.max(
            0,
            toInteger(
                firstValue(

                    data.customers,

                    data.customer_count,

                    data.customerCount,

                    data.total_customers,

                    data.totalCustomers,

                    metrics.customers,

                    metrics.customer_count,

                    metrics.customerCount,

                    kpis.customers,

                    kpis.customer_count,

                    summary.customers,

                    summary.customer_count,

                    executive.customers,

                )
            )
        );


    // =================================================
    // SALES TREND
    // =================================================

    const rawSalesTrend =
        firstValue(

            data.sales_trend,

            data.salesTrend,

            data.sales?.trend,

            data.sales?.sales_trend,

            data.sales?.salesTrend,

            data.sales?.data,

            data.trends?.sales,

            metrics.sales_trend,

            summary.sales_trend,

        );

    const salesTrend =
        normalizeSalesTrend(
            rawSalesTrend
        );


    // =================================================
    // FORECAST
    // =================================================

    const rawForecast =
        firstValue(

            data.forecast,

            data.forecasts,

            data.forecast_data,

            data.forecastData,

            data.sales_forecast,

            data.salesForecast,

            data.demand,

            data.demand_forecast,

            data.demandForecast,

            metrics.forecast,

            summary.forecast,

        );

    const forecast =
        normalizeForecast(
            rawForecast
        );


    // =================================================
    // INVENTORY DATA
    // =================================================

    const rawInventoryData =
        firstValue(

            data.inventory_data,

            data.inventoryData,

            data.inventory?.data,

            data.inventory?.history,

            data.inventory?.trend,

            data.inventory?.products,

            data.inventory?.items,

            metrics.inventory_data,

            summary.inventory_data,

        );

    const inventoryData =
        normalizeInventoryData(
            rawInventoryData
        );


    // =================================================
    // CUSTOMER SEGMENTS
    // =================================================

    const rawCustomerSegments =
        firstValue(

            data.customer_segments,

            data.customerSegments,

            data.customer?.segments,

            data.customer?.data,

            data.customer?.items,

            data.customers_data,

            data.customerData,

            data.segments,

            metrics.customer_segments,

            summary.customer_segments,

        );

    let customerSegments =
        normalizeCustomerSegments(
            rawCustomerSegments
        );


    // =================================================
    // CLUSTER FALLBACK
    // =================================================

    if (
        customerSegments.length === 0 &&
        isObject(data.Clusters)
    ) {

        customerSegments =
            normalizeCustomerSegments(
                normalizeClusters(
                    data.Clusters
                )
            );
    }


    if (
        customerSegments.length === 0 &&
        isObject(data.clusters)
    ) {

        customerSegments =
            normalizeCustomerSegments(
                normalizeClusters(
                    data.clusters
                )
            );
    }


    // =================================================
    // MODEL STATUS
    // =================================================

    const modelStatus =
        toStringValue(
            firstValue(

                data.model_status,

                data.modelStatus,

                data.models_status,

                data.modelsStatus,

                data.ai_status,

                data.aiStatus,

                metrics.model_status,

                metrics.modelStatus,

            ),
            "unknown"
        );


    // =================================================
    // ALERTS
    // =================================================

    let alertCount =
        Math.max(
            0,
            toInteger(
                firstValue(

                    data.alert_count,

                    data.alertCount,

                    data.total_alerts,

                    data.totalAlerts,

                    metrics.alert_count,

                    metrics.alertCount,

                )
            )
        );

    let alertItems = [];


    // -----------------------------------------------
    // ALERT OBJECT
    // -----------------------------------------------

    if (
        isObject(data.alerts)
    ) {

        alertCount =
            Math.max(
                0,
                toInteger(
                    firstValue(

                        data.alerts.count,

                        data.alerts.total,

                        data.alerts.alert_count,

                        data.alerts.alertCount,

                    ),
                    alertCount
                )
            );

        alertItems =
            normalizeAlerts(
                firstValue(

                    data.alerts.alerts,

                    data.alerts.items,

                    data.alerts.data,

                    data.alerts.results,

                )
            );
    }


    // -----------------------------------------------
    // ALERT ARRAY
    // -----------------------------------------------

    else if (
        isArray(data.alerts)
    ) {

        alertItems =
            normalizeAlerts(
                data.alerts
            );

        alertCount =
            alertItems.length;
    }


    // -----------------------------------------------
    // DIRECT ALERT ITEMS
    // -----------------------------------------------

    if (
        alertItems.length === 0 &&
        isArray(data.alert_items)
    ) {

        alertItems =
            normalizeAlerts(
                data.alert_items
            );

        if (
            alertCount === 0
        ) {
            alertCount =
                alertItems.length;
        }
    }


    // -----------------------------------------------
    // ALERT LIST
    // -----------------------------------------------

    if (
        alertItems.length === 0 &&
        isArray(data.alerts_list)
    ) {

        alertItems =
            normalizeAlerts(
                data.alerts_list
            );

        if (
            alertCount === 0
        ) {
            alertCount =
                alertItems.length;
        }
    }


    // -----------------------------------------------
    // FINAL ALERT COUNT
    // -----------------------------------------------

    if (
        alertItems.length > 0 &&
        alertCount === 0
    ) {

        alertCount =
            alertItems.length;
    }


    // =================================================
    // RECOMMENDATIONS
    // =================================================

    const rawRecommendations =
        firstValue(

            data.recommendations,

            data.recommendation,

            data.recommendation_data,

            data.recommendationData,

            data.recommendations?.items,

            data.recommendations?.data,

            metrics.recommendations,

            summary.recommendations,

        );

    let recommendations = [];


    if (
        isArray(rawRecommendations)
    ) {

        recommendations =
            normalizeRecommendations(
                rawRecommendations
            );

    }

    else if (
        isObject(rawRecommendations)
    ) {

        // Handle:
        //
        // {
        //     recommendations: {
        //         items: [...]
        //     }
        // }

        const nested =
            firstValue(

                rawRecommendations.items,

                rawRecommendations.data,

                rawRecommendations.results,

                rawRecommendations.recommendations,

            );

        if (
            isArray(nested)
        ) {

            recommendations =
                normalizeRecommendations(
                    nested
                );

        }

        else {

            recommendations =
                normalizeRecommendations(
                    [
                        rawRecommendations
                    ]
                );
        }
    }


    // =================================================
    // STATUS
    // =================================================

    const rawStatus =
        firstValue(

            data.status,

            data.health,

            data.state,

            metrics.status,

            summary.status,

        );

    const status =
        toStringValue(
            rawStatus,
            "success"
        );


    // =================================================
    // FINAL NORMALIZED DASHBOARD
    // =================================================

    return {

        ...data,

        // ---------------------------------------------
        // KPI
        // ---------------------------------------------

        revenue,

        profit,

        inventory,

        customers,


        // ---------------------------------------------
        // ANALYTICS
        // ---------------------------------------------

        sales_trend:
            salesTrend,

        forecast,

        inventory_data:
            inventoryData,

        customer_segments:
            customerSegments,


        // ---------------------------------------------
        // AI
        // ---------------------------------------------

        model_status:
            modelStatus,


        // ---------------------------------------------
        // ALERTS
        // ---------------------------------------------

        alerts:
            Math.max(
                0,
                alertCount
            ),

        alert_items:
            alertItems,


        // ---------------------------------------------
        // RECOMMENDATIONS
        // ---------------------------------------------

        recommendations:
            recommendations,


        // ---------------------------------------------
        // STATUS
        // ---------------------------------------------

        status,
    };
};


// =====================================================
// FASTAPI ERROR MESSAGE
// =====================================================

const getApiErrorMessage = (
    error,
    fallbackMessage
) => {

    // -----------------------------------------------
    // 401
    // -----------------------------------------------

    if (
        error?.response?.status === 401
    ) {

        return (
            "Your session has expired. " +
            "Please login again."
        );
    }


    // -----------------------------------------------
    // 403
    // -----------------------------------------------

    if (
        error?.response?.status === 403
    ) {

        return (
            error?.response?.data?.detail ||
            "You do not have permission to access this resource."
        );
    }


    // -----------------------------------------------
    // 404
    // -----------------------------------------------

    if (
        error?.response?.status === 404
    ) {

        return (
            error?.response?.data?.detail ||
            "Dashboard endpoint was not found."
        );
    }


    // -----------------------------------------------
    // VALIDATION ERROR
    // -----------------------------------------------

    const detail =
        error?.response?.data?.detail;


    if (
        Array.isArray(detail)
    ) {

        return detail
            .map(
                (item) =>
                    item?.msg ||
                    item?.message ||
                    "Validation error"
            )
            .join(", ");
    }


    // -----------------------------------------------
    // STRING DETAIL
    // -----------------------------------------------

    if (
        typeof detail === "string"
    ) {

        return detail;
    }


    // -----------------------------------------------
    // NETWORK ERROR
    // -----------------------------------------------

    if (
        error?.request &&
        !error?.response
    ) {

        return (
            "Backend server is not reachable. " +
            "Make sure FastAPI is running."
        );
    }


    return (
        error?.message ||
        fallbackMessage
    );
};


// =====================================================
// FETCH EXECUTIVE DASHBOARD
//
// FastAPI:
//
// GET /dashboard/executive
// =====================================================

export const fetchDashboard =
    async () => {

        try {

            const response =
                await api.get(
                    "/dashboard/executive"
                );

            console.log(
                "[Dashboard] Raw response:",
                response?.data
            );

            const dashboard =
                normalizeDashboard(
                    response?.data
                );

            console.log(
                "[Dashboard] Normalized:",
                dashboard
            );

            return dashboard;

        }

        catch (error) {

            console.error(
                "[Dashboard] API error:",
                error
            );

            throw new Error(
                getApiErrorMessage(
                    error,
                    "Unable to load dashboard."
                ),
                { cause: error }
            );
        }
    };


// =====================================================
// FETCH RECOMMENDATIONS
//
// FastAPI:
//
// GET /recommendation/all
//
// ALWAYS RETURNS ARRAY
// =====================================================

export const fetchRecommendations =
    async () => {

        try {

            const response =
                await api.get(
                    "/recommendation/all"
                );

            const data =
                unwrapAxiosResponse(
                    response
                );

            console.log(
                "[Recommendations] Raw response:",
                data
            );


            // -----------------------------------------
            // DIRECT ARRAY
            // -----------------------------------------

            if (
                isArray(data)
            ) {

                return normalizeRecommendations(
                    data
                );
            }


            // -----------------------------------------
            // ALL POSSIBLE ARRAY WRAPPERS
            // -----------------------------------------

            const candidates = [

                data?.recommendations,

                data?.recommendations?.items,

                data?.recommendations?.data,

                data?.recommendations?.results,

                data?.items,

                data?.results,

                data?.data?.recommendations,

                data?.data?.recommendations?.items,

                data?.data?.recommendations?.data,

                data?.data?.recommendations?.results,

                data?.data,

                data?.result?.recommendations,

                data?.result?.recommendations?.items,

                data?.result?.recommendations?.data,

                data?.result,

                data?.payload?.recommendations,

                data?.payload?.items,

                data?.payload?.data,

                data?.payload,

            ];


            for (
                const candidate
                of candidates
            ) {

                if (
                    isArray(candidate)
                ) {

                    return normalizeRecommendations(
                        candidate
                    );
                }
            }


            // -----------------------------------------
            // SINGLE RECOMMENDATION
            // -----------------------------------------

            const single =
                firstValue(

                    data?.recommendation,

                    data?.data?.recommendation,

                    data?.result?.recommendation,

                    data?.payload?.recommendation,

                );

            if (
                isObject(single)
            ) {

                return normalizeRecommendations(
                    [
                        single
                    ]
                );
            }


            return [];

        }

        catch (error) {

            console.error(
                "[Recommendations] API error:",
                error
            );

            // Recommendations are optional.
            return [];
        }
    };


// =====================================================
// FETCH BUSINESS ALERTS
//
// FastAPI:
//
// GET /dashboard/alerts
//
// ALWAYS RETURNS ARRAY
// =====================================================

export const fetchAlerts =
    async () => {

        try {

            const response =
                await api.get(
                    "/dashboard/alerts"
                );

            const data =
                unwrapAxiosResponse(
                    response
                );

            console.log(
                "[Alerts] Raw response:",
                data
            );


            // -----------------------------------------
            // DIRECT ARRAY
            // -----------------------------------------

            if (
                isArray(data)
            ) {

                return normalizeAlerts(
                    data
                );
            }


            // -----------------------------------------
            // ARRAY WRAPPERS
            // -----------------------------------------

            const candidates = [

                data?.alerts,

                data?.alerts?.alerts,

                data?.alerts?.items,

                data?.alerts?.data,

                data?.alerts?.results,

                data?.items,

                data?.results,

                data?.data?.alerts,

                data?.data?.alerts?.alerts,

                data?.data?.alerts?.items,

                data?.data?.alerts?.data,

                data?.data?.alerts?.results,

                data?.data,

                data?.result?.alerts,

                data?.result?.alerts?.items,

                data?.result?.alerts?.data,

                data?.result,

                data?.payload?.alerts,

                data?.payload?.items,

                data?.payload?.data,

                data?.payload,

            ];


            for (
                const candidate
                of candidates
            ) {

                if (
                    isArray(candidate)
                ) {

                    return normalizeAlerts(
                        candidate
                    );
                }
            }


            return [];

        }

        catch (error) {

            console.error(
                "[Alerts] API error:",
                error
            );

            // Alerts are optional.
            return [];
        }
    };


// =====================================================
// DASHBOARD HEALTH
//
// FastAPI:
//
// GET /health
// =====================================================

export const fetchDashboardHealth =
    async () => {

        try {

            const response =
                await api.get(
                    "/health"
                );

            return unwrapAxiosResponse(
                response
            );

        }

        catch (error) {

            console.error(
                "[Dashboard Health] API error:",
                error
            );

            return {

                status:
                    "Unavailable",

                message:
                    getApiErrorMessage(
                        error,
                        "Dashboard health unavailable."
                    ),
            };
        }
    };


// =====================================================
// DEFAULT EXPORT
// =====================================================

const dashboardApi = {

    fetchDashboard,

    fetchRecommendations,

    fetchAlerts,

    fetchDashboardHealth,

    normalizeDashboard,

    EMPTY_DASHBOARD,
};


export default dashboardApi;


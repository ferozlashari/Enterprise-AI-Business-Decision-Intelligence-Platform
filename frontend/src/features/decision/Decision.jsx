
import {
    useEffect,
    useMemo,
    useState,
} from "react";

import {
    Loader2,
    PlayCircle,
    History,
    RefreshCcw,
    ShieldAlert,
    TrendingUp,
    Database,
    Users,
} from "lucide-react";

import {
    runDecisionEngine,
    fetchExecutiveDecisions,
    fetchDecisionRecommendations,
    fetchLatestDecision,
    fetchSalesMetrics,
    fetchForecastMetrics,
    fetchInventoryMetrics,
    fetchCustomerMetrics,
} from "./decision.api";

import RiskCard from "./components/RiskCard";
import RecommendationCard from "./components/RecommendationCard";
import ImpactChart from "./components/ImpactChart";

// =====================================================
// DEFAULT INPUTS
// =====================================================

const DEFAULT_INPUTS = {
    predicted_sales: "",
    inventory: "",
    forecast_growth: "",
    customer_churn: "",
    revenue: "",
    profit: "",
    customers: "",
};

// =====================================================
// BASIC HELPERS
// =====================================================

const isObject = (value) =>
    value !== null &&
    typeof value === "object" &&
    !Array.isArray(value);

const isArray = Array.isArray;

const hasValue = (value) =>
    value !== undefined &&
    value !== null &&
    value !== "";

// =====================================================
// NUMBER NORMALIZATION
// =====================================================

const toNumber = (value, fallback = 0) => {
    if (!hasValue(value)) {
        return fallback;
    }

    if (typeof value === "number") {
        return Number.isFinite(value)
            ? value
            : fallback;
    }

    if (typeof value === "string") {
        const cleaned = value
            .replace(/,/g, "")
            .replace(/\$/g, "")
            .replace(/%/g, "")
            .trim();

        if (!cleaned) {
            return fallback;
        }

        const parsed = Number(cleaned);

        return Number.isFinite(parsed)
            ? parsed
            : fallback;
    }

    const parsed = Number(value);

    return Number.isFinite(parsed)
        ? parsed
        : fallback;
};

const toInteger = (value, fallback = 0) =>
    Math.max(
        0,
        Math.floor(
            toNumber(
                value,
                fallback
            )
        )
    );

const clamp = (
    value,
    min,
    max
) =>
    Math.max(
        min,
        Math.min(
            max,
            value
        )
    );

// =====================================================
// RESPONSE UNWRAPPER
// =====================================================

const unwrapResponse = (response) => {
    if (!response) {
        return null;
    }

    /*
     * Axios response:
     *
     * {
     *     data: {...}
     * }
     */

    if (
        response.data !== undefined &&
        (
            isObject(response.data) ||
            isArray(response.data)
        )
    ) {
        return response.data;
    }

    return response;
};

// =====================================================
// PATH HELPERS
// =====================================================

const getByPath = (
    source,
    path
) => {
    if (
        source === null ||
        source === undefined
    ) {
        return undefined;
    }

    const parts =
        path.split(".");

    let current = source;

    for (const part of parts) {
        if (
            current === null ||
            current === undefined
        ) {
            return undefined;
        }

        if (
            typeof current !== "object"
        ) {
            return undefined;
        }

        current =
            current[part];
    }

    return current;
};

const firstPathValue = (
    source,
    paths
) => {
    for (const path of paths) {
        const value =
            getByPath(
                source,
                path
            );

        if (hasValue(value)) {
            return value;
        }
    }

    return undefined;
};

// =====================================================
// TEXT NORMALIZATION
// =====================================================

/*
 * Handles:
 *
 * "Low profit margin"
 *
 * ["Low profit margin"]
 *
 * {"Low profit margin"}
 *
 * {"Action 1","Action 2","Action 3"}
 *
 * PostgreSQL-style array strings.
 */

const cleanText = (value) => {
    if (
        value === null ||
        value === undefined
    ) {
        return "";
    }

    // -------------------------------------------------
    // STRING
    // -------------------------------------------------

    if (typeof value === "string") {
        let text = value.trim();

        if (!text) {
            return "";
        }

        /*
         * PostgreSQL array representation:
         *
         * {"Low profit margin"}
         *
         * {"Action 1","Action 2","Action 3"}
         */

        if (
            text.startsWith("{") &&
            text.endsWith("}")
        ) {
            const inner =
                text
                    .slice(1, -1)
                    .trim();

            if (!inner) {
                return "";
            }

            const values = [];

            let current = "";
            let insideQuotes = false;
            let escaped = false;

            for (
                const character of inner
            ) {
                if (escaped) {
                    current += character;
                    escaped = false;
                    continue;
                }

                if (
                    character === "\\"
                ) {
                    escaped = true;
                    continue;
                }

                if (
                    character === '"'
                ) {
                    insideQuotes =
                        !insideQuotes;

                    continue;
                }

                if (
                    character === "," &&
                    !insideQuotes
                ) {
                    const cleaned =
                        current.trim();

                    if (cleaned) {
                        values.push(
                            cleaned
                        );
                    }

                    current = "";

                    continue;
                }

                current += character;
            }

            const last =
                current.trim();

            if (last) {
                values.push(last);
            }

            if (values.length > 0) {
                return values
                    .map(cleanText)
                    .filter(Boolean)
                    .join(", ");
            }
        }

        /*
         * JSON array.
         */

        if (
            text.startsWith("[") &&
            text.endsWith("]")
        ) {
            try {
                const parsed =
                    JSON.parse(text);

                if (
                    Array.isArray(parsed)
                ) {
                    return parsed
                        .map(cleanText)
                        .filter(Boolean)
                        .join(", ");
                }
            } catch {
                // Continue.
            }
        }

        /*
         * JSON object.
         */

        if (
            text.startsWith("{") &&
            text.endsWith("}")
        ) {
            try {
                const parsed =
                    JSON.parse(text);

                if (isObject(parsed)) {
                    return Object.values(
                        parsed
                    )
                        .map(cleanText)
                        .filter(Boolean)
                        .join(", ");
                }
            } catch {
                /*
                 * PostgreSQL array was
                 * already handled above.
                 */
            }
        }

        /*
         * Quoted JSON string.
         */

        if (
            text.startsWith('"') &&
            text.endsWith('"')
        ) {
            try {
                const parsed =
                    JSON.parse(text);

                if (
                    typeof parsed === "string"
                ) {
                    return parsed.trim();
                }
            } catch {
                // Continue.
            }
        }

        return text;
    }

    // -------------------------------------------------
    // ARRAY
    // -------------------------------------------------

    if (Array.isArray(value)) {
        return value
            .flat(Infinity)
            .map(cleanText)
            .filter(Boolean)
            .join(", ");
    }

    // -------------------------------------------------
    // NUMBER / BOOLEAN
    // -------------------------------------------------

    if (
        typeof value === "number" ||
        typeof value === "boolean"
    ) {
        return String(value);
    }

    // -------------------------------------------------
    // OBJECT
    // -------------------------------------------------

    if (isObject(value)) {
        return Object.values(value)
            .map(cleanText)
            .filter(Boolean)
            .join(", ");
    }

    return "";
};

// =====================================================
// RISK NORMALIZATION
// =====================================================

const normalizeRiskLevel = (
    value
) => {
    const normalized =
        String(
            value ?? "LOW"
        )
            .trim()
            .toUpperCase();

    if (
        normalized === "CRITICAL"
    ) {
        return "CRITICAL";
    }

    if (
        normalized === "HIGH"
    ) {
        return "HIGH";
    }

    if (
        normalized === "MEDIUM" ||
        normalized === "MODERATE"
    ) {
        return "MEDIUM";
    }

    return "LOW";
};

const normalizeRiskItem = (
    item
) => {
    if (
        item === null ||
        item === undefined
    ) {
        return "";
    }

    if (
        typeof item === "string"
    ) {
        return cleanText(item);
    }

    if (Array.isArray(item)) {
        return item
            .flat(Infinity)
            .map(normalizeRiskItem)
            .filter(Boolean)
            .join(", ");
    }

    if (isObject(item)) {
        const value =
            item.message ??
            item.description ??
            item.reason ??
            item.risk ??
            item.title ??
            item.name ??
            item.text ??
            item.content;

        if (
            value !== undefined
        ) {
            return cleanText(value);
        }

        return cleanText(item);
    }

    return cleanText(item);
};

const normalizeRisks = (
    value
) => {
    if (
        value === null ||
        value === undefined
    ) {
        return [];
    }

    // -------------------------------------------------
    // ARRAY
    // -------------------------------------------------

    if (Array.isArray(value)) {
        return value
            .flat(Infinity)
            .flatMap((item) => {
                if (
                    isObject(item)
                ) {
                    const nested =
                        item.risks ??
                        item.identified_risks ??
                        item.items ??
                        item.data;

                    if (
                        nested !== undefined
                    ) {
                        return normalizeRisks(
                            nested
                        );
                    }
                }

                const text =
                    normalizeRiskItem(
                        item
                    );

                return text
                    ? [text]
                    : [];
            })
            .filter(Boolean);
    }

    // -------------------------------------------------
    // STRING
    // -------------------------------------------------

    if (
        typeof value === "string"
    ) {
        const text =
            value.trim();

        if (!text) {
            return [];
        }

        /*
         * PostgreSQL array.
         */

        if (
            text.startsWith("{") &&
            text.endsWith("}")
        ) {
            const inner =
                text.slice(1, -1);

            const values = [];

            let current = "";
            let insideQuotes = false;
            let escaped = false;

            for (
                const character of inner
            ) {
                if (escaped) {
                    current += character;
                    escaped = false;
                    continue;
                }

                if (
                    character === "\\"
                ) {
                    escaped = true;
                    continue;
                }

                if (
                    character === '"'
                ) {
                    insideQuotes =
                        !insideQuotes;

                    continue;
                }

                if (
                    character === "," &&
                    !insideQuotes
                ) {
                    if (
                        current.trim()
                    ) {
                        values.push(
                            current.trim()
                        );
                    }

                    current = "";

                    continue;
                }

                current += character;
            }

            if (
                current.trim()
            ) {
                values.push(
                    current.trim()
                );
            }

            return values
                .map(cleanText)
                .filter(Boolean);
        }

        /*
         * JSON array.
         */

        if (
            text.startsWith("[") &&
            text.endsWith("]")
        ) {
            try {
                const parsed =
                    JSON.parse(text);

                if (
                    Array.isArray(parsed)
                ) {
                    return normalizeRisks(
                        parsed
                    );
                }
            } catch {
                // Continue.
            }
        }

        /*
         * Normal multiline risks.
         */

        return text
            .split(/\r?\n/)
            .map(
                (item) =>
                    item
                        .replace(
                            /^[-•*]\s*/,
                            ""
                        )
                        .trim()
            )
            .filter(Boolean);
    }

    // -------------------------------------------------
    // OBJECT
    // -------------------------------------------------

    if (isObject(value)) {
        const nested =
            value.risks ??
            value.identified_risks ??
            value.items ??
            value.data;

        if (
            nested !== undefined
        ) {
            return normalizeRisks(
                nested
            );
        }

        const text =
            normalizeRiskItem(
                value
            );

        return text
            ? [text]
            : [];
    }

    return [];
};

const normalizeRecommendations = (
    value
) => {
    if (
        value === null ||
        value === undefined
    ) {
        return [];
    }

    // -------------------------------------------------
    // ARRAY
    // -------------------------------------------------

    if (Array.isArray(value)) {
        return value
            .flat(Infinity)
            .flatMap((item) => {
                if (
                    isObject(item)
                ) {
                    const recommendation =
                        item.recommendation ??
                        item.action ??
                        item.message ??
                        item.description ??
                        item.title ??
                        item.text ??
                        item.content;

                    if (
                        recommendation !==
                        undefined
                    ) {
                        return normalizeRecommendations(
                            recommendation
                        );
                    }

                    const nested =
                        item.recommendations ??
                        item.actions ??
                        item.recommended_actions ??
                        item.items ??
                        item.data;

                    if (
                        nested !== undefined
                    ) {
                        return normalizeRecommendations(
                            nested
                        );
                    }

                    return [];
                }

                const text =
                    cleanText(item);

                return text
                    ? [text]
                    : [];
            })
            .filter(Boolean);
    }

    // -------------------------------------------------
    // STRING
    // -------------------------------------------------

    if (
        typeof value === "string"
    ) {
        const text =
            value.trim();

        if (!text) {
            return [];
        }

        /*
         * PostgreSQL array:
         *
         * {"Action 1","Action 2"}
         */

        if (
            text.startsWith("{") &&
            text.endsWith("}")
        ) {
            const inner =
                text.slice(1, -1);

            const values = [];

            let current = "";
            let insideQuotes = false;
            let escaped = false;

            for (
                const character of inner
            ) {
                if (escaped) {
                    current += character;
                    escaped = false;
                    continue;
                }

                if (
                    character === "\\"
                ) {
                    escaped = true;
                    continue;
                }

                if (
                    character === '"'
                ) {
                    insideQuotes =
                        !insideQuotes;

                    continue;
                }

                if (
                    character === "," &&
                    !insideQuotes
                ) {
                    if (
                        current.trim()
                    ) {
                        values.push(
                            current.trim()
                        );
                    }

                    current = "";

                    continue;
                }

                current += character;
            }

            if (
                current.trim()
            ) {
                values.push(
                    current.trim()
                );
            }

            return values
                .map(cleanText)
                .filter(Boolean);
        }

        /*
         * JSON array.
         */

        if (
            text.startsWith("[") &&
            text.endsWith("]")
        ) {
            try {
                const parsed =
                    JSON.parse(text);

                if (
                    Array.isArray(parsed)
                ) {
                    return normalizeRecommendations(
                        parsed
                    );
                }
            } catch {
                // Continue.
            }
        }

        /*
         * JSON object.
         */

        if (
            text.startsWith("{") &&
            text.endsWith("}")
        ) {
            try {
                const parsed =
                    JSON.parse(text);

                if (isObject(parsed)) {
                    return normalizeRecommendations(
                        parsed
                    );
                }
            } catch {
                // Continue.
            }
        }

        /*
         * Normal multiline response.
         */

        return text
            .split(/\r?\n/)
            .map(
                (item) =>
                    item
                        .replace(
                            /^[-•*]\s*/,
                            ""
                        )
                        .trim()
            )
            .filter(Boolean);
    }

    // -------------------------------------------------
    // OBJECT
    // -------------------------------------------------

    if (isObject(value)) {
        const nested =
            value.recommendations ??
            value.actions ??
            value.recommended_actions ??
            value.items ??
            value.data;

        if (
            nested !== undefined
        ) {
            return normalizeRecommendations(
                nested
            );
        }

        const recommendation =
            value.recommendation ??
            value.action ??
            value.message ??
            value.description ??
            value.title ??
            value.text ??
            value.content;

        if (
            recommendation !== undefined
        ) {
            return normalizeRecommendations(
                recommendation
            );
        }

        return Object.values(value)
            .flatMap(
                (item) =>
                    normalizeRecommendations(
                        item
                    )
            )
            .filter(Boolean);
    }

    return [];
};

// =====================================================
// SALES EXTRACTION
// =====================================================

const extractSalesData = (
    response
) => {
    const source =
        unwrapResponse(response);

    if (!source) {
        return {};
    }

    const predictedSales =
        firstPathValue(
            source,
            [
                "predicted_sales",
                "predictedSales",
                "prediction_value",
                "predicted_sales_value",
                "sales_prediction",

                "data.predicted_sales",
                "data.predictedSales",
                "data.prediction_value",
                "data.predicted_sales_value",
                "data.sales_prediction",

                "result.predicted_sales",
                "result.predictedSales",
                "result.prediction_value",
                "result.sales_prediction",

                "prediction.predicted_sales",
                "prediction.predictedSales",
                "prediction.value",
                "prediction.prediction",
            ]
        );

    const revenue =
        firstPathValue(
            source,
            [
                "revenue",
                "total_revenue",
                "sales_revenue",

                "data.revenue",
                "data.total_revenue",
                "data.sales_revenue",

                "result.revenue",
                "result.total_revenue",
                "result.sales_revenue",

                "metrics.revenue",
                "metrics.total_revenue",
            ]
        );

    const profit =
        firstPathValue(
            source,
            [
                "profit",
                "total_profit",
                "net_profit",

                "data.profit",
                "data.total_profit",
                "data.net_profit",

                "result.profit",
                "result.total_profit",
                "result.net_profit",

                "metrics.profit",
                "metrics.total_profit",
            ]
        );

    return {
        predicted_sales:
            hasValue(predictedSales)
                ? toNumber(
                    predictedSales
                )
                : undefined,

        revenue:
            hasValue(revenue)
                ? toNumber(revenue)
                : undefined,

        profit:
            hasValue(profit)
                ? toNumber(profit)
                : undefined,
    };
};

// =====================================================
// FORECAST EXTRACTION
// =====================================================

const extractForecastData = (
    response
) => {
    const source =
        unwrapResponse(response);

    if (!source) {
        return {};
    }

    const growth =
        firstPathValue(
            source,
            [
                "forecast_growth",
                "forecast_growth_percent",
                "forecast_growth_percentage",
                "growth_rate",
                "growth_percentage",
                "growth_percent",
                "forecast_growth_rate",

                "data.forecast_growth",
                "data.forecast_growth_percent",
                "data.forecast_growth_percentage",
                "data.growth_rate",
                "data.growth_percentage",
                "data.growth_percent",
                "data.forecast_growth_rate",

                "result.forecast_growth",
                "result.forecast_growth_percent",
                "result.growth_rate",
                "result.growth_percentage",
                "result.growth_percent",

                "metrics.forecast_growth",
                "metrics.growth_rate",
                "metrics.growth_percentage",
            ]
        );

    if (!hasValue(growth)) {
        return {
            forecast_growth:
                undefined,
        };
    }

    let number =
        toNumber(
            growth,
            NaN
        );

    if (!Number.isFinite(number)) {
        return {
            forecast_growth:
                undefined,
        };
    }

    /*
     * Ratio:
     *
     * 0.44 -> 44%
     *
     * Percentage:
     *
     * 44 -> 44%
     */

    if (
        number > -1 &&
        number < 1
    ) {
        number *= 100;
    }

    return {
        forecast_growth:
            clamp(
                number,
                -100,
                100
            ),
    };
};

// =====================================================
// INVENTORY EXTRACTION
// =====================================================

const extractInventoryData = (
    response
) => {
    const source =
        unwrapResponse(response);

    if (!source) {
        return {};
    }

    const inventory =
        firstPathValue(
            source,
            [
                "inventory_units",
                "current_stock",
                "inventory",
                "stock",
                "total_inventory",
                "total_stock",
                "inventory_quantity",
                "available_inventory",
                "quantity",

                "data.inventory_units",
                "data.current_stock",
                "data.inventory",
                "data.stock",
                "data.total_inventory",
                "data.total_stock",
                "data.inventory_quantity",
                "data.available_inventory",
                "data.quantity",

                "result.inventory_units",
                "result.current_stock",
                "result.inventory",
                "result.stock",
                "result.total_inventory",
                "result.total_stock",
                "result.inventory_quantity",

                "metrics.inventory",
                "metrics.inventory_units",
                "metrics.current_stock",
                "metrics.stock",

                "summary.inventory",
                "summary.current_stock",
                "summary.total_inventory",
            ]
        );

    return {
        inventory:
            hasValue(inventory)
                ? toNumber(inventory)
                : undefined,
    };
};

// =====================================================
// CUSTOMER EXTRACTION
// =====================================================

const extractCustomerData = (
    response
) => {
    const source =
        unwrapResponse(response);

    if (!source) {
        return {};
    }

    const churn =
        firstPathValue(
            source,
            [
                "customer_churn",
                "churn_rate",
                "churn_percentage",
                "churn_percent",
                "customer_churn_rate",

                "data.customer_churn",
                "data.churn_rate",
                "data.churn_percentage",
                "data.churn_percent",
                "data.customer_churn_rate",

                "result.customer_churn",
                "result.churn_rate",
                "result.churn_percentage",
                "result.churn_percent",

                "metrics.customer_churn",
                "metrics.churn_rate",
                "metrics.churn_percentage",

                "summary.customer_churn",
                "summary.churn_rate",
            ]
        );

    const customers =
        firstPathValue(
            source,
            [
                "customers",
                "customer_count",
                "total_customers",
                "customers_count",

                "data.customers",
                "data.customer_count",
                "data.total_customers",
                "data.customers_count",

                "result.customers",
                "result.customer_count",
                "result.total_customers",

                "metrics.customers",
                "metrics.customer_count",
                "metrics.total_customers",

                "summary.customers",
                "summary.customer_count",
            ]
        );

    let normalizedChurn;

    if (hasValue(churn)) {
        normalizedChurn =
            toNumber(
                churn,
                NaN
            );

        if (
            Number.isFinite(
                normalizedChurn
            )
        ) {
            if (
                normalizedChurn > 0 &&
                normalizedChurn < 1
            ) {
                normalizedChurn *= 100;
            }

            normalizedChurn =
                clamp(
                    normalizedChurn,
                    0,
                    100
                );
        } else {
            normalizedChurn =
                undefined;
        }
    }

    return {
        customer_churn:
            normalizedChurn,

        customers:
            hasValue(customers)
                ? toInteger(
                    customers
                )
                : undefined,
    };
};

// =====================================================
// LIVE INPUT BUILDER
// =====================================================

const buildLiveInputs = ({
    salesResponse,
    forecastResponse,
    inventoryResponse,
    customerResponse,
    previousInputs,
}) => {
    const sales =
        extractSalesData(
            salesResponse
        );

    const forecast =
        extractForecastData(
            forecastResponse
        );

    const inventory =
        extractInventoryData(
            inventoryResponse
        );

    const customer =
        extractCustomerData(
            customerResponse
        );

    const liveOrPrevious = (
        live,
        previous
    ) => {
        if (hasValue(live)) {
            return live;
        }

        return hasValue(previous)
            ? previous
            : "";
    };

    return {
        predicted_sales:
            liveOrPrevious(
                sales.predicted_sales,
                previousInputs.predicted_sales
            ),

        inventory:
            liveOrPrevious(
                inventory.inventory,
                previousInputs.inventory
            ),

        forecast_growth:
            liveOrPrevious(
                forecast.forecast_growth,
                previousInputs.forecast_growth
            ),

        customer_churn:
            liveOrPrevious(
                customer.customer_churn,
                previousInputs.customer_churn
            ),

        revenue:
            liveOrPrevious(
                sales.revenue,
                previousInputs.revenue
            ),

        profit:
            liveOrPrevious(
                sales.profit,
                previousInputs.profit
            ),

        customers:
            liveOrPrevious(
                customer.customers,
                previousInputs.customers
            ),
    };
};

// =====================================================
// RESPONSE METRIC CHECK
// =====================================================

const responseContainsUsefulMetric = (
    response,
    extractor
) => {
    if (!response) {
        return false;
    }

    const result =
        extractor(response);

    return Object.values(
        result
    ).some(hasValue);
};

// =====================================================
// DECISION EXTRACTION
// =====================================================

const extractDecision = (
    response
) => {
    if (!response) {
        return null;
    }

    const source =
        unwrapResponse(response);

    if (!source) {
        return null;
    }

    const candidates = [
        source.decision,

        source.data?.decision,

        source.result?.decision,

        source.latest?.decision,

        source.latest_decision,

        source.data?.latest?.decision,

        source.result?.latest?.decision,
    ];

    for (
        const candidate of candidates
    ) {
        if (isObject(candidate)) {
            return candidate;
        }
    }

    /*
     * Backend may return the decision
     * object directly.
     */

    if (
        isObject(source) &&
        (
            source.risk_level !== undefined ||
            source.risk_score !== undefined ||
            source.identified_risks !== undefined ||
            source.recommendations !== undefined ||
            source.decision_id !== undefined
        )
    ) {
        return source;
    }

    return null;
};

// =====================================================
// RECOMMENDATION RESPONSE EXTRACTION
// =====================================================

const extractRecommendationsFromAny = (
    response
) => {
    if (!response) {
        return [];
    }

    if (Array.isArray(response)) {
        return response;
    }

    const source =
        unwrapResponse(response);

    if (!source) {
        return [];
    }

    const candidates = [
        source.recommendations,
        source.actions,
        source.recommended_actions,

        source.data?.recommendations,
        source.data?.actions,
        source.data?.recommended_actions,

        source.result?.recommendations,
        source.result?.actions,
        source.result?.recommended_actions,

        source.decision?.recommendations,
        source.decision?.actions,

        source.data?.decision?.recommendations,
        source.data?.decision?.actions,

        source.result?.decision?.recommendations,
        source.result?.decision?.actions,
    ];

    for (
        const candidate of candidates
    ) {
        if (
            candidate !== undefined &&
            candidate !== null
        ) {
            return candidate;
        }
    }

    return [];
};

// =====================================================
// HISTORY EXTRACTION
// =====================================================

const extractHistory = (
    response
) => {
    if (!response) {
        return [];
    }

    const source =
        unwrapResponse(response);

    if (!source) {
        return [];
    }

    const candidates = [
        source.history,
        source.decisions,
        source.items,

        source.data?.history,
        source.data?.decisions,
        source.data?.items,

        source.dashboard?.history,
        source.dashboard?.decisions,

        source.result?.history,
        source.result?.decisions,

        source.results,
    ];

    for (
        const candidate of candidates
    ) {
        if (Array.isArray(candidate)) {
            return candidate;
        }
    }

    const single =
        extractDecision(source);

    return single
        ? [single]
        : [];
};

// =====================================================
// HISTORY DECISION
// =====================================================

const getHistoryDecision = (
    entry
) => {
    if (
        !entry ||
        typeof entry !== "object"
    ) {
        return {};
    }

    if (
        isObject(
            entry.decision
        )
    ) {
        return entry.decision;
    }

    if (
        isObject(
            entry.data?.decision
        )
    ) {
        return entry.data.decision;
    }

    if (
        isObject(
            entry.result?.decision
        )
    ) {
        return entry.result.decision;
    }

    return entry;
};

// =====================================================
// HISTORY TIMESTAMP
// =====================================================

const getHistoryTimestamp = (
    entry
) => {
    if (!entry) {
        return null;
    }

    const decision =
        getHistoryDecision(
            entry
        );

    return (
        entry.timestamp ??
        entry.created_at ??
        entry.createdAt ??
        entry.decision_timestamp ??
        entry.executed_at ??
        entry.updated_at ??
        decision.timestamp ??
        decision.created_at ??
        decision.createdAt ??
        decision.executed_at ??
        null
    );
};

// =====================================================
// NORMALIZE DECISION
// =====================================================

const normalizeDecision = (
    value
) => {
    if (!isObject(value)) {
        return null;
    }

    const metrics =
        isObject(value.metrics)
            ? value.metrics
            : {};

    const risks =
        normalizeRisks(
            value.identified_risks ??
            value.risks ??
            value.risk_factors
        );

    const recommendations =
        normalizeRecommendations(
            value.recommendations ??
            value.actions ??
            value.recommended_actions
        );

    let riskScore;

    if (
        hasValue(value.risk_score)
    ) {
        riskScore =
            clamp(
                toNumber(
                    value.risk_score
                ),
                0,
                100
            );
    }

    return {
        ...value,

        /*
         * Never manufacture an ID.
         */

        decision_id:
            value.decision_id ??
            value.id ??
            value.decisionId ??
            null,

        risk_level:
            normalizeRiskLevel(
                value.risk_level ??
                value.risk
            ),

        risk_score:
            riskScore,

        risk_count:
            hasValue(
                value.risk_count
            )
                ? Math.max(
                    0,
                    Math.trunc(
                        toNumber(
                            value.risk_count
                        )
                    )
                )
                : risks.length,

        identified_risks:
            risks,

        recommendations:
            recommendations,

        insights:
            Array.isArray(
                value.insights
            )
                ? value.insights
                : [],

        metrics,
    };
};

// =====================================================
// HISTORY SORT
// =====================================================

const sortHistoryNewestFirst = (
    entries
) => {
    return [...entries].sort(
        (a, b) => {
            const timestampA =
                getHistoryTimestamp(a);

            const timestampB =
                getHistoryTimestamp(b);

            if (
                !timestampA &&
                !timestampB
            ) {
                return 0;
            }

            if (!timestampA) {
                return 1;
            }

            if (!timestampB) {
                return -1;
            }

            const dateA =
                new Date(
                    timestampA
                ).getTime();

            const dateB =
                new Date(
                    timestampB
                ).getTime();

            if (
                Number.isFinite(dateA) &&
                Number.isFinite(dateB)
            ) {
                return dateB - dateA;
            }

            return 0;
        }
    );
};

// =====================================================
// FORMATTERS
// =====================================================

const formatTimestamp = (
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
        return (
            cleanText(value) ||
            "—"
        );
    }

    return date.toLocaleString(
        undefined,
        {
            year: "numeric",
            month: "short",
            day: "numeric",
            hour: "2-digit",
            minute: "2-digit",
        }
    );
};

const formatNumber = (
    value,
    maximumFractionDigits = 2
) => {
    if (!hasValue(value)) {
        return "—";
    }

    const number =
        toNumber(
            value,
            NaN
        );

    if (
        !Number.isFinite(number)
    ) {
        return "—";
    }

    return number.toLocaleString(
        undefined,
        {
            maximumFractionDigits,
        }
    );
};

// =====================================================
// ERROR FORMATTER
// =====================================================

const getErrorMessage = (
    error,
    fallback
) => {
    const detail =
        error?.response?.data?.detail;

    if (Array.isArray(detail)) {
        return (
            detail
                .map(
                    (item) =>
                        item?.msg
                )
                .filter(Boolean)
                .join(", ") ||
            fallback
        );
    }

    if (
        typeof detail === "string"
    ) {
        return detail;
    }

    return (
        error?.message ||
        fallback
    );
};

// =====================================================
// MAIN COMPONENT
// =====================================================

export default function Decision() {
    // =================================================
    // STATE
    // =================================================

    const [
        inputs,
        setInputs,
    ] = useState(
        DEFAULT_INPUTS
    );

    const [
        decision,
        setDecision,
    ] = useState(null);

    const [
        history,
        setHistory,
    ] = useState([]);

    const [
        recommendations,
        setRecommendations,
    ] = useState([]);

    const [
        loading,
        setLoading,
    ] = useState(false);

    const [
        pageLoading,
        setPageLoading,
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
        liveDataLoaded,
        setLiveDataLoaded,
    ] = useState(false);

    // =================================================
    // INITIAL LOAD
    // =================================================

    useEffect(() => {
        loadDashboard(false);

        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    // =================================================
    // LOAD DASHBOARD
    // =================================================

    const loadDashboard = async (
        isRefresh = false
    ) => {
        try {
            if (isRefresh) {
                setRefreshing(true);
            } else {
                setPageLoading(true);
            }

            setError(null);

            const results =
                await Promise.allSettled([
                    fetchExecutiveDecisions(),
                    fetchDecisionRecommendations(),
                    fetchLatestDecision(),
                    fetchSalesMetrics(),
                    fetchForecastMetrics(),
                    fetchInventoryMetrics(),
                    fetchCustomerMetrics(),
                ]);

            const [
                dashboardResult,
                recommendationsResult,
                latestResult,
                salesResult,
                forecastResult,
                inventoryResult,
                customerResult,
            ] = results;

            const dashboardResponse =
                dashboardResult.status ===
                "fulfilled"
                    ? dashboardResult.value
                    : null;

            const recommendationsResponse =
                recommendationsResult.status ===
                "fulfilled"
                    ? recommendationsResult.value
                    : null;

            const latestResponse =
                latestResult.status ===
                "fulfilled"
                    ? latestResult.value
                    : null;

            const salesResponse =
                salesResult.status ===
                "fulfilled"
                    ? salesResult.value
                    : null;

            const forecastResponse =
                forecastResult.status ===
                "fulfilled"
                    ? forecastResult.value
                    : null;

            const inventoryResponse =
                inventoryResult.status ===
                "fulfilled"
                    ? inventoryResult.value
                    : null;

            const customerResponse =
                customerResult.status ===
                "fulfilled"
                    ? customerResult.value
                    : null;

            // =================================================
            // DEBUG
            // =================================================

            console.group(
                "Decision Intelligence"
            );

            console.log(
                "Dashboard:",
                dashboardResponse
            );

            console.log(
                "Recommendations:",
                recommendationsResponse
            );

            console.log(
                "Latest:",
                latestResponse
            );

            console.log(
                "Sales:",
                salesResponse
            );

            console.log(
                "Forecast:",
                forecastResponse
            );

            console.log(
                "Inventory:",
                inventoryResponse
            );

            console.log(
                "Customer:",
                customerResponse
            );

            console.groupEnd();

            // =================================================
            // HISTORY
            // =================================================

            const dashboardHistory =
                extractHistory(
                    dashboardResponse
                );

            setHistory(
                sortHistoryNewestFirst(
                    dashboardHistory
                )
            );

            // =================================================
            // LATEST DECISION
            // =================================================

            const latestDecision =
                normalizeDecision(
                    extractDecision(
                        latestResponse
                    )
                );

            if (latestDecision) {
                setDecision(
                    latestDecision
                );

                if (
                    latestDecision
                        .recommendations
                        .length > 0
                ) {
                    setRecommendations(
                        latestDecision
                            .recommendations
                    );
                }
            }

            // =================================================
            // LIVE INPUTS
            // =================================================

            const liveInputs =
                buildLiveInputs({
                    salesResponse,
                    forecastResponse,
                    inventoryResponse,
                    customerResponse,
                    previousInputs:
                        inputs,
                });

            const hasSalesData =
                responseContainsUsefulMetric(
                    salesResponse,
                    extractSalesData
                );

            const hasForecastData =
                responseContainsUsefulMetric(
                    forecastResponse,
                    extractForecastData
                );

            const hasInventoryData =
                responseContainsUsefulMetric(
                    inventoryResponse,
                    extractInventoryData
                );

            const hasCustomerData =
                responseContainsUsefulMetric(
                    customerResponse,
                    extractCustomerData
                );

            const hasLiveData =
                hasSalesData ||
                hasForecastData ||
                hasInventoryData ||
                hasCustomerData;

            if (hasLiveData) {
                setInputs(
                    liveInputs
                );

                setLiveDataLoaded(
                    true
                );
            }

            // =================================================
            // RECOMMENDATIONS
            // =================================================

            const backendRecommendations =
                normalizeRecommendations(
                    extractRecommendationsFromAny(
                        recommendationsResponse
                    )
                );

            if (
                backendRecommendations.length > 0
            ) {
                setRecommendations(
                    backendRecommendations
                );
            } else if (
                latestDecision
                    ?.recommendations
                    ?.length > 0
            ) {
                setRecommendations(
                    latestDecision
                        .recommendations
                );
            }
        } catch (err) {
            console.error(
                "DECISION DASHBOARD ERROR:",
                err
            );

            setError(
                getErrorMessage(
                    err,
                    "Unable to load decision intelligence."
                )
            );
        } finally {
            setPageLoading(false);
            setRefreshing(false);
        }
    };

    // =================================================
    // INPUT CHANGE
    // =================================================

    const handleChange =
        (field) =>
        (event) => {
            setInputs(
                (previous) => ({
                    ...previous,
                    [field]:
                        event.target.value,
                })
            );
        };

    // =================================================
    // RUN DECISION ENGINE
    // =================================================

    const handleRun = async () => {
        try {
            setLoading(true);
            setError(null);

            const payload = {
                predicted_sales:
                    Math.max(
                        0,
                        toNumber(
                            inputs.predicted_sales
                        )
                    ),

                inventory:
                    Math.max(
                        0,
                        toNumber(
                            inputs.inventory
                        )
                    ),

                forecast_growth:
                    clamp(
                        toNumber(
                            inputs.forecast_growth
                        ),
                        -100,
                        100
                    ),

                customer_churn:
                    clamp(
                        toNumber(
                            inputs.customer_churn
                        ),
                        0,
                        100
                    ),

                revenue:
                    Math.max(
                        0,
                        toNumber(
                            inputs.revenue
                        )
                    ),

                profit:
                    toNumber(
                        inputs.profit
                    ),

                customers:
                    toInteger(
                        inputs.customers
                    ),
            };

            console.log(
                "DECISION ENGINE INPUT:",
                payload
            );

            const result =
                await runDecisionEngine(
                    payload
                );

            console.log(
                "DECISION ENGINE RESULT:",
                result
            );

            const returnedDecision =
                normalizeDecision(
                    extractDecision(
                        result
                    )
                );

            if (returnedDecision) {
                setDecision(
                    returnedDecision
                );

                setRecommendations(
                    Array.isArray(
                        returnedDecision
                            .recommendations
                    )
                        ? returnedDecision
                            .recommendations
                        : []
                );
            }

            /*
             * Refresh latest decision,
             * history and live metrics.
             */

            await loadDashboard(true);
        } catch (err) {
            console.error(
                "DECISION ENGINE ERROR:",
                err
            );

            setError(
                getErrorMessage(
                    err,
                    "The decision engine failed to run."
                )
            );
        } finally {
            setLoading(false);
        }
    };

    // =================================================
    // DISPLAY RECOMMENDATIONS
    // =================================================

    const displayedRecommendations =
        useMemo(
            () => {
                if (
                    Array.isArray(
                        decision?.recommendations
                    ) &&
                    decision
                        .recommendations
                        .length > 0
                ) {
                    return normalizeRecommendations(
                        decision
                            .recommendations
                    );
                }

                return normalizeRecommendations(
                    recommendations
                );
            },
            [
                decision,
                recommendations,
            ]
        );

    // =================================================
    // CURRENT RISK
    // =================================================

    const currentRisk =
        normalizeRiskLevel(
            decision?.risk_level ??
            decision?.risk
        );

    // =================================================
    // IDENTIFIED RISKS
    // =================================================

    const identifiedRisks =
        normalizeRisks(
            decision?.identified_risks ??
            decision?.risks ??
            decision?.risk_factors
        );

    // =================================================
    // RISK SCORE
    // =================================================

    const riskScore =
        hasValue(
            decision?.risk_score
        )
            ? clamp(
                toNumber(
                    decision.risk_score
                ),
                0,
                100
            )
            : null;

    // =================================================
    // DECISION METRICS
    // =================================================

    const decisionMetrics = {
        ...inputs,

        ...(isObject(
            decision?.metrics
        )
            ? decision.metrics
            : {}),
    };

    // =================================================
    // SUMMARY
    // =================================================

    const decisionSummary =
        decision?.summary ??
        decision?.message ??
        decision?.decision_summary ??
        null;

    // =================================================
    // PAGE LOADING
    // =================================================

    if (pageLoading) {
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
                        text-slate-400
                    "
                >
                    <Loader2
                        size={22}
                        className="animate-spin"
                    />

                    Loading Decision Intelligence...
                </div>
            </div>
        );
    }

    // =================================================
    // MAIN UI
    // =================================================

    return (
        <div
            className="
                p-6
                text-white
                space-y-6
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
                    gap-4
                "
            >
                <div>
                    <div
                        className="
                            flex
                            items-center
                            gap-2
                        "
                    >
                        <ShieldAlert
                            size={28}
                            className="text-blue-400"
                        />

                        <h1
                            className="
                                text-3xl
                                font-bold
                            "
                        >
                            Decision Intelligence
                        </h1>
                    </div>

                    <p
                        className="
                            text-slate-400
                            mt-2
                        "
                    >
                        Enterprise decision analysis
                        powered by live business
                        intelligence.
                    </p>
                </div>

                <button
                    type="button"
                    onClick={() =>
                        loadDashboard(true)
                    }
                    disabled={
                        refreshing ||
                        loading
                    }
                    className="
                        flex
                        items-center
                        justify-center
                        gap-2
                        bg-slate-800
                        hover:bg-slate-700
                        disabled:opacity-60
                        px-4
                        py-2.5
                        rounded-lg
                        border
                        border-slate-700
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

            {/* =================================================
                ERROR
            ================================================= */}

            {error && (
                <div
                    className="
                        bg-red-500/10
                        border
                        border-red-500/30
                        rounded-xl
                        px-4
                        py-3
                        text-red-400
                        text-sm
                    "
                >
                    {error}
                </div>
            )}

            {/* =================================================
                STATUS
            ================================================= */}

            <div
                className="
                    flex
                    flex-wrap
                    gap-3
                "
            >
                <div
                    className="
                        flex
                        items-center
                        gap-2
                        bg-slate-900
                        border
                        border-slate-800
                        rounded-lg
                        px-4
                        py-2
                        text-sm
                    "
                >
                    <Database
                        size={16}
                        className="text-blue-400"
                    />

                    <span className="text-slate-400">
                        Decision Engine
                    </span>

                    <span
                        className="
                            text-emerald-400
                            font-semibold
                        "
                    >
                        Connected
                    </span>
                </div>

                <div
                    className="
                        flex
                        items-center
                        gap-2
                        bg-slate-900
                        border
                        border-slate-800
                        rounded-lg
                        px-4
                        py-2
                        text-sm
                    "
                >
                    <TrendingUp
                        size={16}
                        className="text-purple-400"
                    />

                    <span className="text-slate-400">
                        Business Metrics
                    </span>

                    <span
                        className="
                            text-emerald-400
                            font-semibold
                        "
                    >
                        {liveDataLoaded
                            ? "Live"
                            : "Manual"}
                    </span>
                </div>
            </div>

            {/* =================================================
                BUSINESS INPUTS
            ================================================= */}

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
                        flex-col
                        sm:flex-row
                        sm:items-center
                        sm:justify-between
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
                            Business Inputs
                        </h2>

                        <p
                            className="
                                text-slate-500
                                text-sm
                                mt-1
                            "
                        >
                            Automatically populated
                            from live enterprise data.
                        </p>
                    </div>

                    {liveDataLoaded && (
                        <span
                            className="
                                text-xs
                                px-3
                                py-1
                                rounded-full
                                bg-emerald-500/10
                                border
                                border-emerald-500/20
                                text-emerald-400
                                w-fit
                            "
                        >
                            Live backend metrics
                        </span>
                    )}
                </div>

                <div
                    className="
                        grid
                        grid-cols-1
                        sm:grid-cols-2
                        xl:grid-cols-4
                        gap-4
                    "
                >
                    {/* PREDICTED SALES */}

                    <label
                        className="
                            flex
                            flex-col
                            gap-2
                            text-sm
                            text-slate-400
                        "
                    >
                        Predicted Sales

                        <input
                            type="number"
                            min="0"
                            value={
                                inputs.predicted_sales
                            }
                            onChange={
                                handleChange(
                                    "predicted_sales"
                                )
                            }
                            className="
                                bg-slate-800
                                border
                                border-slate-700
                                rounded-lg
                                px-3
                                py-2.5
                                text-white
                                focus:outline-none
                                focus:border-blue-500
                            "
                        />
                    </label>

                    {/* INVENTORY */}

                    <label
                        className="
                            flex
                            flex-col
                            gap-2
                            text-sm
                            text-slate-400
                        "
                    >
                        Inventory Units

                        <input
                            type="number"
                            min="0"
                            value={
                                inputs.inventory
                            }
                            onChange={
                                handleChange(
                                    "inventory"
                                )
                            }
                            className="
                                bg-slate-800
                                border
                                border-slate-700
                                rounded-lg
                                px-3
                                py-2.5
                                text-white
                                focus:outline-none
                                focus:border-blue-500
                            "
                        />
                    </label>

                    {/* FORECAST */}

                    <label
                        className="
                            flex
                            flex-col
                            gap-2
                            text-sm
                            text-slate-400
                        "
                    >
                        Forecast Growth (%)

                        <input
                            type="number"
                            min="-100"
                            max="100"
                            value={
                                inputs.forecast_growth
                            }
                            onChange={
                                handleChange(
                                    "forecast_growth"
                                )
                            }
                            className="
                                bg-slate-800
                                border
                                border-slate-700
                                rounded-lg
                                px-3
                                py-2.5
                                text-white
                                focus:outline-none
                                focus:border-blue-500
                            "
                        />
                    </label>

                    {/* CHURN */}

                    <label
                        className="
                            flex
                            flex-col
                            gap-2
                            text-sm
                            text-slate-400
                        "
                    >
                        Customer Churn (%)

                        <input
                            type="number"
                            min="0"
                            max="100"
                            value={
                                inputs.customer_churn
                            }
                            onChange={
                                handleChange(
                                    "customer_churn"
                                )
                            }
                            className="
                                bg-slate-800
                                border
                                border-slate-700
                                rounded-lg
                                px-3
                                py-2.5
                                text-white
                                focus:outline-none
                                focus:border-blue-500
                            "
                        />
                    </label>

                    {/* REVENUE */}

                    <label
                        className="
                            flex
                            flex-col
                            gap-2
                            text-sm
                            text-slate-400
                        "
                    >
                        Revenue

                        <input
                            type="number"
                            min="0"
                            value={
                                inputs.revenue
                            }
                            onChange={
                                handleChange(
                                    "revenue"
                                )
                            }
                            className="
                                bg-slate-800
                                border
                                border-slate-700
                                rounded-lg
                                px-3
                                py-2.5
                                text-white
                                focus:outline-none
                                focus:border-blue-500
                            "
                        />
                    </label>

                    {/* PROFIT */}

                    <label
                        className="
                            flex
                            flex-col
                            gap-2
                            text-sm
                            text-slate-400
                        "
                    >
                        Profit

                        <input
                            type="number"
                            value={
                                inputs.profit
                            }
                            onChange={
                                handleChange(
                                    "profit"
                                )
                            }
                            className="
                                bg-slate-800
                                border
                                border-slate-700
                                rounded-lg
                                px-3
                                py-2.5
                                text-white
                                focus:outline-none
                                focus:border-blue-500
                            "
                        />
                    </label>

                    {/* CUSTOMERS */}

                    <label
                        className="
                            flex
                            flex-col
                            gap-2
                            text-sm
                            text-slate-400
                        "
                    >
                        Customers

                        <input
                            type="number"
                            min="0"
                            value={
                                inputs.customers
                            }
                            onChange={
                                handleChange(
                                    "customers"
                                )
                            }
                            className="
                                bg-slate-800
                                border
                                border-slate-700
                                rounded-lg
                                px-3
                                py-2.5
                                text-white
                                focus:outline-none
                                focus:border-blue-500
                            "
                        />
                    </label>
                </div>

                {/* RUN BUTTON */}

                <div
                    className="
                        flex
                        flex-col
                        sm:flex-row
                        sm:items-center
                        gap-3
                        mt-5
                    "
                >
                    <button
                        type="button"
                        onClick={handleRun}
                        disabled={loading}
                        className="
                            flex
                            items-center
                            justify-center
                            gap-2
                            bg-blue-600
                            hover:bg-blue-500
                            disabled:opacity-60
                            disabled:cursor-not-allowed
                            text-white
                            font-semibold
                            px-5
                            py-2.5
                            rounded-lg
                        "
                    >
                        {loading ? (
                            <Loader2
                                size={18}
                                className="animate-spin"
                            />
                        ) : (
                            <PlayCircle
                                size={18}
                            />
                        )}

                        {loading
                            ? "Running Decision Engine..."
                            : "Run Decision Engine"}
                    </button>

                    <span
                        className="
                            text-xs
                            text-slate-500
                        "
                    >
                        Values are automatically
                        loaded from the backend
                        and can also be edited
                        manually.
                    </span>
                </div>
            </div>

            {/* =================================================
                RISK + RECOMMENDATIONS
            ================================================= */}

            <div
                className="
                    grid
                    grid-cols-1
                    xl:grid-cols-2
                    gap-6
                "
            >
                <RiskCard
                    riskLevel={
                        currentRisk
                    }
                    risks={
                        identifiedRisks
                    }
                    riskScore={
                        riskScore
                    }
                />

                <RecommendationCard
                    recommendations={
                        displayedRecommendations
                    }
                />
            </div>

            {/* =================================================
                SUMMARY
            ================================================= */}

            {decisionSummary && (
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
                            text-lg
                            font-bold
                            mb-2
                        "
                    >
                        Decision Summary
                    </h2>

                    <p
                        className="
                            text-slate-300
                            leading-relaxed
                        "
                    >
                        {cleanText(
                            decisionSummary
                        )}
                    </p>
                </div>
            )}

            {/* =================================================
                IMPACT CHART
            ================================================= */}

            <ImpactChart
                metrics={
                    decisionMetrics
                }
            />

            {/* =================================================
                DECISION HISTORY
            ================================================= */}

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
                        items-center
                        justify-between
                        gap-3
                        mb-5
                    "
                >
                    <div
                        className="
                            flex
                            items-center
                            gap-2
                        "
                    >
                        <History
                            size={20}
                            className="text-blue-400"
                        />

                        <div>
                            <h2
                                className="
                                    text-white
                                    font-bold
                                    text-xl
                                "
                            >
                                Decision History
                            </h2>

                            <p
                                className="
                                    text-slate-500
                                    text-xs
                                    mt-1
                                "
                            >
                                Previous decisions
                                returned by the
                                backend.
                            </p>
                        </div>
                    </div>

                    <span
                        className="
                            text-xs
                            text-slate-500
                        "
                    >
                        {history.length} decision
                        {history.length === 1
                            ? ""
                            : "s"}
                    </span>
                </div>

                {history.length === 0 ? (
                    <div
                        className="
                            text-center
                            py-10
                            text-slate-500
                        "
                    >
                        <History
                            size={30}
                            className="
                                mx-auto
                                mb-3
                                opacity-50
                            "
                        />

                        <p className="text-sm">
                            No decisions have been
                            recorded yet.
                        </p>

                        <p
                            className="
                                text-xs
                                mt-1
                            "
                        >
                            Run the Decision Engine
                            to create the first
                            decision.
                        </p>
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
                                text-sm
                                text-left
                            "
                        >
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
                                            pr-4
                                            whitespace-nowrap
                                        "
                                    >
                                        Decision ID
                                    </th>

                                    <th
                                        className="
                                            py-3
                                            pr-4
                                            whitespace-nowrap
                                        "
                                    >
                                        Timestamp
                                    </th>

                                    <th
                                        className="
                                            py-3
                                            pr-4
                                        "
                                    >
                                        Risk
                                    </th>

                                    <th
                                        className="
                                            py-3
                                            pr-4
                                        "
                                    >
                                        Score
                                    </th>

                                    <th
                                        className="
                                            py-3
                                            pr-4
                                        "
                                    >
                                        Risks
                                    </th>

                                    <th
                                        className="
                                            py-3
                                        "
                                    >
                                        Recommendation
                                    </th>
                                </tr>
                            </thead>

                            <tbody>
                                {history
                                    .slice(
                                        0,
                                        10
                                    )
                                    .map(
                                        (
                                            entry,
                                            index
                                        ) => {
                                            const entryDecision =
                                                normalizeDecision(
                                                    getHistoryDecision(
                                                        entry
                                                    )
                                                ) || {};

                                            const entryRisks =
                                                normalizeRisks(
                                                    entryDecision
                                                        .identified_risks ??
                                                    entryDecision
                                                        .risks ??
                                                    entryDecision
                                                        .risk_factors
                                                );

                                            const entryRecommendations =
                                                normalizeRecommendations(
                                                    entryDecision
                                                        .recommendations ??
                                                    entryDecision
                                                        .actions ??
                                                    entryDecision
                                                        .recommended_actions
                                                );

                                            const decisionId =
                                                entryDecision
                                                    .decision_id ??
                                                entry?.decision_id ??
                                                entry?.id ??
                                                entry?.decisionId ??
                                                null;

                                            const entryRiskScore =
                                                hasValue(
                                                    entryDecision
                                                        .risk_score
                                                )
                                                    ? clamp(
                                                        toNumber(
                                                            entryDecision
                                                                .risk_score
                                                        ),
                                                        0,
                                                        100
                                                    )
                                                    : null;

                                            return (
                                                <tr
                                                    key={
                                                        decisionId
                                                            ? `${decisionId}-${index}`
                                                            : `history-${index}`
                                                    }
                                                    className="
                                                        border-b
                                                        border-slate-800/60
                                                        hover:bg-slate-800/30
                                                        transition
                                                    "
                                                >
                                                    <td
                                                        className="
                                                            py-3
                                                            pr-4
                                                            text-blue-400
                                                            font-medium
                                                            whitespace-nowrap
                                                        "
                                                    >
                                                        {decisionId ??
                                                            "—"}
                                                    </td>

                                                    <td
                                                        className="
                                                            py-3
                                                            pr-4
                                                            text-slate-300
                                                            whitespace-nowrap
                                                        "
                                                    >
                                                        {formatTimestamp(
                                                            getHistoryTimestamp(
                                                                entry
                                                            )
                                                        )}
                                                    </td>

                                                    <td
                                                        className="
                                                            py-3
                                                            pr-4
                                                        "
                                                    >
                                                        <span
                                                            className="
                                                                inline-flex
                                                                px-2.5
                                                                py-1
                                                                rounded-full
                                                                bg-slate-800
                                                                text-slate-200
                                                                text-xs
                                                                font-semibold
                                                            "
                                                        >
                                                            {
                                                                entryDecision
                                                                    .risk_level
                                                            }
                                                        </span>
                                                    </td>

                                                    <td
                                                        className="
                                                            py-3
                                                            pr-4
                                                            text-slate-300
                                                        "
                                                    >
                                                        {entryRiskScore !==
                                                        null
                                                            ? Math.round(
                                                                entryRiskScore
                                                            )
                                                            : "—"}
                                                    </td>

                                                    <td
                                                        className="
                                                            py-3
                                                            pr-4
                                                            text-slate-300
                                                        "
                                                    >
                                                        {
                                                            entryRisks.length
                                                        }
                                                    </td>

                                                    <td
                                                        className="
                                                            py-3
                                                            text-slate-300
                                                            max-w-md
                                                        "
                                                    >
                                                        {entryRecommendations.length >
                                                        0
                                                            ? entryRecommendations
                                                                .slice(
                                                                    0,
                                                                    3
                                                                )
                                                                .join(
                                                                    ", "
                                                                )
                                                            : "—"}
                                                    </td>
                                                </tr>
                                            );
                                        }
                                    )}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            {/* =================================================
                EXECUTIVE FOOTER
            ================================================= */}

            <div
                className="
                    grid
                    grid-cols-1
                    md:grid-cols-3
                    gap-4
                "
            >
                {/* SALES */}

                <div
                    className="
                        bg-slate-900
                        border
                        border-slate-800
                        rounded-xl
                        p-4
                    "
                >
                    <TrendingUp
                        size={18}
                        className="
                            text-blue-400
                            mb-2
                        "
                    />

                    <p
                        className="
                            text-xs
                            text-slate-500
                        "
                    >
                        Predicted Sales
                    </p>

                    <p
                        className="
                            text-lg
                            font-bold
                            mt-1
                        "
                    >
                        {formatNumber(
                            inputs.predicted_sales
                        )}
                    </p>
                </div>

                {/* INVENTORY */}

                <div
                    className="
                        bg-slate-900
                        border
                        border-slate-800
                        rounded-xl
                        p-4
                    "
                >
                    <Database
                        size={18}
                        className="
                            text-purple-400
                            mb-2
                        "
                    />

                    <p
                        className="
                            text-xs
                            text-slate-500
                        "
                    >
                        Inventory
                    </p>

                    <p
                        className="
                            text-lg
                            font-bold
                            mt-1
                        "
                    >
                        {formatNumber(
                            inputs.inventory,
                            0
                        )}
                    </p>
                </div>

                {/* CHURN */}

                <div
                    className="
                        bg-slate-900
                        border
                        border-slate-800
                        rounded-xl
                        p-4
                    "
                >
                    <Users
                        size={18}
                        className="
                            text-emerald-400
                            mb-2
                        "
                    />

                    <p
                        className="
                            text-xs
                            text-slate-500
                        "
                    >
                        Customer Churn
                    </p>

                    <p
                        className="
                            text-lg
                            font-bold
                            mt-1
                        "
                    >
                        {hasValue(
                            inputs.customer_churn
                        )
                            ? `${formatNumber(
                                inputs.customer_churn
                            )}%`
                            : "—"}
                    </p>
                </div>
            </div>
        </div>
    );
}


import api from "../../api/axios";

// =====================================================
// ENTERPRISE AI
// BUSINESS DECISION INTELLIGENCE
// DECISION API
//
// Responsibilities:
// - API communication
// - Safe number handling
// - Response unwrapping
// - Decision normalization
// - Risk normalization
// - Recommendation normalization
// - Health normalization
// - Decision history normalization
//
// IMPORTANT:
// Backend values always have priority.
// Frontend calculations are FALLBACKS ONLY.
// =====================================================


// =====================================================
// CONFIGURATION
// =====================================================

const HEALTH_CONFIG = {
    sales: {
        low: 500000,
        target: 1000000,
        high: 2000000,
    },

    inventory: {
        critical: 50,
        low: 100,
        healthy: 500,
        high: 5000,
    },

    growth: {
        critical: -20,
        weak: -10,
        neutral: 0,
        healthy: 10,
        strong: 20,
    },

    churn: {
        excellent: 5,
        healthy: 10,
        moderate: 20,
        high: 30,
        critical: 50,
    },
};


// =====================================================
// OBJECT CHECK
// =====================================================

const isObject = (value) => {
    return (
        value !== null &&
        typeof value === "object" &&
        !Array.isArray(value)
    );
};


// =====================================================
// ARRAY CHECK
// =====================================================

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
// OPTIONAL NUMBER
// =====================================================

const toOptionalNumber = (value) => {
    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {
        return null;
    }

    const number = toNumber(value, NaN);

    return Number.isFinite(number)
        ? number
        : null;
};


// =====================================================
// INTEGER
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
// CLAMP
// =====================================================

const clamp = (
    value,
    min = 0,
    max = 100
) => {
    const number = toNumber(
        value,
        min
    );

    return Math.min(
        max,
        Math.max(
            min,
            number
        )
    );
};


// =====================================================
// UNWRAP AXIOS RESPONSE
// =====================================================

const unwrapResponse = (response) => {
    if (!response) {
        return null;
    }

    // AxiosResponse
    if (
        isObject(response) &&
        response.data !== undefined &&
        (
            response.status !== undefined ||
            response.statusText !== undefined ||
            response.headers !== undefined ||
            response.config !== undefined
        )
    ) {
        return response.data;
    }

    // Normal API wrapper
    if (
        isObject(response) &&
        response.data !== undefined &&
        (
            response.success !== undefined ||
            response.message !== undefined ||
            response.error !== undefined
        )
    ) {
        return response.data;
    }

    return response;
};


// =====================================================
// SALES HEALTH FALLBACK
// =====================================================

const calculateSalesHealth = (sales) => {
    const value = Math.max(
        0,
        toNumber(sales)
    );

    if (value <= 0) {
        return 0;
    }

    const {
        low,
        target,
        high,
    } = HEALTH_CONFIG.sales;

    if (value < low) {
        return 25;
    }

    if (value < target) {
        return Math.round(
            25 +
            (
                (value - low) /
                (target - low)
            ) * 25
        );
    }

    if (value < high) {
        return Math.round(
            50 +
            (
                (value - target) /
                (high - target)
            ) * 35
        );
    }

    return 100;
};


// =====================================================
// INVENTORY HEALTH FALLBACK
// =====================================================

const calculateInventoryHealth = (inventory) => {
    const value = Math.max(
        0,
        toNumber(inventory)
    );

    const {
        critical,
        low,
        healthy,
        high,
    } = HEALTH_CONFIG.inventory;

    if (value <= critical) {
        return 15;
    }

    if (value <= low) {
        return 30;
    }

    if (value <= healthy) {
        return Math.round(
            30 +
            (
                (value - low) /
                (healthy - low)
            ) * 50
        );
    }

    if (value <= high) {
        return Math.round(
            80 +
            (
                (value - healthy) /
                (high - healthy)
            ) * 15
        );
    }

    // Very high inventory can indicate overstock.
    return 70;
};


// =====================================================
// GROWTH HEALTH FALLBACK
// =====================================================

const calculateGrowthHealth = (growth) => {
    const value = toNumber(growth);

    const {
        critical,
        weak,
        neutral,
        healthy,
        strong,
    } = HEALTH_CONFIG.growth;

    if (value <= critical) {
        return 0;
    }

    if (value < weak) {
        return Math.round(
            20 +
            (
                (value - critical) /
                (weak - critical)
            ) * 20
        );
    }

    if (value < neutral) {
        return Math.round(
            40 +
            (
                (value - weak) /
                (neutral - weak)
            ) * 10
        );
    }

    if (value < healthy) {
        return Math.round(
            50 +
            (
                value /
                healthy
            ) * 25
        );
    }

    if (value < strong) {
        return Math.round(
            75 +
            (
                (value - healthy) /
                (strong - healthy)
            ) * 25
        );
    }

    return 100;
};


// =====================================================
// CHURN HEALTH FALLBACK
// =====================================================

const calculateChurnHealth = (churn) => {
    const value = clamp(
        churn,
        0,
        100
    );

    const {
        excellent,
        healthy,
        moderate,
        high,
        critical,
    } = HEALTH_CONFIG.churn;

    if (value <= excellent) {
        return 100;
    }

    if (value <= healthy) {
        return Math.round(
            90 -
            (
                (value - excellent) /
                (healthy - excellent)
            ) * 15
        );
    }

    if (value <= moderate) {
        return Math.round(
            75 -
            (
                (value - healthy) /
                (moderate - healthy)
            ) * 25
        );
    }

    if (value <= high) {
        return Math.round(
            50 -
            (
                (value - moderate) /
                (high - moderate)
            ) * 25
        );
    }

    if (value <= critical) {
        return Math.round(
            25 -
            (
                (value - high) /
                (critical - high)
            ) * 25
        );
    }

    return 0;
};


// =====================================================
// NORMALIZE HEALTH
// =====================================================

const normalizeHealth = (
    value,
    fallback = 0
) => {
    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {
        return Math.round(
            clamp(fallback)
        );
    }

    return Math.round(
        clamp(
            toNumber(
                value,
                fallback
            )
        )
    );
};


// =====================================================
// RUN DECISION ENGINE
// =====================================================

export const runDecisionEngine = async (
    payload = {}
) => {

    const requestPayload = {
        predicted_sales: Math.max(
            0,
            toNumber(
                firstValue(
                    payload?.predicted_sales,
                    payload?.predictedSales,
                    payload?.sales
                )
            )
        ),

        inventory: Math.max(
            0,
            toNumber(
                firstValue(
                    payload?.inventory,
                    payload?.inventory_units,
                    payload?.current_stock
                )
            )
        ),

        forecast_growth: Math.max(
            -100,
            Math.min(
                100,
                toNumber(
                    firstValue(
                        payload?.forecast_growth,
                        payload?.forecastGrowth,
                        payload?.growth
                    )
                )
            )
        ),

        customer_churn: Math.min(
            100,
            Math.max(
                0,
                toNumber(
                    firstValue(
                        payload?.customer_churn,
                        payload?.customerChurn,
                        payload?.churn
                    )
                )
            )
        ),

        revenue: Math.max(
            0,
            toNumber(
                firstValue(
                    payload?.revenue,
                    payload?.total_revenue
                )
            )
        ),

        profit: toNumber(
            firstValue(
                payload?.profit,
                payload?.total_profit,
                payload?.net_profit
            )
        ),

        customers: Math.max(
            0,
            toInteger(
                firstValue(
                    payload?.customers,
                    payload?.customer_count,
                    payload?.total_customers
                )
            )
        ),
    };

    console.log(
        "====================================="
    );

    console.log(
        "DECISION ENGINE REQUEST"
    );

    console.log(
        requestPayload
    );

    console.log(
        "====================================="
    );

    try {
        const response = await api.post(
            "/decision/run",
            requestPayload
        );

        console.log(
            "DECISION ENGINE RESPONSE"
        );

        console.log(
            response?.data
        );

        return unwrapResponse(
            response
        );

    } catch (error) {

        console.error(
            "DECISION ENGINE ERROR:",
            error
        );

        console.error(
            "DECISION ERROR RESPONSE:",
            error?.response?.data
        );

        throw error;
    }
};


// =====================================================
// EXECUTIVE DECISIONS
// =====================================================

export const fetchExecutiveDecisions = async () => {
    const response = await api.get(
        "/decision/"
    );

    return unwrapResponse(
        response
    );
};


// =====================================================
// DECISION RECOMMENDATIONS
// =====================================================

export const fetchDecisionRecommendations = async () => {
    const response = await api.get(
        "/decision/recommendations"
    );

    return unwrapResponse(
        response
    );
};


// =====================================================
// LATEST DECISION
// =====================================================

export const fetchLatestDecision = async () => {
    const response = await api.get(
        "/decision/latest"
    );

    return unwrapResponse(
        response
    );
};


// =====================================================
// SALES METRICS
// =====================================================

export const fetchSalesMetrics = async () => {
    const response = await api.get(
        "/sales/"
    );

    return unwrapResponse(
        response
    );
};


// =====================================================
// FORECAST METRICS
// =====================================================

export const fetchForecastMetrics = async () => {
    const response = await api.get(
        "/forecast/sales"
    );

    return unwrapResponse(
        response
    );
};


// =====================================================
// INVENTORY METRICS
// =====================================================

export const fetchInventoryMetrics = async () => {
    const response = await api.get(
        "/inventory/"
    );

    return unwrapResponse(
        response
    );
};


// =====================================================
// CUSTOMER METRICS
// =====================================================

export const fetchCustomerMetrics = async () => {
    const response = await api.get(
        "/customer/stats"
    );

    return unwrapResponse(
        response
    );
};


// =====================================================
// DECISION HEALTH
// =====================================================

export const fetchDecisionHealth = async () => {
    const response = await api.get(
        "/decision/health"
    );

    return unwrapResponse(
        response
    );
};


// =====================================================
// CLEAR DECISION HISTORY
// =====================================================

export const clearDecisionHistory = async () => {
    const response = await api.delete(
        "/decision/history"
    );

    return unwrapResponse(
        response
    );
};


// =====================================================
// NORMALIZE DECISION RESPONSE
// =====================================================

export const normalizeDecisionResponse = (response) => {

    const source = unwrapResponse(
        response
    );

    if (
        !source ||
        !isObject(source)
    ) {
        return null;
    }

    // Direct decision object
    if (
        isObject(
            source.decision
        )
    ) {
        return source.decision;
    }

    // data.decision
    if (
        isObject(
            source.data?.decision
        )
    ) {
        return source.data.decision;
    }

    // data.result
    if (
        isObject(
            source.data?.result
        )
    ) {
        return source.data.result;
    }

    // data itself contains decision fields
    if (
        isObject(
            source.data
        ) &&
        (
            source.data.risk_level !== undefined ||
            source.data.riskLevel !== undefined ||
            source.data.risk_score !== undefined ||
            source.data.riskScore !== undefined ||
            source.data.identified_risks !== undefined ||
            source.data.recommendations !== undefined ||
            source.data.metrics !== undefined
        )
    ) {
        return source.data;
    }

    // result
    if (
        isObject(
            source.result
        )
    ) {
        return source.result;
    }

    // current_decision
    if (
        isObject(
            source.current_decision
        )
    ) {
        return source.current_decision;
    }

    // currentDecision
    if (
        isObject(
            source.currentDecision
        )
    ) {
        return source.currentDecision;
    }

    // dashboard.decision
    if (
        isObject(
            source.dashboard?.decision
        )
    ) {
        return source.dashboard.decision;
    }

    // dashboard.current_decision
    if (
        isObject(
            source.dashboard?.current_decision
        )
    ) {
        return source.dashboard.current_decision;
    }

    // Direct decision object
    if (
        source.risk_level !== undefined ||
        source.riskLevel !== undefined ||
        source.risk_score !== undefined ||
        source.riskScore !== undefined ||
        source.identified_risks !== undefined ||
        source.recommendations !== undefined ||
        source.risk !== undefined ||
        source.metrics !== undefined
    ) {
        return source;
    }

    return null;
};


// =====================================================
// NORMALIZE DECISION HISTORY
// =====================================================

export const normalizeDecisionHistory = (response) => {

    const source = unwrapResponse(
        response
    );

    if (isArray(source)) {
        return source;
    }

    if (
        !source ||
        !isObject(source)
    ) {
        return [];
    }

    const possibleArrays = [
        source.history,

        source.decisions,

        source.dashboard?.history,

        source.dashboard?.decisions,

        source.data?.history,

        source.data?.decisions,

        source.data?.dashboard?.history,

        source.data?.dashboard?.decisions,

        source.result?.history,

        source.result?.decisions,

        source.data?.result?.history,

        source.data?.result?.decisions,

        source.current_decisions,

        source.data?.current_decisions,
    ];

    for (
        const candidate of possibleArrays
    ) {
        if (isArray(candidate)) {
            return candidate;
        }
    }

    const singleDecision =
        normalizeDecisionResponse(
            source
        );

    if (singleDecision) {
        return [
            singleDecision
        ];
    }

    return [];
};


// =====================================================
// HISTORY TIMESTAMP
// =====================================================

export const getHistoryTimestamp = (entry) => {

    if (
        !entry ||
        typeof entry !== "object"
    ) {
        return null;
    }

    return (
        firstValue(
            entry.timestamp,

            entry.created_at,

            entry.createdAt,

            entry.decision_timestamp,

            entry.decisionTimestamp,

            entry.date,

            entry.decision?.timestamp,

            entry.decision?.created_at,

            entry.decision?.createdAt,

            entry.result?.timestamp,

            entry.result?.created_at,

            entry.data?.timestamp,

            entry.data?.created_at
        ) ?? null
    );
};


// =====================================================
// HISTORY DECISION
// =====================================================

export const getHistoryDecision = (entry) => {

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
            entry.result
        )
    ) {
        return entry.result;
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
            entry.data?.result
        )
    ) {
        return entry.data.result;
    }

    if (
        isObject(
            entry.data
        )
    ) {
        return entry.data;
    }

    return entry;
};


// =====================================================
// LATEST DECISION FROM HISTORY
// =====================================================

export const getLatestDecisionFromHistory = (response) => {

    const history =
        normalizeDecisionHistory(
            response
        );

    if (
        history.length === 0
    ) {
        return null;
    }

    const sorted =
        [...history].sort(
            (a, b) => {

                const timestampA =
                    getHistoryTimestamp(
                        a
                    );

                const timestampB =
                    getHistoryTimestamp(
                        b
                    );

                const dateA =
                    timestampA
                        ? new Date(
                            timestampA
                        ).getTime()
                        : 0;

                const dateB =
                    timestampB
                        ? new Date(
                            timestampB
                        ).getTime()
                        : 0;

                const validA =
                    Number.isFinite(
                        dateA
                    );

                const validB =
                    Number.isFinite(
                        dateB
                    );

                if (
                    validA &&
                    validB
                ) {
                    return dateB - dateA;
                }

                if (
                    validB &&
                    !validA
                ) {
                    return 1;
                }

                if (
                    validA &&
                    !validB
                ) {
                    return -1;
                }

                return 0;
            }
        );

    return getHistoryDecision(
        sorted[0]
    );
};


// =====================================================
// NORMALIZE SINGLE RECOMMENDATION
// =====================================================

const normalizeRecommendation = (item) => {

    if (
        item === null ||
        item === undefined
    ) {
        return null;
    }

    if (
        typeof item === "string"
    ) {
        const text = item.trim();

        return text || null;
    }

    if (
        typeof item === "number" ||
        typeof item === "boolean"
    ) {
        return String(item);
    }

    if (
        isObject(item)
    ) {

        const value = firstValue(
            item.recommendation,

            item.action,

            item.recommendation_text,

            item.recommendationText,

            item.message,

            item.description,

            item.title,

            item.text,

            item.reason,

            item.details
        );

        if (
            value !== undefined &&
            value !== null &&
            value !== ""
        ) {
            return {
                ...item,

                recommendation:
                    String(value).trim(),
            };
        }

        return null;
    }

    return String(item);
};


// =====================================================
// EXTRACT RECOMMENDATION CONTAINER
// =====================================================

const extractRecommendationContainer = (
    source,
    depth = 0
) => {

    if (depth > 20) {
        return null;
    }

    if (isArray(source)) {
        return source;
    }

    if (
        typeof source === "string"
    ) {
        return source;
    }

    if (
        !isObject(source)
    ) {
        return null;
    }

    if (
        source.recommendations !== undefined
    ) {
        return source.recommendations;
    }

    if (
        source.recommended_actions !== undefined
    ) {
        return source.recommended_actions;
    }

    if (
        source.recommendedActions !== undefined
    ) {
        return source.recommendedActions;
    }

    if (
        source.recommendation !== undefined
    ) {
        return source.recommendation;
    }

    if (
        source.actions !== undefined
    ) {
        return source.actions;
    }

    const nestedCandidates = [
        source.decision,

        source.current_decision,

        source.currentDecision,

        source.result,

        source.data,

        source.dashboard,

        source.data?.decision,

        source.data?.result,

        source.dashboard?.decision,

        source.dashboard?.current_decision,

        source.result?.decision,

        source.result?.data,

        source.data?.result?.decision,

        source.payload,

        source.response,
    ];

    for (
        const candidate of nestedCandidates
    ) {

        const result =
            extractRecommendationContainer(
                candidate,
                depth + 1
            );

        if (
            result !== null &&
            result !== undefined
        ) {
            return result;
        }
    }

    return null;
};


// =====================================================
// NORMALIZE DECISION RECOMMENDATIONS
// =====================================================

export const normalizeDecisionRecommendations = (
    response
) => {

    const source =
        unwrapResponse(
            response
        );

    const container =
        extractRecommendationContainer(
            source
        );

    if (
        container === null ||
        container === undefined
    ) {
        return [];
    }

    if (isArray(container)) {
        return container
            .map(
                normalizeRecommendation
            )
            .filter(Boolean);
    }

    if (
        typeof container === "string"
    ) {
        return container
            .split(
                /\r?\n|;/
            )
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

    if (
        isObject(container)
    ) {

        const normalized =
            normalizeRecommendation(
                container
            );

        return normalized
            ? [normalized]
            : [];
    }

    return [];
};


// =====================================================
// NORMALIZE RISK LEVEL
// =====================================================

export const normalizeRiskLevel = (value) => {

    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {
        return "LOW";
    }

    if (isObject(value)) {
        value = firstValue(
            value.level,

            value.risk_level,

            value.riskLevel,

            value.name
        );
    }

    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {
        return "LOW";
    }

    const normalized =
        String(value)
            .trim()
            .toUpperCase();

    const aliases = {
        "NOT RUN": "LOW",

        UNKNOWN: "LOW",

        NONE: "LOW",

        NORMAL: "LOW",

        MODERATE: "MEDIUM",

        SEVERE: "HIGH",

        EXTREME: "CRITICAL",

        URGENT: "CRITICAL",

        EMERGENCY: "CRITICAL",
    };

    const resolved =
        aliases[normalized] ??
        normalized;

    const allowed = [
        "LOW",
        "MEDIUM",
        "HIGH",
        "CRITICAL",
    ];

    return allowed.includes(
        resolved
    )
        ? resolved
        : "LOW";
};


// =====================================================
// NORMALIZE RISKS
// =====================================================

export const normalizeRisks = (value) => {

    if (isArray(value)) {

        return value
            .map(
                (item) => {

                    if (
                        typeof item === "string"
                    ) {
                        return item.trim();
                    }

                    if (
                        isObject(item)
                    ) {
                        return (
                            firstValue(
                                item.message,

                                item.description,

                                item.reason,

                                item.risk,

                                item.title,

                                item.name,

                                item.text
                            ) ??
                            JSON.stringify(
                                item
                            )
                        );
                    }

                    return String(
                        item
                    );
                }
            )
            .map(
                (item) =>
                    String(
                        item
                    ).trim()
            )
            .filter(Boolean);
    }

    if (
        typeof value === "string"
    ) {
        return value
            .split(
                /\r?\n|;/
            )
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

    if (isObject(value)) {
        return normalizeRisks(
            [value]
        );
    }

    return [];
};


// =====================================================
// NORMALIZE INSIGHTS
// =====================================================

export const normalizeInsights = (value) => {

    if (isArray(value)) {

        return value
            .map(
                (item) => {

                    if (
                        typeof item === "string"
                    ) {
                        return item.trim();
                    }

                    if (
                        isObject(item)
                    ) {
                        return (
                            firstValue(
                                item.message,

                                item.description,

                                item.insight,

                                item.text,

                                item.title
                            ) ??
                            JSON.stringify(
                                item
                            )
                        );
                    }

                    return String(
                        item
                    );
                }
            )
            .map(
                (item) =>
                    String(
                        item
                    ).trim()
            )
            .filter(Boolean);
    }

    if (
        typeof value === "string"
    ) {
        return value
            .split(
                /\r?\n|;/
            )
            .map(
                (item) =>
                    item.trim()
            )
            .filter(Boolean);
    }

    if (isObject(value)) {
        return normalizeInsights(
            [value]
        );
    }

    return [];
};


// =====================================================
// NORMALIZE METRICS
// =====================================================

export const normalizeDecisionMetrics = (
    metrics = {},
    fallbackSource = {}
) => {

    const source =
        isObject(metrics)
            ? metrics
            : {};

    const fallback =
        isObject(fallbackSource)
            ? fallbackSource
            : {};


    // -------------------------------------------------
    // SALES
    // -------------------------------------------------

    const predictedSales =
        Math.max(
            0,
            toNumber(
                firstValue(
                    source.predicted_sales,

                    source.predictedSales,

                    source.sales,

                    fallback.predicted_sales,

                    fallback.predictedSales,

                    fallback.sales
                )
            )
        );


    // -------------------------------------------------
    // INVENTORY
    // -------------------------------------------------

    const inventory =
        Math.max(
            0,
            toNumber(
                firstValue(
                    source.inventory,

                    source.inventory_units,

                    source.current_stock,

                    fallback.inventory,

                    fallback.inventory_units,

                    fallback.current_stock
                )
            )
        );


    // -------------------------------------------------
    // GROWTH
    // -------------------------------------------------

    const forecastGrowth =
        Math.max(
            -100,
            Math.min(
                100,
                toNumber(
                    firstValue(
                        source.forecast_growth,

                        source.forecastGrowth,

                        source.growth,

                        fallback.forecast_growth,

                        fallback.forecastGrowth,

                        fallback.growth
                    )
                )
            )
        );


    // -------------------------------------------------
    // CHURN
    // -------------------------------------------------

    const customerChurn =
        clamp(
            toNumber(
                firstValue(
                    source.customer_churn,

                    source.customerChurn,

                    source.churn,

                    source.churn_rate,

                    source.churnRate,

                    fallback.customer_churn,

                    fallback.customerChurn,

                    fallback.churn,

                    fallback.churn_rate,

                    fallback.churnRate
                )
            ),
            0,
            100
        );


    // -------------------------------------------------
    // REVENUE
    // -------------------------------------------------

    const revenue =
        Math.max(
            0,
            toNumber(
                firstValue(
                    source.revenue,

                    source.total_revenue,

                    source.totalRevenue,

                    fallback.revenue,

                    fallback.total_revenue,

                    fallback.totalRevenue
                )
            )
        );


    // -------------------------------------------------
    // PROFIT
    // -------------------------------------------------

    const profit =
        toNumber(
            firstValue(
                source.profit,

                source.total_profit,

                source.totalProfit,

                source.net_profit,

                source.netProfit,

                fallback.profit,

                fallback.total_profit,

                fallback.totalProfit,

                fallback.net_profit,

                fallback.netProfit
            )
        );


    // -------------------------------------------------
    // PROFIT MARGIN
    // -------------------------------------------------

    const profitMargin =
        toNumber(
            firstValue(
                source.profit_margin,

                source.profitMargin,

                fallback.profit_margin,

                fallback.profitMargin
            )
        );


    // -------------------------------------------------
    // CUSTOMERS
    // -------------------------------------------------

    const customers =
        Math.max(
            0,
            toInteger(
                firstValue(
                    source.customers,

                    source.customer_count,

                    source.customerCount,

                    source.total_customers,

                    source.totalCustomers,

                    fallback.customers,

                    fallback.customer_count,

                    fallback.customerCount,

                    fallback.total_customers,

                    fallback.totalCustomers
                )
            )
        );


    // -------------------------------------------------
    // BACKEND HEALTH VALUES
    // -------------------------------------------------

    const backendSalesHealth =
        firstValue(
            source.sales_health,

            source.salesHealth,

            source.health?.sales,

            source.business_health?.sales,

            source.businessHealth?.sales,

            fallback.sales_health,

            fallback.salesHealth,

            fallback.health?.sales,

            fallback.business_health?.sales,

            fallback.businessHealth?.sales
        );


    const backendInventoryHealth =
        firstValue(
            source.inventory_health,

            source.inventoryHealth,

            source.health?.inventory,

            source.business_health?.inventory,

            source.businessHealth?.inventory,

            fallback.inventory_health,

            fallback.inventoryHealth,

            fallback.health?.inventory,

            fallback.business_health?.inventory,

            fallback.businessHealth?.inventory
        );


    const backendGrowthHealth =
        firstValue(
            source.growth_health,

            source.growthHealth,

            source.forecast_growth_health,

            source.forecastGrowthHealth,

            source.health?.growth,

            source.business_health?.growth,

            source.businessHealth?.growth,

            fallback.growth_health,

            fallback.growthHealth,

            fallback.forecast_growth_health,

            fallback.forecastGrowthHealth,

            fallback.health?.growth,

            fallback.business_health?.growth,

            fallback.businessHealth?.growth
        );


    const backendChurnHealth =
        firstValue(
            source.churn_health,

            source.churnHealth,

            source.customer_churn_health,

            source.customerChurnHealth,

            source.health?.churn,

            source.business_health?.churn,

            source.businessHealth?.churn,

            fallback.churn_health,

            fallback.churnHealth,

            fallback.customer_churn_health,

            fallback.customerChurnHealth,

            fallback.health?.churn,

            fallback.business_health?.churn,

            fallback.businessHealth?.churn
        );


    // -------------------------------------------------
    // FRONTEND FALLBACK HEALTH
    // -------------------------------------------------

    const fallbackSalesHealth =
        calculateSalesHealth(
            predictedSales
        );

    const fallbackInventoryHealth =
        calculateInventoryHealth(
            inventory
        );

    const fallbackGrowthHealth =
        calculateGrowthHealth(
            forecastGrowth
        );

    const fallbackChurnHealth =
        calculateChurnHealth(
            customerChurn
        );


    // -------------------------------------------------
    // FINAL HEALTH
    // BACKEND HAS PRIORITY
    // -------------------------------------------------

    const salesHealth =
        normalizeHealth(
            backendSalesHealth,
            fallbackSalesHealth
        );

    const inventoryHealth =
        normalizeHealth(
            backendInventoryHealth,
            fallbackInventoryHealth
        );

    const growthHealth =
        normalizeHealth(
            backendGrowthHealth,
            fallbackGrowthHealth
        );

    const churnHealth =
        normalizeHealth(
            backendChurnHealth,
            fallbackChurnHealth
        );


    // -------------------------------------------------
    // OVERALL HEALTH
    // -------------------------------------------------

    const overallHealth =
        Math.round(
            (
                salesHealth +
                inventoryHealth +
                growthHealth +
                churnHealth
            ) / 4
        );


    return {
        predicted_sales:
            predictedSales,

        inventory:
            inventory,

        forecast_growth:
            forecastGrowth,

        customer_churn:
            customerChurn,

        revenue:
            revenue,

        profit:
            profit,

        profit_margin:
            profitMargin,

        customers:
            customers,

        sales_health:
            salesHealth,

        inventory_health:
            inventoryHealth,

        growth_health:
            growthHealth,

        churn_health:
            churnHealth,

        overall_health:
            overallHealth,
    };
};


// =====================================================
// NORMALIZE COMPLETE DECISION
// =====================================================

export const normalizeDecision = (response) => {

    const decision =
        normalizeDecisionResponse(
            response
        );

    if (!decision) {
        return null;
    }


    // -------------------------------------------------
    // METRICS
    // -------------------------------------------------

    const metrics =
        normalizeDecisionMetrics(
            decision.metrics,
            decision
        );


    // -------------------------------------------------
    // RISK SCORE
    // -------------------------------------------------

    const normalizedRiskScore =
        toOptionalNumber(
            firstValue(
                decision.risk_score,

                decision.riskScore,

                decision.score,

                decision.risk?.score,

                decision.risk?.risk_score,

                decision.risk?.riskScore
            )
        );


    // -------------------------------------------------
    // IDENTIFIED RISKS
    // -------------------------------------------------

    const identifiedRisks =
        normalizeRisks(
            firstValue(
                decision.identified_risks,

                decision.identifiedRisks,

                decision.risks,

                decision.risk?.identified_risks,

                decision.risk?.identifiedRisks,

                decision.risk?.risks
            )
        );


    // -------------------------------------------------
    // RECOMMENDATIONS
    // -------------------------------------------------

    const recommendations =
        normalizeDecisionRecommendations(
            firstValue(
                decision.recommendations,

                decision.actions,

                decision.recommended_actions,

                decision.recommendedActions,

                decision.decision?.recommendations
            )
        );


    // -------------------------------------------------
    // RISK COUNT
    // -------------------------------------------------

    const normalizedRiskCount =
        toInteger(
            firstValue(
                decision.risk_count,

                decision.riskCount
            ),
            identifiedRisks.length
        );


    // -------------------------------------------------
    // RISK LEVEL
    // -------------------------------------------------

    const rawRiskLevel =
        firstValue(
            decision.risk_level,

            decision.riskLevel,

            decision.risk?.level,

            decision.risk?.risk_level,

            decision.risk?.riskLevel,

            // Do not directly use the entire risk object
            // unless it has already been converted.
            isObject(decision.risk)
                ? firstValue(
                    decision.risk.level,
                    decision.risk.risk_level,
                    decision.risk.riskLevel,
                    decision.risk.name
                )
                : decision.risk
        );


    // -------------------------------------------------
    // FINAL NORMALIZED DECISION
    // -------------------------------------------------

    return {

        ...decision,

        decision_id:
            firstValue(
                decision.decision_id,

                decision.decisionId,

                response?.decision_id,

                response?.decisionId,

                response?.data?.decision_id,

                response?.data?.decisionId
            ) ?? null,


        risk_level:
            normalizeRiskLevel(
                rawRiskLevel
            ),


        risk_score:
            normalizedRiskScore,


        risk_count:
            Math.max(
                0,
                normalizedRiskCount
            ),


        identified_risks:
            identifiedRisks,


        recommendations:
            Array.isArray(
                recommendations
            )
                ? recommendations
                : [],


        insights:
            normalizeInsights(
                firstValue(
                    decision.insights,

                    decision.business_insights,

                    decision.businessInsights
                )
            ),


        metrics:
            metrics,
    };
};


// =====================================================
// NORMALIZE HISTORY ENTRY
// =====================================================

export const normalizeHistoryEntry = (entry) => {

    if (
        !entry ||
        typeof entry !== "object"
    ) {
        return null;
    }


    const rawDecision =
        getHistoryDecision(
            entry
        );


    const decision =
        normalizeDecision(
            rawDecision
        );


    if (!decision) {
        return null;
    }


    return {

        ...entry,

        decision_id:
            firstValue(
                entry.decision_id,

                entry.decisionId,

                decision.decision_id,

                entry.id
            ) ?? null,


        timestamp:
            getHistoryTimestamp(
                entry
            ),


        decision:
            decision,


        recommendations:
            Array.isArray(
                decision.recommendations
            )
                ? decision.recommendations
                : [],


        identified_risks:
            Array.isArray(
                decision.identified_risks
            )
                ? decision.identified_risks
                : [],


        insights:
            Array.isArray(
                decision.insights
            )
                ? decision.insights
                : [],
    };
};


// =====================================================
// COMPLETE NORMALIZED HISTORY
// =====================================================

export const normalizeDecisionHistoryEntries = (
    response
) => {

    return normalizeDecisionHistory(
        response
    )
        .map(
            normalizeHistoryEntry
        )
        .filter(Boolean)
        .sort(
            (a, b) => {

                const dateA =
                    a.timestamp
                        ? new Date(
                            a.timestamp
                        ).getTime()
                        : NaN;

                const dateB =
                    b.timestamp
                        ? new Date(
                            b.timestamp
                        ).getTime()
                        : NaN;


                const validA =
                    Number.isFinite(
                        dateA
                    );

                const validB =
                    Number.isFinite(
                        dateB
                    );


                if (
                    validA &&
                    validB
                ) {
                    return (
                        dateB -
                        dateA
                    );
                }


                if (
                    validB &&
                    !validA
                ) {
                    return 1;
                }


                if (
                    validA &&
                    !validB
                ) {
                    return -1;
                }


                return 0;
            }
        );
};


// =====================================================
// SAFE RECOMMENDATIONS
// =====================================================

export const getSafeRecommendations = (
    value
) => {

    if (isArray(value)) {
        return value
            .map(
                normalizeRecommendation
            )
            .filter(Boolean);
    }

    return normalizeDecisionRecommendations(
        value
    );
};


// =====================================================
// SAFE RISKS
// =====================================================

export const getSafeRisks = (value) => {

    const result =
        normalizeRisks(
            value
        );

    return Array.isArray(
        result
    )
        ? result
        : [];
};


// =====================================================
// SAFE INSIGHTS
// =====================================================

export const getSafeInsights = (value) => {

    const result =
        normalizeInsights(
            value
        );

    return Array.isArray(
        result
    )
        ? result
        : [];
};


// =====================================================
// DEFAULT EXPORT
// =====================================================

const decisionApi = {

    // API
    runDecisionEngine,

    fetchExecutiveDecisions,

    fetchDecisionRecommendations,

    fetchLatestDecision,

    fetchSalesMetrics,

    fetchForecastMetrics,

    fetchInventoryMetrics,

    fetchCustomerMetrics,

    fetchDecisionHealth,

    clearDecisionHistory,


    // Normalization
    normalizeDecisionResponse,

    normalizeDecisionHistory,

    getHistoryTimestamp,

    getHistoryDecision,

    getLatestDecisionFromHistory,

    normalizeDecisionRecommendations,

    normalizeRiskLevel,

    normalizeRisks,

    normalizeInsights,

    normalizeDecisionMetrics,

    normalizeDecision,

    normalizeHistoryEntry,

    normalizeDecisionHistoryEntries,


    // Safe helpers
    getSafeRecommendations,

    getSafeRisks,

    getSafeInsights,
};


export default decisionApi;
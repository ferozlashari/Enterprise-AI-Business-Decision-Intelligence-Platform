
import {
    TrendingUp,
    Database,
    Users,
    Activity,
} from "lucide-react";

// =====================================================
// SAFE NUMBER
// =====================================================

const toNumber = (value, fallback = null) => {
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
        .replace(/[–—-]{1,}/g, "")
        .trim();

    if (!cleaned) {
        return fallback;
    }

    const numberValue = Number(cleaned);

    return Number.isFinite(numberValue)
        ? numberValue
        : fallback;
};

// =====================================================
// VALID NUMBER
// =====================================================

const hasNumber = (value) => {
    return (
        value !== null &&
        value !== undefined &&
        Number.isFinite(
            Number(value)
        )
    );
};

// =====================================================
// CLAMP
// =====================================================

const clamp = (
    value,
    min = 0,
    max = 100
) => {
    const numberValue = toNumber(
        value,
        min
    );

    return Math.min(
        max,
        Math.max(
            min,
            numberValue
        )
    );
};

// =====================================================
// SALES HEALTH FALLBACK
// =====================================================

const getSalesHealth = (sales) => {
    const value = toNumber(
        sales,
        null
    );

    if (value === null) {
        return null;
    }

    if (value <= 0) {
        return 0;
    }

    /*
     * Fallback only.
     *
     * Backend sales_health has priority.
     */

    const reference = 1000000;

    const score =
        50 +
        20 *
            Math.log10(
                Math.max(
                    1,
                    value / reference
                )
            );

    return Math.round(
        clamp(score)
    );
};

// =====================================================
// INVENTORY HEALTH FALLBACK
// =====================================================

const getInventoryHealth = (
    inventory
) => {
    const value = toNumber(
        inventory,
        null
    );

    if (value === null) {
        return null;
    }

    if (value <= 0) {
        return 0;
    }

    /*
     * Fallback only.
     *
     * Backend inventory_health should
     * eventually use:
     *
     * - demand
     * - safety stock
     * - reorder point
     * - lead time
     */

    const idealInventory = 50000;

    const ratio =
        value / idealInventory;

    let score;

    if (ratio < 0.25) {
        score = 25;
    } else if (ratio < 0.5) {
        score = 50;
    } else if (ratio <= 1.25) {
        score = 100;
    } else if (ratio <= 1.5) {
        score = 80;
    } else if (ratio <= 2) {
        score = 60;
    } else if (ratio <= 3) {
        score = 40;
    } else {
        score = 20;
    }

    return Math.round(
        clamp(score)
    );
};

// =====================================================
// GROWTH HEALTH FALLBACK
// =====================================================

const getGrowthHealth = (
    growth
) => {
    const value = toNumber(
        growth,
        null
    );

    if (value === null) {
        return null;
    }

    if (value <= -20) {
        return 0;
    }

    // -20% => 0
    // -10% => 25
    if (value < -10) {
        return Math.round(
            25 +
                (
                    (value + 20) /
                    10
                ) *
                    25
        );
    }

    // -10% => 25
    // 0% => 50
    if (value < 0) {
        return Math.round(
            25 +
                (
                    (value + 10) /
                    10
                ) *
                    25
        );
    }

    // 0% => 50
    // 10% => 75
    if (value < 10) {
        return Math.round(
            50 +
                (
                    value / 10
                ) *
                    25
        );
    }

    // 10% => 75
    // 20% => 100
    if (value < 20) {
        return Math.round(
            75 +
                (
                    (value - 10) /
                    10
                ) *
                    25
        );
    }

    return 100;
};

// =====================================================
// CHURN HEALTH FALLBACK
// =====================================================

const getChurnHealth = (
    churn
) => {
    const value = toNumber(
        churn,
        null
    );

    if (value === null) {
        return null;
    }

    const safeValue = clamp(
        value,
        0,
        100
    );

    return Math.round(
        clamp(
            100 -
                safeValue * 2
        )
    );
};

// =====================================================
// HEALTH STYLE
// =====================================================

const getHealthClasses = (
    health
) => {
    if (!hasNumber(health)) {
        return {
            text: "text-slate-500",
            bar: "bg-slate-600",
            label: "Unavailable",
        };
    }

    if (health >= 80) {
        return {
            text: "text-emerald-400",
            bar: "bg-emerald-500",
            label: "Healthy",
        };
    }

    if (health >= 60) {
        return {
            text: "text-yellow-400",
            bar: "bg-yellow-500",
            label: "Watch",
        };
    }

    if (health >= 40) {
        return {
            text: "text-orange-400",
            bar: "bg-orange-500",
            label: "At Risk",
        };
    }

    return {
        text: "text-red-400",
        bar: "bg-red-500",
        label: "Critical",
    };
};

// =====================================================
// FORMAT NUMBER
// =====================================================

const formatNumber = (
    value,
    fallback = "—"
) => {
    const numberValue = toNumber(
        value,
        null
    );

    if (numberValue === null) {
        return fallback;
    }

    return numberValue.toLocaleString(
        undefined,
        {
            maximumFractionDigits: 2,
        }
    );
};

// =====================================================
// METRIC CARD
// =====================================================

function MetricCard({
    icon,
    label,
    value,
    health,
    suffix = "",
    description = "",
}) {
    const safeHealth =
        hasNumber(health)
            ? Math.round(
                  clamp(health)
              )
            : null;

    const healthStyle =
        getHealthClasses(
            safeHealth
        );

    const hasValue =
        hasNumber(
            toNumber(
                value,
                null
            )
        );

    return (
        <div
            className="
                bg-slate-800/60
                border
                border-slate-700
                rounded-xl
                p-4
                transition-all
                duration-300
                hover:border-slate-600
                hover:bg-slate-800/80
            "
        >
            {/* HEADER */}

            <div
                className="
                    flex
                    items-center
                    justify-between
                    gap-3
                    mb-3
                "
            >
                <div
                    className="
                        flex
                        items-center
                        gap-2
                        text-slate-400
                        text-sm
                    "
                >
                    {icon}

                    <span>
                        {label}
                    </span>
                </div>

                <span
                    className={`
                        text-xs
                        font-medium
                        ${healthStyle.text}
                    `}
                >
                    {healthStyle.label}
                </span>
            </div>

            {/* VALUE */}

            <div
                className="
                    flex
                    items-baseline
                    gap-1
                "
            >
                <span
                    className="
                        text-2xl
                        font-bold
                        text-white
                    "
                >
                    {hasValue
                        ? formatNumber(
                              value
                          )
                        : "—"}
                </span>

                {suffix &&
                    hasValue && (
                        <span
                            className="
                                text-sm
                                text-slate-400
                            "
                        >
                            {suffix}
                        </span>
                    )}
            </div>

            {/* HEALTH */}

            <div
                className="
                    flex
                    items-center
                    justify-between
                    mt-4
                    mb-2
                "
            >
                <span
                    className="
                        text-xs
                        text-slate-500
                    "
                >
                    Business Health
                </span>

                <span
                    className={`
                        text-xs
                        font-semibold
                        ${healthStyle.text}
                    `}
                >
                    {safeHealth !== null
                        ? `${safeHealth}/100`
                        : "—"}
                </span>
            </div>

            {/* PROGRESS BAR */}

            <div
                className="
                    h-2
                    bg-slate-700
                    rounded-full
                    overflow-hidden
                "
            >
                {safeHealth !== null ? (
                    <div
                        className={`
                            h-full
                            rounded-full
                            transition-all
                            duration-700
                            ${healthStyle.bar}
                        `}
                        style={{
                            width:
                                `${safeHealth}%`,
                        }}
                    />
                ) : (
                    <div
                        className="
                            h-full
                            w-0
                        "
                    />
                )}
            </div>

            {/* DESCRIPTION */}

            {description && (
                <p
                    className="
                        text-xs
                        text-slate-500
                        mt-3
                    "
                >
                    {description}
                </p>
            )}
        </div>
    );
}

// =====================================================
// IMPACT CHART
// =====================================================

export default function ImpactChart({
    metrics = {},
}) {
    // =================================================
    // RAW METRICS
    // =================================================

    const predictedSales =
        toNumber(
            metrics?.predicted_sales,
            null
        );

    const inventory =
        toNumber(
            metrics?.inventory,
            null
        );

    const forecastGrowth =
        toNumber(
            metrics?.forecast_growth,
            null
        );

    const customerChurn =
        toNumber(
            metrics?.customer_churn,
            null
        );

    // =================================================
    // BACKEND HEALTH
    //
    // Backend values have priority.
    // =================================================

    const backendSalesHealth =
        toNumber(
            metrics?.sales_health,
            null
        );

    const backendInventoryHealth =
        toNumber(
            metrics?.inventory_health,
            null
        );

    const backendGrowthHealth =
        toNumber(
            metrics?.growth_health,
            null
        );

    const backendChurnHealth =
        toNumber(
            metrics?.churn_health,
            null
        );

    // =================================================
    // FINAL HEALTH
    // =================================================

    const salesHealth =
        backendSalesHealth !== null
            ? clamp(
                  backendSalesHealth
              )
            : getSalesHealth(
                  predictedSales
              );

    const inventoryHealth =
        backendInventoryHealth !== null
            ? clamp(
                  backendInventoryHealth
              )
            : getInventoryHealth(
                  inventory
              );

    const growthHealth =
        backendGrowthHealth !== null
            ? clamp(
                  backendGrowthHealth
              )
            : getGrowthHealth(
                  forecastGrowth
              );

    const churnHealth =
        backendChurnHealth !== null
            ? clamp(
                  backendChurnHealth
              )
            : getChurnHealth(
                  customerChurn
              );

    // =================================================
    // OVERALL HEALTH
    //
    // Only available metrics are included.
    // Missing values are NOT treated as zero.
    // =================================================

    const backendOverallHealth =
        toNumber(
            metrics?.overall_health,
            null
        );

    const healthValues = [
        salesHealth,
        inventoryHealth,
        growthHealth,
        churnHealth,
    ].filter(
        (value) =>
            value !== null &&
            value !== undefined &&
            Number.isFinite(
                Number(value)
            )
    );

    const calculatedOverallHealth =
        healthValues.length > 0
            ? Math.round(
                  healthValues.reduce(
                      (
                          total,
                          value
                      ) =>
                          total +
                          Number(value),
                      0
                  ) /
                      healthValues.length
              )
            : null;

    const overallHealth =
        backendOverallHealth !== null
            ? Math.round(
                  clamp(
                      backendOverallHealth
                  )
              )
            : calculatedOverallHealth;

    const overallStyle =
        getHealthClasses(
            overallHealth
        );

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
            {/* HEADER */}

            <div
                className="
                    flex
                    flex-col
                    md:flex-row
                    md:items-start
                    md:justify-between
                    gap-4
                    mb-6
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
                        <Activity
                            size={20}
                            className="
                                text-blue-400
                            "
                        />

                        <h2
                            className="
                                text-xl
                                font-bold
                                text-white
                            "
                        >
                            Business Impact Overview
                        </h2>
                    </div>

                    <p
                        className="
                            text-sm
                            text-slate-500
                            mt-1
                        "
                    >
                        Normalized business health
                        metrics from the Decision
                        Engine
                    </p>

                    <p
                        className="
                            text-xs
                            text-slate-600
                            mt-1
                        "
                    >
                        0–100 health scale
                    </p>
                </div>

                {/* OVERALL HEALTH */}

                <div
                    className="
                        min-w-[150px]
                        bg-slate-800/70
                        border
                        border-slate-700
                        rounded-xl
                        px-4
                        py-3
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
                        <span
                            className="
                                text-xs
                                text-slate-500
                            "
                        >
                            Overall Health
                        </span>

                        <span
                            className={`
                                text-xs
                                font-semibold
                                ${overallStyle.text}
                            `}
                        >
                            {
                                overallStyle.label
                            }
                        </span>
                    </div>

                    <div
                        className={`
                            text-2xl
                            font-bold
                            mt-1
                            ${overallStyle.text}
                        `}
                    >
                        {overallHealth !== null
                            ? `${overallHealth}/100`
                            : "—"}
                    </div>

                    <div
                        className="
                            h-1.5
                            bg-slate-700
                            rounded-full
                            overflow-hidden
                            mt-2
                        "
                    >
                        {overallHealth !== null && (
                            <div
                                className={`
                                    h-full
                                    rounded-full
                                    transition-all
                                    duration-700
                                    ${overallStyle.bar}
                                `}
                                style={{
                                    width:
                                        `${overallHealth}%`,
                                }}
                            />
                        )}
                    </div>
                </div>
            </div>

            {/* METRICS */}

            <div
                className="
                    grid
                    grid-cols-1
                    sm:grid-cols-2
                    xl:grid-cols-4
                    gap-4
                "
            >
                {/* SALES */}

                <MetricCard
                    icon={
                        <TrendingUp
                            size={18}
                            className="
                                text-blue-400
                            "
                        />
                    }
                    label="Sales"
                    value={
                        predictedSales
                    }
                    health={
                        salesHealth
                    }
                    description="Predicted sales performance"
                />

                {/* INVENTORY */}

                <MetricCard
                    icon={
                        <Database
                            size={18}
                            className="
                                text-purple-400
                            "
                        />
                    }
                    label="Inventory"
                    value={
                        inventory
                    }
                    health={
                        inventoryHealth
                    }
                    suffix="units"
                    description="Inventory balance and stock health"
                />

                {/* GROWTH */}

                <MetricCard
                    icon={
                        <TrendingUp
                            size={18}
                            className="
                                text-emerald-400
                            "
                        />
                    }
                    label="Growth"
                    value={
                        forecastGrowth
                    }
                    health={
                        growthHealth
                    }
                    suffix="%"
                    description="Forecast business growth"
                />

                {/* CHURN */}

                <MetricCard
                    icon={
                        <Users
                            size={18}
                            className="
                                text-orange-400
                            "
                        />
                    }
                    label="Churn"
                    value={
                        customerChurn
                    }
                    health={
                        churnHealth
                    }
                    suffix="%"
                    description="Customer retention risk"
                />
            </div>
        </div>
    );
}



import {
    ResponsiveContainer,
    PieChart,
    Pie,
    Tooltip,
    Legend,
    Cell,
} from "recharts";

// =====================================================
// ENTERPRISE AI BUSINESS DECISION INTELLIGENCE PLATFORM
//
// CUSTOMER SEGMENTATION PIE CHART
//
// Author: Feroz Ali
//
// Responsibilities:
// - Customer segmentation visualization
// - Safe API data normalization
// - Customer count calculation
// - Percentage calculation
// - Empty-state handling
// - Responsive Recharts visualization
// =====================================================

// =====================================================
// CUSTOMER SEGMENT COLORS
// =====================================================

const COLORS = [
    "#2563eb",
    "#22c55e",
    "#f59e0b",
    "#a855f7",
    "#ef4444",
    "#06b6d4",
    "#ec4899",
    "#84cc16",
];

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

    const cleaned = String(value)
        .replace(/,/g, "")
        .replace(/[$%]/g, "")
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
// CUSTOMER PIE
// =====================================================

export default function CustomerPie({
    data = [],
}) {
    // =================================================
    // NORMALIZE SOURCE DATA
    // =================================================

    const sourceData = Array.isArray(data)
        ? data
        : [];

    // =================================================
    // NORMALIZE CUSTOMER SEGMENTS
    // =================================================

    const chartData = sourceData
        .map((item, index) => {

            // -----------------------------------------
            // STRING ITEM
            // -----------------------------------------

            if (typeof item === "string") {
                return {
                    segment: toStringValue(
                        item,
                        `Cluster ${index + 1}`
                    ),
                    customers: 0,
                };
            }

            // -----------------------------------------
            // NUMBER ITEM
            // -----------------------------------------

            if (typeof item === "number") {
                return {
                    segment:
                        `Cluster ${index + 1}`,

                    customers: Math.max(
                        0,
                        Math.trunc(
                            toNumber(item)
                        )
                    ),
                };
            }

            // -----------------------------------------
            // INVALID ITEM
            // -----------------------------------------

            if (
                !item ||
                typeof item !== "object" ||
                Array.isArray(item)
            ) {
                return null;
            }

            // -----------------------------------------
            // CUSTOMER COUNT
            // -----------------------------------------

            const customerValue = toNumber(
                item.customers ??
                item.customer_count ??
                item.customerCount ??
                item.count ??
                item.value ??
                item.total_customers ??
                item.totalCustomers ??
                item.size ??
                0
            );

            // -----------------------------------------
            // SEGMENT NAME
            // -----------------------------------------

            const segment = toStringValue(
                item.segment ??
                item.name ??
                item.label ??
                item.cluster ??
                item.customer_segment ??
                item.customerSegment ??
                item.cluster_name ??
                item.clusterName,
                `Cluster ${index + 1}`
            );

            return {
                ...item,

                segment,

                customers: Math.max(
                    0,
                    Math.trunc(
                        customerValue
                    )
                ),
            };
        })
        .filter(Boolean);

    // =================================================
    // REMOVE ZERO / INVALID VALUES
    // =================================================

    const validData = chartData.filter(
        (item) =>
            Number.isFinite(
                item.customers
            ) &&
            item.customers > 0
    );

    // =================================================
    // EMPTY STATE
    // =================================================

    if (validData.length === 0) {
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
                <div
                    className="
                        flex
                        flex-col
                        sm:flex-row
                        sm:justify-between
                        sm:items-center
                        gap-2
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
                            Customer Segmentation
                        </h2>

                        <p
                            className="
                                text-slate-400
                                text-sm
                                mt-1
                            "
                        >
                            Customer distribution by cluster
                        </p>
                    </div>

                    <div
                        className="
                            text-blue-400
                            text-sm
                            font-medium
                        "
                    >
                        0 Customers
                    </div>
                </div>

                <div
                    className="
                        h-[350px]
                        flex
                        items-center
                        justify-center
                    "
                >
                    <div className="text-center">
                        <p
                            className="
                                text-slate-400
                                text-sm
                            "
                        >
                            No customer segmentation data available
                        </p>

                        <p
                            className="
                                text-slate-500
                                text-xs
                                mt-2
                            "
                        >
                            Customer cluster information will appear here.
                        </p>
                    </div>
                </div>
            </div>
        );
    }

    // =================================================
    // NUMBER FORMAT
    // =================================================

    const formatNumber = (value) => {
        const number = toNumber(value);

        return new Intl.NumberFormat(
            "en-US",
            {
                maximumFractionDigits: 0,
            }
        ).format(number);
    };

    // =================================================
    // TOTAL CUSTOMERS
    // =================================================

    const totalCustomers =
        validData.reduce(
            (total, item) =>
                total + item.customers,
            0
        );

    // =================================================
    // PERCENTAGE
    // =================================================

    const getPercentage = (
        customers
    ) => {
        if (totalCustomers <= 0) {
            return 0;
        }

        return (
            customers /
            totalCustomers
        ) * 100;
    };

    // =================================================
    // PIE LABEL
    // =================================================

    const renderLabel = ({
        segment,
        customers,
    }) => {
        const percentage =
            getPercentage(customers);

        // Hide very small labels.
        if (percentage < 4) {
            return "";
        }

        const segmentText =
            toStringValue(
                segment,
                "Unknown"
            );

        const shortSegment =
            segmentText.length > 18
                ? `${segmentText.substring(
                    0,
                    15
                )}...`
                : segmentText;

        return (
            `${shortSegment} ` +
            `${percentage.toFixed(1)}%`
        );
    };

    // =================================================
    // TOOLTIP FORMATTER
    // =================================================

    const tooltipFormatter = (
        value,
        name
    ) => {
        const customers =
            toNumber(value);

        const percentage =
            getPercentage(
                customers
            );

        return [
            `${formatNumber(
                customers
            )} (${percentage.toFixed(1)}%)`,

            name ||
                "Customers",
        ];
    };

    // =================================================
    // TOOLTIP LABEL
    // =================================================

    const tooltipLabelFormatter = (
        label
    ) => {
        return `Segment: ${label}`;
    };

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
                hover:border-blue-500
                hover:shadow-blue-500/10
                transition
                duration-200
            "
        >
            {/* =========================================
                HEADER
            ========================================= */}

            <div
                className="
                    flex
                    flex-col
                    sm:flex-row
                    sm:justify-between
                    sm:items-center
                    gap-2
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
                        Customer Segmentation
                    </h2>

                    <p
                        className="
                            text-slate-400
                            text-sm
                            mt-1
                        "
                    >
                        Customer distribution by cluster
                    </p>
                </div>

                <div
                    className="
                        text-blue-400
                        text-sm
                        font-medium
                    "
                >
                    {formatNumber(
                        totalCustomers
                    )} Customers
                </div>
            </div>

            {/* =========================================
                PIE CHART
            ========================================= */}

            <div
                className="
                    w-full
                    h-[350px]
                "
            >
                <ResponsiveContainer
                    width="100%"
                    height="100%"
                >
                    <PieChart>
                        <Pie
                            data={validData}
                            dataKey="customers"
                            nameKey="segment"
                            cx="50%"
                            cy="45%"
                            outerRadius="68%"
                            innerRadius="32%"
                            paddingAngle={2}
                            label={renderLabel}
                            labelLine={{
                                stroke: "#64748b",
                                strokeWidth: 1,
                            }}
                            isAnimationActive={true}
                            animationDuration={600}
                        >
                            {validData.map(
                                (
                                    item,
                                    index
                                ) => (
                                    <Cell
                                        key={
                                            `customer-segment-${index}-${item.segment}`
                                        }
                                        fill={
                                            COLORS[
                                                index %
                                                COLORS.length
                                            ]
                                        }
                                    />
                                )
                            )}
                        </Pie>

                        {/* =================================
                            TOOLTIP
                        ================================= */}

                        <Tooltip
                            contentStyle={{
                                backgroundColor:
                                    "#0f172a",

                                border:
                                    "1px solid #334155",

                                borderRadius:
                                    "8px",

                                color:
                                    "#ffffff",

                                boxShadow:
                                    "0 10px 25px rgba(0,0,0,0.3)",
                            }}

                            labelStyle={{
                                color:
                                    "#cbd5e1",

                                fontWeight:
                                    600,

                                marginBottom:
                                    "4px",
                            }}

                            itemStyle={{
                                color:
                                    "#ffffff",
                            }}

                            labelFormatter={
                                tooltipLabelFormatter
                            }

                            formatter={
                                tooltipFormatter
                            }
                        />

                        {/* =================================
                            LEGEND
                        ================================= */}

                        <Legend
                            verticalAlign="bottom"
                            align="center"
                            layout="horizontal"
                            wrapperStyle={{
                                paddingTop:
                                    "15px",

                                fontSize:
                                    "12px",

                                color:
                                    "#cbd5e1",
                            }}
                        />
                    </PieChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
}


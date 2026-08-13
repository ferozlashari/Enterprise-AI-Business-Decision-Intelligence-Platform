
import {
    DollarSign,
    TrendingUp,
    Package,
    Users,
} from "lucide-react";

// =====================================================
// KPI ICONS
// =====================================================

const icons = {
    Revenue: DollarSign,
    Profit: TrendingUp,
    Inventory: Package,
    Customers: Users,
};

// =====================================================
// KPI BOX
// =====================================================

export default function KPIBox({
    title,
    value,
    trend,
    type = "number",
}) {
    const Icon =
        icons[title] || TrendingUp;

    // =================================================
    // SAFE NUMERIC VALUE
    // =================================================

    const numericValue =
        typeof value === "number"
            ? (
                Number.isFinite(value)
                    ? value
                    : 0
            )
            : Number(
                String(value ?? "")
                    .replace(/,/g, "")
                    .replace(/\$/g, "")
                    .replace(/%/g, "")
                    .trim()
            );

    const safeValue =
        Number.isFinite(numericValue)
            ? numericValue
            : 0;

    // =================================================
    // FORMAT VALUE
    // =================================================

    const formatValue = () => {
        if (type === "currency") {
            return new Intl.NumberFormat(
                "en-US",
                {
                    style: "currency",
                    currency: "USD",
                    minimumFractionDigits: 0,
                    maximumFractionDigits: 0,
                }
            ).format(safeValue);
        }

        if (type === "number") {
            return new Intl.NumberFormat(
                "en-US",
                {
                    maximumFractionDigits: 0,
                }
            ).format(safeValue);
        }

        return String(
            value ?? "0"
        );
    };

    // =================================================
    // TREND
    // =================================================

    const numericTrend =
        typeof trend === "number"
            ? trend
            : Number(
                String(trend ?? "")
                    .replace(/%/g, "")
                    .trim()
            );

    const hasTrend =
        trend !== null &&
        trend !== undefined &&
        trend !== "" &&
        Number.isFinite(numericTrend);

    const trendIsPositive =
        hasTrend &&
        numericTrend >= 0;

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
            <div
                className="
                    flex
                    justify-between
                    items-center
                    gap-4
                "
            >
                {/* KPI INFORMATION */}

                <div className="min-w-0">

                    <p
                        className="
                            text-slate-400
                            text-sm
                            font-medium
                        "
                    >
                        {title}
                    </p>

                    <h2
                        className="
                            text-3xl
                            font-bold
                            text-white
                            mt-2
                            break-words
                        "
                    >
                        {formatValue()}
                    </h2>

                    {/* TREND */}

                    {hasTrend && (
                        <p
                            className={`
                                text-sm
                                mt-2
                                font-medium
                                ${
                                    trendIsPositive
                                        ? "text-green-400"
                                        : "text-red-400"
                                }
                            `}
                        >
                            {trendIsPositive
                                ? "↑"
                                : "↓"}

                            {" "}

                            {Math.abs(
                                numericTrend
                            ).toFixed(1)}

                            %
                        </p>
                    )}

                </div>

                {/* ICON */}

                <div
                    className="
                        bg-blue-500/10
                        p-3
                        rounded-xl
                        shrink-0
                    "
                >
                    <Icon
                        size={35}
                        className="
                            text-blue-400
                        "
                    />
                </div>

            </div>
        </div>
    );
}


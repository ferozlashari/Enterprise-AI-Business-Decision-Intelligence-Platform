
import {
    DollarSign,
    TrendingUp,
    Target,
    BarChart3
} from "lucide-react";

// =====================================================
// ICON MAP
// =====================================================

const ICONS = {
    Revenue: DollarSign,
    Profit: TrendingUp,
    Prediction: Target,
    Growth: TrendingUp
};

// =====================================================
// FORMAT VALUE
// =====================================================

const formatValue = (
    value,
    type = "number"
) => {

    const number = Number(value) || 0;

    // ---------------------------------------------
    // Currency
    // ---------------------------------------------

    if (type === "currency") {

        return new Intl.NumberFormat(
            "en-US",
            {
                style: "currency",
                currency: "USD",
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }
        ).format(number);

    }

    // ---------------------------------------------
    // Percentage
    // ---------------------------------------------

    if (type === "percent") {

        return `${number.toFixed(2)}%`;

    }

    // ---------------------------------------------
    // Normal Number
    // ---------------------------------------------

    return new Intl.NumberFormat(
        "en-US",
        {
            maximumFractionDigits: 2
        }
    ).format(number);

};


// =====================================================
// SALES KPI
// =====================================================

export default function SalesKPI({

    title = "KPI",

    value = 0,

    icon = "Revenue",

    type = "number",

    subtitle = null

}) {

    const Icon =
        ICONS[icon] ||
        BarChart3;


    return (

        <div
            className="
                bg-slate-900
                border
                border-slate-800
                rounded-xl
                p-5
                shadow-sm
                hover:border-slate-700
                transition
            "
        >

            <div
                className="
                    flex
                    items-start
                    justify-between
                    gap-4
                "
            >

                {/* =====================================
                    KPI CONTENT
                ===================================== */}

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
                            text-white
                            text-2xl
                            sm:text-3xl
                            font-bold
                            mt-2
                            break-words
                        "
                    >
                        {formatValue(
                            value,
                            type
                        )}
                    </h2>


                    {subtitle && (

                        <p
                            className="
                                text-slate-500
                                text-xs
                                mt-2
                            "
                        >
                            {subtitle}
                        </p>

                    )}

                </div>


                {/* =====================================
                    KPI ICON
                ===================================== */}

                <div
                    className="
                        shrink-0
                        w-11
                        h-11
                        rounded-lg
                        bg-blue-500/10
                        flex
                        items-center
                        justify-center
                    "
                >

                    <Icon
                        size={24}
                        className="
                            text-blue-400
                        "
                    />

                </div>

            </div>

        </div>

    );

}


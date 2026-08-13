
import {
    Brain,
    TrendingUp,
    Target
} from "lucide-react";


// =====================================================
// FORMAT CURRENCY
// =====================================================

const formatCurrency = (value) => {

    const number =
        Number(value) || 0;


    return new Intl.NumberFormat(
        "en-US",
        {
            style: "currency",
            currency: "USD",
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }
    ).format(number);

};


// =====================================================
// PREDICTION CARD
// =====================================================

export default function PredictionCard({

    prediction = 0,

    model = "AI Model",

    loading = false

}) {


    const numericPrediction =
        Number(prediction) || 0;


    // =================================================
    // LOADING STATE
    // =================================================

    if (loading) {

        return (

            <div
                className="
                    bg-slate-900
                    border
                    border-slate-800
                    rounded-xl
                    p-5
                    shadow-lg
                    animate-pulse
                "
            >

                <div
                    className="
                        h-6
                        w-48
                        bg-slate-800
                        rounded
                    "
                />


                <div
                    className="
                        h-10
                        w-64
                        bg-slate-800
                        rounded
                        mt-6
                    "
                />


                <div
                    className="
                        h-4
                        w-40
                        bg-slate-800
                        rounded
                        mt-5
                    "
                />

            </div>

        );

    }


    // =================================================
    // MAIN CARD
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
                hover:border-slate-700
                transition
            "
        >

            {/* =========================================
                HEADER
            ========================================= */}

            <div
                className="
                    flex
                    items-center
                    justify-between
                    gap-3
                "
            >

                <div
                    className="
                        flex
                        items-center
                        gap-3
                    "
                >

                    {/* AI ICON */}

                    <div
                        className="
                            p-3
                            rounded-lg
                            bg-blue-500/10
                            border
                            border-blue-500/10
                        "
                    >

                        <Brain
                            size={30}
                            className="
                                text-blue-400
                            "
                        />

                    </div>


                    {/* TITLE */}

                    <div>

                        <h2
                            className="
                                text-white
                                font-bold
                                text-xl
                            "
                        >
                            AI Sales Prediction
                        </h2>


                        <p
                            className="
                                text-slate-400
                                text-sm
                                mt-1
                            "
                        >
                            Machine learning forecast
                        </p>

                    </div>

                </div>


                <Target
                    size={22}
                    className="
                        text-purple-400
                    "
                />

            </div>


            {/* =========================================
                PREDICTION VALUE
            ========================================= */}

            <div
                className="
                    mt-6
                "
            >

                <p
                    className="
                        text-slate-400
                        text-sm
                    "
                >
                    Predicted Sales
                </p>


                <h1
                    className="
                        text-3xl
                        md:text-4xl
                        font-bold
                        text-green-400
                        mt-1
                        tracking-tight
                    "
                >
                    {formatCurrency(
                        numericPrediction
                    )}
                </h1>

            </div>


            {/* =========================================
                MODEL INFORMATION
            ========================================= */}

            <div
                className="
                    mt-5
                    flex
                    flex-col
                    sm:flex-row
                    sm:items-center
                    sm:justify-between
                    gap-3
                    border-t
                    border-slate-800
                    pt-4
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

                    <TrendingUp
                        size={18}
                        className="
                            text-green-400
                        "
                    />

                    <span>
                        AI Model
                    </span>

                </div>


                <span
                    className="
                        text-white
                        font-semibold
                        text-sm
                        bg-slate-800
                        px-3
                        py-1.5
                        rounded-lg
                    "
                >
                    {model || "AI Model"}
                </span>

            </div>

        </div>

    );

}



export default function ForecastStats({
    model = "Forecast Model",
    records = 0,
    latestForecast = null,
}) {

    // =====================================================
    // FORMAT NUMBER
    // =====================================================

    const formatNumber = (
        value,
        fallback = "—"
    ) => {

        if (
            value === null ||
            value === undefined ||
            value === ""
        ) {
            return fallback;
        }

        const number = Number(value);

        if (!Number.isFinite(number)) {
            return fallback;
        }

        return number.toLocaleString(
            undefined,
            {
                maximumFractionDigits: 0,
            }
        );
    };


    // =====================================================
    // FORMAT DATE
    // =====================================================

    const formatDate = (value) => {

        if (
            value === null ||
            value === undefined ||
            value === ""
        ) {
            return null;
        }

        const date = new Date(value);

        if (
            Number.isNaN(
                date.getTime()
            )
        ) {
            return String(value);
        }

        return date.toLocaleDateString(
            undefined,
            {
                year: "numeric",
                month: "short",
                day: "numeric",
            }
        );
    };


    // =====================================================
    // NORMALIZE MODEL
    // =====================================================

    const safeModel =
        typeof model === "string" &&
        model.trim()
            ? model.trim()
            : "Forecast Model";


    // =====================================================
    // NORMALIZE RECORDS
    // =====================================================

    const numericRecords =
        Number(records);

    const safeRecords =
        Number.isFinite(
            numericRecords
        )
            ? numericRecords
            : 0;


    // =====================================================
    // NORMALIZE LATEST FORECAST
    // =====================================================

    const safeLatestForecast =
        latestForecast &&
        typeof latestForecast === "object"
            ? latestForecast
            : null;


    // =====================================================
    // LATEST DEMAND
    // =====================================================

    const latestDemand =
        safeLatestForecast?.forecast
        ??
        safeLatestForecast?.demand
        ??
        safeLatestForecast?.predicted_demand
        ??
        safeLatestForecast?.predicted_sales
        ??
        safeLatestForecast?.prediction
        ??
        safeLatestForecast?.yhat
        ??
        safeLatestForecast?.yhat_forecast
        ??
        null;


    // =====================================================
    // LATEST DATE
    // =====================================================

    const latestDate =
        safeLatestForecast?.date
        ??
        safeLatestForecast?.ds
        ??
        safeLatestForecast?.datetime
        ??
        safeLatestForecast?.timestamp
        ??
        null;


    const formattedLatestDate =
        formatDate(
            latestDate
        );


    // =====================================================
    // UI
    // =====================================================

    return (
        <div
            className="
                grid
                grid-cols-1
                sm:grid-cols-3
                gap-4
            "
        >

            {/* =================================================
                FORECAST MODEL
            ================================================= */}

            <div
                className="
                    bg-slate-900
                    border
                    border-slate-800
                    rounded-xl
                    p-5
                    min-w-0
                "
            >

                <p
                    className="
                        text-slate-400
                        text-sm
                    "
                >
                    Forecast Model
                </p>

                <p
                    className="
                        text-xl
                        sm:text-2xl
                        font-bold
                        text-white
                        mt-1
                        break-words
                    "
                    title={safeModel}
                >
                    {safeModel}
                </p>

            </div>


            {/* =================================================
                FORECAST POINTS
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

                <p
                    className="
                        text-slate-400
                        text-sm
                    "
                >
                    Forecast Points
                </p>

                <p
                    className="
                        text-2xl
                        font-bold
                        text-white
                        mt-1
                    "
                >
                    {formatNumber(
                        safeRecords,
                        "0"
                    )}
                </p>

            </div>


            {/* =================================================
                LATEST PREDICTED DEMAND
            ================================================= */}

            <div
                className="
                    bg-slate-900
                    border
                    border-slate-800
                    rounded-xl
                    p-5
                    min-w-0
                "
            >

                <p
                    className="
                        text-slate-400
                        text-sm
                    "
                >
                    Latest Predicted Demand
                </p>

                <p
                    className="
                        text-2xl
                        font-bold
                        text-white
                        mt-1
                    "
                >
                    {formatNumber(
                        latestDemand
                    )}
                </p>


                {/* =================================================
                    LATEST DATE
                ================================================= */}

                {formattedLatestDate && (
                    <p
                        className="
                            text-xs
                            text-slate-500
                            mt-2
                        "
                    >
                        {formattedLatestDate}
                    </p>
                )}

            </div>

        </div>
    );
}


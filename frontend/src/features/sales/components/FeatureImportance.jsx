
import {
    ResponsiveContainer,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    Tooltip,
    CartesianGrid
} from "recharts";


// =====================================================
// FORMAT IMPORTANCE
// (module scope — pure function, no component state)
// =====================================================

const formatImportance = (value) => {

    const number = Number(value) || 0;

    return number.toFixed(4);

};


// =====================================================
// CUSTOM TOOLTIP
// (module scope so it isn't recreated every render)
// =====================================================

const CustomTooltip = ({
    active,
    payload
}) => {

    if (
        !active ||
        !payload ||
        payload.length === 0
    ) {

        return null;

    }


    const item = payload[0]?.payload;


    if (!item) {

        return null;

    }


    return (

        <div
            className="
                bg-slate-950
                border
                border-slate-700
                rounded-lg
                px-4
                py-3
                shadow-xl
                max-w-sm
            "
        >

            <p
                className="
                    text-white
                    font-semibold
                    text-sm
                    break-words
                "
            >
                {item.displayFeature}
            </p>

            <p
                className="
                    text-slate-400
                    text-xs
                    mt-2
                "
            >
                Feature Importance
            </p>

            <p
                className="
                    text-blue-400
                    font-semibold
                    mt-1
                "
            >
                {formatImportance(item.importance)}
            </p>

        </div>

    );

};


// =====================================================
// FEATURE IMPORTANCE
// =====================================================

export default function FeatureImportance({
    data = []
}) {

    // =================================================
    // NORMALIZE FEATURE DATA
    // =================================================

    const chartData = Array.isArray(data)
        ? data
            .filter(
                item =>
                    item &&
                    typeof item === "object"
            )
            .map(item => {

                const rawFeature =
                    item.feature ??
                    item.name ??
                    item.Feature ??
                    "Unknown Feature";


                const importance =
                    Number(
                        item.importance ??
                        item.value ??
                        item.score ??
                        0
                    ) || 0;


                return {

                    feature:
                        String(
                            rawFeature
                        ),

                    displayFeature:
                        formatFeatureName(
                            String(
                                rawFeature
                            )
                        ),

                    importance

                };

            })
            .filter(
                item =>
                    item.importance > 0
            )
            .sort(
                (a, b) =>
                    b.importance -
                    a.importance
            )
        : [];


    // =================================================
    // EMPTY STATE
    // =================================================

    if (chartData.length === 0) {

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

                <h2
                    className="
                        text-white
                        font-bold
                        text-xl
                    "
                >
                    AI Model Explainability
                </h2>


                <p
                    className="
                        text-slate-400
                        mt-3
                        text-sm
                    "
                >
                    No feature importance data available
                </p>

            </div>

        );

    }


    // =================================================
    // FORMAT FEATURE NAME
    // =================================================

    function formatFeatureName(feature) {

        if (!feature) {

            return "Unknown Feature";

        }


        let name =
            String(feature);


        // Remove sklearn transformer prefixes

        name =
            name.replace(
                /^numeric__/i,
                ""
            );


        name =
            name.replace(
                /^categorical__/i,
                ""
            );


        // Convert common encoded names

        name =
            name.replace(
                /^Product ID_/i,
                "Product ID: "
            );


        name =
            name.replace(
                /^Category_/i,
                "Category: "
            );


        name =
            name.replace(
                /^Sub-Category_/i,
                "Sub-Category: "
            );


        name =
            name.replace(
                /^Region_/i,
                "Region: "
            );


        name =
            name.replace(
                /_/g,
                " "
            );


        return name.trim();

    }


    // =================================================
    // MAIN COMPONENT
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

            {/* =========================================
                HEADER
            ========================================== */}

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
                        SHAP Feature Importance
                    </h2>


                    <p
                        className="
                            text-slate-400
                            text-sm
                            mt-1
                        "
                    >
                        Top features influencing the AI sales model
                    </p>

                </div>


                <span
                    className="
                        text-xs
                        text-slate-400
                        bg-slate-800
                        px-3
                        py-1.5
                        rounded-full
                    "
                >
                    {chartData.length} Features
                </span>

            </div>


            {/* =========================================
                CHART
            ========================================== */}

            <ResponsiveContainer
                width="100%"
                height={Math.max(
                    350,
                    chartData.length * 42
                )}
            >

                <BarChart
                    data={chartData}
                    layout="vertical"
                    margin={{
                        top: 10,
                        right: 25,
                        left: 10,
                        bottom: 10
                    }}
                >

                    <CartesianGrid
                        strokeDasharray="3 3"
                        stroke="#334155"
                        horizontal={false}
                    />


                    <XAxis
                        type="number"
                        domain={[
                            0,
                            "auto"
                        ]}
                        tick={{
                            fill: "#94a3b8",
                            fontSize: 12
                        }}
                        tickFormatter={
                            value =>
                                Number(
                                    value
                                ).toFixed(2)
                        }
                        axisLine={{
                            stroke: "#334155"
                        }}
                        tickLine={false}
                    />


                    <YAxis
                        type="category"
                        dataKey="displayFeature"
                        width={230}
                        tick={{
                            fill: "#cbd5e1",
                            fontSize: 11
                        }}
                        axisLine={false}
                        tickLine={false}
                    />


                    <Tooltip
                        content={
                            <CustomTooltip />
                        }
                        cursor={{
                            fill: "rgba(148,163,184,0.08)"
                        }}
                    />


                    <Bar
                        dataKey="importance"
                        name="Importance"
                        radius={[
                            0,
                            6,
                            6,
                            0
                        ]}
                        maxBarSize={28}
                    />

                </BarChart>

            </ResponsiveContainer>

        </div>

    );

}


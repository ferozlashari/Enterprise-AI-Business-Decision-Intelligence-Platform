
import {
    ResponsiveContainer,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    Tooltip,
    CartesianGrid,
    Cell
} from "recharts";


// =====================================================
// CONSTANTS
// =====================================================

const MAX_FEATURES = 15;

const BAR_COLOR = "#3b82f6";


// =====================================================
// FORMAT IMPORTANCE
// =====================================================

const formatImportance = (value) => {

    const number =
        Number(value) || 0;


    return number.toFixed(4);

};


// =====================================================
// FORMAT FEATURE NAME
// =====================================================

const formatFeatureName = (
    value
) => {

    if (
        value === null ||
        value === undefined
    ) {

        return "Unknown Feature";

    }


    let name =
        String(value);


    // ---------------------------------------------
    // Remove preprocessing prefixes
    // ---------------------------------------------

    name =
        name.replace(
            /^numeric__/,
            ""
        );


    name =
        name.replace(
            /^categorical__/,
            ""
        );


    // ---------------------------------------------
    // Convert underscore notation
    // ---------------------------------------------

    name =
        name.replace(
            /_/g,
            " "
        );


    // ---------------------------------------------
    // Clean common prefixes
    // ---------------------------------------------

    name =
        name.replace(
            /^Product ID\s+/i,
            "Product ID: "
        );


    name =
        name.replace(
            /^Category\s+/i,
            "Category: "
        );


    name =
        name.replace(
            /^Sub Category\s+/i,
            "Sub-Category: "
        );


    // ---------------------------------------------
    // Capitalize first letter
    // ---------------------------------------------

    if (
        name.length > 0
    ) {

        name =
            name.charAt(0).toUpperCase() +
            name.slice(1);

    }


    return name;

};


// =====================================================
// NORMALIZE FEATURES
// =====================================================

const normalizeFeatures = (
    data
) => {

    if (
        !Array.isArray(data)
    ) {

        return [];

    }


    const normalized =
        data

            .map((item) => {

                if (
                    typeof item === "string"
                ) {

                    return {

                        feature:
                            formatFeatureName(
                                item
                            ),

                        importance: 0

                    };

                }


                const rawFeature =
                    item?.feature ??
                    item?.Feature ??
                    item?.name ??
                    item?.Name ??
                    item?.feature_name ??
                    item?.["Feature Name"] ??
                    "Unknown Feature";


                const rawImportance =
                    item?.importance ??
                    item?.Importance ??
                    item?.importance_score ??
                    item?.score ??
                    item?.value ??
                    item?.shap_value ??
                    item?.mean_abs_shap ??
                    0;


                const importance =
                    Math.abs(
                        Number(
                            rawImportance
                        ) || 0
                    );


                return {

                    feature:
                        formatFeatureName(
                            rawFeature
                        ),

                    importance

                };

            })

            .filter(
                item =>
                    Number.isFinite(
                        item.importance
                    )
            )

            .sort(
                (a, b) =>
                    b.importance -
                    a.importance
            );


    return normalized;

};


// =====================================================
// TOOLTIP
// =====================================================

function CustomTooltip({
    active,
    payload
}) {

    if (
        !active ||
        !payload ||
        payload.length === 0
    ) {

        return null;

    }


    const item =
        payload[0]?.payload;


    if (!item) {

        return null;

    }


    return (

        <div
            className="
                max-w-xs
                bg-slate-950
                border
                border-slate-700
                rounded-lg
                px-4
                py-3
                shadow-xl
            "
        >

            <p
                className="
                    text-slate-300
                    text-xs
                    mb-1
                "
            >
                Feature
            </p>


            <p
                className="
                    text-white
                    font-semibold
                    text-sm
                    break-words
                "
            >
                {item.feature}
            </p>


            <div
                className="
                    mt-2
                    flex
                    items-center
                    justify-between
                    gap-4
                "
            >

                <span
                    className="
                        text-slate-500
                        text-xs
                    "
                >
                    SHAP Importance
                </span>


                <span
                    className="
                        text-blue-400
                        font-bold
                        text-sm
                    "
                >
                    {formatImportance(
                        item.importance
                    )}
                </span>

            </div>

        </div>

    );

}


// =====================================================
// FEATURE IMPORTANCE
// =====================================================

export default function FeatureImportance({

    data = []

}) {


    // =================================================
    // NORMALIZE
    // =================================================

    const normalizedData =
        normalizeFeatures(
            data
        );


    // =================================================
    // TOP FEATURES
    // =================================================

    const chartData =
        normalizedData
            .slice(
                0,
                MAX_FEATURES
            )
            .reverse();


    // =================================================
    // TOTAL FEATURES
    // =================================================

    const totalFeatures =
        normalizedData.length;


    // =================================================
    // TOP FEATURE
    // =================================================

    const topFeature =
        normalizedData[0];


    // =================================================
    // EMPTY STATE
    // =================================================

    if (
        chartData.length === 0
    ) {

        return (

            <div
                className="
                    bg-slate-900
                    border
                    border-slate-800
                    rounded-xl
                    p-5
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
                        Top features influencing
                        the AI sales model
                    </p>

                </div>


                <div
                    className="
                        mt-5
                        h-[350px]
                        flex
                        items-center
                        justify-center
                        border
                        border-slate-800
                        rounded-lg
                    "
                >

                    <p
                        className="
                            text-slate-500
                        "
                    >
                        No feature importance
                        data available
                    </p>

                </div>

            </div>

        );

    }


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
                shadow-sm
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
                    sm:items-start
                    sm:justify-between
                    gap-4
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
                        Top features influencing
                        the AI sales model
                    </p>

                </div>


                <div
                    className="
                        bg-blue-500/10
                        border
                        border-blue-500/20
                        rounded-lg
                        px-3
                        py-2
                        text-right
                        shrink-0
                    "
                >

                    <p
                        className="
                            text-slate-500
                            text-xs
                        "
                    >
                        Features
                    </p>


                    <p
                        className="
                            text-blue-400
                            font-bold
                            text-sm
                        "
                    >
                        {totalFeatures}
                    </p>

                </div>

            </div>


            {/* =========================================
                TOP FEATURE SUMMARY
            ========================================= */}

            {topFeature && (

                <div
                    className="
                        mb-5
                        bg-slate-950/60
                        border
                        border-slate-800
                        rounded-lg
                        px-4
                        py-3
                        flex
                        flex-col
                        sm:flex-row
                        sm:items-center
                        sm:justify-between
                        gap-3
                    "
                >

                    <div
                        className="
                            min-w-0
                        "
                    >

                        <p
                            className="
                                text-slate-500
                                text-xs
                            "
                        >
                            Most Influential Feature
                        </p>


                        <p
                            className="
                                text-white
                                font-semibold
                                mt-1
                                truncate
                            "
                            title={
                                topFeature.feature
                            }
                        >
                            {topFeature.feature}
                        </p>

                    </div>


                    <div
                        className="
                            text-left
                            sm:text-right
                            shrink-0
                        "
                    >

                        <p
                            className="
                                text-blue-400
                                font-bold
                            "
                        >
                            {formatImportance(
                                topFeature.importance
                            )}
                        </p>


                        <p
                            className="
                                text-slate-500
                                text-xs
                            "
                        >
                            SHAP importance
                        </p>

                    </div>

                </div>

            )}


            {/* =========================================
                CHART
            ========================================= */}

            <ResponsiveContainer
                width="100%"
                height={
                    Math.max(
                        350,
                        chartData.length * 38
                    )
                }
            >

                <BarChart
                    data={chartData}
                    layout="vertical"
                    margin={{
                        top: 5,
                        right: 20,
                        left: 10,
                        bottom: 5
                    }}
                >

                    <CartesianGrid
                        strokeDasharray="3 3"
                        stroke="#334155"
                        horizontal={false}
                    />


                    <XAxis
                        type="number"
                        tick={{
                            fill: "#94a3b8",
                            fontSize: 11
                        }}
                        axisLine={{
                            stroke: "#334155"
                        }}
                        tickLine={false}
                        domain={[
                            0,
                            "auto"
                        ]}
                    />


                    <YAxis
                        type="category"
                        dataKey="feature"
                        width={190}
                        tick={{
                            fill: "#cbd5e1",
                            fontSize: 11
                        }}
                        axisLine={false}
                        tickLine={false}
                    />


                    <Tooltip
                        cursor={{
                            fill:
                                "rgba(51,65,85,0.25)"
                        }}
                        content={
                            <CustomTooltip />
                        }
                    />


                    <Bar
                        dataKey="importance"
                        radius={[
                            0,
                            5,
                            5,
                            0
                        ]}
                        maxBarSize={24}
                    >

                        {chartData.map(
                            (
                                item,
                                index
                            ) => (

                                <Cell
                                    key={
                                        `feature-${index}`
                                    }
                                    fill={
                                        BAR_COLOR
                                    }
                                />

                            )
                        )}

                    </Bar>

                </BarChart>

            </ResponsiveContainer>


            {/* =========================================
                FOOTER
            ========================================= */}

            <div
                className="
                    mt-4
                    pt-4
                    border-t
                    border-slate-800
                    flex
                    flex-col
                    sm:flex-row
                    sm:items-center
                    sm:justify-between
                    gap-2
                "
            >

                <span
                    className="
                        text-slate-500
                        text-xs
                    "
                >
                    Showing top{" "}
                    {Math.min(
                        MAX_FEATURES,
                        totalFeatures
                    )}{" "}
                    features
                </span>


                <span
                    className="
                        text-slate-500
                        text-xs
                    "
                >
                    SHAP model explainability
                </span>

            </div>

        </div>

    );

}


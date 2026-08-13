
// =====================================================
// ENTERPRISE AI BUSINESS DECISION INTELLIGENCE PLATFORM
//
// RecommendationCard
//
// Responsibilities:
// - Safely render AI recommendations
// - Handle multiple backend response formats
// - Prevent recommendations.map errors
// - Normalize recommendation fields
// - Format confidence scores
// - Display priority/severity
// - Handle empty/null/invalid responses
// =====================================================

// =====================================================
// SAFE STRING
// =====================================================

const toSafeString = (value, fallback = "") => {
    if (
        value === null ||
        value === undefined
    ) {
        return fallback;
    }

    if (
        typeof value === "object"
    ) {
        return fallback;
    }

    const result = String(value).trim();

    return result || fallback;
};


// =====================================================
// EXTRACT TEXT FROM OBJECT
// =====================================================

const extractText = (
    value,
    fallback = ""
) => {

    if (
        value === null ||
        value === undefined
    ) {
        return fallback;
    }

    if (
        typeof value === "string" ||
        typeof value === "number" ||
        typeof value === "boolean"
    ) {
        return String(value);
    }

    if (
        typeof value === "object"
    ) {

        const nestedValue =
            value.text ??
            value.message ??
            value.description ??
            value.value ??
            value.name ??
            value.title;

        if (
            nestedValue !== undefined &&
            nestedValue !== null &&
            typeof nestedValue !== "object"
        ) {
            return String(
                nestedValue
            ).trim();
        }
    }

    return fallback;
};


// =====================================================
// EXTRACT RECOMMENDATION ARRAY
//
// Supports:
// [
//   {...}
// ]
//
// {
//   recommendations: [...]
// }
//
// {
//   data: {
//      recommendations: [...]
//   }
// }
//
// {
//   result: {
//      recommendations: [...]
//   }
// }
//
// {
//   recommendation: {...}
// }
// =====================================================

const extractRecommendations = (
    response,
    depth = 0
) => {

    // Prevent infinite recursive objects
    if (depth > 10) {
        return [];
    }


    // Direct array
    if (
        Array.isArray(response)
    ) {
        return response;
    }


    // Invalid primitive
    if (
        response === null ||
        response === undefined ||
        typeof response !== "object"
    ) {
        return [];
    }


    // Common array properties
    const arrayCandidates = [
        response.recommendations,
        response.items,
        response.results,
        response.data,
        response.result,
        response.payload,
    ];


    for (
        const candidate
        of arrayCandidates
    ) {

        if (
            Array.isArray(candidate)
        ) {
            return candidate;
        }
    }


    // Nested wrappers
    const nestedCandidates = [
        response.recommendations,
        response.data,
        response.result,
        response.payload,
        response.dashboard,
        response.executive,
    ];


    for (
        const candidate
        of nestedCandidates
    ) {

        if (
            candidate &&
            typeof candidate === "object"
        ) {

            const nested =
                extractRecommendations(
                    candidate,
                    depth + 1
                );

            if (
                nested.length > 0
            ) {
                return nested;
            }
        }
    }


    // Single recommendation object
    const singleRecommendation =
        response.recommendation;


    if (
        singleRecommendation &&
        typeof singleRecommendation === "object" &&
        !Array.isArray(
            singleRecommendation
        )
    ) {

        return [
            singleRecommendation,
        ];
    }


    return [];
};


// =====================================================
// CONFIDENCE FORMATTER
// =====================================================

const formatConfidence = (
    value
) => {

    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {
        return "N/A";
    }


    let confidence;


    // Object confidence
    if (
        typeof value === "object"
    ) {

        confidence =
            Number(
                value.score ??
                value.value ??
                value.confidence ??
                value.confidence_score
            );

    } else {

        confidence =
            Number(value);

    }


    if (
        !Number.isFinite(
            confidence
        )
    ) {
        return "N/A";
    }


    // Backend may return:
    // 0.85
    // 85
    // "85%"
    //
    // Normalize all to percentage.

    if (
        confidence >= 0 &&
        confidence <= 1
    ) {

        confidence =
            confidence * 100;

    }


    confidence =
        Math.max(
            0,
            Math.min(
                100,
                confidence
            )
        );


    return `${Math.round(
        confidence
    )}%`;
};


// =====================================================
// PRIORITY CLASS
// =====================================================

const getPriorityClass = (
    priority
) => {

    const value =
        String(
            priority || "Normal"
        ).toLowerCase();


    if (
        value.includes("critical") ||
        value.includes("urgent")
    ) {

        return "text-red-300";

    }


    if (
        value.includes("high")
    ) {

        return "text-red-400";

    }


    if (
        value.includes("medium") ||
        value.includes("moderate")
    ) {

        return "text-yellow-400";

    }


    if (
        value.includes("low")
    ) {

        return "text-green-400";

    }


    return "text-blue-400";
};


// =====================================================
// PRIORITY BADGE
// =====================================================

const getPriorityBadgeClass = (
    priority
) => {

    const value =
        String(
            priority || "Normal"
        ).toLowerCase();


    if (
        value.includes("critical") ||
        value.includes("urgent") ||
        value.includes("high")
    ) {

        return (
            "bg-red-500/10 " +
            "border-red-500/20"
        );

    }


    if (
        value.includes("medium") ||
        value.includes("moderate")
    ) {

        return (
            "bg-yellow-500/10 " +
            "border-yellow-500/20"
        );

    }


    if (
        value.includes("low")
    ) {

        return (
            "bg-green-500/10 " +
            "border-green-500/20"
        );

    }


    return (
        "bg-blue-500/10 " +
        "border-blue-500/20"
    );
};


// =====================================================
// NORMALIZE SINGLE RECOMMENDATION
// =====================================================

const normalizeRecommendation = (
    item,
    index
) => {

    // Handle primitive recommendation
    if (
        typeof item !== "object" ||
        item === null
    ) {

        const text =
            extractText(
                item,
                "AI Recommendation"
            );

        return {
            id:
                `recommendation-${index + 1}`,

            title:
                text,

            priority:
                "Normal",

            description:
                text,

            confidence:
                null,

            category:
                "AI",

            source:
                null,
        };
    }


    const title =
        extractText(
            item.title ??
            item.name ??
            item.recommendation ??
            item.action ??
            item.recommended_action ??
            item.recommendedAction ??
            item.subject,
            "AI Recommendation"
        );


    const priority =
        extractText(
            item.priority ??
            item.severity ??
            item.level ??
            item.risk_level ??
            item.riskLevel,
            "Normal"
        );


    const description =
        extractText(
            item.description ??
            item.message ??
            item.reason ??
            item.details ??
            item.explanation ??
            item.rationale ??
            item.recommendation,
            "No description available"
        );


    const confidence =
        item.confidence ??
        item.confidence_score ??
        item.confidenceScore ??
        item.score ??
        item.probability ??
        null;


    const category =
        extractText(
            item.category ??
            item.type ??
            item.module ??
            item.source,
            ""
        );


    const id =
        item.id ??
        item.recommendation_id ??
        item.recommendationId ??
        item.uuid ??
        `recommendation-${index + 1}`;


    return {
        ...item,

        id,

        title,

        priority,

        description,

        confidence,

        category,

        source:
            extractText(
                item.source,
                ""
            ),
    };
};


// =====================================================
// RECOMMENDATION CARD
// =====================================================

export default function RecommendationCard({
    recommendations = [],
}) {

    // =================================================
    // NORMALIZE RESPONSE
    // =================================================

    const items =
        extractRecommendations(
            recommendations
        )
        .map(
            (
                item,
                index
            ) =>
                normalizeRecommendation(
                    item,
                    index
                )
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

            {/* =========================================
                HEADER
            ========================================= */}

            <div
                className="
                    flex
                    justify-between
                    items-center
                    gap-3
                    mb-4
                "
            >

                <h2
                    className="
                        text-xl
                        font-bold
                        text-white
                    "
                >
                    AI Recommendations
                </h2>


                {items.length > 0 && (

                    <span
                        className="
                            text-xs
                            text-blue-400
                            bg-blue-500/10
                            border
                            border-blue-500/20
                            px-2
                            py-1
                            rounded-full
                            whitespace-nowrap
                        "
                    >
                        {items.length}{" "}
                        {items.length === 1
                            ? "Recommendation"
                            : "Recommendations"}
                    </span>

                )}

            </div>


            {/* =========================================
                EMPTY STATE
            ========================================= */}

            {items.length === 0 ? (

                <div
                    className="
                        h-[250px]
                        flex
                        items-center
                        justify-center
                        text-center
                    "
                >

                    <div>

                        <p
                            className="
                                text-slate-400
                            "
                        >
                            No AI recommendations available
                        </p>


                        <p
                            className="
                                text-slate-600
                                text-xs
                                mt-2
                            "
                        >
                            Recommendations will appear here
                            when the AI engine generates them.
                        </p>

                    </div>

                </div>

            ) : (

                /* =====================================
                   RECOMMENDATION LIST
                ===================================== */

                <div
                    className="
                        space-y-4
                        max-h-[500px]
                        overflow-y-auto
                        pr-1
                    "
                >

                    {items.map(
                        (
                            item,
                            index
                        ) => {

                            const priority =
                                toSafeString(
                                    item.priority,
                                    "Normal"
                                );


                            const category =
                                toSafeString(
                                    item.category,
                                    ""
                                );


                            return (

                                <div
                                    key={
                                        String(
                                            item.id ??
                                            `recommendation-${index}`
                                        )
                                    }
                                    className="
                                        bg-slate-800
                                        rounded-xl
                                        p-4
                                        border
                                        border-slate-700
                                        hover:border-slate-600
                                        transition
                                        duration-200
                                    "
                                >

                                    {/* =================
                                        TITLE
                                    ================= */}

                                    <div
                                        className="
                                            flex
                                            justify-between
                                            items-start
                                            gap-4
                                        "
                                    >

                                        <h3
                                            className="
                                                text-white
                                                font-semibold
                                                text-lg
                                                leading-snug
                                                break-words
                                            "
                                        >
                                            {item.title}
                                        </h3>


                                        <span
                                            className={`
                                                text-xs
                                                font-semibold
                                                whitespace-nowrap
                                                px-2
                                                py-1
                                                rounded-full
                                                border
                                                ${getPriorityBadgeClass(
                                                    priority
                                                )}
                                                ${getPriorityClass(
                                                    priority
                                                )}
                                            `}
                                        >
                                            {priority}
                                        </span>

                                    </div>


                                    {/* =================
                                        DESCRIPTION
                                    ================= */}

                                    <p
                                        className="
                                            text-slate-300
                                            mt-3
                                            leading-relaxed
                                            break-words
                                        "
                                    >
                                        {item.description}
                                    </p>


                                    {/* =================
                                        FOOTER
                                    ================= */}

                                    <div
                                        className="
                                            mt-4
                                            flex
                                            flex-wrap
                                            justify-between
                                            items-center
                                            gap-3
                                        "
                                    >

                                        <span
                                            className="
                                                text-sm
                                                text-green-400
                                                font-medium
                                            "
                                        >
                                            Confidence:{" "}
                                            {formatConfidence(
                                                item.confidence
                                            )}
                                        </span>


                                        {category && (

                                            <span
                                                className="
                                                    text-xs
                                                    text-slate-500
                                                    bg-slate-900
                                                    px-2
                                                    py-1
                                                    rounded
                                                "
                                            >
                                                {category}
                                            </span>

                                        )}

                                    </div>

                                </div>

                            );

                        }
                    )}

                </div>

            )}

        </div>

    );
}


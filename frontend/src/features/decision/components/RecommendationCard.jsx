
import {
    Lightbulb,
    ArrowRight,
    CheckCircle2,
    AlertCircle,
    Target,
} from "lucide-react";

import { getSafeRecommendations } from "../decision.api";
// =====================================================
// ENTERPRISE AI
// BUSINESS DECISION INTELLIGENCE
// RECOMMENDATION CARD
//
// Responsibilities:
// - Render normalized recommendations safely
// - Never assume recommendations is an array
// - Support backend recommendation objects
// - Support string recommendations
// - Display priority / severity
// - Display optional details
//
// IMPORTANT:
// All heavy response normalization is handled by
// decision.api.js.
// =====================================================

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
// SAFE STRING
// =====================================================

const safeString = (
    value,
    fallback = ""
) => {
    if (
        value === undefined ||
        value === null
    ) {
        return fallback;
    }

    if (
        typeof value === "object"
    ) {
        return fallback;
    }

    const text = String(value).trim();

    return text || fallback;
};

// =====================================================
// CLEAN DISPLAY TEXT
// =====================================================
//
// This is intentionally lightweight because
// decision.api.js already performs normalization.
//
// It only handles final UI cleanup.
// =====================================================

const cleanDisplayText = (
    value
) => {
    const text = safeString(value);

    if (!text) {
        return "";
    }

    return text
        .replace(/^[-•*]\s*/, "")
        .replace(/\s+/g, " ")
        .trim();
};

// =====================================================
// GET RECOMMENDATION TEXT
// =====================================================

const getRecommendationText = (
    item
) => {

    // -------------------------------------------------
    // String
    // -------------------------------------------------

    if (
        typeof item === "string"
    ) {
        return cleanDisplayText(
            item
        );
    }

    // -------------------------------------------------
    // Number / Boolean
    // -------------------------------------------------

    if (
        typeof item === "number" ||
        typeof item === "boolean"
    ) {
        return String(item);
    }

    // -------------------------------------------------
    // Object
    // -------------------------------------------------

    if (
        isObject(item)
    ) {
        return cleanDisplayText(
            firstValue(
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
            )
        );
    }

    return "";
};

// =====================================================
// GET PRIORITY
// =====================================================

const getPriority = (
    item
) => {

    if (
        !isObject(item)
    ) {
        return "NORMAL";
    }

    const priority = firstValue(
        item.priority,
        item.severity,
        item.urgency,
        item.level,
        item.risk_level,
        item.riskLevel
    );

    if (!priority) {
        return "NORMAL";
    }

    const normalized = String(
        priority
    )
        .trim()
        .toUpperCase();

    const aliases = {
        URGENT: "CRITICAL",
        EMERGENCY: "CRITICAL",
        CRITICAL: "CRITICAL",

        IMPORTANT: "HIGH",
        SEVERE: "HIGH",
        HIGH: "HIGH",

        MODERATE: "MEDIUM",
        MEDIUM: "MEDIUM",

        LOW: "LOW",

        NORMAL: "NORMAL",
        STANDARD: "NORMAL",
        RECOMMENDED: "NORMAL",
    };

    return (
        aliases[normalized] ??
        "NORMAL"
    );
};

// =====================================================
// PRIORITY CONFIG
// =====================================================

const priorityConfig = {

    CRITICAL: {
        label: "Critical",
        badge:
            "bg-red-500/10 text-red-400 border-red-500/30",
        icon: AlertCircle,
        iconClass:
            "text-red-400",
    },

    HIGH: {
        label: "High Priority",
        badge:
            "bg-orange-500/10 text-orange-400 border-orange-500/30",
        icon: AlertCircle,
        iconClass:
            "text-orange-400",
    },

    MEDIUM: {
        label: "Medium Priority",
        badge:
            "bg-yellow-500/10 text-yellow-400 border-yellow-500/30",
        icon: Target,
        iconClass:
            "text-yellow-400",
    },

    LOW: {
        label: "Low Priority",
        badge:
            "bg-blue-500/10 text-blue-400 border-blue-500/30",
        icon: Target,
        iconClass:
            "text-blue-400",
    },

    NORMAL: {
        label: "Recommended",
        badge:
            "bg-blue-500/10 text-blue-400 border-blue-500/30",
        icon: Lightbulb,
        iconClass:
            "text-blue-400",
    },
};

// =====================================================
// NORMALIZE FOR UI
// =====================================================

const normalizeForUI = (
    recommendations
) => {

    const safe =
        getSafeRecommendations(
            recommendations
        );

    if (
        !Array.isArray(safe)
    ) {
        return [];
    }

    const normalized = [];
    const seen = new Set();

    for (
        const item of safe
    ) {

        const text =
            getRecommendationText(
                item
            );

        if (!text) {
            continue;
        }

        const key =
            text
                .toLowerCase()
                .replace(/\s+/g, " ")
                .trim();

        if (
            seen.has(key)
        ) {
            continue;
        }

        seen.add(key);

        normalized.push({
            item,
            text,
        });
    }

    return normalized;
};

// =====================================================
// MAIN COMPONENT
// =====================================================

export default function RecommendationCard({
    recommendations = [],
}) {

    // =================================================
    // FINAL SAFE ARRAY
    // =================================================

    const items =
        normalizeForUI(
            recommendations
        );

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
                    flex-col
                    sm:flex-row
                    sm:items-center
                    sm:justify-between
                    gap-3
                    mb-5
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

                        <Lightbulb
                            size={20}
                            className="
                                text-blue-400
                            "
                        />

                        <h2
                            className="
                                text-white
                                font-bold
                                text-xl
                            "
                        >
                            Recommended Actions
                        </h2>

                    </div>

                    <p
                        className="
                            text-slate-500
                            text-xs
                            mt-1
                        "
                    >
                        AI-generated business actions
                        based on current decision metrics
                    </p>

                </div>

                {/* =====================================
                    ACTION COUNT
                ===================================== */}

                {items.length > 0 && (

                    <span
                        className="
                            self-start
                            sm:self-auto
                            bg-blue-500/10
                            text-blue-400
                            border
                            border-blue-500/20
                            text-sm
                            font-medium
                            px-3
                            py-1.5
                            rounded-full
                        "
                    >
                        {items.length} Action
                        {items.length !== 1
                            ? "s"
                            : ""}
                    </span>

                )}

            </div>

            {/* =========================================
                EMPTY STATE
            ========================================= */}

            {items.length === 0 ? (

                <div
                    className="
                        border
                        border-slate-800
                        bg-slate-800/30
                        rounded-lg
                        px-5
                        py-8
                        text-center
                    "
                >

                    <CheckCircle2
                        size={28}
                        className="
                            mx-auto
                            text-emerald-400
                            mb-3
                        "
                    />

                    <p
                        className="
                            text-slate-300
                            text-sm
                            font-medium
                        "
                    >
                        No recommendations generated yet
                    </p>

                    <p
                        className="
                            text-slate-500
                            text-xs
                            mt-1
                        "
                    >
                        Run the Decision Engine to generate
                        business actions from live metrics.
                    </p>

                </div>

            ) : (

                <ul
                    className="
                        space-y-3
                    "
                >

                    {items.map(
                        (
                            recommendation,
                            index
                        ) => {

                            const {
                                item,
                                text,
                            } = recommendation;

                            // ---------------------------------
                            // PRIORITY
                            // ---------------------------------

                            const priority =
                                getPriority(
                                    item
                                );

                            const config =
                                priorityConfig[
                                    priority
                                ] ??
                                priorityConfig.NORMAL;

                            const PriorityIcon =
                                config.icon;

                            // ---------------------------------
                            // DETAILS
                            // ---------------------------------

                            const details =
                                isObject(item)
                                    ? firstValue(
                                        item.details,
                                        item.reason,
                                        item.description
                                    )
                                    : null;

                            const cleanDetails =
                                cleanDisplayText(
                                    details
                                );

                            return (

                                <li
                                    key={`${text}-${index}`}
                                    className="
                                        group
                                        bg-slate-800/40
                                        border
                                        border-slate-800
                                        rounded-lg
                                        p-4
                                        hover:border-blue-500/40
                                        hover:bg-slate-800/60
                                        transition
                                    "
                                >

                                    <div
                                        className="
                                            flex
                                            items-start
                                            gap-3
                                        "
                                    >

                                        {/* =====================
                                            ACTION ICON
                                        ===================== */}

                                        <div
                                            className="
                                                bg-blue-500/10
                                                text-blue-400
                                                rounded-lg
                                                p-2
                                                shrink-0
                                            "
                                        >

                                            <Lightbulb
                                                size={17}
                                            />

                                        </div>

                                        {/* =====================
                                            CONTENT
                                        ===================== */}

                                        <div
                                            className="
                                                flex-1
                                                min-w-0
                                            "
                                        >

                                            <div
                                                className="
                                                    flex
                                                    flex-wrap
                                                    items-center
                                                    gap-2
                                                    mb-1.5
                                                "
                                            >

                                                <span
                                                    className="
                                                        text-xs
                                                        font-semibold
                                                        text-slate-400
                                                    "
                                                >
                                                    Action{" "}
                                                    {index + 1}
                                                </span>

                                                {/* PRIORITY */}

                                                <span
                                                    className={`
                                                        flex
                                                        items-center
                                                        gap-1
                                                        text-[11px]
                                                        font-medium
                                                        px-2
                                                        py-0.5
                                                        rounded-full
                                                        border
                                                        ${config.badge}
                                                    `}
                                                >

                                                    <PriorityIcon
                                                        size={11}
                                                        className={
                                                            config.iconClass
                                                        }
                                                    />

                                                    {
                                                        config.label
                                                    }

                                                </span>

                                            </div>

                                            {/* =================
                                                RECOMMENDATION
                                            ================= */}

                                            <p
                                                className="
                                                    text-sm
                                                    text-slate-200
                                                    leading-relaxed
                                                    break-words
                                                "
                                            >
                                                {text}
                                            </p>

                                            {/* =================
                                                DETAILS
                                            ================= */}

                                            {cleanDetails &&
                                                cleanDetails !==
                                                    text && (

                                                <p
                                                    className="
                                                        text-xs
                                                        text-slate-500
                                                        mt-2
                                                        leading-relaxed
                                                    "
                                                >
                                                    {
                                                        cleanDetails
                                                    }
                                                </p>

                                            )}

                                        </div>

                                        {/* =====================
                                            ARROW
                                        ===================== */}

                                        <ArrowRight
                                            size={17}
                                            className="
                                                text-slate-600
                                                mt-1
                                                shrink-0
                                                group-hover:text-blue-400
                                                group-hover:translate-x-0.5
                                                transition
                                            "
                                        />

                                    </div>

                                </li>

                            );

                        }
                    )}

                </ul>

            )}

        </div>
    );
}


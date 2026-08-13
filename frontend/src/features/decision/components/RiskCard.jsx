
import {
    ShieldAlert,
    ShieldCheck,
    ShieldQuestion,
    AlertTriangle,
    Activity,
    ShieldX,
} from "lucide-react";

// =====================================================
// RISK CONFIGURATION
// =====================================================

const riskConfig = {
    LOW: {
        icon: ShieldCheck,

        badge:
            "bg-emerald-500/10 text-emerald-400 border-emerald-500/30",

        bar: "bg-emerald-500",

        width: "33%",

        title: "Low Business Risk",

        description:
            "Business indicators are currently within healthy ranges.",
    },

    MEDIUM: {
        icon: ShieldQuestion,

        badge:
            "bg-yellow-500/10 text-yellow-400 border-yellow-500/30",

        bar: "bg-yellow-500",

        width: "50%",

        title: "Moderate Business Risk",

        description:
            "Some business indicators require monitoring and corrective action.",
    },

    HIGH: {
        icon: ShieldAlert,

        badge:
            "bg-orange-500/10 text-orange-400 border-orange-500/30",

        bar: "bg-orange-500",

        width: "65%",

        title: "High Business Risk",

        description:
            "Several business indicators require immediate attention.",
    },

    CRITICAL: {
        icon: ShieldX,

        badge:
            "bg-red-500/10 text-red-400 border-red-500/30",

        bar: "bg-red-500",

        width: "90%",

        title: "Critical Business Risk",

        description:
            "Critical business indicators require immediate management attention.",
    },
};

// =====================================================
// NORMALIZE RISK LEVEL
// =====================================================

const normalizeRiskLevel = (value) => {
    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {
        return "LOW";
    }

    const normalized = String(value)
        .trim()
        .toUpperCase();

    const aliases = {
        MODERATE: "MEDIUM",
        SEVERE: "HIGH",
        NOT_RUN: "LOW",
        "NOT RUN": "LOW",
        UNKNOWN: "LOW",
        NONE: "LOW",
        "N/A": "LOW",
        NA: "LOW",
    };

    const resolved =
        aliases[normalized] || normalized;

    return riskConfig[resolved]
        ? resolved
        : "LOW";
};

// =====================================================
// CLEAN TEXT
// =====================================================

const cleanText = (value) => {
    if (
        value === null ||
        value === undefined
    ) {
        return "";
    }

    if (typeof value === "string") {
        return value.trim();
    }

    if (typeof value === "number") {
        return String(value);
    }

    return "";
};

// =====================================================
// EXTRACT RISK MESSAGE
// =====================================================

const getRiskMessage = (risk) => {
    if (
        risk === null ||
        risk === undefined
    ) {
        return "";
    }

    // ---------------------------------------------
    // STRING
    // ---------------------------------------------

    if (typeof risk === "string") {
        return risk
            .replace(/^\s*[-•*]\s*/, "")
            .trim();
    }

    // ---------------------------------------------
    // NUMBER
    // ---------------------------------------------

    if (typeof risk === "number") {
        return String(risk);
    }

    // ---------------------------------------------
    // OBJECT
    // ---------------------------------------------

    if (
        typeof risk === "object" &&
        !Array.isArray(risk)
    ) {
        const possibleFields = [
            "message",
            "description",
            "reason",
            "risk",
            "title",
            "name",
            "detail",
            "factor",
            "label",
        ];

        for (const field of possibleFields) {
            const value = cleanText(
                risk?.[field]
            );

            if (value) {
                return value;
            }
        }

        // Handle objects such as:
        // { "Inventory shortage risk": true }

        const objectKeys =
            Object.keys(risk);

        if (objectKeys.length > 0) {
            return objectKeys
                .filter(
                    (key) =>
                        key &&
                        key !== "undefined"
                )
                .map((key) =>
                    key
                        .replace(/_/g, " ")
                        .trim()
                )
                .join(", ");
        }

        return "";
    }

    // ---------------------------------------------
    // ARRAY
    // ---------------------------------------------

    if (Array.isArray(risk)) {
        return risk
            .map(getRiskMessage)
            .filter(Boolean)
            .join(", ");
    }

    return String(risk).trim();
};

// =====================================================
// NORMALIZE RISKS
// =====================================================

const normalizeRisks = (risks) => {
    if (
        risks === null ||
        risks === undefined
    ) {
        return [];
    }

    // ---------------------------------------------
    // ARRAY
    // ---------------------------------------------

    if (Array.isArray(risks)) {
        return risks
            .flatMap((risk) => {
                // Handle nested arrays
                if (Array.isArray(risk)) {
                    return risk;
                }

                return [risk];
            })
            .map(getRiskMessage)
            .flatMap((risk) =>
                risk
                    ? risk
                        .split(/\r?\n|;/)
                        .map((item) =>
                            item
                                .replace(
                                    /^[-•*]\s*/,
                                    ""
                                )
                                .trim()
                        )
                        .filter(Boolean)
                    : []
            )
            .filter(Boolean);
    }

    // ---------------------------------------------
    // STRING
    // ---------------------------------------------

    if (typeof risks === "string") {
        const text = risks.trim();

        if (!text) {
            return [];
        }

        return text
            .split(/\r?\n|;/)
            .map((risk) =>
                risk
                    .replace(
                        /^[-•*]\s*/,
                        ""
                    )
                    .trim()
            )
            .filter(Boolean);
    }

    // ---------------------------------------------
    // OBJECT
    // ---------------------------------------------

    if (
        typeof risks === "object"
    ) {
        // Object with a risks array
        if (
            Array.isArray(
                risks.risks
            )
        ) {
            return normalizeRisks(
                risks.risks
            );
        }

        // Object with risk factors
        if (
            Array.isArray(
                risks.risk_factors
            )
        ) {
            return normalizeRisks(
                risks.risk_factors
            );
        }

        const message =
            getRiskMessage(risks);

        return message
            ? [message]
            : [];
    }

    return [];
};

// =====================================================
// NORMALIZE NUMBER
// =====================================================

const normalizeNumber = (
    value,
    fallback = null
) => {
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

    if (typeof value === "string") {
        const cleaned = value
            .replace(/,/g, "")
            .replace(/%/g, "")
            .replace(/\$/g, "")
            .trim();

        if (!cleaned) {
            return fallback;
        }

        const number =
            Number(cleaned);

        return Number.isFinite(number)
            ? number
            : fallback;
    }

    const number =
        Number(value);

    return Number.isFinite(number)
        ? number
        : fallback;
};

// =====================================================
// NORMALIZE RISK COUNT
// =====================================================

const normalizeRiskCount = (
    riskCount,
    riskItems
) => {
    const backendCount =
        normalizeNumber(
            riskCount
        );

    if (
        backendCount !== null &&
        backendCount >= 0
    ) {
        return Math.trunc(
            backendCount
        );
    }

    return riskItems.length;
};

// =====================================================
// MAIN COMPONENT
// =====================================================

export default function RiskCard({
    riskLevel = "LOW",
    risks = [],
    riskScore = null,
    riskCount = null,
}) {
    // =================================================
    // NORMALIZE LEVEL
    // =================================================

    const level =
        normalizeRiskLevel(
            riskLevel
        );

    const config =
        riskConfig[level];

    const Icon =
        config.icon;

    // =================================================
    // NORMALIZE RISKS
    // =================================================

    const items =
        normalizeRisks(
            risks
        );

    // =================================================
    // RISK SCORE
    // =================================================

    const numericScore =
        normalizeNumber(
            riskScore
        );

    const hasRiskScore =
        numericScore !== null;

    // =================================================
    // DISPLAY SCORE
    // =================================================

    const displayScore =
        hasRiskScore
            ? Math.min(
                100,
                Math.max(
                    0,
                    numericScore
                )
            )
            : null;

    // =================================================
    // RISK COUNT
    // =================================================

    const displayRiskCount =
        normalizeRiskCount(
            riskCount,
            items
        );

    // =================================================
    // HAS RISKS
    //
    // Backend risk_count and actual risk
    // descriptions are the source of truth.
    // =================================================

    const hasRisks =
        displayRiskCount > 0 ||
        items.length > 0;

    // =================================================
    // DISPLAY
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
                        <Activity
                            size={20}
                            className="text-blue-400"
                        />

                        <h2
                            className="
                                text-white
                                font-bold
                                text-xl
                            "
                        >
                            Risk Assessment
                        </h2>
                    </div>

                    <p
                        className="
                            text-slate-500
                            text-xs
                            mt-1
                        "
                    >
                        Enterprise business risk evaluation
                    </p>
                </div>

                {/* =====================================
                    RISK BADGE
                ===================================== */}

                <span
                    className={`
                        self-start
                        sm:self-auto
                        flex
                        items-center
                        gap-1.5
                        text-sm
                        font-semibold
                        px-3
                        py-1.5
                        rounded-full
                        border
                        ${config.badge}
                    `}
                >
                    <Icon size={16} />

                    {level}
                </span>
            </div>

            {/* =========================================
                RISK STATUS
            ========================================= */}

            <div
                className="
                    bg-slate-800/40
                    border
                    border-slate-800
                    rounded-lg
                    p-4
                    mb-5
                "
            >
                <div
                    className="
                        flex
                        items-center
                        justify-between
                        gap-4
                        mb-2
                    "
                >
                    <div>
                        <p
                            className="
                                text-white
                                font-semibold
                            "
                        >
                            {config.title}
                        </p>

                        <p
                            className="
                                text-slate-400
                                text-sm
                                mt-1
                            "
                        >
                            {config.description}
                        </p>
                    </div>

                    {/* =================================
                        RISK SCORE
                    ================================= */}

                    {hasRiskScore && (
                        <div
                            className="
                                text-right
                                shrink-0
                            "
                        >
                            <p
                                className="
                                    text-2xl
                                    font-bold
                                    text-white
                                "
                            >
                                {Math.round(
                                    displayScore
                                )}
                            </p>

                            <p
                                className="
                                    text-xs
                                    text-slate-500
                                "
                            >
                                Risk Score
                            </p>
                        </div>
                    )}
                </div>

                {/* =====================================
                    RISK SCORE BAR
                ===================================== */}

                <div
                    className="
                        w-full
                        h-2
                        bg-slate-800
                        rounded-full
                        overflow-hidden
                        mt-4
                    "
                    role="progressbar"
                    aria-valuenow={
                        hasRiskScore
                            ? displayScore
                            : undefined
                    }
                    aria-valuemin="0"
                    aria-valuemax="100"
                    aria-label="Business risk score"
                >
                    {hasRiskScore ? (
                        <div
                            className={`
                                h-full
                                rounded-full
                                transition-all
                                duration-700
                                ${config.bar}
                            `}
                            style={{
                                width:
                                    `${displayScore}%`,
                            }}
                        />
                    ) : (
                        <div
                            className={`
                                h-full
                                rounded-full
                                transition-all
                                duration-500
                                ${config.bar}
                            `}
                            style={{
                                width:
                                    config.width,
                            }}
                        />
                    )}
                </div>
            </div>

            {/* =========================================
                RISK COUNT
            ========================================= */}

            <div
                className="
                    flex
                    items-center
                    justify-between
                    bg-slate-800/30
                    border
                    border-slate-800
                    rounded-lg
                    px-4
                    py-3
                    mb-4
                "
            >
                <div>
                    <p
                        className="
                            text-slate-400
                            text-sm
                        "
                    >
                        Identified Risks
                    </p>

                    <p
                        className="
                            text-white
                            text-2xl
                            font-bold
                            mt-0.5
                        "
                    >
                        {displayRiskCount}
                    </p>
                </div>

                <AlertTriangle
                    size={24}
                    className={
                        hasRisks
                            ? "text-yellow-400"
                            : "text-emerald-400"
                    }
                />
            </div>

            {/* =========================================
                RISK DETAILS
            ========================================= */}

            {!hasRisks ? (
                <div
                    className="
                        flex
                        items-center
                        gap-3
                        bg-emerald-500/5
                        border
                        border-emerald-500/20
                        rounded-lg
                        px-4
                        py-4
                    "
                >
                    <ShieldCheck
                        size={20}
                        className="
                            text-emerald-400
                            shrink-0
                        "
                    />

                    <div>
                        <p
                            className="
                                text-emerald-400
                                font-medium
                                text-sm
                            "
                        >
                            No risks identified
                        </p>

                        <p
                            className="
                                text-slate-500
                                text-xs
                                mt-1
                            "
                        >
                            All evaluated business metrics
                            are currently within healthy ranges.
                        </p>
                    </div>
                </div>
            ) : (
                <div>
                    <p
                        className="
                            text-slate-400
                            text-sm
                            font-medium
                            mb-2
                        "
                    >
                        Risk Factors
                    </p>

                    {items.length === 0 ? (
                        <div
                            className="
                                flex
                                items-center
                                gap-3
                                bg-yellow-500/5
                                border
                                border-yellow-500/20
                                rounded-lg
                                px-4
                                py-4
                            "
                        >
                            <AlertTriangle
                                size={20}
                                className="
                                    text-yellow-400
                                    shrink-0
                                "
                            />

                            <p
                                className="
                                    text-yellow-400
                                    text-sm
                                "
                            >
                                The backend reported risks,
                                but no risk descriptions were returned.
                            </p>
                        </div>
                    ) : (
                        <ul
                            className="
                                space-y-2
                            "
                        >
                            {items.map(
                                (
                                    risk,
                                    index
                                ) => {
                                    const message =
                                        getRiskMessage(
                                            risk
                                        );

                                    if (!message) {
                                        return null;
                                    }

                                    return (
                                        <li
                                            key={`${index}-${message}`}
                                            className="
                                                flex
                                                items-start
                                                gap-3
                                                text-sm
                                                text-slate-300
                                                bg-slate-800/50
                                                border
                                                border-slate-800
                                                rounded-lg
                                                px-3
                                                py-3
                                            "
                                        >
                                            <AlertTriangle
                                                size={17}
                                                className="
                                                    text-red-400
                                                    mt-0.5
                                                    shrink-0
                                                "
                                            />

                                            <span className="break-words">
                                                {message}
                                            </span>
                                        </li>
                                    );
                                }
                            )}
                        </ul>
                    )}
                </div>
            )}
        </div>
    );
}


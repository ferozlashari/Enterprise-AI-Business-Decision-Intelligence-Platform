
import {
    CheckCircle2,
    XCircle,
    Activity,
    Server,
    ShieldCheck
} from "lucide-react";


// =====================================================
// SALES HEALTH
// =====================================================

export default function SalesHealth({

    health = {}

}) {

    // =================================================
    // SAFE VALUES
    // =================================================

    const status =
        health?.status ||
        "Unknown";


    const service =
        health?.service ||
        "Sales Intelligence API";


    const backend =
        health?.backend ||
        "API Server";


    const success =
        health?.success !== false;


    // =================================================
    // STATUS NORMALIZATION
    // =================================================

    const normalizedStatus =
        String(status)
            .trim()
            .toLowerCase();


    const isHealthy =
        success &&
        (
            normalizedStatus === "healthy" ||
            normalizedStatus === "active" ||
            normalizedStatus === "running" ||
            normalizedStatus === "ok"
        );


    const isUnknown =
        normalizedStatus === "unknown";


    // =================================================
    // DISPLAY STATUS
    // =================================================

    const displayStatus =
        isHealthy
            ? "Healthy"
            : isUnknown
                ? "Unknown"
                : "Unhealthy";


    // =================================================
    // STATUS STYLING
    // =================================================

    const statusClass =
        isHealthy
            ? {
                text: "text-green-400",
                bg: "bg-green-500/10",
                border: "border-green-500/20",
                dot: "bg-green-500"
            }
            : isUnknown
                ? {
                    text: "text-yellow-400",
                    bg: "bg-yellow-500/10",
                    border: "border-yellow-500/20",
                    dot: "bg-yellow-500"
                }
                : {
                    text: "text-red-400",
                    bg: "bg-red-500/10",
                    border: "border-red-500/20",
                    dot: "bg-red-500"
                };


    // =================================================
    // STATUS ICON
    // =================================================

    const StatusIcon =
        isHealthy
            ? CheckCircle2
            : XCircle;


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
                    items-start
                    justify-between
                    gap-4
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
                            className="
                                text-blue-400
                            "
                        />


                        <h2
                            className="
                                text-white
                                text-xl
                                font-bold
                            "
                        >
                            Sales Service Status
                        </h2>

                    </div>


                    <p
                        className="
                            text-slate-400
                            text-sm
                            mt-1
                        "
                    >
                        Sales intelligence API health
                    </p>

                </div>


                <div
                    className={`
                        flex
                        items-center
                        gap-2
                        px-3
                        py-2
                        rounded-lg
                        border
                        ${statusClass.bg}
                        ${statusClass.border}
                    `}
                >

                    <span
                        className={`
                            w-2
                            h-2
                            rounded-full
                            ${statusClass.dot}
                        `}
                    />


                    <span
                        className={`
                            text-sm
                            font-semibold
                            ${statusClass.text}
                        `}
                    >
                        {displayStatus}
                    </span>

                </div>

            </div>


            {/* =========================================
                STATUS PANEL
            ========================================= */}

            <div
                className="
                    mt-5
                    bg-slate-950/60
                    border
                    border-slate-800
                    rounded-lg
                    p-4
                "
            >

                <div
                    className="
                        flex
                        items-center
                        gap-3
                    "
                >

                    <div
                        className={`
                            w-11
                            h-11
                            rounded-lg
                            flex
                            items-center
                            justify-center
                            ${statusClass.bg}
                        `}
                    >

                        <StatusIcon
                            size={24}
                            className={
                                statusClass.text
                            }
                        />

                    </div>


                    <div>

                        <p
                            className="
                                text-slate-500
                                text-xs
                                uppercase
                                tracking-wide
                            "
                        >
                            Current Status
                        </p>


                        <p
                            className={`
                                text-lg
                                font-bold
                                mt-1
                                ${statusClass.text}
                            `}
                        >
                            {displayStatus}
                        </p>

                    </div>

                </div>

            </div>


            {/* =========================================
                SERVICE INFORMATION
            ========================================= */}

            <div
                className="
                    mt-4
                    grid
                    grid-cols-1
                    sm:grid-cols-2
                    gap-3
                "
            >

                <div
                    className="
                        bg-slate-950/60
                        border
                        border-slate-800
                        rounded-lg
                        p-4
                    "
                >

                    <div
                        className="
                            flex
                            items-center
                            gap-2
                            mb-2
                        "
                    >

                        <Server
                            size={17}
                            className="
                                text-blue-400
                            "
                        />


                        <span
                            className="
                                text-slate-500
                                text-xs
                            "
                        >
                            Service
                        </span>

                    </div>


                    <p
                        className="
                            text-white
                            text-sm
                            font-semibold
                        "
                    >
                        {service}
                    </p>

                </div>


                <div
                    className="
                        bg-slate-950/60
                        border
                        border-slate-800
                        rounded-lg
                        p-4
                    "
                >

                    <div
                        className="
                            flex
                            items-center
                            gap-2
                            mb-2
                        "
                    >

                        <ShieldCheck
                            size={17}
                            className="
                                text-green-400
                            "
                        />


                        <span
                            className="
                                text-slate-500
                                text-xs
                            "
                        >
                            Backend
                        </span>

                    </div>


                    <p
                        className="
                            text-white
                            text-sm
                            font-semibold
                        "
                    >
                        {backend}
                    </p>

                </div>

            </div>


            {/* =========================================
                FOOTER
            ========================================= */}

            <div
                className="
                    mt-4
                    pt-4
                    border-t
                    border-slate-800
                "
            >

                <div
                    className="
                        flex
                        items-center
                        justify-between
                        gap-3
                    "
                >

                    <span
                        className="
                            text-slate-500
                            text-xs
                        "
                    >
                        Sales Intelligence API
                    </span>


                    <span
                        className={`
                            text-xs
                            font-medium
                            ${statusClass.text}
                        `}
                    >
                        {isHealthy
                            ? "Operational"
                            : "Attention Required"}
                    </span>

                </div>

            </div>

        </div>

    );

}


import {
    AlertCircle,
    AlertTriangle,
    Info,
    CheckCircle
} from "lucide-react";


const severityConfig = {
    HIGH: {
        icon: AlertTriangle,
        style:
            "bg-red-500/10 border-red-500/30 text-red-400"
    },

    MEDIUM: {
        icon: AlertCircle,
        style:
            "bg-yellow-500/10 border-yellow-500/30 text-yellow-400"
    },

    LOW: {
        icon: Info,
        style:
            "bg-blue-500/10 border-blue-500/30 text-blue-400"
    },

    INFO: {
        icon: Info,
        style:
            "bg-blue-500/10 border-blue-500/30 text-blue-400"
    }
};


export default function AlertCard({
    alerts = []
}) {

    const items = Array.isArray(alerts)
        ? alerts
        : [];


    const safeText = (value) => {

        if (
            value === null ||
            value === undefined ||
            value === ""
        ) {
            return "N/A";
        }

        if (typeof value === "object") {
            try {
                return JSON.stringify(value);
            } catch {
                return "N/A";
            }
        }

        return String(value);
    };


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

            <div
                className="
                    flex
                    justify-between
                    items-center
                    mb-5
                "
            >

                <h2
                    className="
                        text-white
                        font-bold
                        text-xl
                    "
                >
                    Business Alerts
                </h2>


                {items.length > 0 && (
                    <span
                        className="
                            bg-red-500/10
                            text-red-400
                            text-sm
                            px-3
                            py-1
                            rounded-full
                        "
                    >
                        {items.length} Alert
                        {items.length !== 1
                            ? "s"
                            : ""}
                    </span>
                )}

            </div>


            {items.length === 0 ? (

                <div
                    className="
                        h-[250px]
                        flex
                        flex-col
                        items-center
                        justify-center
                    "
                >

                    <CheckCircle
                        size={40}
                        className="
                            text-green-400
                            mb-3
                        "
                    />

                    <p
                        className="
                            text-slate-400
                            text-center
                        "
                    >
                        No active business alerts
                    </p>

                </div>

            ) : (

                <div
                    className="
                        space-y-4
                        max-h-[500px]
                        overflow-y-auto
                        pr-1
                    "
                >

                    {items.map(
                        (alert, index) => {

                            const severity =
                                safeText(
                                    alert?.severity ??
                                    alert?.priority ??
                                    alert?.level ??
                                    "LOW"
                                )
                                .trim()
                                .toUpperCase();


                            const config =
                                severityConfig[
                                    severity
                                ] ??
                                severityConfig.LOW;


                            const Icon =
                                config.icon;


                            const title =
                                alert?.title ??
                                alert?.name ??
                                alert?.type ??
                                "Business Alert";


                            const message =
                                alert?.message ??
                                alert?.description ??
                                alert?.detail ??
                                alert?.reason ??
                                "No details available";


                            const category =
                                alert?.category ??
                                alert?.type ??
                                "System";


                            const time =
                                alert?.time ??
                                alert?.created_at ??
                                alert?.timestamp ??
                                "Now";


                            return (
                                <div
                                    key={
                                        alert?.id ??
                                        `${severity}-${index}`
                                    }
                                    className={`
                                        border
                                        rounded-xl
                                        p-4
                                        ${config.style}
                                    `}
                                >

                                    <div
                                        className="
                                            flex
                                            justify-between
                                            items-start
                                            gap-4
                                        "
                                    >

                                        <div
                                            className="
                                                flex
                                                items-center
                                                gap-3
                                            "
                                        >

                                            <Icon
                                                size={24}
                                            />

                                            <h3
                                                className="
                                                    font-semibold
                                                    text-white
                                                "
                                            >
                                                {safeText(
                                                    title
                                                )}
                                            </h3>

                                        </div>


                                        <span
                                            className="
                                                text-xs
                                                font-semibold
                                                uppercase
                                                tracking-wide
                                            "
                                        >
                                            {severity}
                                        </span>

                                    </div>


                                    <p
                                        className="
                                            mt-3
                                            text-slate-300
                                            leading-relaxed
                                        "
                                    >
                                        {safeText(
                                            message
                                        )}
                                    </p>


                                    <div
                                        className="
                                            flex
                                            justify-between
                                            mt-3
                                            text-sm
                                            text-slate-400
                                            gap-4
                                        "
                                    >

                                        <span>
                                            {safeText(
                                                category
                                            )}
                                        </span>

                                        <span>
                                            {safeText(
                                                time
                                            )}
                                        </span>

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
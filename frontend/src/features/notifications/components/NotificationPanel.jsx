import {
    AlertTriangle,
    AlertCircle,
    Info,
    Check,
    CheckCheck,
    Loader2,
    RefreshCcw,
} from "lucide-react";


const SEVERITY_STYLE = {
    CRITICAL: {
        icon: AlertTriangle,
        color: "text-red-400",
        badge: "bg-red-500/10 text-red-400",
    },
    HIGH: {
        icon: AlertTriangle,
        color: "text-orange-400",
        badge: "bg-orange-500/10 text-orange-400",
    },
    MEDIUM: {
        icon: AlertCircle,
        color: "text-yellow-400",
        badge: "bg-yellow-500/10 text-yellow-400",
    },
    LOW: {
        icon: Info,
        color: "text-blue-400",
        badge: "bg-blue-500/10 text-blue-400",
    },
};


export default function NotificationPanel({
    alerts,
    loading,
    error,
    busyId,
    canManage,
    onAcknowledge,
    onResolve,
    onRefresh,
}) {

    return (
        <div
            className="
                absolute
                right-0
                top-12
                w-96
                max-h-[28rem]
                overflow-y-auto
                bg-slate-900
                border
                border-slate-800
                rounded-xl
                shadow-2xl
                z-50
            "
        >

            <div
                className="
                    flex
                    items-center
                    justify-between
                    px-4
                    py-3
                    border-b
                    border-slate-800
                    sticky
                    top-0
                    bg-slate-900
                "
            >
                <h3 className="text-white font-semibold text-sm">
                    Business Alerts
                </h3>

                <button
                    onClick={onRefresh}
                    disabled={loading}
                    className="
                        text-slate-400
                        hover:text-white
                        disabled:opacity-50
                        transition
                    "
                    title="Refresh"
                >
                    <RefreshCcw
                        size={14}
                        className={loading ? "animate-spin" : ""}
                    />
                </button>
            </div>

            {error && (
                <div className="px-4 py-3 text-red-400 text-xs">
                    {error}
                </div>
            )}

            {!error && loading && alerts.length === 0 && (
                <div className="flex items-center gap-2 text-slate-400 text-sm px-4 py-6 justify-center">
                    <Loader2 size={16} className="animate-spin" />
                    Loading alerts...
                </div>
            )}

            {!loading && !error && alerts.length === 0 && (
                <p className="text-slate-500 text-sm text-center px-4 py-8">
                    No active alerts — everything looks healthy.
                </p>
            )}

            <ul className="divide-y divide-slate-800">

                {alerts.map((alert) => {

                    const style =
                        SEVERITY_STYLE[alert.severity] ||
                        SEVERITY_STYLE.MEDIUM;

                    const Icon = style.icon;

                    const isBusy = busyId === alert.id;

                    return (

                        <li
                            key={alert.id}
                            className="px-4 py-3"
                        >
                            <div className="flex items-start gap-2.5">

                                <Icon
                                    size={16}
                                    className={`${style.color} mt-0.5 shrink-0`}
                                />

                                <div className="flex-1 min-w-0">

                                    <div className="flex items-center gap-2">
                                        <p className="text-white text-sm font-medium truncate">
                                            {alert.title}
                                        </p>

                                        <span
                                            className={`
                                                text-[10px]
                                                font-semibold
                                                px-1.5
                                                py-0.5
                                                rounded
                                                shrink-0
                                                ${style.badge}
                                            `}
                                        >
                                            {alert.severity}
                                        </span>
                                    </div>

                                    <p className="text-slate-400 text-xs mt-1 leading-relaxed">
                                        {alert.message}
                                    </p>

                                    {canManage && (
                                        <div className="flex items-center gap-3 mt-2">

                                            {!alert.is_read && (
                                                <button
                                                    onClick={() =>
                                                        onAcknowledge(alert.id)
                                                    }
                                                    disabled={isBusy}
                                                    className="
                                                        flex
                                                        items-center
                                                        gap-1
                                                        text-xs
                                                        text-blue-400
                                                        hover:text-blue-300
                                                        disabled:opacity-50
                                                        transition
                                                    "
                                                >
                                                    <Check size={12} />
                                                    Acknowledge
                                                </button>
                                            )}

                                            <button
                                                onClick={() =>
                                                    onResolve(alert.id)
                                                }
                                                disabled={isBusy}
                                                className="
                                                    flex
                                                    items-center
                                                    gap-1
                                                    text-xs
                                                    text-emerald-400
                                                    hover:text-emerald-300
                                                    disabled:opacity-50
                                                    transition
                                                "
                                            >
                                                {isBusy ? (
                                                    <Loader2
                                                        size={12}
                                                        className="animate-spin"
                                                    />
                                                ) : (
                                                    <CheckCheck size={12} />
                                                )}
                                                Resolve
                                            </button>

                                        </div>
                                    )}

                                </div>

                            </div>
                        </li>

                    );

                })}

            </ul>

        </div>
    );

}

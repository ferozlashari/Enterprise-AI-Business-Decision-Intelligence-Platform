import { useContext, useEffect, useRef, useState } from "react";

import { Bell } from "lucide-react";

import { AuthContext } from "../../../context/AuthContext";

import {
    fetchActiveAlerts,
    acknowledgeAlert,
    resolveAlert,
} from "../notifications.api";

import NotificationPanel from "./NotificationPanel";


const POLL_INTERVAL_MS = 30000;

const MANAGE_ROLES = ["admin", "executive", "manager"];


export default function NotificationBell() {

    const { user } = useContext(AuthContext);

    const [open, setOpen] = useState(false);

    const [alerts, setAlerts] = useState([]);

    const [loading, setLoading] = useState(false);

    const [error, setError] = useState(null);

    const [busyId, setBusyId] = useState(null);

    const containerRef = useRef(null);


    const canManage = MANAGE_ROLES.includes(
        String(user?.role || "").toLowerCase()
    );


    useEffect(() => {

        loadAlerts();

        const interval = setInterval(
            loadAlerts,
            POLL_INTERVAL_MS
        );

        return () => clearInterval(interval);

    }, []);


    useEffect(() => {

        const handleClickOutside = (event) => {

            if (
                containerRef.current &&
                !containerRef.current.contains(event.target)
            ) {
                setOpen(false);
            }

        };

        document.addEventListener("mousedown", handleClickOutside);

        return () =>
            document.removeEventListener(
                "mousedown",
                handleClickOutside
            );

    }, []);


    const loadAlerts = async () => {

        try {

            setLoading(true);
            setError(null);

            const data = await fetchActiveAlerts();

            setAlerts(
                Array.isArray(data?.alerts) ? data.alerts : []
            );

        } catch (err) {

            setError(
                err?.message || "Unable to load alerts."
            );

        } finally {

            setLoading(false);

        }

    };


    const handleAcknowledge = async (alertId) => {

        try {

            setBusyId(alertId);

            await acknowledgeAlert(alertId);

            setAlerts((prev) =>
                prev.map((alert) =>
                    alert.id === alertId
                        ? { ...alert, is_read: true }
                        : alert
                )
            );

        } catch {
            // Non-fatal — alert stays unacknowledged, user can retry.
        } finally {
            setBusyId(null);
        }

    };


    const handleResolve = async (alertId) => {

        try {

            setBusyId(alertId);

            await resolveAlert(alertId);

            setAlerts((prev) =>
                prev.filter((alert) => alert.id !== alertId)
            );

        } catch {
            // Non-fatal — alert stays active, user can retry.
        } finally {
            setBusyId(null);
        }

    };


    const unreadCount = alerts.filter(
        (alert) => !alert.is_read
    ).length;


    return (
        <div className="relative" ref={containerRef}>

            <button
                onClick={() => setOpen((prev) => !prev)}
                className="relative text-slate-400 hover:text-white transition"
                aria-label="Notifications"
            >
                <Bell size={20} />

                {unreadCount > 0 && (
                    <span
                        className="
                            absolute
                            -top-1.5
                            -right-1.5
                            bg-red-500
                            text-white
                            text-[10px]
                            font-bold
                            min-w-[16px]
                            h-4
                            rounded-full
                            flex
                            items-center
                            justify-center
                            px-1
                        "
                    >
                        {unreadCount > 9 ? "9+" : unreadCount}
                    </span>
                )}
            </button>

            {open && (
                <NotificationPanel
                    alerts={alerts}
                    loading={loading}
                    error={error}
                    busyId={busyId}
                    canManage={canManage}
                    onAcknowledge={handleAcknowledge}
                    onResolve={handleResolve}
                    onRefresh={loadAlerts}
                />
            )}

        </div>
    );

}

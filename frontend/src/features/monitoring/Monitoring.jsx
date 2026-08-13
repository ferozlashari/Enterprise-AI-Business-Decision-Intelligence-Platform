import { useEffect, useState } from "react";

import { Activity, Loader2 } from "lucide-react";

import {
    fetchSystemHealth,
    fetchSystemMetrics,
    fetchServiceHealth
} from "./monitoring.api";

import PlatformStats from "./components/PlatformStats";
import ServiceHealthGrid from "./components/ServiceHealthGrid";


const REFRESH_INTERVAL_MS = 15000;


export default function Monitoring() {

    const [health, setHealth] = useState(null);

    const [metrics, setMetrics] = useState(null);

    const [services, setServices] = useState([]);

    const [loading, setLoading] = useState(true);

    const [error, setError] = useState(null);


    useEffect(() => {

        loadMonitoring();

        const interval = setInterval(
            loadMonitoring,
            REFRESH_INTERVAL_MS
        );

        return () => clearInterval(interval);

    }, []);


    const loadMonitoring = async () => {

        try {

            setError(null);

            const [healthRes, metricsRes, servicesRes] =
                await Promise.all([
                    fetchSystemHealth(),
                    fetchSystemMetrics(),
                    fetchServiceHealth()
                ]);

            setHealth(healthRes);
            setMetrics(metricsRes);
            setServices(servicesRes);

        } catch (err) {

            setError(
                err?.message || "Unable to load platform status."
            );

        } finally {

            setLoading(false);

        }

    };


    if (loading) {

        return (
            <div className="p-6 text-white flex items-center gap-2 justify-center py-20">
                <Loader2 size={20} className="animate-spin" />
                Checking platform status...
            </div>
        );

    }


    return (
        <div className="p-6 text-white space-y-6">

            <div>
                <h1 className="text-3xl font-bold flex items-center gap-2">
                    <Activity className="text-emerald-400" size={28} />
                    Platform Monitoring
                </h1>
                <p className="text-slate-400 mt-1">
                    Live status of the API gateway and downstream
                    services — refreshes every 15 seconds.
                </p>
            </div>

            {error && (
                <div
                    className="
                        bg-red-500/10
                        border
                        border-red-500/30
                        text-red-400
                        text-sm
                        rounded-lg
                        px-4
                        py-3
                    "
                >
                    {error}
                </div>
            )}

            <PlatformStats health={health} metrics={metrics} />

            <ServiceHealthGrid services={services} />

        </div>
    );

}

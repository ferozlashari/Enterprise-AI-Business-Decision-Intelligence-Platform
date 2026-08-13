import { useState } from "react";

import { Trash2, Loader2, CheckCircle2 } from "lucide-react";

import { clearCache } from "../settings.api";


export default function CacheAdmin() {

    const [clearing, setClearing] = useState(false);

    const [message, setMessage] = useState(null);

    const [error, setError] = useState(null);


    const handleClearCache = async () => {

        try {

            setClearing(true);
            setError(null);
            setMessage(null);

            const result = await clearCache();

            setMessage(
                result?.message || "Cache cleared successfully."
            );

        } catch (err) {

            setError(err?.message || "Unable to clear the cache.");

        } finally {

            setClearing(false);

        }

    };


    return (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">

            <h2 className="text-white font-bold text-xl mb-2">
                Cache
            </h2>

            <p className="text-slate-400 text-sm mb-4">
                Clear the server-side Redis cache. Cached
                predictions, forecasts, and copilot answers
                will be recomputed on next request.
            </p>

            <button
                onClick={handleClearCache}
                disabled={clearing}
                className="
                    flex
                    items-center
                    gap-2
                    bg-slate-800
                    hover:bg-slate-700
                    disabled:opacity-60
                    text-white
                    text-sm
                    font-medium
                    px-4
                    py-2.5
                    rounded-lg
                    border
                    border-slate-700
                    transition
                "
            >
                {clearing ? (
                    <Loader2 size={16} className="animate-spin" />
                ) : (
                    <Trash2 size={16} />
                )}
                {clearing ? "Clearing..." : "Clear Cache"}
            </button>

            {message && (
                <div className="flex items-center gap-2 text-emerald-400 text-sm mt-3">
                    <CheckCircle2 size={14} />
                    {message}
                </div>
            )}

            {error && (
                <div className="text-red-400 text-sm mt-3">
                    {error}
                </div>
            )}

        </div>
    );

}

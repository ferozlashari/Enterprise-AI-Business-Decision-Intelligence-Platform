import { useState } from "react";

import {
    PlayCircle,
    Loader2,
    CheckCircle2,
    ListTodo
} from "lucide-react";

import {
    triggerSalesPredictionTask,
    triggerReportGenerationTask,
    triggerRagRebuildTask
} from "../settings.api";


const TASKS = [
    {
        key: "sales",
        label: "Run Sales Prediction",
        description: "Re-run the sales prediction model as a background job.",
        trigger: triggerSalesPredictionTask
    },
    {
        key: "reports",
        label: "Generate Reports",
        description: "Rebuild all enterprise report JSON files.",
        trigger: triggerReportGenerationTask
    },
    {
        key: "rag",
        label: "Rebuild Knowledge Base",
        description: "Re-index the RAG vector database used by the AI Copilot.",
        trigger: triggerRagRebuildTask
    }
];


export default function TaskAdmin() {

    const [running, setRunning] = useState(null);

    const [results, setResults] = useState({});

    const [errors, setErrors] = useState({});


    const handleRun = async (task) => {

        try {

            setRunning(task.key);

            setErrors((prev) => ({ ...prev, [task.key]: null }));

            const result = await task.trigger();

            setResults((prev) => ({
                ...prev,
                [task.key]: result?.task_id
            }));

        } catch (err) {

            setErrors((prev) => ({
                ...prev,
                [task.key]: err?.message || "Failed to start task."
            }));

        } finally {

            setRunning(null);

        }

    };


    return (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">

            <div className="flex items-center gap-2 mb-2">
                <ListTodo size={18} className="text-slate-400" />
                <h2 className="text-white font-bold text-xl">
                    Background Tasks
                </h2>
            </div>

            <p className="text-slate-400 text-sm mb-4">
                Trigger enterprise data pipeline jobs. Each task
                runs asynchronously via Celery.
            </p>

            <div className="space-y-3">

                {TASKS.map((task) => (

                    <div
                        key={task.key}
                        className="
                            flex
                            items-center
                            justify-between
                            gap-4
                            bg-slate-800/50
                            border
                            border-slate-800
                            rounded-lg
                            px-4
                            py-3
                        "
                    >

                        <div>
                            <p className="text-white text-sm font-medium">
                                {task.label}
                            </p>
                            <p className="text-slate-400 text-xs mt-0.5">
                                {task.description}
                            </p>

                            {results[task.key] && (
                                <p className="flex items-center gap-1.5 text-emerald-400 text-xs mt-1.5">
                                    <CheckCircle2 size={12} />
                                    Queued — task ID {results[task.key]}
                                </p>
                            )}

                            {errors[task.key] && (
                                <p className="text-red-400 text-xs mt-1.5">
                                    {errors[task.key]}
                                </p>
                            )}
                        </div>

                        <button
                            onClick={() => handleRun(task)}
                            disabled={running === task.key}
                            className="
                                flex
                                items-center
                                gap-2
                                shrink-0
                                bg-blue-600
                                hover:bg-blue-500
                                disabled:opacity-60
                                text-white
                                text-xs
                                font-semibold
                                px-3
                                py-2
                                rounded-lg
                                transition
                            "
                        >
                            {running === task.key ? (
                                <Loader2 size={14} className="animate-spin" />
                            ) : (
                                <PlayCircle size={14} />
                            )}
                            Run
                        </button>

                    </div>

                ))}

            </div>

        </div>
    );

}

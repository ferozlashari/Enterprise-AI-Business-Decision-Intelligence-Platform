
import { useCallback, useEffect, useState } from "react";

import {
    Loader2,
    RefreshCcw,
    FileText,
    AlertCircle,
    PlayCircle,
    CheckCircle2
} from "lucide-react";

import {
    fetchExecutiveReport,
    fetchReportFiles,
    fetchSalesReport,
    fetchInventoryReport,
    fetchCustomerReport,
    fetchBusinessReport,
    fetchForecastReport,
    fetchKpiReport,
    fetchDashboardReport,
    fetchCopilotReport,
    generateReports
} from "./reports.api";

import ExecutiveStats from "./components/ExecutiveStats";
import ReportTabs from "./components/ReportTabs";
import ReportFileList from "./components/ReportFileList";

// =====================================================
// REPORT TABS
// =====================================================

const TABS = [
    {
        key: "sales",
        label: "Sales",
        fetcher: fetchSalesReport
    },
    {
        key: "inventory",
        label: "Inventory",
        fetcher: fetchInventoryReport
    },
    {
        key: "customer",
        label: "Customer",
        fetcher: fetchCustomerReport
    },
    {
        key: "forecast",
        label: "Forecast",
        fetcher: fetchForecastReport
    },
    {
        key: "business",
        label: "Business KPI",
        fetcher: fetchBusinessReport
    },
    {
        key: "kpi",
        label: "KPI",
        fetcher: fetchKpiReport
    },
    {
        key: "dashboard",
        label: "Dashboard",
        fetcher: fetchDashboardReport
    },
    {
        key: "copilot",
        label: "AI Insight",
        fetcher: fetchCopilotReport
    }
];

// =====================================================
// REPORTS PAGE
// =====================================================

export default function Reports() {

    const [summary, setSummary] = useState(null);

    const [files, setFiles] = useState([]);

    const [loading, setLoading] = useState(true);

    const [error, setError] = useState(null);

    const [activeTab, setActiveTab] = useState("sales");

    const [tabData, setTabData] = useState(null);

    const [tabLoading, setTabLoading] = useState(false);

    const [generating, setGenerating] = useState(false);

    const [generateMessage, setGenerateMessage] = useState(null);

    // =================================================
    // LOAD OVERVIEW
    // =================================================

    const loadOverview = useCallback(async () => {

        try {

            setLoading(true);
            setError(null);

            const [executive, fileList] = await Promise.all([
                fetchExecutiveReport(),
                fetchReportFiles()
            ]);

            setSummary(
                executive && typeof executive === "object"
                    ? executive
                    : {}
            );

            setFiles(
                Array.isArray(fileList?.files)
                    ? fileList.files
                    : []
            );

        } catch (err) {

            console.error(
                "Enterprise Reports overview error:",
                err
            );

            setError(
                err?.response?.data?.detail ||
                err?.response?.data?.message ||
                err?.message ||
                "Unable to load enterprise reports."
            );

            setSummary({});
            setFiles([]);

        } finally {

            setLoading(false);

        }

    }, []);

    // =================================================
    // LOAD ACTIVE REPORT
    // =================================================

    const loadTab = useCallback(async (tabKey) => {

        const tab = TABS.find(
            (item) => item.key === tabKey
        );

        if (!tab) {
            return;
        }

        try {

            setTabLoading(true);

            // Clear old report immediately.
            setTabData(null);

            const data = await tab.fetcher();

            setTabData(
                data && typeof data === "object"
                    ? data
                    : {}
            );

        } catch (err) {

            console.error(
                `${tabKey} report error:`,
                err
            );

            setTabData({
                error:
                    err?.response?.data?.detail ||
                    err?.response?.data?.message ||
                    err?.message ||
                    "Failed to load report."
            });

        } finally {

            setTabLoading(false);

        }

    }, []);

    // =================================================
    // INITIAL OVERVIEW
    // =================================================

    useEffect(() => {

        loadOverview();

    }, [loadOverview]);

    // =================================================
    // LOAD ACTIVE TAB
    // =================================================

    useEffect(() => {

        loadTab(activeTab);

    }, [activeTab, loadTab]);

    // =================================================
    // REFRESH EVERYTHING
    // =================================================

    const handleRefresh = async () => {

        await Promise.all([
            loadOverview(),
            loadTab(activeTab)
        ]);

    };

    // =================================================
    // GENERATE REPORTS
    // (queues the background job that rebuilds every report
    // file on disk from the latest data)
    // =================================================

    const handleGenerate = async () => {

        try {

            setGenerating(true);
            setGenerateMessage(null);

            const result = await generateReports();

            setGenerateMessage(
                result?.task_id
                    ? `Queued — task ID ${result.task_id}. Files will refresh below shortly.`
                    : "Report generation queued."
            );

        } catch (err) {

            setGenerateMessage(
                err?.response?.data?.detail ||
                err?.message ||
                "Unable to queue report generation."
            );

        } finally {

            setGenerating(false);

        }

    };

    // =================================================
    // INITIAL LOADING
    // =================================================

    if (loading) {

        return (
            <div className="
                min-h-[400px]
                flex
                items-center
                justify-center
                text-white
            ">

                <div className="
                    flex
                    items-center
                    gap-3
                    text-slate-400
                ">

                    <Loader2
                        size={22}
                        className="animate-spin"
                    />

                    Loading enterprise reports...

                </div>

            </div>
        );

    }

    // =================================================
    // RENDER
    // =================================================

    return (
        <div className="
            p-6
            text-white
            space-y-6
        ">

            {/* =========================================
                PAGE HEADER
            ========================================= */}

            <div className="
                flex
                items-center
                justify-between
                gap-4
                flex-wrap
            ">

                <div>

                    <div className="
                        flex
                        items-center
                        gap-3
                    ">

                        <FileText
                            size={28}
                            className="text-blue-400"
                        />

                        <h1 className="
                            text-3xl
                            font-bold
                        ">
                            Enterprise Reports
                        </h1>

                    </div>

                    <p className="
                        text-slate-400
                        mt-1
                    ">
                        Executive summary and generated
                        report archive.
                    </p>

                </div>

                <div className="flex items-center gap-2">

                    <button
                        onClick={handleGenerate}
                        disabled={generating}
                        className="
                            flex
                            items-center
                            gap-2
                            text-sm
                            text-white
                            bg-blue-600
                            hover:bg-blue-500
                            disabled:opacity-50
                            disabled:cursor-not-allowed
                            rounded-lg
                            px-4
                            py-2
                            transition
                        "
                    >

                        {generating ? (
                            <Loader2 size={15} className="animate-spin" />
                        ) : (
                            <PlayCircle size={15} />
                        )}

                        Generate Reports

                    </button>

                    <button
                        onClick={handleRefresh}
                        disabled={loading || tabLoading}
                        className="
                            flex
                            items-center
                            gap-2
                            text-sm
                            text-slate-300
                            bg-slate-800
                            hover:bg-slate-700
                            disabled:opacity-50
                            disabled:cursor-not-allowed
                            border
                            border-slate-700
                            rounded-lg
                            px-4
                            py-2
                            transition
                        "
                    >

                        <RefreshCcw
                            size={15}
                            className={
                                tabLoading
                                    ? "animate-spin"
                                    : ""
                            }
                        />

                        Refresh

                    </button>

                </div>

            </div>

            {generateMessage && (

                <div className="
                    flex
                    items-center
                    gap-2
                    bg-blue-500/10
                    border
                    border-blue-500/30
                    text-blue-300
                    text-sm
                    rounded-lg
                    px-4
                    py-3
                ">
                    <CheckCircle2 size={16} className="shrink-0" />
                    {generateMessage}
                </div>

            )}

            {/* =========================================
                ERROR
            ========================================= */}

            {error && (

                <div className="
                    flex
                    items-start
                    gap-3
                    bg-red-500/10
                    border
                    border-red-500/30
                    text-red-400
                    text-sm
                    rounded-lg
                    px-4
                    py-3
                ">

                    <AlertCircle
                        size={18}
                        className="mt-0.5 shrink-0"
                    />

                    <div>

                        <p className="font-medium">
                            Report loading failed
                        </p>

                        <p className="text-red-400/80 mt-1">
                            {error}
                        </p>

                    </div>

                </div>

            )}

            {/* =========================================
                EXECUTIVE STATISTICS
            ========================================= */}

            <ExecutiveStats
                summary={summary || {}}
            />

            {/* =========================================
                REPORT TABS
            ========================================= */}

            <ReportTabs
                tabs={TABS}
                activeTab={activeTab}
                onSelect={setActiveTab}
                data={tabData}
                loading={tabLoading}
            />

            {/* =========================================
                GENERATED REPORT FILES
            ========================================= */}

            <ReportFileList
                files={files}
            />

        </div>
    );
}


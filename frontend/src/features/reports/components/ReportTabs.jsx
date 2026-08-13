
import { useMemo } from "react";
import {
    Loader2,
    Package,
    TrendingUp,
    Users,
    BarChart3,
    DollarSign,
    Database,
    Target,
    MapPin,
    Award
} from "lucide-react";


// =====================================================
// HELPERS
// =====================================================

const toNumber = (value, fallback = 0) => {

    const parsed = Number(value);

    return Number.isFinite(parsed)
        ? parsed
        : fallback;
};


const money = (value) => {

    return `$${toNumber(value).toLocaleString("en-US", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    })}`;
};


const number = (value) => {

    return toNumber(value).toLocaleString("en-US", {
        minimumFractionDigits: 0,
        maximumFractionDigits: 2
    });
};


const percent = (value) => {

    return `${toNumber(value).toFixed(2)}%`;
};


// =====================================================
// KPI CARD
// =====================================================

function KPI({
    icon: Icon,
    label,
    value,
    description
}) {

    return (
        <div
            className="
                bg-slate-950
                border
                border-slate-800
                rounded-xl
                p-4
            "
        >

            <div className="flex items-center gap-2 text-slate-400 text-sm mb-2">

                <Icon
                    size={16}
                    className="text-blue-400"
                />

                {label}

            </div>

            <div className="text-xl font-bold text-white">
                {value}
            </div>

            {description && (
                <div className="text-xs text-slate-500 mt-1">
                    {description}
                </div>
            )}

        </div>
    );
}


// =====================================================
// TABLE
// =====================================================

function DataTable({
    columns,
    rows
}) {

    if (!Array.isArray(rows) || rows.length === 0) {

        return (
            <div className="text-center text-slate-500 py-8">
                No data available.
            </div>
        );
    }

    return (
        <div className="overflow-x-auto">

            <table className="w-full text-sm">

                <thead>

                    <tr className="border-b border-slate-800">

                        {columns.map((column) => (

                            <th
                                key={column.key}
                                className="
                                    text-left
                                    text-slate-400
                                    font-medium
                                    px-4
                                    py-3
                                    whitespace-nowrap
                                "
                            >
                                {column.label}
                            </th>

                        ))}

                    </tr>

                </thead>


                <tbody>

                    {rows.map((row, index) => (

                        <tr
                            key={index}
                            className="
                                border-b
                                border-slate-800/60
                                hover:bg-slate-800/30
                            "
                        >

                            {columns.map((column) => (

                                <td
                                    key={column.key}
                                    className="
                                        px-4
                                        py-3
                                        text-slate-300
                                        whitespace-nowrap
                                    "
                                >
                                    {column.render
                                        ? column.render(row)
                                        : row?.[column.key] ?? "—"}
                                </td>

                            ))}

                        </tr>

                    ))}

                </tbody>

            </table>

        </div>
    );
}


// =====================================================
// SALES REPORT
// =====================================================

function SalesReport({ data }) {

    const sales = data || {};

    const categorySales =
        Array.isArray(sales.category_sales)
            ? sales.category_sales
            : [];

    const regionSales =
        Array.isArray(sales.region_sales)
            ? sales.region_sales
            : [];

    const salesTrend =
        Array.isArray(sales.sales_trend)
            ? sales.sales_trend
            : [];

    return (

        <div className="space-y-5">

            {/* KPI */}

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">

                <KPI
                    icon={DollarSign}
                    label="Revenue"
                    value={money(sales.revenue ?? sales.total_sales)}
                    description="Total sales revenue"
                />

                <KPI
                    icon={TrendingUp}
                    label="Predicted Sales"
                    value={money(
                        sales.predicted_sales ??
                        sales.prediction
                    )}
                    description="AI prediction"
                />

                <KPI
                    icon={Target}
                    label="Model R²"
                    value={toNumber(sales.r2_score).toFixed(3)}
                    description="Prediction model score"
                />

                <KPI
                    icon={Award}
                    label="Best Category"
                    value={sales.best_category ?? "—"}
                    description="Highest sales category"
                />

            </div>


            {/* CATEGORY */}

            <div className="bg-slate-950 border border-slate-800 rounded-xl p-5">

                <h3 className="text-white font-semibold mb-4 flex items-center gap-2">

                    <BarChart3
                        size={18}
                        className="text-blue-400"
                    />

                    Sales by Category

                </h3>


                <DataTable

                    columns={[
                        {
                            key: "category",
                            label: "Category"
                        },
                        {
                            key: "sales",
                            label: "Sales",
                            render: (row) =>
                                money(row.sales)
                        }
                    ]}

                    rows={categorySales}

                />

            </div>


            {/* REGION */}

            <div className="bg-slate-950 border border-slate-800 rounded-xl p-5">

                <h3 className="text-white font-semibold mb-4 flex items-center gap-2">

                    <MapPin
                        size={18}
                        className="text-blue-400"
                    />

                    Sales by Region

                </h3>


                <DataTable

                    columns={[
                        {
                            key: "region",
                            label: "Region"
                        },
                        {
                            key: "sales",
                            label: "Sales",
                            render: (row) =>
                                money(row.sales)
                        }
                    ]}

                    rows={regionSales}

                />

            </div>


            {/* MONTHLY TREND */}

            <div className="bg-slate-950 border border-slate-800 rounded-xl p-5">

                <h3 className="text-white font-semibold mb-4 flex items-center gap-2">

                    <TrendingUp
                        size={18}
                        className="text-blue-400"
                    />

                    Monthly Sales Trend

                </h3>


                <DataTable

                    columns={[
                        {
                            key: "month",
                            label: "Month"
                        },
                        {
                            key: "sales",
                            label: "Sales",
                            render: (row) =>
                                money(row.sales)
                        }
                    ]}

                    rows={salesTrend}

                />

            </div>


            {/* BEST REGION */}

            <div className="bg-slate-950 border border-slate-800 rounded-xl p-5">

                <div className="flex items-center justify-between">

                    <div>

                        <p className="text-sm text-slate-500">
                            Best Performing Region
                        </p>

                        <p className="text-xl font-bold text-white mt-1">
                            {sales.best_region ?? "—"}
                        </p>

                    </div>


                    <MapPin
                        size={28}
                        className="text-blue-400"
                    />

                </div>

            </div>

        </div>
    );
}


// =====================================================
// INVENTORY REPORT
// =====================================================

function InventoryReport({ data }) {

    const inventory = data || {};

    const inventoryValue =
        inventory.inventory ??
        inventory.Inventory ??
        inventory.inventory_count ??
        0;

    const demand =
        inventory.demand ??
        inventory.Demand ??
        0;

    const products =
        inventory.products ??
        inventory.Products ??
        inventory.inventory_count ??
        0;

    const inventoryData =
        Array.isArray(inventory.inventory_data)
            ? inventory.inventory_data
            : [];

    return (

        <div className="space-y-5">

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">

                <KPI
                    icon={Package}
                    label="Inventory"
                    value={number(inventoryValue)}
                    description="Current inventory quantity"
                />

                <KPI
                    icon={TrendingUp}
                    label="Demand"
                    value={number(demand)}
                    description="Predicted / calculated demand"
                />

                <KPI
                    icon={Database}
                    label="Products"
                    value={number(products)}
                    description="Inventory product quantity"
                />

            </div>


            <div className="bg-slate-950 border border-slate-800 rounded-xl p-5">

                <h3 className="text-white font-semibold mb-4 flex items-center gap-2">

                    <Package
                        size={18}
                        className="text-blue-400"
                    />

                    Inventory Overview

                </h3>


                <DataTable

                    columns={[
                        {
                            key: "product",
                            label: "Product"
                        },
                        {
                            key: "quantity",
                            label: "Quantity",
                            render: (row) =>
                                number(row.quantity)
                        },
                        {
                            key: "demand",
                            label: "Demand",
                            render: (row) =>
                                number(row.demand)
                        }
                    ]}

                    rows={inventoryData}

                />

            </div>

        </div>
    );
}


// =====================================================
// CUSTOMER REPORT
// =====================================================

function CustomerReport({ data }) {

    const customer = data || {};

    const customers =
        customer.customers ??
        customer.Customers ??
        customer.customer_count ??
        customer.total_customers ??
        0;

    const churn =
        customer.churn ??
        customer.customer_churn ??
        customer.churn_rate ??
        null;

    return (

        <div className="space-y-5">

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">

                <KPI
                    icon={Users}
                    label="Customers"
                    value={number(customers)}
                    description="Enterprise customers"
                />

                <KPI
                    icon={TrendingUp}
                    label="Customer Churn"
                    value={
                        churn === null
                            ? "—"
                            : percent(churn)
                    }
                    description="Customer retention indicator"
                />

                <KPI
                    icon={Target}
                    label="Customer Status"
                    value={
                        churn === null
                            ? "Available"
                            : toNumber(churn) > 10
                                ? "At Risk"
                                : "Healthy"
                    }
                    description="Based on churn"
                />

            </div>


            <div className="bg-slate-950 border border-slate-800 rounded-xl p-5">

                <h3 className="text-white font-semibold mb-3">
                    Customer Intelligence
                </h3>

                <p className="text-slate-400 text-sm">
                    Customer analytics returned by the enterprise
                    customer intelligence service.
                </p>

            </div>

        </div>
    );
}


// =====================================================
// BUSINESS KPI REPORT
// =====================================================

function BusinessReport({ data }) {

    const business = data || {};

    const revenue =
        business.revenue ??
        business.total_sales ??
        0;

    const profit =
        business.profit ??
        0;

    const growth =
        business.growth ??
        business.sales_growth ??
        null;

    const customers =
        business.customers ??
        business.total_customers ??
        0;

    return (

        <div className="space-y-5">

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">

                <KPI
                    icon={DollarSign}
                    label="Revenue"
                    value={money(revenue)}
                    description="Enterprise revenue"
                />

                <KPI
                    icon={TrendingUp}
                    label="Profit"
                    value={money(profit)}
                    description="Enterprise profit"
                />

                <KPI
                    icon={Users}
                    label="Customers"
                    value={number(customers)}
                    description="Customer base"
                />

                <KPI
                    icon={Target}
                    label="Growth"
                    value={
                        growth === null
                            ? "—"
                            : percent(growth)
                    }
                    description="Business growth"
                />

            </div>


            <div className="bg-slate-950 border border-slate-800 rounded-xl p-5">

                <h3 className="text-white font-semibold mb-3">
                    Business Performance
                </h3>

                <p className="text-slate-400 text-sm">
                    Consolidated business performance indicators
                    returned by the enterprise reporting engine.
                </p>

            </div>

        </div>
    );
}


// =====================================================
// MAIN COMPONENT
// =====================================================

export default function ReportTabs({
    tabs,
    activeTab,
    onSelect,
    data,
    loading
}) {

    const renderedReport = useMemo(() => {

        if (!data) {
            return null;
        }

        if (data.error) {

            return (
                <div className="text-red-400 text-sm">
                    {data.error}
                </div>
            );
        }


        switch (activeTab) {

            case "sales":
                return <SalesReport data={data} />;

            case "inventory":
                return <InventoryReport data={data} />;

            case "customer":
                return <CustomerReport data={data} />;

            case "business":
                return <BusinessReport data={data} />;

            default:
                return (
                    <div className="text-slate-500">
                        No report selected.
                    </div>
                );
        }

    }, [activeTab, data]);


    return (

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">

            {/* =================================================
                HEADER
            ================================================= */}

            <div className="mb-5">

                <h2 className="text-white font-bold text-xl">
                    Business Reports
                </h2>

                <p className="text-slate-500 text-sm mt-1">
                    Detailed enterprise analytics
                </p>

            </div>


            {/* =================================================
                TABS
            ================================================= */}

            <div className="flex items-center gap-2 mb-6 flex-wrap">

                {tabs.map((tab) => (

                    <button
                        key={tab.key}
                        onClick={() => onSelect(tab.key)}
                        className={`
                            text-sm
                            font-medium
                            px-4
                            py-2
                            rounded-lg
                            transition
                            ${
                                activeTab === tab.key
                                    ? "bg-blue-600 text-white"
                                    : "bg-slate-800 text-slate-300 hover:bg-slate-700"
                            }
                        `}
                    >
                        {tab.label}
                    </button>

                ))}

            </div>


            {/* =================================================
                CONTENT
            ================================================= */}

            {loading ? (

                <div className="flex items-center gap-2 text-slate-400 py-12 justify-center">

                    <Loader2
                        size={20}
                        className="animate-spin"
                    />

                    Loading {activeTab} report...

                </div>

            ) : (

                renderedReport

            )}


            {/* =================================================
                RAW DATA
            ================================================= */}

            {!loading && data && (

                <details className="mt-6">

                    <summary
                        className="
                            cursor-pointer
                            text-xs
                            text-slate-500
                            hover:text-slate-300
                            select-none
                        "
                    >
                        Show raw report data
                    </summary>


                    <pre
                        className="
                            mt-3
                            bg-slate-950
                            border
                            border-slate-800
                            rounded-lg
                            p-4
                            text-xs
                            text-slate-400
                            overflow-x-auto
                            max-h-96
                            overflow-y-auto
                        "
                    >
                        {JSON.stringify(data, null, 2)}
                    </pre>

                </details>

            )}

        </div>

    );
}


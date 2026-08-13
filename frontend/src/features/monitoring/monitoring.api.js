import api from "../../api/axios";


// =====================================================
// PLATFORM HEALTH
// =====================================================

export const fetchSystemHealth = async () => {

    const response = await api.get("/monitor/health");

    return response.data;

};


// =====================================================
// REQUEST METRICS
// =====================================================

export const fetchSystemMetrics = async () => {

    const response = await api.get("/monitor/metrics");

    return response.data;

};


// =====================================================
// PER-SERVICE HEALTH CHECKS
// =====================================================

export const fetchServiceHealth = async () => {

    const [sales, inventory, forecast, customer, reports, copilot] =
        await Promise.allSettled([
            api.get("/sales/health"),
            api.get("/inventory/health"),
            api.get("/forecast/health"),
            api.get("/customer/health"),
            api.get("/reports/health"),
            api.get("/copilot/health")
        ]);

    const resolve = (result, name) => ({
        name,
        status:
            result.status === "fulfilled"
                ? result.value?.data?.status ?? "Healthy"
                : "Unreachable"
    });

    return [
        resolve(sales, "Sales"),
        resolve(inventory, "Inventory"),
        resolve(forecast, "Forecast"),
        resolve(customer, "Customer"),
        resolve(reports, "Reports"),
        resolve(copilot, "Copilot")
    ];

};


import api from "../../api/axios";

// =====================================================
// ENTERPRISE REPORT API
// =====================================================

const unwrap = (response) => {
    return response?.data ?? {};
};

// =====================================================
// ALL REPORTS
// =====================================================

export const fetchAllReports = async () => {
    const response = await api.get("/reports/all");
    return unwrap(response);
};

// =====================================================
// SALES REPORT
// =====================================================

export const fetchSalesReport = async () => {
    const response = await api.get("/reports/sales");
    return unwrap(response);
};

// =====================================================
// INVENTORY REPORT
// =====================================================

export const fetchInventoryReport = async () => {
    const response = await api.get("/reports/inventory");
    return unwrap(response);
};

// =====================================================
// CUSTOMER REPORT
// =====================================================

export const fetchCustomerReport = async () => {
    const response = await api.get("/reports/customer");
    return unwrap(response);
};

// =====================================================
// BUSINESS KPI REPORT
// =====================================================

export const fetchBusinessReport = async () => {
    const response = await api.get("/reports/business");
    return unwrap(response);
};

// =====================================================
// EXECUTIVE REPORT
// =====================================================

export const fetchExecutiveReport = async () => {
    const response = await api.get("/reports/executive");
    return unwrap(response);
};

// =====================================================
// FORECAST REPORT
// =====================================================

export const fetchForecastReport = async () => {
    const response = await api.get("/reports/forecast");
    return unwrap(response);
};

// =====================================================
// KPI REPORT
// =====================================================

export const fetchKpiReport = async () => {
    const response = await api.get("/reports/kpi");
    return unwrap(response);
};

// =====================================================
// DASHBOARD REPORT
// =====================================================

export const fetchDashboardReport = async () => {
    const response = await api.get("/reports/dashboard");
    return unwrap(response);
};

// =====================================================
// COPILOT / AI INSIGHT REPORT
// =====================================================

export const fetchCopilotReport = async () => {
    const response = await api.get("/reports/copilot");
    return unwrap(response);
};

// =====================================================
// GENERATE REPORTS
// (triggers the Celery background job that regenerates all
// report files on disk — same job Settings > Background Tasks
// exposes, surfaced here too since it's report-specific)
// =====================================================

export const generateReports = async () => {
    const response = await api.post("/tasks/reports");
    return unwrap(response);
};

// =====================================================
// GENERATED REPORT FILES
// =====================================================

export const fetchReportFiles = async () => {
    const response = await api.get("/reports/files");
    return unwrap(response);
};


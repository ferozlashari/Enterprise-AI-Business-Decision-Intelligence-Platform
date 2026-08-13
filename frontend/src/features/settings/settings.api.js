import api from "../../api/axios";


// =====================================================
// CLEAR REDIS CACHE
// =====================================================

export const clearCache = async () => {

    const response = await api.delete("/cache/clear");

    return response.data;

};


// =====================================================
// BACKGROUND TASKS (CELERY)
// =====================================================

export const triggerSalesPredictionTask = async () => {

    const response = await api.post("/tasks/sales");

    return response.data;

};


export const triggerReportGenerationTask = async () => {

    const response = await api.post("/tasks/reports");

    return response.data;

};


export const triggerRagRebuildTask = async () => {

    const response = await api.post("/tasks/rag");

    return response.data;

};

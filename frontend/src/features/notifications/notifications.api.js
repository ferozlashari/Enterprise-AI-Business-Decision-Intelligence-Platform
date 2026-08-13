import api from "../../api/axios";


// =====================================================
// ACTIVE ALERTS
// =====================================================

export const fetchActiveAlerts = async () => {

    const response = await api.get("/alerts/");

    return response.data;

};


// =====================================================
// GENERATE ALERTS
// (re-runs the business alert detection engine)
// =====================================================

export const generateAlerts = async () => {

    const response = await api.post("/alerts/generate");

    return response.data;

};


// =====================================================
// ACKNOWLEDGE ALERT
// =====================================================

export const acknowledgeAlert = async (alertId) => {

    const response = await api.post(
        `/alerts/${alertId}/acknowledge`
    );

    return response.data;

};


// =====================================================
// RESOLVE ALERT
// =====================================================

export const resolveAlert = async (alertId) => {

    const response = await api.post(
        `/alerts/${alertId}/resolve`
    );

    return response.data;

};


import api from "../../api/axios";


// =====================================================
// SALES / DEMAND FORECAST
// =====================================================

export const fetchSalesForecast = async () => {

    try {

        const response =
            await api.get(
                "/forecast/sales"
            );

        const payload =
            response?.data
            ??
            {};

        console.log(
            "RAW SALES FORECAST API RESPONSE:",
            payload
        );

        /*
         * Backend response:
         *
         * {
         *     success: true,
         *     sales_forecast: {
         *         status: "success",
         *         module: "Demand Forecasting",
         *         available: true,
         *         model: "Facebook Prophet",
         *         records: 100,
         *         forecast: [...]
         *     }
         * }
         *
         * Return the complete payload because
         * Forecast.jsx can read:
         *
         * salesRes?.sales_forecast
         */

        return payload;

    }

    catch (error) {

        console.error(
            "SALES FORECAST API ERROR:",
            error
        );

        throw error;

    }

};


// =====================================================
// INVENTORY FORECAST
// =====================================================

export const fetchInventoryForecast = async () => {

    try {

        const response =
            await api.get(
                "/forecast/inventory"
            );

        const payload =
            response?.data
            ??
            {};

        console.log(
            "RAW INVENTORY FORECAST API RESPONSE:",
            payload
        );

        /*
         * Backend response:
         *
         * {
         *     success: true,
         *     inventory_forecast: {
         *         status: "success",
         *         module: "Inventory Prediction",
         *         available: true,
         *         records: 100,
         *         inventory: [...],
         *         total_inventory: 5000,
         *         total_demand: 3000
         *     }
         * }
         *
         * Return the complete payload so Forecast.jsx
         * can read:
         *
         * inventoryRes?.inventory_forecast
         */

        return payload;

    }

    catch (error) {

        console.error(
            "INVENTORY FORECAST API ERROR:",
            error
        );

        throw error;

    }

};


// =====================================================
// COMPLETE FORECAST INTELLIGENCE
// =====================================================

export const fetchAllForecasts = async () => {

    try {

        const response =
            await api.get(
                "/forecast/all"
            );

        const payload =
            response?.data
            ??
            {};

        console.log(
            "RAW COMPLETE FORECAST RESPONSE:",
            payload
        );

        return payload;

    }

    catch (error) {

        console.error(
            "COMPLETE FORECAST API ERROR:",
            error
        );

        throw error;

    }

};


// =====================================================
// FORECAST HEALTH
// =====================================================

export const fetchForecastHealth = async () => {

    try {

        const response =
            await api.get(
                "/forecast/health"
            );

        return (
            response?.data
            ??
            {}
        );

    }

    catch (error) {

        console.error(
            "FORECAST HEALTH API ERROR:",
            error
        );

        throw error;

    }

};


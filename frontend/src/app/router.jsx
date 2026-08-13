import { createBrowserRouter } from "react-router-dom";

import MainLayout from "../components/layout/MainLayout";
import ProtectedRoute from "../components/common/ProtectedRoute";
import NotFound from "../components/common/NotFound";

import Login from "../features/auth/Login";
import Register from "../features/auth/Register";
import ForgotPassword from "../features/auth/ForgotPassword";
import ResetPassword from "../features/auth/ResetPassword";

import Dashboard from "../features/dashboard/Dashboard";
import Sales from "../features/sales/Sales";
import Inventory from "../features/inventory/Inventory";
import Forecast from "../features/forecast/Forecast";
import Customer from "../features/customer/Customer";
import Decision from "../features/decision/Decision";
import Copilot from "../features/copilot/Copilot";
import Reports from "../features/reports/Reports";
import Monitoring from "../features/monitoring/Monitoring";
import Settings from "../features/settings/Settings";

const router = createBrowserRouter([
    // =====================================================
    // PUBLIC AUTH ROUTES
    // =====================================================

    {
        path: "/login",
        element: <Login />,
    },

    {
        path: "/register",
        element: <Register />,
    },

    {
        path: "/forgot-password",
        element: <ForgotPassword />,
    },

    // Query-string format:
    // /reset-password?token=XXXXXXXX
    {
        path: "/reset-password",
        element: <ResetPassword />,
    },

    // Path-parameter format:
    // /reset-password/XXXXXXXX
    {
        path: "/reset-password/:token",
        element: <ResetPassword />,
    },

    // =====================================================
    // PROTECTED APPLICATION ROUTES
    // =====================================================

    {
        path: "/",
        element: (
            <ProtectedRoute>
                <MainLayout />
            </ProtectedRoute>
        ),

        children: [
            {
                index: true,
                element: <Dashboard />,
            },

            {
                path: "sales",
                element: <Sales />,
            },

            {
                path: "inventory",
                element: <Inventory />,
            },

            {
                path: "forecast",
                element: <Forecast />,
            },

            {
                path: "customer",
                element: <Customer />,
            },

            {
                path: "decision",
                element: <Decision />,
            },

            {
                path: "copilot",
                element: <Copilot />,
            },

            {
                path: "reports",
                element: <Reports />,
            },

            {
                path: "monitoring",
                element: <Monitoring />,
            },

            {
                path: "settings",
                element: <Settings />,
            },
        ],
    },

    // =====================================================
    // 404
    // =====================================================

    {
        path: "*",
        element: <NotFound />,
    },
]);

export default router;


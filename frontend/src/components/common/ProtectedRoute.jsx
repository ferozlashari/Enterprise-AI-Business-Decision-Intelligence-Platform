
import { useContext } from "react";
import { Navigate, useLocation } from "react-router-dom";

import { AuthContext } from "../../context/AuthContext";

export default function ProtectedRoute({ children }) {
    const auth = useContext(AuthContext);
    const location = useLocation();

    // =====================================================
    // AUTH PROVIDER CHECK
    // =====================================================

    if (!auth) {
        return (
            <div className="min-h-screen bg-slate-950 text-red-400 flex items-center justify-center px-4">
                <div className="text-center">
                    <h1 className="text-xl font-semibold mb-2">
                        Authentication Error
                    </h1>

                    <p className="text-slate-400 text-sm">
                        Authentication provider is not available.
                    </p>
                </div>
            </div>
        );
    }

    const {
        isAuthenticated,
        loading,
    } = auth;

    // =====================================================
    // AUTH INITIALIZATION
    // =====================================================

    if (loading) {
        return (
            <div className="min-h-screen bg-slate-950 text-white flex items-center justify-center px-4">
                <div className="text-center">
                    <div className="text-xl font-semibold mb-2">
                        Loading Enterprise AI...
                    </div>

                    <p className="text-slate-400 text-sm">
                        Verifying your authentication session.
                    </p>
                </div>
            </div>
        );
    }

    // =====================================================
    // NOT AUTHENTICATED
    // =====================================================

    if (!isAuthenticated) {
        return (
            <Navigate
                to="/login"
                replace
                state={{
                    from: location.pathname,
                }}
            />
        );
    }

    // =====================================================
    // AUTHENTICATED
    // =====================================================

    return children;
}


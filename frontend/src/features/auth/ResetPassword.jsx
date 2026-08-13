
import { useState } from "react";
import {
    useNavigate,
    useSearchParams,
    useParams,
    Link,
} from "react-router-dom";

import { resetPasswordApi } from "../../api/auth.api";

export default function ResetPassword() {

    const navigate = useNavigate();

    const [searchParams] =
        useSearchParams();

    const { token: routeToken } =
        useParams();

    // =====================================================
    // GET RESET TOKEN
    // Supports:
    // /reset-password?token=ABC
    // /reset-password/ABC
    // =====================================================

    const queryToken =
        searchParams.get("token");

    const token =
        String(
            queryToken ||
            routeToken ||
            ""
        ).trim();

    // =====================================================
    // STATE
    // =====================================================

    const [password, setPassword] =
        useState("");

    const [confirmPassword, setConfirmPassword] =
        useState("");

    const [showPassword, setShowPassword] =
        useState(false);

    const [showConfirmPassword, setShowConfirmPassword] =
        useState(false);

    const [error, setError] =
        useState("");

    const [success, setSuccess] =
        useState("");

    const [loading, setLoading] =
        useState(false);

    // =====================================================
    // ERROR HANDLER
    // =====================================================

    const getErrorMessage = (err) => {

        const detail =
            err?.response?.data?.detail;

        if (Array.isArray(detail)) {

            return detail
                .map(
                    (item) =>
                        item?.msg ||
                        "Invalid input"
                )
                .join(", ");
        }

        if (typeof detail === "string") {

            return detail;
        }

        if (err?.message) {

            return err.message;
        }

        return (
            "Unable to reset your password."
        );
    };

    // =====================================================
    // SUBMIT
    // =====================================================

    const handleSubmit = async (e) => {

        e.preventDefault();

        if (loading) {
            return;
        }

        setError("");
        setSuccess("");

        // =================================================
        // TOKEN VALIDATION
        // =================================================

        if (!token) {

            setError(
                "Invalid or missing password reset token."
            );

            return;
        }

        // =================================================
        // PASSWORD VALIDATION
        // =================================================

        if (!password) {

            setError(
                "Please enter a new password."
            );

            return;
        }

        if (password.length < 6) {

            setError(
                "Password must contain at least 6 characters."
            );

            return;
        }

        // =================================================
        // CONFIRM PASSWORD
        // =================================================

        if (!confirmPassword) {

            setError(
                "Please confirm your new password."
            );

            return;
        }

        if (password !== confirmPassword) {

            setError(
                "Passwords do not match."
            );

            return;
        }

        // =================================================
        // RESET PASSWORD
        // =================================================

        try {

            setLoading(true);

            const response =
                await resetPasswordApi(
                    token,
                    password
                );

            console.log(
                "RESET PASSWORD RESPONSE:",
                response
            );

            // =================================================
            // CLEAR OLD AUTH SESSION
            // =================================================

            localStorage.removeItem(
                "token"
            );

            localStorage.removeItem(
                "user"
            );

            localStorage.removeItem(
                "remember_me"
            );

            // =================================================
            // SUCCESS
            // =================================================

            setPassword("");

            setConfirmPassword("");

            setSuccess(
                response?.message ||
                "Your password has been reset successfully."
            );

            // =================================================
            // REDIRECT TO LOGIN
            // =================================================

            window.setTimeout(() => {

                navigate(
                    "/login",
                    {
                        replace: true,
                    }
                );

            }, 1500);

        }

        catch (err) {

            console.error(
                "RESET PASSWORD ERROR:",
                err
            );

            setError(
                getErrorMessage(err)
            );

        }

        finally {

            setLoading(false);

        }

    };

    // =====================================================
    // INVALID TOKEN PAGE
    // =====================================================

    if (!token) {

        return (

            <div
                className="
                    min-h-screen
                    flex
                    items-center
                    justify-center
                    bg-slate-950
                    px-4
                    py-8
                "
            >

                <div
                    className="
                        w-full
                        max-w-md
                        bg-slate-900
                        border
                        border-slate-800
                        rounded-2xl
                        p-8
                        shadow-2xl
                        text-center
                    "
                >

                    <h1
                        className="
                            text-2xl
                            font-bold
                            text-red-400
                            mb-4
                        "
                    >
                        Invalid Reset Link
                    </h1>

                    <p
                        className="
                            text-gray-400
                            mb-6
                        "
                    >
                        The password reset token is
                        missing or invalid.
                    </p>

                    <Link
                        to="/forgot-password"
                        className="
                            inline-block
                            bg-blue-600
                            hover:bg-blue-700
                            px-5
                            py-3
                            rounded-lg
                            text-white
                            font-semibold
                        "
                    >
                        Request New Reset Link
                    </Link>

                </div>

            </div>
        );
    }

    // =====================================================
    // RESET PASSWORD PAGE
    // =====================================================

    return (

        <div
            className="
                min-h-screen
                flex
                items-center
                justify-center
                bg-slate-950
                px-4
                py-8
            "
        >

            <form
                onSubmit={handleSubmit}
                className="
                    w-full
                    max-w-md
                    bg-slate-900
                    border
                    border-slate-800
                    rounded-2xl
                    p-8
                    shadow-2xl
                "
            >

                {/* =================================================
                    HEADER
                ================================================= */}

                <div
                    className="
                        text-center
                        mb-8
                    "
                >

                    <h1
                        className="
                            text-3xl
                            font-bold
                            text-blue-400
                            mb-2
                        "
                    >
                        Reset Password
                    </h1>

                    <p
                        className="
                            text-gray-400
                            text-sm
                        "
                    >
                        Create a new password for
                        your Enterprise AI account.
                    </p>

                </div>


                {/* =================================================
                    ERROR
                ================================================= */}

                {error && (

                    <div
                        role="alert"
                        className="
                            bg-red-500/20
                            border
                            border-red-500/30
                            text-red-300
                            p-3
                            rounded-lg
                            mb-5
                            text-sm
                        "
                    >
                        {error}
                    </div>

                )}


                {/* =================================================
                    SUCCESS
                ================================================= */}

                {success && (

                    <div
                        role="status"
                        className="
                            bg-green-500/20
                            border
                            border-green-500/30
                            text-green-300
                            p-3
                            rounded-lg
                            mb-5
                            text-sm
                        "
                    >
                        {success}

                        <p className="
                            mt-2
                            text-green-400/80
                            text-xs
                        ">
                            Redirecting you to login...
                        </p>

                    </div>

                )}


                {/* =================================================
                    NEW PASSWORD
                ================================================= */}

                <div className="mb-5">

                    <label
                        htmlFor="new-password"
                        className="
                            block
                            text-sm
                            text-gray-300
                            mb-2
                        "
                    >
                        New Password
                    </label>

                    <div className="relative">

                        <input
                            id="new-password"
                            type={
                                showPassword
                                    ? "text"
                                    : "password"
                            }
                            autoComplete="new-password"
                            placeholder="Enter new password"
                            value={password}
                            onChange={(e) =>
                                setPassword(
                                    e.target.value
                                )
                            }
                            disabled={
                                loading ||
                                Boolean(success)
                            }
                            required
                            minLength={6}
                            className="
                                w-full
                                p-3
                                pr-16
                                rounded-lg
                                bg-slate-800
                                text-white
                                border
                                border-slate-700
                                outline-none
                                focus:border-blue-500
                                focus:ring-1
                                focus:ring-blue-500
                                disabled:opacity-50
                            "
                        />

                        <button
                            type="button"
                            onClick={() =>
                                setShowPassword(
                                    (previous) =>
                                        !previous
                                )
                            }
                            disabled={
                                loading ||
                                Boolean(success)
                            }
                            className="
                                absolute
                                right-3
                                top-1/2
                                -translate-y-1/2
                                text-blue-400
                                text-sm
                                hover:text-blue-300
                                disabled:opacity-50
                            "
                        >
                            {showPassword
                                ? "Hide"
                                : "Show"}
                        </button>

                    </div>

                </div>


                {/* =================================================
                    CONFIRM PASSWORD
                ================================================= */}

                <div className="mb-6">

                    <label
                        htmlFor="confirm-password"
                        className="
                            block
                            text-sm
                            text-gray-300
                            mb-2
                        "
                    >
                        Confirm New Password
                    </label>

                    <div className="relative">

                        <input
                            id="confirm-password"
                            type={
                                showConfirmPassword
                                    ? "text"
                                    : "password"
                            }
                            autoComplete="new-password"
                            placeholder="Confirm new password"
                            value={confirmPassword}
                            onChange={(e) =>
                                setConfirmPassword(
                                    e.target.value
                                )
                            }
                            disabled={
                                loading ||
                                Boolean(success)
                            }
                            required
                            minLength={6}
                            className="
                                w-full
                                p-3
                                pr-16
                                rounded-lg
                                bg-slate-800
                                text-white
                                border
                                border-slate-700
                                outline-none
                                focus:border-blue-500
                                focus:ring-1
                                focus:ring-blue-500
                                disabled:opacity-50
                            "
                        />

                        <button
                            type="button"
                            onClick={() =>
                                setShowConfirmPassword(
                                    (previous) =>
                                        !previous
                                )
                            }
                            disabled={
                                loading ||
                                Boolean(success)
                            }
                            className="
                                absolute
                                right-3
                                top-1/2
                                -translate-y-1/2
                                text-blue-400
                                text-sm
                                hover:text-blue-300
                                disabled:opacity-50
                            "
                        >
                            {showConfirmPassword
                                ? "Hide"
                                : "Show"}
                        </button>

                    </div>

                </div>


                {/* =================================================
                    RESET BUTTON
                ================================================= */}

                <button
                    type="submit"
                    disabled={
                        loading ||
                        Boolean(success)
                    }
                    className="
                        w-full
                        bg-blue-600
                        hover:bg-blue-700
                        disabled:bg-blue-800
                        disabled:cursor-not-allowed
                        p-3
                        rounded-lg
                        text-white
                        font-semibold
                        transition
                    "
                >
                    {loading
                        ? "Resetting..."
                        : success
                        ? "Password Reset Successfully"
                        : "Reset Password"}
                </button>


                {/* =================================================
                    LOGIN
                ================================================= */}

                <div
                    className="
                        text-center
                        mt-6
                        text-sm
                        text-gray-400
                    "
                >

                    <span>
                        Remember your password?
                    </span>

                    <Link
                        to="/login"
                        className="
                            text-blue-400
                            ml-2
                            hover:text-blue-300
                            hover:underline
                        "
                    >
                        Login
                    </Link>

                </div>

            </form>

        </div>
    );
}


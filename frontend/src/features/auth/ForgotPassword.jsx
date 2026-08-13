
import { useState } from "react";
import { Link } from "react-router-dom";

import { forgotPasswordApi } from "../../api/auth.api";

export default function ForgotPassword() {

    const [email, setEmail] =
        useState("");

    const [loading, setLoading] =
        useState(false);

    const [error, setError] =
        useState("");

    const [success, setSuccess] =
        useState("");

    const [resetUrl, setResetUrl] =
        useState("");


    // =====================================================
    // SUBMIT FORGOT PASSWORD
    // =====================================================

    const handleSubmit = async (e) => {

        e.preventDefault();

        setError("");
        setSuccess("");
        setResetUrl("");


        // =================================================
        // CLEAN EMAIL
        // =================================================

        const cleanEmail =
            String(email || "")
                .trim()
                .toLowerCase();


        // =================================================
        // REQUIRED
        // =================================================

        if (!cleanEmail) {

            setError(
                "Please enter your email address."
            );

            return;
        }


        // =================================================
        // BLOCK MARKDOWN EMAIL
        // =================================================

        if (
            cleanEmail.includes("[") ||
            cleanEmail.includes("]") ||
            cleanEmail.includes("mailto:")
        ) {

            setError(
                "Please enter only the email address. Example: lashariferoz8@gmail.com"
            );

            return;
        }


        // =================================================
        // EMAIL FORMAT
        // =================================================

        const emailPattern =
            /^[^\s@]+@[^\s@]+\.[^\s@]+$/;


        if (!emailPattern.test(cleanEmail)) {

            setError(
                "Please enter a valid email address."
            );

            return;
        }


        // =================================================
        // API REQUEST
        // =================================================

        try {

            setLoading(true);


            console.log(
                "FORGOT PASSWORD EMAIL SENT:",
                cleanEmail
            );


            const response =
                await forgotPasswordApi(
                    cleanEmail
                );


            console.log(
                "FORGOT PASSWORD RESPONSE:",
                response
            );


            // =================================================
            // SUCCESS MESSAGE
            // =================================================

            setSuccess(
                response?.message ||
                "If an account exists with this email, password reset instructions have been sent."
            );


            // =================================================
            // DEVELOPMENT RESET URL
            // =================================================

            if (response?.reset_url) {

                console.log(
                    "RESET URL:",
                    response.reset_url
                );


                setResetUrl(
                    response.reset_url
                );

            }


            // =================================================
            // CLEAR EMAIL
            // =================================================

            setEmail("");


        }

        catch (err) {

            console.error(
                "FORGOT PASSWORD ERROR:",
                err
            );


            const detail =
                err?.response?.data?.detail;


            // =================================================
            // FASTAPI VALIDATION ERROR
            // =================================================

            if (Array.isArray(detail)) {

                setError(
                    detail
                        .map(
                            (item) =>
                                item?.msg ||
                                "Invalid input"
                        )
                        .join(", ")
                );

            }


            // =================================================
            // FASTAPI ERROR
            // =================================================

            else if (
                typeof detail === "string"
            ) {

                setError(detail);

            }


            // =================================================
            // AXIOS ERROR
            // =================================================

            else if (
                err?.message
            ) {

                setError(
                    err.message
                );

            }


            // =================================================
            // FALLBACK
            // =================================================

            else {

                setError(
                    "Unable to process your password reset request."
                );

            }

        }

        finally {

            setLoading(false);

        }

    };


    // =====================================================
    // UI
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

                {/* HEADER */}

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
                        Forgot Password
                    </h1>


                    <p
                        className="
                            text-gray-400
                            text-sm
                        "
                    >
                        Enter your registered email address
                    </p>

                </div>


                {/* ERROR */}

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


                {/* SUCCESS */}

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
                    </div>

                )}


                {/* DEVELOPMENT RESET URL */}

                {resetUrl && (

                    <div
                        className="
                            bg-blue-500/10
                            border
                            border-blue-500/30
                            rounded-lg
                            p-4
                            mb-5
                        "
                    >

                        <p
                            className="
                                text-blue-300
                                text-sm
                                font-semibold
                                mb-2
                            "
                        >
                            Development Reset Link
                        </p>


                        <p
                            className="
                                text-gray-400
                                text-xs
                                mb-3
                            "
                        >
                            Password email delivery is not
                            configured yet. Use this development
                            link to reset the password.
                        </p>


                        <a
                            href={resetUrl}
                            className="
                                block
                                w-full
                                text-center
                                bg-blue-600
                                hover:bg-blue-700
                                text-white
                                px-4
                                py-3
                                rounded-lg
                                font-semibold
                                transition
                            "
                        >
                            Open Password Reset Page
                        </a>


                        <p
                            className="
                                text-gray-500
                                text-xs
                                break-all
                                mt-3
                            "
                        >
                            {resetUrl}
                        </p>

                    </div>

                )}


                {/* EMAIL */}

                <div className="mb-6">

                    <label
                        htmlFor="forgot-email"
                        className="
                            block
                            text-sm
                            text-gray-300
                            mb-2
                        "
                    >
                        Email Address
                    </label>


                    <input
                        id="forgot-email"
                        name="email"
                        type="email"
                        autoComplete="email"
                        placeholder="Enter your registered email"
                        value={email}
                        onChange={(e) =>
                            setEmail(
                                e.target.value
                            )
                        }
                        disabled={loading}
                        required
                        className="
                            w-full
                            bg-slate-800
                            p-3
                            rounded-lg
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

                </div>


                {/* SUBMIT */}

                <button
                    type="submit"
                    disabled={loading}
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
                        ? "Processing..."
                        : "Send Reset Instructions"}

                </button>


                {/* LOGIN */}

                <div
                    className="
                        text-center
                        text-gray-400
                        mt-6
                        text-sm
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
                        Back to Login
                    </Link>

                </div>

            </form>

        </div>

    );
}


import { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";

import { registerApi } from "../../api/auth.api";

export default function Register() {
const navigate = useNavigate();


const [username, setUsername] = useState("");
const [email, setEmail] = useState("");
const [password, setPassword] = useState("");
const [confirmPassword, setConfirmPassword] = useState("");

const [role, setRole] = useState("Analyst");

const [showPassword, setShowPassword] = useState(false);
const [showConfirmPassword, setShowConfirmPassword] = useState(false);

const [error, setError] = useState("");
const [success, setSuccess] = useState("");
const [loading, setLoading] = useState(false);

const [redirecting, setRedirecting] = useState(false);

/*
=========================================================
CLEANUP REDIRECT TIMER
=========================================================
*/

useEffect(() => {
    return () => {
        // Component cleanup intentionally kept here
        // so future timers can be safely added.
    };
}, []);

/*
=========================================================
FASTAPI ERROR HANDLER
=========================================================
*/

const getErrorMessage = (err) => {
    const detail = err?.response?.data?.detail;

    // FastAPI validation error
    if (Array.isArray(detail)) {
        return detail
            .map((item) => {
                if (typeof item === "string") {
                    return item;
                }

                return item?.msg || "Invalid input";
            })
            .join(", ");
    }

    // Normal FastAPI HTTPException
    if (typeof detail === "string") {
        return detail;
    }

    // Axios error message
    if (err?.message) {
        return err.message;
    }

    return "Registration failed. Please try again.";
};

/*
=========================================================
FORM SUBMIT
=========================================================
*/

const handleSubmit = async (e) => {
    e.preventDefault();

    if (loading) {
        return;
    }

    setError("");
    setSuccess("");

    /*
    -----------------------------------------------------
    CLEAN INPUT
    -----------------------------------------------------
    */

    const cleanUsername = username.trim();
    const cleanEmail = email.trim().toLowerCase();

    /*
    -----------------------------------------------------
    USERNAME VALIDATION
    -----------------------------------------------------
    */

    if (!cleanUsername) {
        setError("Please enter a username.");
        return;
    }

    if (cleanUsername.length < 3) {
        setError(
            "Username must contain at least 3 characters."
        );
        return;
    }

    /*
    -----------------------------------------------------
    EMAIL VALIDATION
    -----------------------------------------------------
    */

    if (!cleanEmail) {
        setError("Please enter your email address.");
        return;
    }

    const emailPattern =
        /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!emailPattern.test(cleanEmail)) {
        setError(
            "Please enter a valid email address."
        );
        return;
    }

    /*
    -----------------------------------------------------
    PASSWORD VALIDATION
    -----------------------------------------------------
    */

    if (!password) {
        setError("Please enter a password.");
        return;
    }

    if (password.length < 6) {
        setError(
            "Password must contain at least 6 characters."
        );
        return;
    }

    /*
    -----------------------------------------------------
    CONFIRM PASSWORD
    -----------------------------------------------------
    */

    if (!confirmPassword) {
        setError(
            "Please confirm your password."
        );
        return;
    }

    if (password !== confirmPassword) {
        setError(
            "Passwords do not match."
        );
        return;
    }

    /*
    -----------------------------------------------------
    ROLE VALIDATION
    -----------------------------------------------------

    Executive/Admin accounts should normally be created
    by an administrator rather than self-registered.
    -----------------------------------------------------
    */

    const allowedRegistrationRoles = [
        "Analyst",
        "Manager"
    ];

    if (!allowedRegistrationRoles.includes(role)) {
        setError(
            "Invalid registration role."
        );
        return;
    }

    /*
    -----------------------------------------------------
    REGISTER
    -----------------------------------------------------
    */

    try {
        setLoading(true);

        const payload = {
            username: cleanUsername,
            email: cleanEmail,
            password: password,
            role: role
        };

        console.log(
            "REGISTER REQUEST:",
            payload
        );

        const response = await registerApi(payload);

        console.log(
            "REGISTER RESPONSE:",
            response
        );

        /*
        -------------------------------------------------
        SUCCESS
        -------------------------------------------------
        */

        setSuccess(
            "Account created successfully. Redirecting to login..."
        );

        setUsername("");
        setEmail("");
        setPassword("");
        setConfirmPassword("");
        setRole("Analyst");

        setRedirecting(true);

        /*
        -------------------------------------------------
        REDIRECT
        -------------------------------------------------
        */

        window.setTimeout(() => {
            navigate("/login", {
                replace: true
            });
        }, 1200);

    } catch (err) {
        console.error(
            "REGISTER ERROR:",
            err
        );

        setError(
            getErrorMessage(err)
        );

    } finally {
        setLoading(false);
    }
};

/*
=========================================================
RENDER
=========================================================
*/

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
            {/* =========================================
                HEADER
            ========================================== */}

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
                    Create Account
                </h1>

                <p
                    className="
                        text-gray-400
                        text-sm
                    "
                >
                    Enterprise AI Business Intelligence
                </p>
            </div>

            {/* =========================================
                ERROR
            ========================================== */}

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

            {/* =========================================
                SUCCESS
            ========================================== */}

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

            {/* =========================================
                USERNAME
            ========================================== */}

            <div className="mb-4">
                <label
                    htmlFor="register-username"
                    className="
                        block
                        text-sm
                        text-gray-300
                        mb-2
                    "
                >
                    Username
                </label>

                <input
                    id="register-username"
                    type="text"
                    autoComplete="username"
                    placeholder="Enter your username"
                    value={username}
                    onChange={(e) =>
                        setUsername(e.target.value)
                    }
                    disabled={loading || redirecting}
                    required
                    minLength={3}
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

            {/* =========================================
                EMAIL
            ========================================== */}

            <div className="mb-4">
                <label
                    htmlFor="register-email"
                    className="
                        block
                        text-sm
                        text-gray-300
                        mb-2
                    "
                >
                    Email
                </label>

                <input
                    id="register-email"
                    type="email"
                    autoComplete="email"
                    placeholder="Enter your email"
                    value={email}
                    onChange={(e) =>
                        setEmail(e.target.value)
                    }
                    disabled={loading || redirecting}
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

            {/* =========================================
                PASSWORD
            ========================================== */}

            <div className="mb-4">
                <label
                    htmlFor="register-password"
                    className="
                        block
                        text-sm
                        text-gray-300
                        mb-2
                    "
                >
                    Password
                </label>

                <div className="relative">
                    <input
                        id="register-password"
                        type={
                            showPassword
                                ? "text"
                                : "password"
                        }
                        autoComplete="new-password"
                        placeholder="Enter your password"
                        value={password}
                        onChange={(e) =>
                            setPassword(e.target.value)
                        }
                        disabled={loading || redirecting}
                        required
                        minLength={6}
                        className="
                            w-full
                            bg-slate-800
                            p-3
                            pr-16
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

                    <button
                        type="button"
                        onClick={() =>
                            setShowPassword(
                                (previous) =>
                                    !previous
                            )
                        }
                        disabled={loading || redirecting}
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

            {/* =========================================
                CONFIRM PASSWORD
            ========================================== */}

            <div className="mb-4">
                <label
                    htmlFor="register-confirm-password"
                    className="
                        block
                        text-sm
                        text-gray-300
                        mb-2
                    "
                >
                    Confirm Password
                </label>

                <div className="relative">
                    <input
                        id="register-confirm-password"
                        type={
                            showConfirmPassword
                                ? "text"
                                : "password"
                        }
                        autoComplete="new-password"
                        placeholder="Confirm your password"
                        value={confirmPassword}
                        onChange={(e) =>
                            setConfirmPassword(
                                e.target.value
                            )
                        }
                        disabled={loading || redirecting}
                        required
                        minLength={6}
                        className="
                            w-full
                            bg-slate-800
                            p-3
                            pr-16
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

                    <button
                        type="button"
                        onClick={() =>
                            setShowConfirmPassword(
                                (previous) =>
                                    !previous
                            )
                        }
                        disabled={loading || redirecting}
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

            {/* =========================================
                ROLE
            ========================================== */}

            <div className="mb-6">
                <label
                    htmlFor="register-role"
                    className="
                        block
                        text-sm
                        text-gray-300
                        mb-2
                    "
                >
                    Account Role
                </label>

                <select
                    id="register-role"
                    value={role}
                    onChange={(e) =>
                        setRole(e.target.value)
                    }
                    disabled={loading || redirecting}
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
                >
                    <option value="Analyst">
                        Analyst
                    </option>

                    <option value="Manager">
                        Manager
                    </option>
                </select>

                <p
                    className="
                        text-xs
                        text-slate-500
                        mt-2
                    "
                >
                    Executive and Admin roles are managed by an administrator.
                </p>
            </div>

            {/* =========================================
                REGISTER BUTTON
            ========================================== */}

            <button
                type="submit"
                disabled={loading || redirecting}
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
                {redirecting
                    ? "Redirecting..."
                    : loading
                    ? "Creating..."
                    : "Create Account"}
            </button>

            {/* =========================================
                LOGIN LINK
            ========================================== */}

            <p
                className="
                    text-center
                    text-gray-400
                    mt-6
                    text-sm
                "
            >
                Already have an account?

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
            </p>
        </form>
    </div>
);


}

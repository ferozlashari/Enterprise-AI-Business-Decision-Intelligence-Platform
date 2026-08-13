
import {
    useState,
    useContext,
} from "react";

import {
    useNavigate,
    Link,
} from "react-router-dom";

import {
    AuthContext,
} from "../../context/AuthContext";

import {
    loginApi,
} from "../../api/auth.api";


export default function Login() {

    const navigate = useNavigate();

    const auth = useContext(
        AuthContext
    );


    // =====================================================
    // STATE
    // (declared unconditionally, before any early return, so
    // hook order never changes between renders)
    // =====================================================

    const [username, setUsername] =
        useState("");

    const [password, setPassword] =
        useState("");

    const [showPassword, setShowPassword] =
        useState(false);

    const [rememberMe, setRememberMe] =
        useState(false);

    const [error, setError] =
        useState("");

    const [loading, setLoading] =
        useState(false);


    // =====================================================
    // AUTH CONTEXT CHECK
    // =====================================================

    if (!auth) {

        return (
            <div className="
                min-h-screen
                flex
                items-center
                justify-center
                bg-slate-950
                text-red-400
                px-4
            ">
                Authentication provider is not available.
            </div>
        );

    }


    const {
        login,
    } = auth;


    // =====================================================
    // ERROR HANDLER
    // =====================================================

    const getErrorMessage = (err) => {

        const detail =
            err?.response?.data?.detail;


        // FastAPI validation errors

        if (Array.isArray(detail)) {

            return detail
                .map((item) => {

                    if (
                        typeof item === "string"
                    ) {
                        return item;
                    }

                    return (
                        item?.msg ||
                        "Invalid input"
                    );

                })
                .join(", ");

        }


        // FastAPI HTTPException

        if (
            typeof detail === "string"
        ) {

            return detail;

        }


        // Axios / JavaScript error

        if (
            err?.message
        ) {

            return err.message;

        }


        return (
            "Invalid username or password."
        );

    };


    // =====================================================
    // LOGIN SUBMIT
    // =====================================================

    const handleSubmit = async (e) => {

        e.preventDefault();


        if (loading) {
            return;
        }


        setError("");


        // -------------------------------------------------
        // USERNAME VALIDATION
        // -------------------------------------------------

        const cleanUsername =
            username.trim();


        if (!cleanUsername) {

            setError(
                "Please enter your username."
            );

            return;

        }


        // -------------------------------------------------
        // PASSWORD VALIDATION
        // -------------------------------------------------

        if (!password) {

            setError(
                "Please enter your password."
            );

            return;

        }


        try {

            setLoading(true);


            // -------------------------------------------------
            // BACKEND LOGIN
            // -------------------------------------------------

            const data =
                await loginApi(
                    cleanUsername,
                    password
                );


            console.log(
                "LOGIN RESPONSE:",
                data
            );


            // -------------------------------------------------
            // VALIDATE TOKEN
            // -------------------------------------------------

            if (
                !data?.access_token
            ) {

                throw new Error(
                    "Login succeeded but no access token was returned."
                );

            }


            // -------------------------------------------------
            // USER DATA
            // -------------------------------------------------

            const loggedInUser =
                data?.user || null;


            // -------------------------------------------------
            // UPDATE AUTH CONTEXT
            // -------------------------------------------------

            login(
                data.access_token,
                loggedInUser
            );


            // -------------------------------------------------
            // REMEMBER ME
            // -------------------------------------------------

            if (rememberMe) {

                localStorage.setItem(
                    "remember_me",
                    "true"
                );

            } else {

                localStorage.removeItem(
                    "remember_me"
                );

            }


            // -------------------------------------------------
            // REDIRECT
            // -------------------------------------------------

            navigate(
                "/",
                {
                    replace: true,
                }
            );


        } catch (err) {

            console.error(
                "LOGIN ERROR:",
                err
            );


            setError(
                getErrorMessage(err)
            );


        } finally {

            setLoading(false);

        }

    };


    // =====================================================
    // UI
    // =====================================================

    return (

        <div className="
            min-h-screen
            flex
            items-center
            justify-center
            bg-slate-950
            px-4
            py-8
        ">

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
                ================================================== */}

                <div className="
                    text-center
                    mb-8
                ">

                    <h1 className="
                        text-3xl
                        font-bold
                        text-blue-400
                        mb-2
                    ">
                        Enterprise AI
                    </h1>

                    <p className="
                        text-gray-400
                        text-sm
                    ">
                        Business Intelligence Platform
                    </p>

                </div>


                {/* =================================================
                    ERROR
                ================================================== */}

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
                    USERNAME
                ================================================== */}

                <div className="mb-4">

                    <label
                        htmlFor="login-username"
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
                        id="login-username"
                        type="text"
                        autoComplete="username"
                        placeholder="Enter your username"
                        value={username}
                        onChange={(e) =>
                            setUsername(
                                e.target.value
                            )
                        }
                        disabled={loading}
                        required
                        className="
                            w-full
                            p-3
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

                </div>


                {/* =================================================
                    PASSWORD
                ================================================== */}

                <div className="mb-4">

                    <label
                        htmlFor="login-password"
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
                            id="login-password"
                            type={
                                showPassword
                                    ? "text"
                                    : "password"
                            }
                            autoComplete="current-password"
                            placeholder="Enter your password"
                            value={password}
                            onChange={(e) =>
                                setPassword(
                                    e.target.value
                                )
                            }
                            disabled={loading}
                            required
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
                            disabled={loading}
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
                    REMEMBER ME + FORGOT PASSWORD
                ================================================== */}

                <div className="
                    flex
                    flex-col
                    sm:flex-row
                    sm:items-center
                    sm:justify-between
                    gap-3
                    mb-6
                ">

                    <label
                        htmlFor="remember-me"
                        className="
                            flex
                            items-center
                            gap-2
                            text-gray-400
                            text-sm
                            cursor-pointer
                            select-none
                        "
                    >

                        <input
                            id="remember-me"
                            type="checkbox"
                            checked={rememberMe}
                            onChange={(e) =>
                                setRememberMe(
                                    e.target.checked
                                )
                            }
                            disabled={loading}
                            className="
                                w-4
                                h-4
                                cursor-pointer
                            "
                        />

                        <span>
                            Remember me
                        </span>

                    </label>


                    <Link
                        to="/forgot-password"
                        className="
                            text-blue-400
                            text-sm
                            whitespace-nowrap
                            hover:text-blue-300
                            hover:underline
                        "
                    >
                        Forgot Password?
                    </Link>

                </div>


                {/* =================================================
                    LOGIN BUTTON
                ================================================== */}

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
                        ? "Signing in..."
                        : "Login"}
                </button>


                {/* =================================================
                    REGISTER
                ================================================== */}

                <div className="
                    text-center
                    text-gray-400
                    mt-6
                    text-sm
                ">

                    <span>
                        Don't have an account?
                    </span>


                    <Link
                        to="/register"
                        className="
                            text-blue-400
                            ml-2
                            hover:text-blue-300
                            hover:underline
                        "
                    >
                        Register
                    </Link>

                </div>

            </form>

        </div>

    );

}


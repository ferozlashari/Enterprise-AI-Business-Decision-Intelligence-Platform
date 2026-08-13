
import axios from "axios";

// =====================================================
// API CLIENT
// =====================================================

const api = axios.create({

    baseURL:
        import.meta.env.VITE_API_URL ||
        "http://127.0.0.1:8000",

    timeout: 120000,

    headers: {
        "Content-Type": "application/json",
    },

});


// =====================================================
// JWT TOKEN ATTACHMENT
// =====================================================

api.interceptors.request.use(

    (config) => {

        const token =
            localStorage.getItem("token");


        if (token) {

            config.headers =
                config.headers || {};


            config.headers.Authorization =
                `Bearer ${token}`;

        }


        return config;

    },


    (error) => {

        return Promise.reject(
            error
        );

    }

);


// =====================================================
// RESPONSE HANDLING
// =====================================================

api.interceptors.response.use(

    (response) => {

        return response;

    },


    async (error) => {

        // =================================================
        // NO RESPONSE
        // =================================================

        if (!error.response) {

            error.message =
                "Server is not reachable. Please make sure the backend is running.";

            return Promise.reject(
                error
            );

        }


        const status =
            error.response.status;


        const detail =
            error.response.data?.detail;


        const message =
            error.response.data?.message;


        // =================================================
        // FASTAPI VALIDATION ERROR
        // =================================================

        if (Array.isArray(detail)) {

            error.message =
                detail
                    .map((item) => {

                        if (
                            typeof item ===
                            "string"
                        ) {

                            return item;

                        }


                        const location =
                            Array.isArray(
                                item?.loc
                            )
                                ? item.loc.join(".")
                                : "";


                        const itemMessage =
                            item?.msg ||
                            item?.message ||
                            "Invalid input";


                        return location
                            ? `${location}: ${itemMessage}`
                            : itemMessage;

                    })
                    .join("\n");

        }


        // =================================================
        // FASTAPI HTTP EXCEPTION
        // =================================================

        else if (
            typeof detail === "string"
        ) {

            error.message =
                detail;

        }


        // =================================================
        // GENERIC BACKEND MESSAGE
        // =================================================

        else if (
            typeof message === "string"
        ) {

            error.message =
                message;

        }


        // =================================================
        // UNAUTHORIZED
        // =================================================

        if (status === 401) {

            const requestUrl =
                error.config?.url || "";


            const isLoginRequest =
                requestUrl.includes(
                    "/auth/login"
                );


            /*
             * Do not redirect when login itself
             * returns 401.
             */

            if (!isLoginRequest) {

                localStorage.removeItem(
                    "token"
                );

                localStorage.removeItem(
                    "user"
                );

                localStorage.removeItem(
                    "remember_me"
                );


                if (
                    window.location.pathname !==
                    "/login"
                ) {

                    window.location.href =
                        "/login";

                }

            }

        }


        // =================================================
        // FORBIDDEN
        // =================================================

        if (status === 403) {

            if (
                typeof detail !== "string"
            ) {

                error.message =
                    "You do not have permission to perform this action.";

            }

        }


        // =================================================
        // NOT FOUND
        // =================================================

        if (status === 404) {

            if (
                typeof detail !== "string"
            ) {

                error.message =
                    "Requested resource was not found.";

            }

        }


        // =================================================
        // SERVER ERROR
        // =================================================

        if (status >= 500) {

            if (
                typeof detail !== "string" &&
                typeof message !== "string"
            ) {

                error.message =
                    "The server encountered an error. Please try again.";

            }

        }


        return Promise.reject(
            error
        );

    }

);


// =====================================================
// EXPORT
// =====================================================

export default api;


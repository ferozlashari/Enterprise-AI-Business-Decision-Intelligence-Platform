
import {
    createContext,
    useEffect,
    useState,
} from "react";

import { profileApi } from "../api/auth.api";

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {

    // =====================================================
    // STATE
    // =====================================================

    const [user, setUser] = useState(null);

    const [loading, setLoading] =
        useState(true);


    // =====================================================
    // RESTORE AUTHENTICATION SESSION
    // =====================================================

    useEffect(() => {

        let mounted = true;


        const restoreSession = async () => {

            const token =
                localStorage.getItem("token");


            // -------------------------------------------------
            // NO TOKEN
            // -------------------------------------------------

            if (!token) {

                if (mounted) {

                    setUser(null);
                    setLoading(false);

                }

                return;
            }


            // -------------------------------------------------
            // VERIFY TOKEN WITH BACKEND
            // -------------------------------------------------

            try {

                const response =
                    await profileApi();


                console.log(
                    "AUTH ME RESPONSE:",
                    response
                );


                /*
                 * Backend may return either:
                 *
                 * {
                 *     user: {...}
                 * }
                 *
                 * or:
                 *
                 * {...user}
                 */

                const currentUser =
                    response?.user ||
                    response;


                // -------------------------------------------------
                // VALIDATE USER RESPONSE
                // -------------------------------------------------

                if (
                    !currentUser ||
                    typeof currentUser !== "object" ||
                    !currentUser.username
                ) {

                    throw new Error(
                        "Invalid authentication response."
                    );

                }


                // -------------------------------------------------
                // UPDATE STATE
                // -------------------------------------------------

                if (mounted) {

                    setUser(
                        currentUser
                    );

                }


                // -------------------------------------------------
                // KEEP LOCAL STORAGE IN SYNC
                // -------------------------------------------------

                localStorage.setItem(
                    "user",
                    JSON.stringify(
                        currentUser
                    )
                );


            } catch (error) {

                console.error(
                    "SESSION RESTORE ERROR:",
                    error
                );


                // -------------------------------------------------
                // INVALID / EXPIRED TOKEN
                // -------------------------------------------------

                localStorage.removeItem(
                    "token"
                );

                localStorage.removeItem(
                    "user"
                );


                if (mounted) {

                    setUser(null);

                }


            } finally {

                if (mounted) {

                    setLoading(false);

                }

            }

        };


        restoreSession();


        // -------------------------------------------------
        // CLEANUP
        // -------------------------------------------------

        return () => {

            mounted = false;

        };

    }, []);


    // =====================================================
    // LOGIN
    // =====================================================

    const login = (
        token,
        loggedInUser
    ) => {

        if (!token) {

            throw new Error(
                "Access token is missing."
            );

        }


        // -------------------------------------------------
        // SAVE TOKEN
        // -------------------------------------------------

        localStorage.setItem(
            "token",
            token
        );


        // -------------------------------------------------
        // SAVE USER
        // -------------------------------------------------

        if (loggedInUser) {

            localStorage.setItem(
                "user",
                JSON.stringify(
                    loggedInUser
                )
            );

            setUser(
                loggedInUser
            );

        } else {

            /*
             * Token exists but user object
             * was not supplied.
             *
             * Keep user null until /auth/me
             * verifies the session.
             */

            setUser(null);

        }

    };


    // =====================================================
    // LOGOUT
    // =====================================================

    const logout = () => {

        localStorage.removeItem(
            "token"
        );

        localStorage.removeItem(
            "user"
        );

        localStorage.removeItem(
            "remember_me"
        );


        setUser(null);

    };


    // =====================================================
    // AUTHENTICATION STATUS
    // =====================================================

    const isAuthenticated =
        Boolean(
            user &&
            user.username
        );


    // =====================================================
    // CONTEXT
    // =====================================================

    return (

        <AuthContext.Provider
            value={{
                user,
                login,
                logout,
                loading,
                isAuthenticated,
            }}
        >

            {children}

        </AuthContext.Provider>

    );

}


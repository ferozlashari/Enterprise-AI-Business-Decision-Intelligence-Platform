
import api from "./axios";

// =====================================================
// LOGIN
// =====================================================

export const loginApi = async (
    username,
    password
) => {

    const response =
        await api.post(
            "/auth/login",
            {
                username:
                    String(username || "").trim(),

                password,
            }
        );


    return response.data;

};


// =====================================================
// PROFILE / CURRENT USER
// =====================================================

export const profileApi = async () => {

    const response =
        await api.get(
            "/auth/me"
        );


    return response.data;

};


// =====================================================
// REGISTER
// =====================================================

export const registerApi = async (
    data
) => {

    const response =
        await api.post(
            "/auth/register",
            data
        );


    return response.data;

};


// =====================================================
// FORGOT PASSWORD
// =====================================================

export const forgotPasswordApi = async (
    email
) => {

    const cleanEmail =
        String(email || "")
            .trim()
            .toLowerCase();


    const response =
        await api.post(
            "/auth/forgot-password",
            {
                email:
                    cleanEmail,
            }
        );


    return response.data;

};


// =====================================================
// RESET PASSWORD
// =====================================================

export const resetPasswordApi = async (
    token,
    password
) => {

    const cleanToken =
        String(token || "")
            .trim();


    const response =
        await api.post(
            "/auth/reset-password",
            {
                token:
                    cleanToken,

                password,
            }
        );


    return response.data;

};


// =====================================================
// LOGOUT
// =====================================================

export const logoutApi = () => {

    localStorage.removeItem(
        "token"
    );


    localStorage.removeItem(
        "user"
    );


    localStorage.removeItem(
        "remember_me"
    );


    return true;

};


// =====================================================
// CHANGE PASSWORD
// =====================================================

export const changePasswordApi = async (
    currentPassword,
    newPassword
) => {

    const response =
        await api.post(
            "/auth/change-password",
            {
                current_password: currentPassword,
                new_password: newPassword,
            }
        );


    return response.data;

};


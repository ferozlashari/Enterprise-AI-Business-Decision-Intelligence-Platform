import { useState } from "react";

import {
    KeyRound,
    Loader2,
    CheckCircle2,
    Eye,
    EyeOff,
} from "lucide-react";

import { changePasswordApi } from "../../../api/auth.api";


export default function ChangePasswordCard() {

    const [currentPassword, setCurrentPassword] = useState("");

    const [newPassword, setNewPassword] = useState("");

    const [confirmPassword, setConfirmPassword] = useState("");

    const [showPasswords, setShowPasswords] = useState(false);

    const [submitting, setSubmitting] = useState(false);

    const [message, setMessage] = useState(null);

    const [error, setError] = useState(null);


    const resetForm = () => {

        setCurrentPassword("");
        setNewPassword("");
        setConfirmPassword("");

    };


    const handleSubmit = async (event) => {

        event.preventDefault();

        setError(null);
        setMessage(null);

        if (!currentPassword || !newPassword || !confirmPassword) {

            setError("Fill in all three fields.");
            return;

        }

        if (newPassword.length < 6) {

            setError("New password must be at least 6 characters.");
            return;

        }

        if (newPassword !== confirmPassword) {

            setError("New password and confirmation don't match.");
            return;

        }

        try {

            setSubmitting(true);

            const result = await changePasswordApi(
                currentPassword,
                newPassword
            );

            setMessage(
                result?.message || "Password changed successfully."
            );

            resetForm();

        } catch (err) {

            setError(
                err?.response?.data?.detail ||
                err?.message ||
                "Unable to change password."
            );

        } finally {

            setSubmitting(false);

        }

    };


    const inputType = showPasswords ? "text" : "password";


    return (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">

            <div className="flex items-center gap-2 mb-2">
                <KeyRound size={18} className="text-slate-400" />
                <h2 className="text-white font-bold text-xl">
                    Change Password
                </h2>
            </div>

            <p className="text-slate-400 text-sm mb-4">
                You'll need your current password to set a new one.
            </p>

            <form onSubmit={handleSubmit} className="space-y-3 max-w-sm">

                <label className="flex flex-col gap-1 text-sm text-slate-400">
                    Current password
                    <input
                        type={inputType}
                        value={currentPassword}
                        onChange={(e) => setCurrentPassword(e.target.value)}
                        autoComplete="current-password"
                        className="
                            bg-slate-800
                            border
                            border-slate-700
                            rounded-lg
                            px-3
                            py-2
                            text-white
                            focus:outline-none
                            focus:border-blue-500
                        "
                    />
                </label>

                <label className="flex flex-col gap-1 text-sm text-slate-400">
                    New password
                    <input
                        type={inputType}
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                        autoComplete="new-password"
                        className="
                            bg-slate-800
                            border
                            border-slate-700
                            rounded-lg
                            px-3
                            py-2
                            text-white
                            focus:outline-none
                            focus:border-blue-500
                        "
                    />
                </label>

                <label className="flex flex-col gap-1 text-sm text-slate-400">
                    Confirm new password
                    <input
                        type={inputType}
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        autoComplete="new-password"
                        className="
                            bg-slate-800
                            border
                            border-slate-700
                            rounded-lg
                            px-3
                            py-2
                            text-white
                            focus:outline-none
                            focus:border-blue-500
                        "
                    />
                </label>

                <button
                    type="button"
                    onClick={() => setShowPasswords((prev) => !prev)}
                    className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-white transition"
                >
                    {showPasswords ? (
                        <EyeOff size={13} />
                    ) : (
                        <Eye size={13} />
                    )}
                    {showPasswords ? "Hide" : "Show"} passwords
                </button>

                {error && (
                    <p className="text-red-400 text-sm">{error}</p>
                )}

                {message && (
                    <p className="flex items-center gap-1.5 text-emerald-400 text-sm">
                        <CheckCircle2 size={14} />
                        {message}
                    </p>
                )}

                <button
                    type="submit"
                    disabled={submitting}
                    className="
                        flex
                        items-center
                        gap-2
                        bg-blue-600
                        hover:bg-blue-500
                        disabled:opacity-60
                        text-white
                        text-sm
                        font-medium
                        px-4
                        py-2.5
                        rounded-lg
                        transition
                    "
                >
                    {submitting ? (
                        <Loader2 size={16} className="animate-spin" />
                    ) : (
                        <KeyRound size={16} />
                    )}
                    {submitting ? "Updating..." : "Update Password"}
                </button>

            </form>

        </div>
    );

}

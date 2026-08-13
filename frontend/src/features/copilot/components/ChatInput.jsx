
import { useState } from "react";

import {
    Send,
} from "lucide-react";

// =========================================================
// Enterprise AI Copilot
// Chat Input
// =========================================================

export default function ChatInput({
    onSend,
    disabled = false,
}) {

    const [value, setValue] =
        useState("");


    // =====================================================
    // Submit
    // =====================================================

    const handleSubmit = (event) => {

        event.preventDefault();


        const trimmed =
            value.trim();


        if (
            !trimmed ||
            disabled
        ) {
            return;
        }


        if (
            typeof onSend !== "function"
        ) {

            console.error(
                "ChatInput: onSend must be a function."
            );

            return;
        }


        onSend(trimmed);


        setValue("");

    };


    // =====================================================
    // Input Change
    // =====================================================

    const handleChange = (event) => {

        setValue(
            event.target.value
        );

    };


    // =====================================================
    // Render
    // =====================================================

    return (

        <form
            onSubmit={handleSubmit}
            className="
                border-t
                border-slate-800
                bg-slate-950
                p-4
                flex
                gap-3
            "
        >

            <label
                htmlFor="copilot-question"
                className="sr-only"
            >
                Ask Enterprise AI Copilot
            </label>


            <input
                id="copilot-question"
                name="question"
                type="text"
                value={value}
                onChange={handleChange}
                disabled={disabled}
                autoComplete="off"
                spellCheck="true"
                placeholder="Ask about sales, inventory, customers, forecasts..."
                className="
                    flex-1
                    min-w-0
                    bg-slate-800
                    border
                    border-slate-700
                    rounded-lg
                    px-4
                    py-2.5
                    text-white
                    text-sm
                    placeholder:text-slate-500
                    focus:outline-none
                    focus:border-blue-500
                    focus:ring-2
                    focus:ring-blue-500/20
                    disabled:opacity-50
                    disabled:cursor-not-allowed
                    transition
                "
            />


            <button
                type="submit"
                disabled={
                    disabled ||
                    !value.trim()
                }
                aria-label="Send question"
                title="Send question"
                className="
                    flex
                    items-center
                    justify-center
                    gap-2
                    bg-blue-600
                    hover:bg-blue-500
                    active:bg-blue-700
                    disabled:opacity-50
                    disabled:cursor-not-allowed
                    text-white
                    font-semibold
                    px-4
                    py-2.5
                    rounded-lg
                    transition
                    focus:outline-none
                    focus:ring-2
                    focus:ring-blue-500/40
                "
            >

                <Send size={16} />

                <span className="hidden sm:inline">
                    Send
                </span>

            </button>

        </form>

    );

}


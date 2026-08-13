
// =========================================================
// Enterprise AI Business Intelligence Platform
// Enterprise AI Copilot
// =========================================================

import {
    useEffect,
    useRef,
    useState,
} from "react";

import {
    AlertCircle,
    Bot,
    Loader2,
    RotateCcw,
    ShieldCheck,
    Sparkles,
} from "lucide-react";

import {
    chat as sendCopilotMessage,
} from "../../api/ragApi";

import {
    extractCopilotAnswer,
    extractCopilotError,
    validateCopilotResponse,
    normalizeQuestion,
} from "./utils/copilotUtils";

import ChatMessage from "./components/ChatMessage";
import ChatInput from "./components/ChatInput";
import SuggestedPrompts from "./components/SuggestedPrompts";

import "./copilot.css";


// =========================================================
// INITIAL MESSAGE
// =========================================================

const INITIAL_MESSAGE = {
    id: "welcome",

    role: "assistant",

    content:
        "Hi, I'm your Enterprise AI Copilot. " +
        "Ask me about sales, inventory, customers, forecasts, " +
        "risks, or business decisions. " +
        "I'll use the enterprise RAG and analytics pipeline " +
        "to provide an evidence-based answer.",

    timestamp: new Date(),
};


// =========================================================
// MAIN COMPONENT
// =========================================================

export default function Copilot() {

    const [
        messages,
        setMessages,
    ] = useState([
        INITIAL_MESSAGE,
    ]);


    const [
        loading,
        setLoading,
    ] = useState(false);


    const [
        error,
        setError,
    ] = useState(null);


    const bottomRef =
        useRef(null);


    // =====================================================
    // AUTO SCROLL
    // =====================================================

    useEffect(() => {

        bottomRef.current?.scrollIntoView({
            behavior: "smooth",
        });

    }, [
        messages,
        loading,
    ]);


    // =====================================================
    // SEND MESSAGE
    // =====================================================

    const handleSend = async (question) => {

        const trimmed =
            normalizeQuestion(question);


        // -------------------------------------------------
        // VALIDATE QUESTION
        // -------------------------------------------------

        if (
            !trimmed ||
            loading
        ) {

            return;
        }


        // -------------------------------------------------
        // ADD USER MESSAGE
        // -------------------------------------------------

        const userMessage = {

            id:
                `user-${Date.now()}`,

            role:
                "user",

            content:
                trimmed,

            timestamp:
                new Date(),

        };


        setMessages(
            (previous) => [
                ...previous,
                userMessage,
            ]
        );


        setLoading(true);

        setError(null);


        try {

            // =================================================
            // DEBUG REQUEST
            // =================================================

            console.log(
                "========================================"
            );

            console.log(
                "COPILOT REQUEST"
            );

            console.log(
                "Question:",
                trimmed
            );

            console.log(
                "========================================"
            );


            // =================================================
            // CALL COPILOT / RAG API
            // =================================================
            //
            // ragApi.js should handle:
            //
            // POST /copilot/chat
            //
            // and return response.data.
            //
            // Therefore we do NOT use response.data here.
            //
            // =================================================

            const data =
                await sendCopilotMessage(
                    trimmed
                );


            // =================================================
            // DEBUG RESPONSE
            // =================================================

            console.log(
                "========================================"
            );

            console.log(
                "COPILOT RAW RESPONSE"
            );

            console.log(
                data
            );

            console.log(
                "========================================"
            );


            // =================================================
            // VALIDATE RESPONSE
            // =================================================

            const validation =
                validateCopilotResponse(
                    data
                );


            if (
                !validation.valid
            ) {

                throw new Error(
                    validation.message
                );

            }


            // =================================================
            // EXTRACT CLEAN ANSWER
            // =================================================

            const answer =
                validation.answer ||
                extractCopilotAnswer(
                    data
                );


            if (!answer) {

                console.error(
                    "EMPTY COPILOT ANSWER:",
                    data
                );


                throw new Error(
                    "The Copilot backend returned an empty answer."
                );

            }


            // =================================================
            // ADD ASSISTANT MESSAGE
            // =================================================

            const assistantMessage = {

                id:
                    `assistant-${Date.now()}`,

                role:
                    "assistant",

                content:
                    answer,

                timestamp:
                    new Date(),

            };


            setMessages(
                (previous) => [
                    ...previous,
                    assistantMessage,
                ]
            );


        }

        catch (err) {

            console.error(
                "========================================"
            );

            console.error(
                "COPILOT ERROR"
            );

            console.error(
                err
            );

            console.error(
                "========================================"
            );


            setError(
                extractCopilotError(
                    err
                )
            );

        }

        finally {

            setLoading(false);


            // -------------------------------------------------
            // RETURN FOCUS TO INPUT
            // -------------------------------------------------

            setTimeout(() => {

                document
                    .getElementById(
                        "copilot-question"
                    )
                    ?.focus();

            }, 100);

        }

    };


    // =====================================================
    // CLEAR CHAT
    // =====================================================

    const handleClear = () => {

        if (loading) {

            return;
        }


        setMessages([
            {
                ...INITIAL_MESSAGE,

                id:
                    `welcome-${Date.now()}`,

                timestamp:
                    new Date(),

            },
        ]);


        setError(null);


        setTimeout(() => {

            document
                .getElementById(
                    "copilot-question"
                )
                ?.focus();

        }, 100);

    };


    // =====================================================
    // RENDER
    // =====================================================

    return (

        <div className="copilot-page">

            <div className="copilot-shell">


                {/* =================================================
                    HEADER
                ================================================= */}

                <header className="copilot-header">

                    <div className="copilot-brand">

                        <div className="copilot-logo">

                            <Bot
                                size={27}
                            />

                        </div>


                        <div>

                            <div className="copilot-title-row">

                                <h1 className="copilot-title">

                                    AI Copilot

                                </h1>


                                <span className="copilot-online">

                                    <span className="copilot-online-dot" />

                                    Enterprise AI Online

                                </span>

                            </div>


                            <p className="copilot-subtitle">

                                Enterprise Business Intelligence Assistant

                            </p>

                        </div>

                    </div>


                    <button
                        type="button"
                        className="copilot-clear-button"
                        onClick={handleClear}
                        disabled={
                            loading ||
                            messages.length <= 1
                        }
                        title="Start a new conversation"
                    >

                        <RotateCcw
                            size={16}
                        />

                        New Chat

                    </button>

                </header>


                {/* =================================================
                    INTRO
                ================================================= */}

                <section className="copilot-intro">

                    <div className="copilot-intro-icon">

                        <Sparkles
                            size={20}
                        />

                    </div>


                    <div>

                        <h2>
                            Ask your business anything
                        </h2>


                        <p>

                            Ask questions about sales,
                            inventory, customers, forecasts,
                            risks, or business decisions.
                            Answers are generated using
                            enterprise RAG and analytics data.

                        </p>

                    </div>

                </section>


                {/* =================================================
                    CHAT
                ================================================= */}

                <main className="copilot-chat">


                    {/* =================================================
                        MESSAGES
                    ================================================= */}

                    <div className="copilot-messages">

                        {messages.map(
                            (message) => (

                                <ChatMessage
                                    key={
                                        message.id
                                    }

                                    role={
                                        message.role
                                    }

                                    content={
                                        message.content
                                    }

                                    timestamp={
                                        message.timestamp
                                    }

                                />

                            )
                        )}


                        {/* =================================================
                            THINKING
                        ================================================= */}

                        {loading && (

                            <div
                                className="
                                    copilot-message
                                    assistant-message
                                "
                            >

                                <div
                                    className="
                                        copilot-avatar
                                    "
                                >

                                    <Sparkles
                                        size={18}
                                    />

                                </div>


                                <div
                                    className="
                                        copilot-message-body
                                    "
                                >

                                    <div
                                        className="
                                            copilot-message-header
                                        "
                                    >

                                        <span
                                            className="
                                                copilot-message-name
                                            "
                                        >

                                            Enterprise AI

                                        </span>


                                        <span
                                            className="
                                                copilot-message-time
                                            "
                                        >

                                            Now

                                        </span>

                                    </div>


                                    <div
                                        className="
                                            copilot-thinking
                                        "
                                    >

                                        <Loader2
                                            size={16}
                                            className="
                                                copilot-spinner
                                            "
                                        />

                                        <span>
                                            Analyzing enterprise data...
                                        </span>


                                        <span
                                            className="
                                                thinking-dots
                                            "
                                        >

                                            ...

                                        </span>

                                    </div>

                                </div>

                            </div>

                        )}


                        <div
                            ref={
                                bottomRef
                            }
                        />

                    </div>


                    {/* =================================================
                        ERROR
                    ================================================= */}

                    {error && (

                        <div
                            className="
                                copilot-error
                            "
                        >

                            <AlertCircle
                                size={17}
                            />


                            <div
                                className="
                                    copilot-error-content
                                "
                            >

                                <strong>
                                    Copilot error
                                </strong>


                                <span>
                                    {error}
                                </span>

                            </div>


                            <button
                                type="button"
                                onClick={() =>
                                    setError(null)
                                }
                                className="
                                    copilot-error-close
                                "
                                title="Dismiss error"
                                aria-label="Dismiss error"
                            >

                                ×

                            </button>

                        </div>

                    )}


                    {/* =================================================
                        SUGGESTED PROMPTS
                    ================================================= */}

                    {messages.length <= 1 &&
                        !loading && (

                            <SuggestedPrompts
                                onSelect={
                                    handleSend
                                }
                            />

                        )}


                    {/* =================================================
                        INPUT
                    ================================================= */}

                    <ChatInput
                        onSend={
                            handleSend
                        }

                        disabled={
                            loading
                        }
                    />


                    {/* =================================================
                        FOOTER
                    ================================================= */}

                    <div
                        className="
                            copilot-input-footer
                        "
                    >

                        <span>

                            <ShieldCheck
                                size={13}
                            />

                            Enterprise RAG enabled

                        </span>


                        <span>

                            Press Enter to send

                        </span>

                    </div>

                </main>

            </div>

        </div>

    );

}


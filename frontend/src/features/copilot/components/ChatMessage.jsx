
import { useState } from "react";

import {
    Bot,
    User,
    Copy,
    Check,
} from "lucide-react";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

// =========================================================
// Enterprise AI Business Intelligence Platform
// ChatMessage
// =========================================================

export default function ChatMessage({
    role,
    content,
}) {

    const [copied, setCopied] =
        useState(false);


    const isUser =
        role === "user";


    const messageContent =
        String(
            content || ""
        );


    // =====================================================
    // COPY ASSISTANT ANSWER
    // =====================================================

    const handleCopy = async () => {

        try {

            await navigator.clipboard.writeText(
                messageContent
            );


            setCopied(true);


            setTimeout(() => {

                setCopied(false);

            }, 1500);

        }

        catch (error) {

            console.error(
                "Copy failed:",
                error
            );

        }

    };


    // =====================================================
    // USER MESSAGE
    // =====================================================

    if (isUser) {

        return (

            <div className="copilot-message user">

                <div className="copilot-user-row">

                    <div>

                        <div className="
                            copilot-message-meta
                            user-meta
                        ">

                            <span>
                                You
                            </span>

                        </div>


                        <div className="
                            copilot-message-bubble
                        ">

                            {messageContent}

                        </div>

                    </div>


                    <div className="
                        copilot-user-icon
                    ">

                        <User size={17} />

                    </div>

                </div>

            </div>

        );

    }


    // =====================================================
    // ASSISTANT MESSAGE
    // =====================================================

    return (

        <div className="
            copilot-message
            assistant
        ">

            <div className="
                copilot-assistant-row
            ">

                <div className="
                    copilot-assistant-icon
                ">

                    <Bot size={17} />

                </div>


                <div className="
                    copilot-assistant-content
                ">

                    <div className="
                        copilot-message-meta
                    ">

                        <span>
                            Enterprise AI
                        </span>

                    </div>


                    <div className="
                        copilot-message-bubble
                    ">

                        <div className="
                            copilot-answer
                        ">

                            <ReactMarkdown
                                remarkPlugins={[
                                    remarkGfm,
                                ]}
                                components={{

                                    h1: ({
                                        children,
                                    }) => (
                                        <h1>
                                            {children}
                                        </h1>
                                    ),

                                    h2: ({
                                        children,
                                    }) => (
                                        <h2>
                                            {children}
                                        </h2>
                                    ),

                                    h3: ({
                                        children,
                                    }) => (
                                        <h3>
                                            {children}
                                        </h3>
                                    ),

                                    h4: ({
                                        children,
                                    }) => (
                                        <h4>
                                            {children}
                                        </h4>
                                    ),

                                    p: ({
                                        children,
                                    }) => (
                                        <p>
                                            {children}
                                        </p>
                                    ),

                                    ul: ({
                                        children,
                                    }) => (
                                        <ul>
                                            {children}
                                        </ul>
                                    ),

                                    ol: ({
                                        children,
                                    }) => (
                                        <ol>
                                            {children}
                                        </ol>
                                    ),

                                    li: ({
                                        children,
                                    }) => (
                                        <li>
                                            {children}
                                        </li>
                                    ),

                                    strong: ({
                                        children,
                                    }) => (
                                        <strong>
                                            {children}
                                        </strong>
                                    ),

                                    em: ({
                                        children,
                                    }) => (
                                        <em>
                                            {children}
                                        </em>
                                    ),

                                    blockquote: ({
                                        children,
                                    }) => (
                                        <blockquote>
                                            {children}
                                        </blockquote>
                                    ),

                                    a: ({
                                        children,
                                        href,
                                    }) => (
                                        <a
                                            href={href}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                        >
                                            {children}
                                        </a>
                                    ),

                                    code: ({
                                        children,
                                        className,
                                    }) => {

                                        const isCodeBlock =
                                            Boolean(
                                                className
                                            );


                                        if (
                                            isCodeBlock
                                        ) {

                                            return (
                                                <pre>
                                                    <code
                                                        className={
                                                            className
                                                        }
                                                    >
                                                        {children}
                                                    </code>
                                                </pre>
                                            );

                                        }


                                        return (
                                            <code>
                                                {children}
                                            </code>
                                        );

                                    },


                                    table: ({
                                        children,
                                    }) => (
                                        <div className="
                                            copilot-table-wrapper
                                        ">
                                            <table>
                                                {children}
                                            </table>
                                        </div>
                                    ),

                                    thead: ({
                                        children,
                                    }) => (
                                        <thead>
                                            {children}
                                        </thead>
                                    ),

                                    tbody: ({
                                        children,
                                    }) => (
                                        <tbody>
                                            {children}
                                        </tbody>
                                    ),

                                    tr: ({
                                        children,
                                    }) => (
                                        <tr>
                                            {children}
                                        </tr>
                                    ),

                                    th: ({
                                        children,
                                    }) => (
                                        <th>
                                            {children}
                                        </th>
                                    ),

                                    td: ({
                                        children,
                                    }) => (
                                        <td>
                                            {children}
                                        </td>
                                    ),

                                }}
                            >

                                {messageContent}

                            </ReactMarkdown>

                        </div>

                    </div>


                    <div className="
                        copilot-message-actions
                    ">

                        <button
                            type="button"
                            className="
                                copilot-copy-button
                            "
                            onClick={handleCopy}
                            title="Copy answer"
                        >

                            {copied ? (

                                <>
                                    <Check size={13} />
                                    Copied
                                </>

                            ) : (

                                <>
                                    <Copy size={13} />
                                    Copy
                                </>

                            )}

                        </button>

                    </div>

                </div>

            </div>

        </div>

    );

}


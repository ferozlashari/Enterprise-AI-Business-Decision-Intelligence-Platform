
// =========================================================
// Enterprise AI Business Intelligence Platform
// Copilot Utilities
// =========================================================

/**
 * Safely convert any backend value into a string.
 */
export function safeString(value) {

    if (
        value === null ||
        value === undefined
    ) {
        return "";
    }

    if (
        typeof value === "string"
    ) {
        return value.trim();
    }

    return String(value).trim();
}


// =========================================================
// Extract Copilot Answer
// =========================================================

export function extractCopilotAnswer(data) {

    if (!data) {
        return "";
    }


    // -----------------------------------------------------
    // 1. Preferred RAG structure
    // -----------------------------------------------------

    const ragAnswer =
        safeString(
            data?.rag_insight?.answer
        );

    if (ragAnswer) {
        return ragAnswer;
    }


    // -----------------------------------------------------
    // 2. Nested RAG structure
    // -----------------------------------------------------

    const nestedRagAnswer =
        safeString(
            data?.response?.rag_insight?.answer
        );

    if (nestedRagAnswer) {
        return nestedRagAnswer;
    }


    // -----------------------------------------------------
    // 3. Direct answer
    // -----------------------------------------------------

    const answer =
        safeString(
            data?.answer
        );

    if (answer) {
        return answer;
    }


    // -----------------------------------------------------
    // 4. Nested answer
    // -----------------------------------------------------

    const nestedAnswer =
        safeString(
            data?.response?.answer
        );

    if (nestedAnswer) {
        return nestedAnswer;
    }


    // -----------------------------------------------------
    // 5. Business analysis object
    // -----------------------------------------------------

    if (
        data?.business_analysis &&
        typeof data.business_analysis === "object"
    ) {

        const analysisAnswer =
            safeString(
                data.business_analysis.answer
            );

        if (analysisAnswer) {
            return analysisAnswer;
        }


        const analysisResponse =
            safeString(
                data.business_analysis.response
            );

        if (analysisResponse) {
            return analysisResponse;
        }


        const analysisResult =
            safeString(
                data.business_analysis.result
            );

        if (analysisResult) {
            return analysisResult;
        }


        const analysisInsight =
            safeString(
                data.business_analysis.insight
            );

        if (analysisInsight) {
            return analysisInsight;
        }
    }


    // -----------------------------------------------------
    // 6. Nested business analysis object
    // -----------------------------------------------------

    if (
        data?.response?.business_analysis &&
        typeof data.response.business_analysis === "object"
    ) {

        const analysisAnswer =
            safeString(
                data.response.business_analysis.answer
            );

        if (analysisAnswer) {
            return analysisAnswer;
        }


        const analysisResponse =
            safeString(
                data.response.business_analysis.response
            );

        if (analysisResponse) {
            return analysisResponse;
        }


        const analysisResult =
            safeString(
                data.response.business_analysis.result
            );

        if (analysisResult) {
            return analysisResult;
        }


        const analysisInsight =
            safeString(
                data.response.business_analysis.insight
            );

        if (analysisInsight) {
            return analysisInsight;
        }
    }


    // -----------------------------------------------------
    // 7. Business analysis string
    // -----------------------------------------------------

    const businessAnalysis =
        safeString(
            data?.business_analysis
        );

    if (businessAnalysis) {
        return businessAnalysis;
    }


    // -----------------------------------------------------
    // 8. Nested business analysis string
    // -----------------------------------------------------

    const nestedBusinessAnalysis =
        safeString(
            data?.response?.business_analysis
        );

    if (nestedBusinessAnalysis) {
        return nestedBusinessAnalysis;
    }


    // -----------------------------------------------------
    // 9. Direct response string
    // -----------------------------------------------------

    const directResponse =
        safeString(
            data?.response
        );

    if (directResponse) {
        return directResponse;
    }


    // -----------------------------------------------------
    // 10. Nested response.response
    // -----------------------------------------------------

    const nestedResponse =
        safeString(
            data?.response?.response
        );

    if (nestedResponse) {
        return nestedResponse;
    }


    // -----------------------------------------------------
    // 11. Nested response.result
    // -----------------------------------------------------

    const nestedResult =
        safeString(
            data?.response?.result
        );

    if (nestedResult) {
        return nestedResult;
    }


    // -----------------------------------------------------
    // 12. Direct result
    // -----------------------------------------------------

    const result =
        safeString(
            data?.result
        );

    if (result) {
        return result;
    }


    // -----------------------------------------------------
    // 13. Direct message
    // -----------------------------------------------------

    const message =
        safeString(
            data?.message
        );

    if (message) {
        return message;
    }


    // -----------------------------------------------------
    // 14. Nested message
    // -----------------------------------------------------

    const nestedMessage =
        safeString(
            data?.response?.message
        );

    if (nestedMessage) {
        return nestedMessage;
    }


    // -----------------------------------------------------
    // Nothing found
    // -----------------------------------------------------

    return "";
}


// =========================================================
// Clean Copilot Answer
// =========================================================

export function cleanCopilotAnswer(answer) {

    let text =
        safeString(answer);


    if (!text) {
        return "";
    }


    // -----------------------------------------------------
    // Normalize line endings
    // -----------------------------------------------------

    text =
        text.replace(
            /\r\n/g,
            "\n"
        );


    // -----------------------------------------------------
    // Normalize old Mac line endings
    // -----------------------------------------------------

    text =
        text.replace(
            /\r/g,
            "\n"
        );


    // -----------------------------------------------------
    // Remove excessive blank lines
    // -----------------------------------------------------

    text =
        text.replace(
            /\n{3,}/g,
            "\n\n"
        );


    // -----------------------------------------------------
    // Remove trailing whitespace
    // -----------------------------------------------------

    text =
        text
            .split("\n")
            .map(
                (line) =>
                    line.trimEnd()
            )
            .join("\n");


    // -----------------------------------------------------
    // Detect exact duplicated answer
    //
    // Only removes the second half if the complete
    // second half is exactly identical to the first half.
    // -----------------------------------------------------

    const lines =
        text.split("\n");


    if (
        lines.length >= 8 &&
        lines.length % 2 === 0
    ) {

        const midpoint =
            lines.length / 2;


        const firstHalf =
            lines
                .slice(
                    0,
                    midpoint
                )
                .join("\n")
                .trim();


        const secondHalf =
            lines
                .slice(
                    midpoint
                )
                .join("\n")
                .trim();


        if (
            firstHalf &&
            secondHalf &&
            firstHalf === secondHalf
        ) {

            text =
                firstHalf;
        }
    }


    return text.trim();
}


// =========================================================
// Normalize User Question
// =========================================================

export function normalizeQuestion(question) {

    return String(
        question || ""
    )
        .replace(
            /\s+/g,
            " "
        )
        .trim();
}


// =========================================================
// Validate Copilot Response
// =========================================================

export function validateCopilotResponse(data) {

    if (!data) {

        return {

            valid: false,

            message:
                "No response was received from the Copilot API."

        };
    }


    // -----------------------------------------------------
    // Explicit backend failure
    // -----------------------------------------------------

    if (
        data?.success === false
    ) {

        return {

            valid: false,

            message:
                safeString(
                    data?.message ||
                    data?.detail ||
                    data?.error
                ) ||
                "Enterprise AI Copilot returned an error."

        };
    }


    if (
        data?.status === "error"
    ) {

        return {

            valid: false,

            message:
                safeString(
                    data?.message ||
                    data?.detail ||
                    data?.error
                ) ||
                "Enterprise AI Copilot returned an error."

        };
    }


    // -----------------------------------------------------
    // Extract answer
    // -----------------------------------------------------

    const rawAnswer =
        extractCopilotAnswer(
            data
        );


    const answer =
        cleanCopilotAnswer(
            rawAnswer
        );


    // -----------------------------------------------------
    // Empty response
    // -----------------------------------------------------

    if (!answer) {

        return {

            valid: false,

            message:
                "The Copilot backend returned an empty answer."

        };
    }


    // -----------------------------------------------------
    // Valid response
    // -----------------------------------------------------

    return {

        valid: true,

        message: null,

        answer

    };
}


// =========================================================
// Extract Backend Error
// =========================================================

export function extractCopilotError(error) {

    // -----------------------------------------------------
    // FastAPI string detail
    // -----------------------------------------------------

    const detail =
        error?.response?.data?.detail;


    if (
        typeof detail === "string" &&
        detail.trim()
    ) {

        return detail.trim();
    }


    // -----------------------------------------------------
    // FastAPI validation error
    // -----------------------------------------------------

    if (
        Array.isArray(detail)
    ) {

        return detail
            .map(
                (item) => {

                    if (
                        typeof item === "string"
                    ) {

                        return item;
                    }


                    const location =
                        Array.isArray(
                            item?.loc
                        )
                            ? item.loc.join(".")
                            : "";


                    const message =
                        item?.msg ||
                        item?.message ||
                        "Invalid input";


                    return location
                        ? `${location}: ${message}`
                        : message;
                }
            )
            .join(", ");
    }


    // -----------------------------------------------------
    // Backend message
    // -----------------------------------------------------

    const message =
        error?.response?.data?.message;


    if (
        typeof message === "string" &&
        message.trim()
    ) {

        return message.trim();
    }


    // -----------------------------------------------------
    // Backend error
    // -----------------------------------------------------

    const backendError =
        error?.response?.data?.error;


    if (
        typeof backendError === "string" &&
        backendError.trim()
    ) {

        return backendError.trim();
    }


    // -----------------------------------------------------
    // Axios error
    // -----------------------------------------------------

    if (
        typeof error?.message === "string" &&
        error.message.trim()
    ) {

        return error.message.trim();
    }


    // -----------------------------------------------------
    // Default
    // -----------------------------------------------------

    return (
        "The Enterprise AI Copilot failed to respond."
    );
}


// =========================================================
// Suggested Prompts
// =========================================================

export const COPILOT_PROMPTS = [

    {
        title: "Inventory Risk",

        question:
            "Summarize current inventory risk."
    },


    {
        title: "Sales Performance",

        question:
            "What are our top performing product categories?"
    },


    {
        title: "Regional Sales",

        question:
            "Which regions show declining sales?"
    },


    {
        title: "Forecast",

        question:
            "What are the most important sales forecast risks?"
    },


    {
        title: "Customers",

        question:
            "Which customer segments are most valuable?"
    },


    {
        title: "Business Risk",

        question:
            "What are the biggest business risks right now?"
    },


    {
        title: "Decision",

        question:
            "What business decisions should management prioritize?"
    }

];


// =========================================================
// Initial Assistant Message
// =========================================================

export const INITIAL_COPILOT_MESSAGE =
    "Hi, I'm your Enterprise AI Copilot. " +
    "Ask me about sales, inventory, customers, " +
    "forecasts, risks, or business decisions. " +
    "I'll use the enterprise RAG and analytics pipeline " +
    "to provide an evidence-based answer.";



// =========================================================
// Enterprise AI Business Intelligence Platform
// RAG / Copilot API
//
// File:
// src/api/ragApi.js
// =========================================================

import api from "./axios";


// =========================================================
// SEND COPILOT MESSAGE
// =========================================================

export async function sendCopilotMessage(question) {

    const cleanQuestion =
        String(question || "").trim();


    // -----------------------------------------------------
    // Validate question
    // -----------------------------------------------------

    if (!cleanQuestion) {

        throw new Error(
            "Copilot question cannot be empty."
        );

    }


    // -----------------------------------------------------
    // Debug request
    // -----------------------------------------------------

    console.log(
        "========================================"
    );

    console.log(
        "COPILOT API REQUEST"
    );

    console.log(
        "Question:",
        cleanQuestion
    );

    console.log(
        "========================================"
    );


    try {

        // -------------------------------------------------
        // POST /copilot/chat
        // -------------------------------------------------

        const response =
            await api.post(
                "/copilot/chat",
                {
                    question:
                        cleanQuestion,
                }
            );


        // -------------------------------------------------
        // Debug response
        // -------------------------------------------------

        console.log(
            "========================================"
        );

        console.log(
            "COPILOT API RESPONSE"
        );

        console.log(
            response.data
        );

        console.log(
            "========================================"
        );


        // -------------------------------------------------
        // Return actual backend JSON
        //
        // Copilot.jsx expects:
        //
        // const data = await sendCopilotMessage(...)
        //
        // Therefore return response.data,
        // NOT the complete Axios response.
        // -------------------------------------------------

        return response.data;

    }

    catch (error) {

        console.error(
            "========================================"
        );

        console.error(
            "COPILOT API ERROR"
        );

        console.error(
            error
        );

        console.error(
            "========================================"
        );


        // -------------------------------------------------
        // Preserve Axios error so copilotUtils.js can
        // extract:
        //
        // error.response.data.detail
        // error.response.data.message
        // error.message
        // -------------------------------------------------

        throw error;

    }

}


// =========================================================
// COPILOT HEALTH
// =========================================================

export async function fetchCopilotHealth() {

    try {

        const response =
            await api.get(
                "/copilot/health"
            );


        console.log(
            "COPILOT HEALTH RESPONSE:",
            response.data
        );


        return response.data;

    }

    catch (error) {

        console.error(
            "COPILOT HEALTH ERROR:",
            error
        );

        throw error;

    }

}


// =========================================================
// COPILOT BUILD
// =========================================================

export async function fetchCopilotBuild() {

    try {

        const response =
            await api.get(
                "/copilot/build"
            );


        console.log(
            "COPILOT BUILD RESPONSE:",
            response.data
        );


        return response.data;

    }

    catch (error) {

        console.error(
            "COPILOT BUILD ERROR:",
            error
        );

        throw error;

    }

}


// =========================================================
// COMPATIBILITY ALIASES
//
// Allows Copilot.jsx to use:
//
// import { chat } from "../../api/ragApi";
//
// =========================================================

export const chat =
    sendCopilotMessage;


export const health =
    fetchCopilotHealth;


export const build =
    fetchCopilotBuild;


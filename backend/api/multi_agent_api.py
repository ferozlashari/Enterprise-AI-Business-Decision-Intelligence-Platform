"""
=========================================================

Enterprise AI Business Decision Intelligence Platform

Multi Agent API

Author : Feroz Ali

=========================================================
"""


from fastapi import APIRouter, HTTPException


from pydantic import BaseModel



from backend.orchestrator.orchestrator import (
    EnterpriseOrchestrator
)




router = APIRouter(

    prefix="/ai",

    tags=["Enterprise AI"]

)



orchestrator = EnterpriseOrchestrator()




# =====================================================
# Request Schema
# =====================================================

class ChatRequest(BaseModel):

    question: str





# =====================================================
# Enterprise AI Chat
# =====================================================

@router.post("/chat")
def chat(
    request: ChatRequest
):


    try:


        result = orchestrator.chat(

            request.question

        )


        return {


            "success":

            True,


            "response":

            result


        }



    except Exception as e:


        raise HTTPException(

            status_code=500,

            detail=str(e)

        )





# =====================================================
# Health
# =====================================================

@router.get("/health")
def health():


    return {


        "status":

        "Healthy",


        "service":

        "Enterprise Multi Agent System"

    }
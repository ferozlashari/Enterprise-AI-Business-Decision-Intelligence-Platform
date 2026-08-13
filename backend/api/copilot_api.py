"""
=========================================================

Enterprise AI Business Decision Intelligence Platform

Executive AI Copilot API

Author : Feroz Ali

=========================================================
"""


from fastapi import (
    APIRouter,
    HTTPException
)


from pydantic import (
    BaseModel,
    Field
)


from backend.services.copilot_service import (
    CopilotService
)


from backend.cache.decorators import (
    redis_cache
)


from rag.rag_manager import (
    RAGManager
)






# =====================================================
# Router Configuration
# =====================================================


router = APIRouter(

    prefix="/copilot",

    tags=["AI Copilot"]

)






# =====================================================
# Lazy Service Initialization
# =====================================================


service = None



def get_service():


    global service



    if service is None:


        service = CopilotService()



    return service







# =====================================================
# Request Schema
# =====================================================


class CopilotRequest(BaseModel):


    question: str = Field(

        ...,

        min_length=3,

        max_length=500,

        description="Enterprise business question"

    )









# =====================================================
# Cached AI Response Generator
# =====================================================


@redis_cache(

    expire=1800

)

def generate_ai_response(

    question: str

):


    return get_service().ask(

        question

    )









# =====================================================
# Build Enterprise Knowledge Base
# =====================================================


@router.post("/build")
def build_knowledge_base():


    try:


        rag = RAGManager.get_instance()



        result = rag.build_vector_database()



        return {


            "success":

            True,


            "message":

            "Knowledge base build completed",


            "result":

            result


        }





    except Exception as e:



        raise HTTPException(

            status_code=500,

            detail=str(e)

        )









# =====================================================
# AI Chat Endpoint
# =====================================================


@router.post("/chat")
def ask_copilot(

    request: CopilotRequest

):


    try:


        result = generate_ai_response(

            request.question.strip()

        )



        return {


            "success":

            True,



            "question":

            request.question,



            "response":

            result


        }





    except Exception as e:



        raise HTTPException(

            status_code=500,

            detail=str(e)

        )









# =====================================================
# Health Check
# =====================================================


@router.get("/health")
def copilot_health():


    try:


        rag = RAGManager.get_instance()



        return {


            "status":

            "Healthy",



            "service":

            "Executive AI Copilot",



            "llm":

            "Groq",



            "documents":

            rag.vector_store.index.ntotal,



            "endpoint":

            "/copilot/chat"


        }





    except Exception as e:



        return {


            "status":

            "error",


            "message":

            str(e)

        }
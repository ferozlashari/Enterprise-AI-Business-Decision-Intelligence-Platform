from fastapi import APIRouter

from backend.copilot.copilot import EnterpriseCopilot

router = APIRouter(
    prefix="/copilot",
    tags=["Enterprise Copilot"]
)

copilot = EnterpriseCopilot()


@router.post("/chat")
def chat(question: str):

    return {

        "answer": copilot.ask(question)

    }
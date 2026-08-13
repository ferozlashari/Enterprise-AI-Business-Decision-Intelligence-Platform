from backend.orchestrator.router import EnterpriseOrchestrator
from backend.llm.groq_client import ask_llm

from rag.rag_pipeline import EnterpriseRAG

from backend.copilot.prompt_builder import PromptBuilder


class EnterpriseCopilot:

    def __init__(self):

        self.rag = EnterpriseRAG()

        self.orchestrator = EnterpriseOrchestrator()

        self.prompt = PromptBuilder()

    def ask(self, question):

        rag_context = self.rag.ask(question)

        business_result = self.orchestrator.chat(question)

        prompt = self.prompt.build(

            question,

            rag_context,

            business_result

        )

        answer = ask_llm.invoke(prompt)

        return answer.content
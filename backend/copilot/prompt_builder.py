class PromptBuilder:

    def build(self, question, rag_context, agent_result):

        return f"""
You are an Enterprise Business AI Assistant.

User Question:
{question}

Enterprise Knowledge:
{rag_context}

Business Analysis:
{agent_result}

Give an executive-level business answer.
"""
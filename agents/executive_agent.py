"""
Enterprise AI Business Decision Intelligence Platform

Executive Intelligence Agent

Author : Feroz Ali
"""

from agents.base_agent import BaseAgent

from agents.decision_agent import DecisionAgent

from agents.inventory_agent import InventoryAgent

from backend.llm.groq_client import ask_llm



class ExecutiveAgent(BaseAgent):


    def __init__(self):

        super().__init__(
            "Executive Agent"
        )


        self.decision_agent = DecisionAgent()


        self.inventory_agent = InventoryAgent()



    # =====================================================
    # Business Risk Analysis
    # =====================================================

    def business_risks(self):


        try:


            health = self.inventory_agent.execute(

                {
                    "action": "health"
                }

            )


            risks = []



            if isinstance(
                health,
                dict
            ):


                if health.get(
                    "Low Stock",
                    0
                ) > 0:


                    risks.append(
                        "Inventory shortage risk detected."
                    )



                if health.get(
                    "Over Stock",
                    0
                ) > 0:


                    risks.append(
                        "Over inventory risk detected."
                    )



            if not risks:


                risks.append(
                    "No critical risks detected."
                )


            return risks



        except Exception as e:


            return [

                f"Risk analysis failed: {str(e)}"

            ]





    # =====================================================
    # AI Executive Summary
    # =====================================================

    def generate_executive_insight(
            self,
            data
    ):


        prompt = f"""

You are a CEO level Enterprise AI Assistant.

Analyze:

{data}


Generate:

1. Current business situation

2. Major risks

3. Growth opportunities

4. Recommended decisions

5. Executive action plan


Provide professional business recommendations.

"""



        try:


            response = ask_llm(
                prompt
            )


            return response



        except Exception as e:


            return {

                "message":
                "LLM unavailable",

                "error":
                str(e)

            }





    # =====================================================
    # Executive Dashboard
    # =====================================================

    def executive_dashboard(self):


        try:


            decision_result = (

                self.decision_agent.business_decision()

            )



            dashboard_data = {


                "Business Risks":

                    self.business_risks(),



                "Inventory":

                    self.inventory_agent.execute(

                        {
                            "action":
                            "summary"
                        }

                    ),



                "Decision Engine":

                    decision_result,



                "Recommendations":

                    decision_result.get(

                        "executive_recommendation",

                        []

                    )

            }



            dashboard_data[

                "AI Executive Insight"

            ] = self.generate_executive_insight(

                dashboard_data

            )



            return dashboard_data



        except Exception as e:


            return {


                "status":
                "error",


                "message":
                str(e)

            }





    # =====================================================
    # Executive Copilot
    # =====================================================

    def copilot(
            self,
            question
    ):


        dashboard = self.executive_dashboard()



        prompt = f"""

You are an Enterprise AI Executive Copilot.


Business Information:

{dashboard}


User Question:

{question}


Provide a clear executive answer.

"""



        try:


            answer = ask_llm(
                prompt
            )


            return {


                "question":

                    question,


                "answer":

                    answer

            }



        except Exception as e:


            return {


                "question":

                    question,


                "answer":

                    "Unable to generate response",


                "error":

                    str(e)

            }





    # =====================================================
    # Agent Interface
    # =====================================================

    def execute(
            self,
            task
    ):


        action = task.get(
            "action"
        )



        if action == "dashboard":


            return self.executive_dashboard()



        elif action == "copilot":


            return self.copilot(

                task.get(

                    "question",

                    ""

                )

            )



        return {


            "status":

            "error",


            "message":

            "Unknown executive action"

        }





if __name__ == "__main__":


    agent = ExecutiveAgent()


    result = agent.execute(

        {

            "action":

            "dashboard"

        }

    )


    print(result)
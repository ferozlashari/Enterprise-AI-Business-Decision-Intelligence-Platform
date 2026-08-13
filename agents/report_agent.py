"""
=========================================================
Enterprise AI Business Decision Intelligence Platform
Report Agent
Author : Feroz Ali
=========================================================
"""


from datetime import datetime


from agents.base_agent import BaseAgent

from agents.executive_agent import ExecutiveAgent

from agents.decision_agent import DecisionAgent

from agents.inventory_agent import InventoryAgent



class ReportAgent(BaseAgent):


    def __init__(self):

        super().__init__("Report Agent")


        self.executive_agent = ExecutiveAgent()

        self.decision_agent = DecisionAgent()

        self.inventory_agent = InventoryAgent()



    # =====================================================
    # Inventory Report
    # =====================================================

    def inventory_report(self):


        return {


            "summary":

                self.inventory_agent.execute(

                    {
                        "action":"summary"
                    }

                ),



            "health":

                self.inventory_agent.execute(

                    {
                        "action":"health"
                    }

                ),



            "recommendations":

                self.inventory_agent.execute(

                    {
                        "action":"recommendation"
                    }

                )

        }



    # =====================================================
    # Executive Report
    # =====================================================

    def executive_report(self):


        return self.executive_agent.execute(

            {

                "action":"dashboard"

            }

        )



    # =====================================================
    # Decision Report
    # =====================================================

    def decision_report(self):


        return self.decision_agent.execute(

            {

                "action":"decision"

            }

        )



    # =====================================================
    # AI Generated Report Summary
    # =====================================================

    def generate_summary(self, report_data):


        from backend.llm.groq_client import ask_llm



        prompt=f"""

You are an Enterprise Report Analyst.


Analyze this business report:


{report_data}


Create:

1. Executive summary

2. Important findings

3. Business risks

4. Recommended actions


"""


        return ask_llm(prompt)



    # =====================================================
    # Complete Enterprise Report
    # =====================================================

    def enterprise_report(self):


        report = {


            "generated_at":

                datetime.now().strftime(

                    "%Y-%m-%d %H:%M:%S"

                ),



            "inventory":

                self.inventory_report(),



            "executive":

                self.executive_report(),



            "decision":

                self.decision_report()

        }



        report["AI Summary"] = (

            self.generate_summary(

                report

            )

        )


        return report




    # =====================================================
    # Execute
    # =====================================================

    def execute(self, task):


        action = task.get("action")



        if action == "report":


            return self.enterprise_report()



        return {


            "status":"error",

            "message":"Unknown task."

        }





if __name__=="__main__":


    agent = ReportAgent()



    result = agent.execute(

        {

            "action":"report"

        }

    )


    print(result)
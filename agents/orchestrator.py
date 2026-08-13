"""
=========================================================
Enterprise AI Business Decision Intelligence Platform
AI Orchestrator
Author : Feroz Ali
=========================================================
"""


from agents.data_agent import DataAgent
from agents.forecast_agent import ForecastAgent
from agents.inventory_agent import InventoryAgent
from agents.decision_agent import DecisionAgent
from agents.executive_agent import ExecutiveAgent
from agents.report_agent import ReportAgent




class EnterpriseAIOrchestrator:


    def __init__(self):


        # Core Agents

        self.data_agent = DataAgent()

        self.forecast_agent = ForecastAgent()

        self.inventory_agent = InventoryAgent()


        self.decision_agent = DecisionAgent(
            
        )


        self.executive_agent = ExecutiveAgent()


        self.report_agent = ReportAgent()



    # =====================================================
    # Data
    # =====================================================

    def load_data(self, filename):

        return self.data_agent.execute(

            {
                "action":"load",
                "filename":filename
            }

        )



    # =====================================================
    # Forecast
    # =====================================================

    def forecast(
            self,
            model_name,
            data
    ):

        return self.forecast_agent.execute(

            {

                "action":"forecast",

                "model":model_name,

                "data":data

            }

        )



    # =====================================================
    # Inventory
    # =====================================================

    def inventory(self):

        return self.inventory_agent.execute(

            {
                "action":"summary"
            }

        )



    # =====================================================
    # Decision
    # =====================================================

    def decision(
            self,
            model_name=None,
            data=None
    ):


        return self.decision_agent.execute(

            {

                "action":"decision",

                "model":model_name,

                "data":data

            }

        )



    # =====================================================
    # Executive Dashboard
    # =====================================================

    def dashboard(self):

        return self.executive_agent.execute(

            {
                "action":"dashboard"
            }

        )



    # =====================================================
    # AI Copilot
    # =====================================================

    def copilot(self, question):


        return self.executive_agent.execute(

            {

                "action":"copilot",

                "question":question

            }

        )



    # =====================================================
    # Report
    # =====================================================

    def report(self):

        return self.report_agent.execute(

            {
                "action":"report"
            }

        )



    # =====================================================
    # Complete Enterprise Pipeline
    # =====================================================

    def run(
            self,
            model_name=None,
            forecast_data=None
    ):


        return {


            "inventory":

                self.inventory(),



            "decision":

                self.decision(

                    model_name,

                    forecast_data

                ),



            "executive":

                self.dashboard(),



            "report":

                self.report()

        }





if __name__=="__main__":


    system = EnterpriseAIOrchestrator()



    sample={


        "Store":1,

        "Temperature":26.2,

        "Fuel_Price":3.18,

        "CPI":210.45,

        "Unemployment":7.2,

        "Holiday_Flag":0

    }



    result = system.run(

        model_name="best_sales_model.pkl",

        forecast_data=sample

    )


    print(result)



    print(
        "\n====== COPILOT ======\n"
    )


    print(

        system.copilot(

            "Explain major business risks"

        )

    )
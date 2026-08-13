"""
=========================================================

Enterprise AI Business Decision Intelligence Platform

Enterprise Orchestrator

Author : Feroz Ali

=========================================================
"""


from backend.orchestrator.planner import Planner

from backend.orchestrator.executor import Executor

from backend.orchestrator.response_builder import ResponseBuilder





class EnterpriseOrchestrator:



    def __init__(self):


        self.planner = Planner()


        self.executor = Executor()


        self.builder = ResponseBuilder()




    # =====================================================
    # Enterprise AI Chat
    # =====================================================

    def chat(
            self,
            question: str
    ):


        try:


            # Create execution plan

            plan = self.planner.create_plan(

                question

            )



            # Execute LangGraph

            result = self.executor.execute(

                plan,

                question

            )



            # Build final response

            response = self.builder.build(

                result

            )



            return {


                "question":

                question,


                "plan":

                plan,


                "result":

                response,


                "raw":

                result


            }



        except Exception as e:


            return {


                "status":

                "error",


                "message":

                str(e)

            }
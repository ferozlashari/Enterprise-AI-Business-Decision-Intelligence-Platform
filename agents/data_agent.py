"""
=========================================================
Enterprise AI Business Decision Intelligence Platform
Data Agent
Author : Feroz Ali
=========================================================
"""


from pathlib import Path

import pandas as pd

from agents.base_agent import BaseAgent

from config.settings import settings



class DataAgent(BaseAgent):


    def __init__(self):

        super().__init__("Data Agent")


        # Now controlled by settings.py
        self.data_dir = Path(
            settings.DATASET_DIR
        )



    # =====================================================
    # Load CSV
    # =====================================================

    def load_csv(self, filename):


        filepath = self.data_dir / filename



        if not filepath.exists():

            return {

                "status": "error",

                "message": f"{filename} not found",

                "path": str(filepath)

            }



        try:

            df = pd.read_csv(filepath)



            return {

                "status": "success",

                "rows": len(df),

                "columns": len(df.columns),

                "data": df

            }



        except Exception as e:


            return {

                "status": "error",

                "message": str(e)

            }



    # =====================================================
    # Dataset Summary
    # =====================================================

    def dataset_summary(self, df):


        return {


            "rows": len(df),


            "columns": len(df.columns),


            "features": list(df.columns),


            "missing_values":

                df.isnull().sum().to_dict(),



            "data_types":

                df.dtypes.astype(str).to_dict()

        }



    # =====================================================
    # Execute Task
    # =====================================================

    def execute(self, task):


        action = task.get("action")



        if action == "load":


            return self.load_csv(

                task["filename"]

            )



        elif action == "summary":



            result = self.load_csv(

                task["filename"]

            )



            if result["status"] == "success":


                return self.dataset_summary(

                    result["data"]

                )


            return result



        else:


            return {


                "status": "error",

                "message": "Unknown task"

            }





if __name__ == "__main__":


    agent = DataAgent()



    result = agent.execute(

        {

            "action": "summary",

            "filename": "superstore.csv"

        }

    )



    print(result)
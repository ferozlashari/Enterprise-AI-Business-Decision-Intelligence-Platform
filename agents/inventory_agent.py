"""
=========================================================
Enterprise AI Business Decision Intelligence Platform
Inventory Agent
Author : Feroz Ali
=========================================================
"""


from pathlib import Path

import pandas as pd


from agents.base_agent import BaseAgent

from config.settings import settings




class InventoryAgent(BaseAgent):


    def __init__(self):

        super().__init__("Inventory Agent")


        self.data_dir = Path(
            settings.DATASET_DIR
        )



    # =====================================================
    # Load Inventory Dataset
    # =====================================================

    def load_inventory(
            self,
            filename="inventory_dataset.csv"
    ):


        filepath = self.data_dir / filename



        if not filepath.exists():

            return None



        return pd.read_csv(filepath)




    # =====================================================
    # Inventory Summary
    # =====================================================

    def inventory_summary(self, df):


        return {


            "Total Products":

                len(df),



            "Total Stock":

                int(df["Stock"].sum()),



            "Average Stock":

                round(
                    float(df["Stock"].mean()),
                    2
                ),



            "Minimum Stock":

                int(df["Stock"].min()),



            "Maximum Stock":

                int(df["Stock"].max())

        }




    # =====================================================
    # Low Stock Products
    # =====================================================

    def low_stock_products(
            self,
            df,
            threshold=20
    ):


        low = df[

            df["Stock"] <= threshold

        ]


        return low.to_dict(

            orient="records"

        )





    # =====================================================
    # Overstock Products
    # =====================================================

    def overstock_products(
            self,
            df,
            threshold=500
    ):


        over = df[

            df["Stock"] >= threshold

        ]


        return over.to_dict(

            orient="records"

        )




    # =====================================================
    # Inventory Health
    # =====================================================

    def inventory_health(self, df):


        low = len(

            df[df["Stock"] <= 20]

        )


        over = len(

            df[df["Stock"] >= 500]

        )


        normal = len(df) - low - over



        return {


            "Healthy":

                normal,


            "Low Stock":

                low,


            "Over Stock":

                over

        }




    # =====================================================
    # AI Recommendations
    # =====================================================

    def recommendations(self, df):


        recommendations=[]



        low = self.low_stock_products(df)


        over = self.overstock_products(df)



        if low:


            recommendations.append(

                "Increase inventory for low stock products."

            )



        if over:


            recommendations.append(

                "Reduce purchasing for overstock products."

            )



        if not recommendations:


            recommendations.append(

                "Inventory levels are healthy."

            )


        return recommendations





    # =====================================================
    # Execute
    # =====================================================

    def execute(self, task):


        df = self.load_inventory()



        if df is None:


            return {


                "status":"error",

                "message":

                "Inventory dataset not found."

            }




        action = task.get("action")



        if action=="summary":


            return self.inventory_summary(df)



        elif action=="low_stock":


            return self.low_stock_products(df)



        elif action=="overstock":


            return self.overstock_products(df)



        elif action=="health":


            return self.inventory_health(df)



        elif action=="recommendation":


            return self.recommendations(df)




        return {


            "status":"error",

            "message":"Unknown task."

        }





if __name__=="__main__":


    agent = InventoryAgent()



    result = agent.execute(

        {

            "action":"summary"

        }

    )


    print(result)
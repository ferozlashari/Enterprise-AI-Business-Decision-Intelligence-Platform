"""
Enterprise AI Business Decision Intelligence Platform

Forecast Intelligence Agent

Author : Feroz Ali
"""


from pathlib import Path

import joblib

import pandas as pd


from agents.base_agent import BaseAgent

from config.settings import settings




class ForecastAgent(BaseAgent):


    def __init__(self):

        super().__init__(
            "Forecast Agent"
        )


        self.model_dir = Path(
            settings.MODEL_DIR
        )





    # =====================================================
    # Load Forecast Model
    # =====================================================

    def load_model(
            self,
            model_name
    ):


        try:


            model_path = (
                self.model_dir /
                model_name
            )


            if not model_path.exists():


                return None



            return joblib.load(
                model_path
            )



        except Exception:


            return None






    # =====================================================
    # Prophet Forecast
    # =====================================================

    def prophet_forecast(
            self,
            model,
            periods=12
    ):


        try:


            future = model.make_future_dataframe(

                periods=periods,

                freq="MS"

            )



            forecast = model.predict(

                future

            )



            result = forecast[

                [

                    "ds",

                    "yhat"

                ]

            ].tail(periods)



            return {


                "status":

                    "success",



                "type":

                    "prophet",



                "model":

                    "Facebook Prophet",



                "forecast":

                    result.to_dict(

                        orient="records"

                    )

            }



        except Exception as e:



            return {


                "status":

                    "error",



                "message":

                    str(e)

            }








    # =====================================================
    # Machine Learning Prediction
    # =====================================================

    def ml_prediction(
            self,
            model,
            data
    ):


        try:



            if isinstance(data, dict):


                data = pd.DataFrame(

                    [

                        data

                    ]

                )



            prediction = model.predict(

                data

            )



            value = float(

                prediction[0]

            )



            return {


                "status":

                    "success",



                "type":

                    "machine_learning",



                "model":

                    "best_sales_model.pkl",



                "prediction":

                    value,



                "predicted_sales":

                    value

            }




        except Exception as e:



            return {


                "status":

                    "error",



                "message":

                    str(e)

            }







    # =====================================================
    # Main Forecast
    # =====================================================

    def forecast(
            self,
            model_name,
            input_data=None
    ):



        model = self.load_model(

            model_name

        )



        if model is None:


            return {


                "status":

                    "error",



                "message":

                    f"Model {model_name} not found"

            }






        # Prophet Model

        if hasattr(

            model,

            "make_future_dataframe"

        ):


            return self.prophet_forecast(

                model

            )






        # Machine Learning Model

        return self.ml_prediction(

            model,

            input_data or {}

        )







    # =====================================================
    # Health Check
    # =====================================================

    def health(self):


        return {


            "agent":

                "Forecast Agent",



            "model_directory":

                str(

                    self.model_dir

                ),



            "status":

                "healthy"

        }








    # =====================================================
    # Execute Interface
    # =====================================================

    def execute(
            self,
            task
    ):



        action = task.get(

            "action"

        )




        if action == "forecast":


            return self.forecast(

                task.get(

                    "model",

                    "best_sales_model.pkl"

                ),


                task.get(

                    "data",

                    {}

                )

            )





        elif action == "health":


            return self.health()





        return {


            "status":

                "error",



            "message":

                "Unknown forecast action"

        }







# =====================================================
# Test
# =====================================================

if __name__ == "__main__":


    agent = ForecastAgent()



    result = agent.execute(

        {


            "action":

                "forecast",



            "model":

                "best_sales_model.pkl",



            "data":

                {


                    "Store":

                        1,


                    "Temperature":

                        26.5,


                    "Fuel_Price":

                        3.15,


                    "CPI":

                        211.45,


                    "Unemployment":

                        7.1,


                    "Holiday_Flag":

                        0

                }

        }

    )



    print(result)
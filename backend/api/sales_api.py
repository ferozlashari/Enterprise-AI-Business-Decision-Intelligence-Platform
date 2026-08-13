"""
=========================================================

Enterprise AI Business Decision Intelligence Platform

Sales Intelligence API

Author : Feroz Ali

=========================================================
"""


from fastapi import APIRouter, HTTPException

from backend.services.prediction_service import PredictionService



router = APIRouter(

    prefix="/sales",

    tags=[
        "Sales Intelligence"
    ]

)



# Service Instance

service = PredictionService()



# =====================================================
# SALES DASHBOARD
# =====================================================


@router.get("/")
def sales_dashboard():

    try:

        result = service.get_sales_prediction()


        return {


            "success": True,


            "total_sales":

                result.get(

                    "total_sales",

                    result.get(

                        "Revenue",

                        0

                    )

                ),



            "profit":

                result.get(

                    "profit",

                    result.get(

                        "Profit",

                        0

                    )

                ),



            "growth":

                result.get(

                    "growth",

                    result.get(

                        "Growth",

                        0

                    )

                ),



            "predicted_sales":

                result.get(

                    "predicted_sales",

                    result.get(

                        "prediction",

                        0

                    )

                ),



            "model":

                result.get(

                    "model",

                    "XGBoost"

                ),



            "sales_trend":

                result.get(

                    "sales_trend",

                    result.get(

                        "Sales Trend",

                        []

                    )

                ),



            "category_sales":

                result.get(

                    "category_sales",

                    result.get(

                        "Category Sales",

                        []

                    )

                ),



            "region_sales":

                result.get(

                    "region_sales",

                    result.get(

                        "Region Sales",

                        []

                    )

                )


        }



    except Exception as e:


        raise HTTPException(

            status_code=500,

            detail=str(e)

        )





# =====================================================
# SALES PREDICTION
# =====================================================


@router.get("/predict")
def sales_prediction():

    try:


        result = service.get_sales_prediction()



        return {


            "success": True,


            "predicted_sales":

                result.get(

                    "predicted_sales",

                    result.get(

                        "prediction",

                        0

                    )

                ),



            "model":

                result.get(

                    "model",

                    "XGBoost"

                )


        }



    except Exception as e:


        raise HTTPException(

            status_code=500,

            detail=str(e)

        )





# =====================================================
# FEATURE IMPORTANCE
# =====================================================


@router.get("/feature-importance")
def feature_importance():

    try:


        result = service.get_feature_importance()



        return {


            "success": True,


            "features": result


        }



    except Exception as e:


        raise HTTPException(

            status_code=500,

            detail=str(e)

        )





# =====================================================
# SALES REPORT
# =====================================================


@router.get("/report")
def sales_report():

    try:


        result = service.get_sales_prediction()



        return {


            "success": True,


            "report": {


                "total_sales":

                    result.get(

                        "total_sales",

                        result.get(

                            "Revenue",

                            0

                        )

                    ),



                "profit":

                    result.get(

                        "profit",

                        result.get(

                            "Profit",

                            0

                        )

                    ),



                "average_sales":

                    result.get(

                        "average_sales",

                        0

                    ),



                "best_category":

                    result.get(

                        "best_category",

                        "N/A"

                    ),



                "predicted_sales":

                    result.get(

                        "predicted_sales",

                        result.get(

                            "prediction",

                            0

                        )

                    ),



                "model":

                    result.get(

                        "model",

                        "XGBoost"

                    ),



                "sales_trend":

                    result.get(

                        "sales_trend",

                        result.get(

                            "Sales Trend",

                            []

                        )

                    ),



                "category_sales":

                    result.get(

                        "category_sales",

                        result.get(

                            "Category Sales",

                            []

                        )

                    ),



                "region_sales":

                    result.get(

                        "region_sales",

                        result.get(

                            "Region Sales",

                            []

                        )

                    )


            }


        }



    except Exception as e:


        raise HTTPException(

            status_code=500,

            detail=str(e)

        )





# =====================================================
# SALES ANALYSIS
# =====================================================


@router.get("/analysis")
def sales_analysis():

    try:


        result = service.get_sales_prediction()



        return {


            "success": True,


            "analysis": result


        }



    except Exception as e:


        raise HTTPException(

            status_code=500,

            detail=str(e)

        )





# =====================================================
# HEALTH CHECK
# =====================================================


@router.get("/health")
def health():

    return {


        "status":

            "Healthy",



        "service":

            "Sales Intelligence API"


    }
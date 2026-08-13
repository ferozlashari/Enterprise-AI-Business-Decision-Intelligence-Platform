"""
=========================================================

Enterprise AI Business Decision Intelligence Platform

Inventory Prediction API

Author : Feroz Ali

=========================================================
"""


from fastapi import (
    APIRouter,
    HTTPException
)


from backend.services.prediction_service import (
    PredictionService
)



router = APIRouter(

    prefix="/inventory",

    tags=["Inventory Prediction"]

)




# =====================================================
# Inventory API Home
# =====================================================

@router.get("/")
def home():


    return {


        "module":

        "Inventory Prediction API",


        "status":

        "Running"

    }




# =====================================================
# Inventory Prediction
# =====================================================

@router.get("/predict")
def inventory_prediction():


    try:


        result = (

            PredictionService

            .get_inventory_prediction()

        )



        return {


            "success":

            True,


            "inventory_prediction":

            result

        }



    except Exception as e:


        raise HTTPException(

            status_code=500,

            detail=str(e)

        )





# =====================================================
# Complete Inventory Intelligence
# =====================================================

@router.get("/all")
def inventory_all():


    try:


        result = (

            PredictionService

            .get_inventory_prediction()

        )



        return {


            "success":

            True,


            "module":

            "Inventory Intelligence",



            "result":

            result

        }



    except Exception as e:


        raise HTTPException(

            status_code=500,

            detail=str(e)

        )





# =====================================================
# Inventory Health
# =====================================================

@router.get("/health")
def health():


    return {


        "status":

        "Healthy",


        "service":

        "Inventory Prediction"

    }
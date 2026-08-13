"""
=========================================================

Enterprise AI Business Decision Intelligence Platform

Customer Intelligence API

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

    prefix="/customer",

    tags=["Customer Intelligence"]

)




# =====================================================
# Customer Home
# =====================================================

@router.get("/")
def customer_home():


    return {


        "message":

        "Customer Intelligence API Running",


        "module":

        "Customer Analytics"

    }





# =====================================================
# Customer Summary
# =====================================================

@router.get("/summary")
def customer_summary():


    try:


        result = (

            PredictionService

            .get_customer_segments()

        )


        return {


            "success":

            True,


            "customer_summary":

            result

        }



    except Exception as e:


        raise HTTPException(

            status_code=500,

            detail=str(e)

        )





# =====================================================
# Customer Segmentation
# =====================================================

@router.get("/segments")
def customer_segments():


    try:


        result = (

            PredictionService

            .get_customer_segments()

        )


        return {


            "success":

            True,


            "segments":

            result

        }



    except Exception as e:


        raise HTTPException(

            status_code=500,

            detail=str(e)

        )





# =====================================================
# Customer Analysis
# =====================================================

@router.get("/analysis")
def customer_analysis():


    try:


        result = (

            PredictionService

            .get_customer_segments()

        )


        return {


            "success":

            True,


            "customer_analysis":

            result

        }



    except Exception as e:


        raise HTTPException(

            status_code=500,

            detail=str(e)

        )





# =====================================================
# Customer Statistics
# =====================================================

@router.get("/stats")
def customer_stats():


    try:


        data = (

            PredictionService

            .get_customer_segments()

        )



        return {


            "success":

            True,


            "statistics":

            {


                "total_customers":

                data.get(

                    "total_customers",

                    0

                ),



                "segments":

                data.get(

                    "segments",

                    data.get(

                        "clusters",

                        {}

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
# Complete Customer Intelligence
# =====================================================

@router.get("/all")
def customer_all():


    try:


        segmentation = (

            PredictionService

            .get_customer_segments()

        )


        return {


            "success":

            True,


            "module":

            "Customer Intelligence",



            "segmentation":

            segmentation

        }



    except Exception as e:


        raise HTTPException(

            status_code=500,

            detail=str(e)

        )





# =====================================================
# Health
# =====================================================

@router.get("/health")
def customer_health():


    return {


        "status":

        "Healthy",


        "service":

        "Customer Intelligence"

    }
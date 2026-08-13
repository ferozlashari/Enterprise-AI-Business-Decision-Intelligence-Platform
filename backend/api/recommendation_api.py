"""
=========================================================

Enterprise AI Business Decision Intelligence Platform

Recommendation API

Author : Feroz Ali

=========================================================
"""


from fastapi import (
    APIRouter,
    HTTPException
)


from backend.services.recommendation_service import (
    RecommendationService
)



router = APIRouter(

    prefix="/recommendation",

    tags=["Recommendation"]

)



service = RecommendationService()




# =====================================================
# Recommendation Home
# =====================================================

@router.get("/")
def recommendation_home():


    return {


        "module":

        "AI Recommendation Engine",


        "status":

        "Running"

    }





# =====================================================
# Generate Recommendations
# =====================================================

@router.get("/generate")
def get_recommendations():


    try:


        result = (

            service

            .get_recommendations()

        )


        return {


            "success":

            True,


            "recommendations":

            result

        }



    except Exception as e:


        raise HTTPException(

            status_code=500,

            detail=str(e)

        )





# =====================================================
# All Recommendations
# =====================================================

@router.get("/all")
def all_recommendations():


    try:


        result = (

            service

            .get_recommendations()

        )


        return {


            "success":

            True,


            "module":

            "Business Recommendation Intelligence",



            "data":

            result

        }



    except Exception as e:


        raise HTTPException(

            status_code=500,

            detail=str(e)

        )





# =====================================================
# Health Check
# =====================================================

@router.get("/health")
def recommendation_health():


    return {


        "status":

        "Healthy",


        "service":

        "RecommendationService"

    }
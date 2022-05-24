# 3rd-party
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status

# Project
from skarbonka.serializers import LoanSampleSerializer

loan_schema = swagger_auto_schema(
    responses={
        status.HTTP_200_OK: openapi.Response(
            description="",
            schema=LoanSampleSerializer,
        )
    }
)

withdraw_post_schema = swagger_auto_schema(
    responses={
        status.HTTP_202_ACCEPTED: openapi.Response(
            description="",
            examples={"application/json": {"message": "Transaction must be accepted by parent."}},
        ),
        status.HTTP_400_BAD_REQUEST: openapi.Response(
            description="",
            examples={"application/json": {"message": "Exceeded the allowable limit!"}},
        ),
        status.HTTP_201_CREATED: openapi.Response(
            description="", examples={"application/json": {"amount": 30.50}}
        ),
    }
)

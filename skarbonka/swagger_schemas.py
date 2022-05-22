# 3rd-party
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status

# Project
from skarbonka.serializers import LoanSampleSerializer

loan_schema = swagger_auto_schema(
    responses={
        status.HTTP_200_OK: openapi.Response(
            description="response description",
            schema=LoanSampleSerializer,
        )
    }
)

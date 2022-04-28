# Standard Library
import datetime

# 3rd-party
from rest_framework import status
from rest_framework.response import Response

# Project
from accounts.models import ControlType
from skarbonka.enum import TransactionStatus


def period_limit_check(user):
    """If user exceeded the allowable limit return False and Response otherwise just True"""
    if user.parental_control == ControlType.PERIODIC:
        period = datetime.datetime.now() - datetime.timedelta(days=user.days_limit_period)
        limit = user.sum_periodic_limit
        if user.outcome(period) >= limit:
            return True, Response(
                {"message": "Exceeded the allowable limit!"}, status.HTTP_400_BAD_REQUEST
            )
    return False, None

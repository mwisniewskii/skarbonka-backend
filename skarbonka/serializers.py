# 3rd-party
from rest_framework import serializers

# Local
from .models import Allowance
from .models import Loan
from .models import Notification


class AllowanceSerializer(serializers.ModelSerializer):
    """Allowance for a child serializer."""

    class Meta:
        model = Allowance

        fields = (
            'id',
            'child',
            'amount',
            'frequency',
            'execute_time',
            'day_of_month',
            'day_of_week',
        )
        read_only_fields = ('id',)


class NotificationSerializer(serializers.ModelSerializer):
    """Allowance for a child serializer."""

    class Meta:
        model = Notification

        fields = (
            'content',
            'created_at',
            'resource',
            'target',
        )


class LoanChildSerializer(serializers.ModelSerializer):

    class Meta:
        model = Loan

        fields = (
            'id',
            'reason',
            'lender',
            'amount',
            'status',
            'payment_date',
            'created_at',
        )
        read_only_fields = ('id', 'created_at', 'payment_date', 'status')


class LoanParentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Loan

        fields = (
            'id',
            'reason',
            'borrower',
            'amount',
            'status',
            'payment_date',
            'created_at',
        )
        read_only_fields = ('id', 'created_at', 'amount', 'reason', 'borrower')


class LoanSampleSerializer(serializers.Serializer):
    child = LoanChildSerializer(many=True)
    parent = LoanParentSerializer(many=True)

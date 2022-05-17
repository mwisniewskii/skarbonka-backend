# 3rd-party
from rest_framework import serializers

# Local
from .models import Allowance
from .models import Loan
from .models import Notification
from .models import Transaction


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
            'url',
        )


class DepositSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ("amount",)


class LoanPayoffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ('amount',)


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
            'paid',
        )
        read_only_fields = ('id', 'created_at', 'payment_date', 'status', 'paid')


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
            'paid',
        )
        read_only_fields = ('id', 'created_at', 'amount', 'reason', 'borrower', 'paid')


class LoanSampleSerializer(serializers.Serializer):
    child = LoanChildSerializer(many=True)
    parent = LoanParentSerializer(many=True)


class CreateWithdrawSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ('amount',)


class WithdrawSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction

        fields = (
            'amount',
            'sender',
            'datetime',
            'state',
        )
        read_only_fields = (
            'amount',
            'sender',
            'datetime',
        )

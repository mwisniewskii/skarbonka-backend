# 3rd-party
from rest_framework import serializers

# Local
from .models import Allowance
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
            'resource',
            'target',
        )


class TransactionSerializer(serializers.ModelSerializer):
    """Transaction between users serializer"""

    class Meta:
        model = Transaction

        fields = (
            'recipient',
            'title',
            'description',
            'amount',
        )

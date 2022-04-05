from rest_framework import serializers

from .models import Allowance
from .models import Notifications


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
        model = Notifications

        fields = (
            'content',
            'created_at',
            'resource',
            'target',
        )

from rest_framework import serializers

from .models import Allowance


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


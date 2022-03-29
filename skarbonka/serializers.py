from rest_framework import serializers

from .models import Transaction


class DepositSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ("amount",)

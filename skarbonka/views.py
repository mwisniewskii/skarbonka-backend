# 3rd-party

from venv import create

from rest_framework import viewsets
from rest_framework.generics import get_object_or_404

# Local
from .models import Transaction, TransactionType
from .permissions import UserPermitions
from .serializers import DepositSerializer


class DepositViewSet(viewsets.ModelViewSet):

    serializer_class = DepositSerializer
    permission_classes = (UserPermitions,)

    def perform_create(self, serializer):
        serializer.save(
            recipient=self.request.user, title='deposit', types=TransactionType.DEPOSIT
        )

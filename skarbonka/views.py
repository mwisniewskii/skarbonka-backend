# 3rd-party

from rest_framework import viewsets
from rest_framework.generics import get_object_or_404

# Local
from .models import Transaction, TransactionType
from .permissions import AuthenticatedPermissions
from .serializers import DepositSerializer


class DepositViewSet(viewsets.ModelViewSet):

    serializer_class = DepositSerializer
    permission_classes = (AuthenticatedPermissions,)

    def perform_create(self, serializer):
        serializer.save(
            recipient=self.request.user, title='deposit', types=TransactionType.DEPOSIT
        )

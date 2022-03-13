from rest_framework import viewsets
from rest_framework.generics import get_object_or_404

from .models import CustomUser
from .permissions import HeadOfFamily
from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = (HeadOfFamily,)

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return CustomUser.objects.all()
        return CustomUser.objects.filter(family=user.family)

    def get_object(self):
        obj = get_object_or_404(CustomUser.objects.filter(id=self.kwargs["pk"]))
        self.check_object_permissions(self.request, obj)
        return obj

    def perform_create(self, serializer):
        serializer.save(family=self.request.user.family)


        
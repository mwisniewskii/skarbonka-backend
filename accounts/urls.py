# Django
from django.conf.urls import url
from django.urls import path
from django.views.generic import TemplateView

# Local
from .views import UserViewSet

userList = UserViewSet.as_view(
    {
        "get": "list",
        "post": "create",
    }
)

userDetail = UserViewSet.as_view(
    {
        "get": "retrieve",
        "put": "update",
        "delete": "destroy",
    }
)


urlpatterns = [
    path("users/", userList, name="users"),
    path("users/<int:pk>/", userDetail, name="user"),
    url(
        r'^account-confirm-email/(?P<key>[-:\w]+)/$',
        TemplateView.as_view(),
        name='account_confirm_email',
    ),
    path(
        "confirmResetPassword/<uidb64>/<token>/",
        TemplateView.as_view(),
        name="password_reset_confirm",
    ),
]

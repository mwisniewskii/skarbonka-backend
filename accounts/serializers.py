# Django
from django.conf import settings

# 3rd-party
from allauth.account import app_settings as allauth_settings
from allauth.account.adapter import get_adapter
from allauth.account.forms import default_token_generator
from allauth.account.utils import setup_user_email
from dj_rest_auth.forms import AllAuthPasswordResetForm
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer
from rest_framework import serializers
from rest_framework.authtoken.admin import User

# Local
from .models import CustomUser
from .models import Family


class CustomRegisterSerializer(RegisterSerializer):
    """Use default serializer except don't user username."""

    username = None
    email = serializers.EmailField(required=allauth_settings.EMAIL_REQUIRED)

    first_name = serializers.CharField(required=True, write_only=True)
    last_name = serializers.CharField(required=True, write_only=True)
    password1 = serializers.CharField(required=True, write_only=True)
    password2 = serializers.CharField(required=True, write_only=True)

    def get_cleaned_data(self):  # noqa: D102
        return {
            "first_name": self.validated_data.get("first_name", ""),
            "last_name": self.validated_data.get("last_name", ""),
            "password1": self.validated_data.get("password1", ""),
            "email": self.validated_data.get("email", ""),
        }

    def save(self, request):  # noqa: D102
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        family = Family.objects.create()
        user.family = family
        adapter.save_user(request, user, self)
        setup_user_email(request, user, [])
        family.save()
        user.save()
        return user


class CustomLoginSerializer(LoginSerializer):
    """Use default serializer except don't user username."""

    username = None


class UserSerializer(serializers.ModelSerializer):
    """Family resources serializer."""

    class Meta:  # noqa: D106
        model = CustomUser
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "user_type",
            "parental_control",
            "balance",
        )
        read_only_fields = ("id", "balance")

    def password_reset(self, request):
        """Send email with password reset."""
        opts = {
            "use_https": request.is_secure(),
            "from_email": getattr(settings, "DEFAULT_FROM_EMAIL"),
            "request": request,
            "token_generator": default_token_generator,
        }
        reset_form = AllAuthPasswordResetForm(data=self.initial_data)
        if not reset_form.is_valid():
            raise serializers.ValidationError(reset_form.errors)
        reset_form.save(**opts)

    def create(self, validated_data):
        request = self.context.get("request")
        password = User.objects.make_random_password(64)
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        email = setup_user_email(request, user, [])
        email.verified = True
        email.save()
        self.password_reset(request)
        return user

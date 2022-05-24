# 3rd-party
import factory
from dj_rest_auth.utils import jwt_encode
from django.http import SimpleCookie

from project import settings


def jwt_cookie(user):
    token, _ = jwt_encode(user)
    cookies = {settings.JWT_AUTH_COOKIE: token}
    return SimpleCookie(cookies)


class FamilyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'accounts.Family'


class UserFactory(factory.django.DjangoModelFactory):

    email = factory.Faker("email")
    family = factory.SubFactory(FamilyFactory)
    user_type = 1
    parental_control = 1
    first_name = factory.Faker("name")
    last_name = factory.Faker("name")

    class Meta:
        model = 'accounts.CustomUser'

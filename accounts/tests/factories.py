# 3rd-party
import factory


class FamilyFactory(factory.django.DjangoModelFactory):

    name = factory.Faker("name")

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

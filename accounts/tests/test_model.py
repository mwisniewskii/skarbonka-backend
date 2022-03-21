from django.test import TestCase

from accounts.models import CustomUser


class CustomUserTest(TestCase):
    def setUp(self) -> None:
        self.user = CustomUser(
            1,
        )

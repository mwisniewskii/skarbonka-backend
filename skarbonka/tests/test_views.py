# 3rd-party
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

# Project
from accounts.tests.factories import UserFactory


class AllowanceTest(APITestCase):
    def setUp(self):
        self.parent = UserFactory()
        self.child = UserFactory(family=self.parent.family)
        self.client = APIClient()
        self.client.force_authenticate(self.child)


class NotificationTest(APITestCase):
    pass


class DepositTest(APITestCase):
    pass


class LoanTest(APITestCase):
    pass


class WithdrawTest(APITestCase):
    pass

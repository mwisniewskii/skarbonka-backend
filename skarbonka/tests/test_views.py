# 3rd-party
from dj_rest_auth.utils import jwt_encode
from django.http import SimpleCookie
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

# Project
from accounts.tests.factories import UserFactory
from accounts.enum import ControlType
from project import settings
from skarbonka.enum import TransactionState
from skarbonka.models import Transaction


class AllowanceTest(APITestCase):
    def setUp(self):
        self.parent = UserFactory()
        self.child = UserFactory(family=self.parent.family)
        self.client = APIClient()
        self.client.force_authenticate(self.child)


class NotificationTest(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_notification_get(self):
        pass


class LoanTest(APITestCase):
    def setUp(self):
        pass

    def test_loan(self):
        pass


class DepositTest(APITestCase):

    def setUp(self):
        self.child = UserFactory()
        self.client = APIClient()
        token, _ = jwt_encode(self.child)
        cookies = {settings.JWT_AUTH_COOKIE: token}
        self.client.cookies = SimpleCookie(cookies)
        self.url = reverse('deposits')

    def test_deposit(self):
        response = self.client.post(self.url, {'amount': 10.0})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(self.url, {'amount': -10.0})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)



class WithdrawCreateTest(APITestCase):

    def setUp(self):
        self.parent = UserFactory()
        self.child = UserFactory(family=self.parent.family)
        self.client = APIClient()
        token, _ = jwt_encode(self.child)
        cookies = {settings.JWT_AUTH_COOKIE: token}
        self.client.cookies = SimpleCookie(cookies)
        self.url = reverse('withdraw')
        Transaction.objects.create(recipient=self.child, amount=1000, title='', state=TransactionState.ACCEPTED)

    def test_withdraw_without_parental_control(self):
        self.assertEqual(1000, self.child.balance)
        response = self.client.post(self.url, {'amount': 10.0})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(self.url, {'amount': -10.0})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_withdraw_with_periodic_limit(self):
        self.child.parental_control = ControlType.PERIODIC
        self.child.sum_periodic_limit = 100
        self.child.days_limit_period = 1
        self.child.save()
        response = self.client.post(self.url, {'amount': 50.0})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(self.url, {'amount': 100.0})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_withdraw_with_confirmation_control(self):
        self.child.parental_control = ControlType.CONFIRMATION
        self.child.save()
        response = self.client.post(self.url, {'amount': 10.0})
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)




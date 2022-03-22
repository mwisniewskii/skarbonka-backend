from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase

from accounts.tests.factories import UserFactory


class UsersCollectionTest(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_get(self):
        url = reverse('users')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.logout()
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post(self):
        url = reverse('users')
        data = {
            'first_name': 'Imie',
            'last_name': 'Nazwisko',
            'user_type': '1',
            'parental_control': '1',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data['email'] = 'test@mail.com'
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class UsersDetailTest(APITestCase):
    def setUp(self):
        self.user1 = UserFactory()
        self.user2 = UserFactory()
        self.user3 = UserFactory(family=self.user1.family)
        self.client = APIClient()
        self.client.force_authenticate(self.user1)

    def test_get(self):
        url1 = reverse('user', args=(self.user1.pk,))
        url2 = reverse('user', args=(self.user2.pk,))
        response = self.client.get(url1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.logout()
        response = self.client.get(url2)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch(self):
        url = reverse('user', args=(self.user3.pk,))
        data = {
            "id": self.user3.pk,
            "email": self.user3.email,
            "first_name": "Jurek",
            "last_name": "Sznurek",
            "user_type": 1,
            "parental_control": 1,
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.force_authenticate(self.user2)
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete(self):
        url = reverse('user', args=(self.user2.pk,))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        url = reverse('user', args=(self.user3.pk,))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

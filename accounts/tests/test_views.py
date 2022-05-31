# 3rd-party
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

# Project
from accounts.tests.factories import UserFactory
from accounts.tests.factories import jwt_cookie


class UsersCollectionTest(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client = APIClient()
        self.client.cookies = jwt_cookie(self.user)

    def test_get_list_of_family_members(self):
        url = reverse('users')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.logout()
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_family_member(self):
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
        self.client.cookies = jwt_cookie(self.user1)

    def test_get_family_member_by_family_member(self):
        url = reverse('user', args=(self.user1.pk,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_family_member_by_stranger(self):
        url = reverse('user', args=(self.user2.pk,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_family_list_by_unauthorized(self):
        url = reverse('user', args=(self.user1.pk,))
        self.client.logout()
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_family_member_name(self):
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
        self.client.cookies = jwt_cookie(self.user2)

        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_id_family_member(self):
        url = reverse('user', args=(self.user3.pk,))
        user_pk = self.user3.pk
        data = {
            "id": 9999,
            "email": self.user3.email,
            "first_name": "Jurek",
            "last_name": "Sznurek",
            "user_type": 1,
            "parental_control": 1,
        }
        response = self.client.put(url, data)
        self.assertEqual(self.user3.pk, user_pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_family_member(self):
        url = reverse('user', args=(self.user3.pk,))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_family_member_by_stranger(self):
        url = reverse('user', args=(self.user2.pk,))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

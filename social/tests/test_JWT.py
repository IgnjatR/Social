import json

from django.urls import reverse
from rest_framework.test import APITestCase, APIClient

from ..models import Account


class TestJWTToken(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url_obtain = reverse('token_obtain_pair')
        self.url_refresh = reverse('token_refresh')
        self.url_verify = reverse('token_verify')
        self.user = Account.objects.create_user(username='test_user', email='testmail@gmail.com',
                                                password='test_password')
        self.data = {'username': 'test_user', 'password': 'test_password'}

    def test_obtain_token(self):
        response = self.client.post(self.url_obtain, data=self.data)

        self.assertEquals(response.status_code, 200)

    def test_refresh_token(self):
        data = {'refresh': json.loads(self.client.post(self.url_obtain, data=self.data).content)['refresh']}
        response = self.client.post(self.url_refresh, data=data)
        self.assertEquals(response.status_code, 200)

    def test_verify_token(self):
        data = {'token': json.loads(self.client.post(self.url_obtain, data=self.data).content)['access']}
        response = self.client.post(self.url_verify, data=data)
        self.assertEquals(response.status_code, 200)

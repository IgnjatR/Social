from django.urls import reverse
from rest_framework.test import APITestCase, APIClient

from ..models import Account


class TestAccountListViewSet(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('accounts-list')
        self.data = {'username': 'test_user', 'password': 'test_password', 'email': 'testmail@gmail.com'}

    def test_account_list_view_set_GET(self):
        response = self.client.get(self.url)
        self.assertAlmostEquals(response.status_code, 200)

    def test_account_list_view_set_POST_valid_data(self):
        response = self.client.post(self.url + '?bot=True', data=self.data, format='json')

        self.assertEquals(response.status_code, 201)

    def test_account_list_view_set_POST_fake_email(self):
        data = self.data.copy()
        data['email'] = 'testmail@gmadsdkil.com'
        response = self.client.post(self.url, data=data, format='json')

        self.assertEquals(response.status_code, 400)

    def test_account_list_view_set_POST_user_already_exists(self):
        Account.objects.create_user(username='test_user', email='testmail@gmail.com', password='test_password')
        response = self.client.post(self.url, data=self.data, format='json')
        self.assertEquals(response.status_code, 400)

from rest_framework.test import APITestCase, APIClient

from ..models import Account


class TestSessionLogIn(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.data = {'username': 'test_user', 'password': 'test_password'}
        self.user = Account.objects.create_user(username='test_user', email='testmail@gmail.com',
                                                password='test_password')

    def test_log_in_valid_data(self):
        response = self.client.login(username='test_user', password='test_password')
        self.assertEquals(response, True)

    def test_log_in_invalid_data(self):
        response = self.client.login(username='wrong username', password='test_password')
        self.assertEquals(response, False)

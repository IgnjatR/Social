from django.urls import reverse
from rest_framework.test import APITestCase, APIClient


class TestLikeListViewSet(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('likes-list')

    def test_like_list_view_set_GET(self):
        response = self.client.get(self.url)
        self.assertAlmostEquals(response.status_code, 200)

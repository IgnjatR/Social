import json

from django.urls import reverse
from rest_framework.test import APITestCase, APIClient

from ..models import Post, Account, Like


class TestPostListViewSet(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url_obtain = reverse('token_obtain_pair')

        self.url = reverse('posts-list')
        self.user = Account.objects.create_user(username='test_user', email='testmail@gmail.com',
                                                password='test_password')
        self.second_user = Account.objects.create_user(username='second test_user', email='testmail@gmail.com',
                                                       password='test_password')
        self.data = {'post_title': 'random title', 'post_content': 'random content'}

    def test_post_list_view_set_GET(self):
        response = self.client.get(self.url)
        self.assertAlmostEquals(response.status_code, 200)

    def test_post_list_view_set_POST_session_auth(self):
        self.client.login(username='test_user', password='test_password')

        response = self.client.post(self.url, data=self.data, format='json')
        self.assertEquals(response.status_code, 201)

    def test_post_list_view_set_POST_did_not_logged_in(self):
        response = self.client.post(self.url, data=self.data, format='json')
        self.assertEquals(response.status_code, 403)

    def test_post_list_view_set_POST_JWT_auth_valid_token(self):
        data = 'Bearer ' + json.loads(
            self.client.post(self.url_obtain, data={'username': 'test_user', 'password': 'test_password'}).content)[
            'access']
        header = {'HTTP_AUTHORIZATION': data}
        response = self.client.post(self.url, self.data, 'json', **header)
        self.assertAlmostEquals(response.status_code, 201)

    def test_post_list_view_set_POST_JWT_auth_invalid_token(self):
        data = 'Bearer ' + 'invalid token'
        header = {'HTTP_AUTHORIZATION': data}
        response = self.client.post(self.url, self.data, 'json', **header)
        self.assertAlmostEquals(response.status_code, 403)

    def test_post_list_view_set_POST_same_title(self):
        self.client.login(username='test_user', password='test_password')
        Post.objects.create(post_title='random title', post_content='Different content', author=self.user)

        response = self.client.post(self.url, data=self.data, format='json')
        self.assertEquals(response.status_code, 400)

    def test_like_post_that_has_not_been_liked(self):
        post = Post.objects.create(post_title='random title', post_content='Different content', author=self.second_user)

        self.client.login(username='test_user', password='test_password')
        response = self.client.get(self.url + str(post.pk) + '/like_post/')

        self.assertEquals(response.status_code, 201)

    def test_like_post_that_has_been_liked(self):
        post = Post.objects.create(post_title='random title', post_content='Different content', author=self.second_user)
        Like.objects.create(related_post=post, related_user=self.user)
        self.client.login(username='test_user', password='test_password')
        response = self.client.get(self.url + str(post.pk) + '/like_post/')

        self.assertEquals(response.status_code, 405)

    def test_like_your_own_post(self):
        post = Post.objects.create(post_title='random title', post_content='Different content',
                                   author=self.user)
        self.client.login(username='test_user', password='test_password')
        response = self.client.get(self.url + str(post.pk) + '/like_post/')

        self.assertEquals(response.status_code, 405)

    def test_unlike_post_that_has_been_liked(self):
        post = Post.objects.create(post_title='random title', post_content='Different content', author=self.second_user)
        Like.objects.create(related_post=post, related_user=self.user)

        self.client.login(username='test_user', password='test_password')
        response = self.client.get(self.url + str(post.pk) + '/unlike_post/')

        self.assertEquals(response.status_code, 201)

    def test_unlike_post_that_has_not_been_liked(self):
        post = Post.objects.create(post_title='random title', post_content='Different content', author=self.second_user)
        self.client.login(username='test_user', password='test_password')
        response = self.client.get(self.url + str(post.pk) + '/unlike_post/')

        self.assertEquals(response.status_code, 405)

    def test_unlike_your_own_post(self):
        post = Post.objects.create(post_title='random title', post_content='Different content',
                                   author=self.user)
        self.client.login(username='test_user', password='test_password')
        response = self.client.get(self.url + str(post.pk) + '/unlike_post/')

        self.assertEquals(response.status_code, 405)

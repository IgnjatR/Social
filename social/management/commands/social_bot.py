import json
import os
import random

import requests
from django.core.management import BaseCommand
from faker import Factory


class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.posts = []
        self.likes = 0
        self.token = ''


class Post:
    def __init__(self, title, content, user, link):
        self.user = user
        self.title = title
        self.content = content
        self.likes_number = 0
        self.like_link = link

    def __str__(self):
        return self.title


class Command(BaseCommand):
    """All functions for automated bot"""

    sign_up_url = 'http://localhost:8000/api/accounts/?bot=True'
    log_in_url = 'http://localhost:8000/api/token'
    faker = Factory.create()
    created_users = []

    def sign_up_all(self):
        """Sign up number of users, given in bot_config.json file"""

        i = 0
        session = requests.Session()

        while i < self.number_of_users:
            self.sign_up(session)
            i += 1
        session.close()

    def sign_up(self, session):
        """Sign up individual users"""

        while True:

            data = self.get_credentials()
            response = session.post(self.sign_up_url, data=data)
            if response.status_code == 201:
                self.created_users.append(User(data['username'], data['password']))
                break

    def log_in(self):
        """Log in all users, using users from sign_up_all method"""

        session = requests.Session()
        for user in self.created_users:
            self.get_new_token(user, session)
        session.close()

    def get_new_token(self, user, session):
        """For given user, generates JSON Web Token (JWT), and assigns it to user.token"""

        while True:
            response = session.post('http://localhost:8000/api/token',
                                    data={'username': user.username, 'password': user.password})
            if response.status_code == 200:
                user.token = json.loads(response.content)['access']
                break

    def create_all_posts(self):
        """For all created users, creates random number of posts, in range from 1 to  max_posts_per_user,
         given in bot_config.json file """

        session = requests.Session()
        for user in self.created_users:
            self.create_post(user, session)
        session.close()

    def create_post(self, user, session):
        """Creates random number od posts for given user, ranging from 1 to max_posts_per_user,
         given in bot_config.json file"""

        number_of_post_per_user = random.randrange(1, self.max_posts_per_user)
        i = 0
        while (i < number_of_post_per_user):
            while True:
                title = self.faker.sentence()
                content = self.faker.text()
                response = session.post(url='http://localhost:8000/api/posts/',
                                        data={'post_title': title, 'post_content': content},
                                        headers={'Authorization': 'Bearer ' + user.token})

                # check if token is expired, and get new one if it is
                if response.status_code == 401:
                    self.get_new_token(user, session)

                if response.status_code == 201:
                    user.posts.append(Post(title, content, user, json.loads(response.content)['like_post']))

                    i += 1
                    break

    def like(self):
        """Function that generates likes, following this criteria:
        Next user to perform a like is the user who has most posts and has not reached max likes.
        User performs “like” activity until he reaches max likes.
        User can only like random posts from users who have at least one post with 0 likes.
        If there is no posts with 0 likes, bot stops.
        Users cannot like their own posts.
        Posts can be liked multiple times, but one user can like a certain post only once."""

        session = requests.Session()
        while True:
            current_user = self.get_user_with_max_posts()
            posts_that_can_be_liked = self.get_available_posts(current_user)

            # all users have reached max likes limit, or there are no posts with 0 likes
            if current_user is None or len(posts_that_can_be_liked) == 0:
                break
            self.start_to_like(session, current_user, posts_that_can_be_liked)

    def start_to_like(self, session, user, posts):
        """For given user, start liking until number of user likes has reached max_likes_per_user,
         given in bot_config.json, or there are no available posts to like"""

        posts_copy = posts.copy()

        while user.likes < self.max_likes_per_user:
            while True:

                if len(posts_copy) <= 0:
                    return
                post = random.choice(posts_copy)

                response = session.get(post.like_link, headers={'Authorization': 'Bearer ' + user.token})

                # check if token is expired, and get new one if it is
                if response.status_code == 401:
                    self.get_new_token(user, session)

                if response.status_code == 201:
                    posts_copy.remove(post)
                    posts[posts.index(post)].likes_number += 1
                    user.likes += 1
                    break

    def get_user_with_max_posts(self):
        """Returns user who is next to perform like. It looks for the user with max number of posts,
         but who is not reached max number of likes, given in bot_config.json.
         If all users are reached max number of likes, function returns None"""

        max_posts = -1
        condition = False
        location = -1

        for user in self.created_users:

            if user.likes >= self.max_likes_per_user:
                continue

            if len(user.posts) > max_posts:
                condition = True
                max_posts = len(user.posts)
                location = self.created_users.index(user)

        if condition:
            return self.created_users[location]
        else:
            return None

    def get_available_posts(self, current_user):
        """Creates list of all possible posts, for current_user to perform like
        Check all users if they have at least one post with zero likes, and if there is,
        extends posts list with all user's posts
        """

        posts = []
        for user in self.created_users:
            if user == current_user:
                continue
            for post in user.posts:
                if post.likes_number == 0:
                    posts.extend(user.posts)
                    break

        return posts

    def get_credentials(self):
        """Returns random username, password and email, generated by faker module"""

        return {'username': self.faker.user_name(), 'password': self.faker.password(), 'email': self.faker.email()}

    def read_config_file(self):
        """Reads number_of_users, max_posts_per_user and max_likes_per_user from bot_config.json file,
         and assigns it to class attributes  """

        with open(os.path.abspath('bot_config.json')) as file:
            data = json.load(file)
            self.number_of_users = data['number_of_users']
            self.max_posts_per_user = data['max_posts_per_user']
            self.max_likes_per_user = data['max_likes_per_user']

    def handle(self, *args, **options):
        """Runs all bot's functions"""

        self.read_config_file()

        if self.number_of_users == 0:
            return

        self.sign_up_all()

        self.log_in()

        if self.max_posts_per_user != 0:
            self.create_all_posts()

        if self.max_likes_per_user != 0:
            self.like()

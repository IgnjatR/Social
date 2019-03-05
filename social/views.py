import clearbit
from django.conf import settings
from pyhunter import PyHunter
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .exceptions import EmailDoNotExists
from .models import Account, Post, Like
from .permisions import IsOwnerOrReadOnlyPost
from .serializers import AccountListSerializer, PostSerializer, LikeSerializer, AccountDetailsSerializer


class AccountListViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all().order_by('id')
    serializer_class = AccountListSerializer

    def perform_create(self, serializer):
        """Check if user is bot, and if it is not, use pyhunter to validate email, and use clearbit to enrich user data """

        user = serializer.save()
        bot = self.request.query_params.get('bot', '')
        if not bot:

            # NOTE if it is not working, it is because i have reached the limit for the number of verification requests per domain
            # to solve it temporarily, just change email domain to a different one
            if not self.check_if_mail_is_valid(user.email):
                raise EmailDoNotExists()

            clearbit.key = settings.CLEARBIT_KEY
            user.user_details = clearbit.Enrichment.find(email=user.email, stream=True)

        user.set_password(user.password)

        user.save()

    @action(detail=True)
    def read_details(self, request, pk=None):
        """Display full user details"""
        queryset = Account.objects.get(pk=pk)
        serializer = AccountDetailsSerializer(queryset, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def check_if_mail_is_valid(self, email):
        """Uses pyhunter to check if email is valid
        Return True if it is, and False if it is not valid"""
        hunter = PyHunter(api_key=settings.HUNTER_API_KEY)
        try:
            data = hunter.email_verifier(email)
            print(data)
            if data['result'] == 'undeliverable':
                return False
            return True
        except:
            return False


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('pk')
    serializer_class = PostSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnlyPost)

    @action(detail=True)
    def like_post(self, request, pk=None):
        """Function for post liking.
        Creates like, if user is authenticated, is not owner of the post, and if he is not already liked this post, else displays error."""
        post = self.get_object()
        if post.author == request.user:
            return Response({'error': 'You can not like your own post'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

        if request.user.is_anonymous:
            return Response({'error': 'You must be logged in !'}, status=status.HTTP_401_UNAUTHORIZED)
        like, created = Like.objects.get_or_create(related_post=post, related_user=request.user)

        if not created:
            return Response({'error': 'Already liked this post'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

        serializer = LikeSerializer(like, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True)
    def unlike_post(self, request, pk=None):
        """Function for post unliking.
                Deletes like, if user is authenticated, is not owner of the post, and if he already liked this post, else displays error."""
        post = self.get_object()
        user = request.user
        if user.is_anonymous:
            return Response({'error': 'You must be logged in !'}, status=status.HTTP_401_UNAUTHORIZED)

        if post.author == user:
            return Response({'error': 'You can not unlike your own post'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

        if Like.objects.filter(related_post=post, related_user=user).exists():
            like = Like.objects.get(related_post=post, related_user=user)
            like.delete()
            serializer = LikeSerializer(like, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response({'error': 'You did not liked this post, you can not unlike it'},
                        status=status.HTTP_405_METHOD_NOT_ALLOWED)


class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all().order_by('pk')
    serializer_class = LikeSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

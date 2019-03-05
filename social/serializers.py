from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.reverse import reverse

from .exceptions import PostTitleAlreadyExists
from .models import Account, Like, Post


class AccountListSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(style={'input_type': 'password'})

    account = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'password', 'account')
        extra_kwargs = {'password': {'write_only': True}}

    def get_account(self, obj):
        """Returns link to account details"""

        return reverse('accounts-read-details', args=[obj.pk], request=self.context['request'])


class PostSerializer(serializers.ModelSerializer):
    like_post = serializers.SerializerMethodField()
    unlike_post = serializers.SerializerMethodField()
    likes_number = serializers.SerializerMethodField()
    post_title = serializers.CharField(required=True)
    post_content = serializers.CharField(required=True)
    author = serializers.StringRelatedField(read_only=True)
    edit_post = serializers.SerializerMethodField()

    def create(self, validated_data):
        """Creates post if post_title does not exists, and assign post author to current, logged in user"""

        if Post.objects.filter(post_title=validated_data['post_title']).exists():
            raise PostTitleAlreadyExists
        validated_data['author'] = self.context['request'].user
        return super(PostSerializer, self).create(validated_data)

    class Meta:
        model = Post
        fields = ('like_post', 'unlike_post', 'id', 'post_title', 'post_content', 'author', 'likes_number', 'edit_post')

    def get_likes_number(self, obj):
        """Returns number of likes for post"""

        return obj.likes.count()

    def get_like_post(self, obj):
        """Returns link for post like"""

        return reverse('posts-like-post', args=[obj.pk], request=self.context['request'])

    def get_unlike_post(self, obj):
        """Return link for post unlike"""

        return reverse('posts-unlike-post', args=[obj.pk], request=self.context['request'])

    def get_edit_post(self, obj):
        """Return post details"""

        return reverse('posts-detail', args=[obj.pk], request=self.context['request'])


class AccountDetailsSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(style={'input_type': 'password'})
    posts = serializers.StringRelatedField(many=True, read_only=True)
    likes_number = serializers.SerializerMethodField()

    user_details = serializers.JSONField(read_only=True)

    class Meta:
        model = Account
        fields = (
            'id', 'username', 'first_name', 'last_name', 'email', 'password', 'posts', 'likes_number', 'user_details')

    def get_likes_number(self, obj):
        """Returns number of likes per user"""

        return obj.likes.count()


class LikeSerializer(serializers.ModelSerializer):
    related_user = serializers.StringRelatedField(read_only=True)

    def create(self, validated_data):
        """Creates like if user is not anonymous, and set like author to that user"""

        if self.context['request'].user.is_anonymous:
            return Response({'error': 'You must be logged in for this operation !'})

        validated_data['related_user'] = self.context['request'].user
        return super(LikeSerializer, self).create(validated_data)

    class Meta:
        model = Like
        fields = '__all__'

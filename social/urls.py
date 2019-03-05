from django.urls import path, include
from rest_framework import routers

from . import views

namespace = 'social'
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

router = routers.DefaultRouter()
router.register('accounts', views.AccountListViewSet, base_name='accounts')
router.register('posts', views.PostViewSet, base_name='posts')
router.register('likes', views.LikeViewSet, base_name='likes')

urlpatterns = [
    path('token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify', TokenVerifyView.as_view(), name='token_verify'),
    path('', include(router.urls)),
    path('docs', include(('rest_framework.urls', 'api'), namespace='social')),
]

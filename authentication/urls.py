from django.urls import path
from .views import RegisterUserView, UserInfoView, VerifyEmailView

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='auth_register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('userinfo/<int:user_id>/', UserInfoView.as_view(), name='user-info'),
    path('userinfo/', UserInfoView.as_view(), name='userinfo-self'),
    path('userinfo/<int:user_id>/', UserInfoView.as_view(), name='userinfo-specific'),
     path('verify-email/', VerifyEmailView.as_view(), name='verify-email')
]
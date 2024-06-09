from django.urls import path
from .views import RegisterUserView, UserInfoView, VerifyEmailView, LookupUsersView, ResetPasswordView, ForgotPasswordView, LoginUserView, ResendVerificationCodeView

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='auth_register'),
    path('login/', LoginUserView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('userinfo/<int:user_id>/', UserInfoView.as_view(), name='user-info'),
    path('userinfo/', UserInfoView.as_view(), name='userinfo-self'),
    path('userinfo/<int:user_id>/', UserInfoView.as_view(), name='userinfo-specific'),
     path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
     path('lookup/', LookupUsersView.as_view(), name='lookup_users'),
     path('password-reset/', ResetPasswordView.as_view(), name='password-reset'),
     path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
     path('resend-verification-code/', ResendVerificationCodeView.as_view(), name='resend-verification-code'),
    
]
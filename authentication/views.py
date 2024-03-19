from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from .models import User, UserInfo
from .serializers import UserSerializer, UserInfoSerializer
from django.utils import timezone
from django.contrib.auth import authenticate
from .utils import send_verification_email

class RegisterUserView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            send_verification_email(user)
            return Response({"user": serializer.data,  "detail": "Check your email for the verification code."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserInfoView(APIView):
   
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.request.method == 'POST':
            return  [AllowAny()]
        else:
            return [IsAuthenticated()]
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        try:
            # Retrieve the user by email
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

        # Check if the password is correct
        if user.check_password(password):
            # Proceed if the user is not active (assuming they are unverified)
            if not user.is_active:
                if UserInfo.objects.filter(user=user).exists():
                    return Response({"detail": "UserInfo already exists. Please verify your email to update your info."}, status=status.HTTP_400_BAD_REQUEST)

                # Exclude email and password from the serializer data
                mutable_data = request.data.copy()
                mutable_data.pop('email', None)
                mutable_data.pop('password', None)

                serializer = UserInfoSerializer(data=mutable_data)
                if serializer.is_valid():
                    serializer.save(user=user)
                    return Response({**serializer.data, email: email, password: password}, status=status.HTTP_201_CREATED)
               
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"detail": "Verified users should not use this method."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)
        
    def patch(self, request):
        userinfo = get_object_or_404(UserInfo, user=request.user)  # Ensure it's the user's own UserInfo
        serializer = UserInfoSerializer(userinfo, data=request.data, partial=True)  # Allow partial updates
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyEmailView(APIView):

    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')
        try:
            user = User.objects.get(email=email, verification_code=code)
        except User.DoesNotExist:
            return Response({"error": "Invalid email or verification code."}, status=status.HTTP_400_BAD_REQUEST)

        if timezone.now() - user.code_sent_at <= timezone.timedelta(minutes=30):  # 30 minutes validity
            user.is_active = True
            user.verification_code = None
            user.save()
            return Response({"success": "Email verified successfully."})
        else:
            return Response({"error": "Verification code has expired."}, status=status.HTTP_400_BAD_REQUEST)

class LookupUsersView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        last_50_users = User.objects.order_by('-last_login')[:50]
        serializer = UserSerializer(last_50_users, many=True)
        return Response(serializer.data)